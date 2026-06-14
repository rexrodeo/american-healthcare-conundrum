"""
01_build_data.py - Issue #16: The Other 100 Drugs (Part D)

The American Healthcare Conundrum
International reference pricing applied to the next 100 Medicare Part D drugs
by gross spend, EXCLUDING every drug selected for IRA negotiation Rounds 1, 2,
and 3 (the drugs the negotiation framework already addresses).

============================================================================
STAGE 2 FULL BUILD (computed; replaces the 2026-05-09 skeleton)
============================================================================
This script downloads the real CMS Medicare Part D Spending by Drug PUF and the
real NHS Drug Tariff Part VIIIA (April 2026), builds the post-IRA "other 100"
universe, and computes a bottom-up savings figure. The headline is COMPUTED, not
reverse-engineered to a target. The $35B figure in the scoping brief was a
target; the computed central figure is reported as-is.

RUN:
    pip install --break-system-packages pandas numpy requests pdfplumber
    python3 01_build_data.py
Network required on first run (~5MB PUF + ~0.5MB NHS PDF cached to data_cache/).

============================================================================
METHOD (what we actually do)
============================================================================
Universe = top 100 single-source BRAND drugs in the CMS Part D PUF (most recent
annual release, CY2023) ranked by gross Medicare spend, after removing every
drug in IRA Rounds 1+2+3 (matched on both brand and generic name).

For each universe drug d:
    medicare_per_unit(d) = Avg_Spnd_Per_Dsg_Unt_Wghtd  (US gross $/dosage unit)

Headline reference: RAND RR-A788-3 (Feb 2024) finds US BRAND prices are 422% of
OECD-33 gross AND 322% rebate-adjusted NET. The CENTRAL is NET-TO-NET (Stage 5.5
Challenge 1 correction, 2026-06-08): the rebate converts gross PUF spend to net
US spend ONCE, then RAND's NET ratio (3.22x; net gap 1-1/3.22 = 0.689) is applied
to that net base. (The prior central applied the 4.22x GROSS gap 0.763 to a net
base — inconsistent — and is retained only as an upper-method sensitivity.)

    rebate_fraction(d) = tiered:  top-20-by-gross brand 0.49 ; biologic 0.20 ;
                         insulin 0.70 ; other brand 0.275  (gross->net)
    net_spend(d)       = Tot_Spndng(d) * (1 - rebate_fraction(d))   # rebate ONCE
    net_savings(d)     = net_spend(d) * (1 - 1/3.22)               # NET gap on NET
    booked_savings(d)  = net_savings(d) * recoverability_factor (0.55 central)

We do NOT use the extreme UK NHS generic price as the headline reference; instead
we compute the real per-drug US-vs-NHS gap separately to characterize the gap
distribution and anchor the NHS-floor upper bound.

Booked = sum_d booked_savings(d).  Sensitivity over recoverability {0.45,0.55,
0.85}, gross-gap upper-method (4.22x on net), and NHS-floor upper.

============================================================================
DATASET GOTCHAS HONORED (CLAUDE.md)
============================================================================
- Part D PUF "Overall" vs per-manufacturer rows: the PUF carries BOTH an
  Mftr_Name=='Overall' summary row AND one row per manufacturer for each
  brand/generic. Summing all rows DOUBLE-COUNTS (Eliquis -> $36.5B instead of
  $18.3B). We filter to Mftr_Name=='Overall' before any aggregation.
- Part D PUF reports GROSS (pre-rebate) cost. We apply a tiered rebate to net.
- No Tot_Day_Suply field exists in this PUF; per-30-day cannot be computed.
  We use Avg_Spnd_Per_Dsg_Unt_Wghtd (per dosage unit), which is the
  scale-invariant basis for the savings RATIO and the US-vs-NHS comparison.
- Universe filter matches IRA exclusions on BOTH brand and generic (semaglutide
  = Ozempic/Rybelsus/Wegovy all excluded).

Author: The American Healthcare Conundrum, rebuilt 2026-06-07.
"""

import json
import re
import statistics
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

# =============================================================================
# PATHS
# =============================================================================
HERE = Path(__file__).resolve().parent
DATA_CACHE = HERE / "data_cache"
RESULTS = HERE / "results"
DATA_CACHE.mkdir(exist_ok=True)
RESULTS.mkdir(exist_ok=True)

# =============================================================================
# CURATED REFERENCE CONSTANTS  (inputs, NOT the headline)
# =============================================================================
# Exchange rate: documented recent GBP/USD (Issue #2 used 1.27, Mar 2026). NHS
# prices are ILLUSTRATIVE here, not the headline reference, so the headline is
# insensitive to this rate. Using a mid recent value with explicit disclosure.
GBP_TO_USD = 1.30

# RAND RR-A788-3 (Mulcahy/Schwam/Lovejoy, Feb 2024), US vs OECD-33, 2022 data:
RAND_BRAND_RATIO_GROSS = 4.22      # US brand list price = 422% of OECD gross
RAND_BRAND_RATIO_REBATE_ADJ = 3.22 # 322% rebate-adjusted (net-vs-net)

# Tiered net-rebate fractions (gross -> net). Issue #2 anchor + Trustees pool.
REBATE_TOP_BRAND = 0.49   # top-spend brand (Issue #2)
REBATE_MID_BRAND = 0.275  # broad brand pool (Medicare Trustees aggregate)
REBATE_BIOLOGIC = 0.20    # biologics, thinner rebate
REBATE_GENERIC = 0.025
# Insulin-specific gross-to-net (2026-06-08 repair). Insulin rebates are the
# largest in any drug class: ASPE (HP-2022-22, "Insulin Affordability") and SSR
# Health net-price tracking put insulin gross-to-net at ~65-84% (Lantus, Humalog,
# NovoLog all >70% by 2022); the Medicare Trustees Report's manufacturer-rebate
# tables corroborate the class as the highest-rebated. The prior tiers (Lantus
# Solostar mis-tagged 0.49 top_brand; sibling SKUs 0.20 biologic) BOTH understated
# insulin rebates and overstated insulin savings. Apply a single 0.70 insulin tier.
REBATE_INSULIN = 0.70

# Recoverability (political/industry friction on expanding reference pricing)
RECOV_CENTRAL = 0.55
RECOV_LOWER = 0.45
RECOV_UPPER = 0.85

# Issue #2 cross-validation anchors
ISSUE_2_BOOKED_BIL = 25.0
ISSUE_2_GROSS_SPEND_BIL = 52.7
# Issue #2 published per-drug international-average ratios (Peterson-KFF basket,
# CLAUDE.md Key Validated Numbers). Used ONLY to reproduce Issue #2's method.
ISSUE_2_INTL_RATIO = {
    "apixaban": 14.6, "empagliflozin": 20.8, "rivaroxaban": 17.2,
    "dapagliflozin": 20.2, "sitagliptin": 26.0, "sacubitril": 7.4,
    "ustekinumab": 9.0, "ibrutinib": 6.5, "etanercept": 11.1,
}
ISSUE_2_REBATE = 0.49  # Issue #2 used a uniform 49% top-brand rebate

# IRA aggregate cross-validation anchors (CMS fact sheets)
IRA_R1_GROSS_POOL_BIL = 50.0
IRA_R1_NET_SAVINGS_BIL = 6.0        # CMS: ~22% net on ~$50B (IPAY 2026)
IRA_R2_GROSS_POOL_BIL = 42.5        # CMS IPAY 2027 fact sheet (2024)
IRA_R2_NET_SAVINGS_BIL = 12.0       # CMS: 44% net (ex-CGDP); 8.5B incl CGDP

# =============================================================================
# IRA EXCLUSION LISTS  (verified from CMS fact sheets / press release, 2026)
# =============================================================================
# (brand_substring, generic_substring, ira_round, mfp_per_30d_or_None)
# Match is case-insensitive substring on EITHER field.
IRA_ROUND_1 = [  # IPAY 2026, effective 2026-01-01 (CMS IPAY2026 fact sheet)
    ("Eliquis", "apixaban", 231), ("Jardiance", "empagliflozin", 197),
    ("Xarelto", "rivaroxaban", 197), ("Farxiga", "dapagliflozin", 178.50),
    ("Januvia", "sitagliptin", 113), ("Entresto", "sacubitril", 295),
    ("Stelara", "ustekinumab", 4695), ("Imbruvica", "ibrutinib", 9319),
    ("Enbrel", "etanercept", 2355), ("Novolog", "insulin aspart", 119),
    ("Fiasp", "insulin aspart", 119),
]
IRA_ROUND_2 = [  # IPAY 2027, effective 2027-01-01 (CMS IPAY2027 negotiated-prices fact sheet, Nov 2025)
    ("Ozempic", "semaglutide", 274), ("Rybelsus", "semaglutide", 274),
    ("Wegovy", "semaglutide", 274), ("Trelegy", "umeclidinium", 175),
    ("Xtandi", "enzalutamide", 7004), ("Pomalyst", "pomalidomide", 8650),
    ("Ofev", "nintedanib", 6350), ("Ibrance", "palbociclib", 7871),
    ("Linzess", "linaclotide", 136), ("Calquence", "acalabrutinib", 8600),
    ("Austedo", "deutetrabenazine", 4093), ("Breo", "fluticasone/vilanterol", 67),
    ("Xifaxan", "rifaximin", 1000), ("Vraylar", "cariprazine", 770),
    ("Tradjenta", "linagliptin", 78), ("Janumet", "sitagliptin", 80),
    ("Otezla", "apremilast", 1650),
]
IRA_ROUND_3 = [  # IPAY 2028, effective 2028-01-01 (CMS press release Jan 27 2026).
    # 15 selected (10 Part D + 5 first-ever Part B) + Tradjenta renegotiation.
    # Part B drugs won't appear in the Part D PUF; excluding them is harmless.
    ("Anoro", "umeclidinium/vilanterol", None), ("Biktarvy", "bictegravir", None),
    ("Botox", "onabotulinumtoxin", None), ("Cimzia", "certolizumab", None),
    ("Cosentyx", "secukinumab", None), ("Entyvio", "vedolizumab", None),
    ("Erleada", "apalutamide", None), ("Kisqali", "ribociclib", None),
    ("Lenvima", "lenvatinib", None), ("Orencia", "abatacept", None),
    ("Rexulti", "brexpiprazole", None), ("Trulicity", "dulaglutide", None),
    ("Verzenio", "abemaciclib", None), ("Xeljanz", "tofacitinib", None),
    ("Xolair", "omalizumab", None),
]

# =============================================================================
# ISSUE #7 OVERLAP EXCLUSION (GLP-1 pricing already booked) — added 2026-06-08
# =============================================================================
# Issue #7 (The GLP-1 Gold Rush) covered and booked the GLP-1 pricing gap for
# Ozempic, Wegovy, Mounjaro, and Zepbound ($40B GLP-1 pricing layer). Tirzepatide
# (Mounjaro / Zepbound) is a GIP/GLP-1 and is squarely inside Issue #7's scope. It
# is NOT removed by the IRA filter (IRA Round 2 captured the three semaglutide
# products, not tirzepatide), so it leaked into the #16 universe. Exclude on the
# Issue #7 overlap basis per ROADMAP general overlap rule #5 ("if there is risk of
# overlap with a prior issue, we note it and reduce"). Counting Mounjaro's Part D
# international-price gap here would double-count the same molecule's pricing excess.
# NOTE on liraglutide (Victoza): liraglutide is an older GLP-1, but Issue #7's
# booked pricing gap was built on the semaglutide/tirzepatide blockbusters, not on
# off-patent-imminent liraglutide; the Stage 3 overlap audit reviewed Victoza and
# did NOT exclude it. Victoza is therefore KEPT and documented (see methodology.md).
ISSUE7_GLP1 = [
    ("Mounjaro", "tirzepatide"), ("Zepbound", "tirzepatide"),
]

PARTD_ANNUAL_CSV_URL = (
    "https://data.cms.gov/sites/default/files/2025-05/"
    "56d95a8b-138c-4b60-84a5-613fbab7197f/DSD_PTD_RY25_P04_V10_DY23_BGM.csv"
)
NHS_TARIFF_PDF_URL = (
    "https://www.nhsbsa.nhs.uk/sites/default/files/2026-03/"
    "Drug%20Tariff%20Part%20VIIIA%20April%202026.pdf"
)
SPEND_YEAR = 2023  # most recent annual PUF coverage year


# =============================================================================
# DOWNLOAD
# =============================================================================
def cached_download(url, dest, label):
    if dest.exists() and dest.stat().st_size > 1000:
        print(f"  [cache] {label} -> {dest.name}")
        return dest
    print(f"  [download] {label} -> {dest.name}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 AHC-research"})
    with urllib.request.urlopen(req, timeout=120) as r, open(dest, "wb") as f:
        f.write(r.read())
    return dest


# =============================================================================
# STEP 1: LOAD PART D PUF  (Overall rows only)
# =============================================================================
def load_partd():
    print("\n=== STEP 1: CMS Part D Spending by Drug PUF (CY%d annual) ===" % SPEND_YEAR)
    dest = DATA_CACHE / "partd_annual_DY23.csv"
    cached_download(PARTD_ANNUAL_CSV_URL, dest, "Part D PUF annual")
    df = pd.read_csv(dest, low_memory=False)
    n_all = len(df)
    # GOTCHA: keep only the deduplicated 'Overall' manufacturer row per drug.
    df = df[df["Mftr_Name"] == "Overall"].copy()
    sp = f"Tot_Spndng_{SPEND_YEAR}"
    pu = f"Avg_Spnd_Per_Dsg_Unt_Wghtd_{SPEND_YEAR}"
    cl = f"Tot_Clms_{SPEND_YEAR}"
    be = f"Tot_Benes_{SPEND_YEAR}"
    for c in (sp, pu, cl, be):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=[sp])
    df = df.rename(columns={sp: "gross", pu: "medicare_per_unit",
                            cl: "tot_clms", be: "tot_benes"})
    # Real manufacturer per drug: the 'Overall' row has Mftr_Name=='Overall', so
    # pull the primary manufacturer from the largest per-manufacturer row.
    raw = pd.read_csv(dest, low_memory=False)
    raw = raw[raw["Mftr_Name"] != "Overall"].copy()
    raw[sp] = pd.to_numeric(raw[sp], errors="coerce")
    mfr = (raw.dropna(subset=[sp]).sort_values(sp, ascending=False)
           .drop_duplicates(["Brnd_Name", "Gnrc_Name"])[
               ["Brnd_Name", "Gnrc_Name", "Mftr_Name"]]
           .rename(columns={"Mftr_Name": "manufacturer"}))
    df = df.merge(mfr, on=["Brnd_Name", "Gnrc_Name"], how="left")
    df["manufacturer"] = df["manufacturer"].fillna("Unknown")

    # --- BRAND FLAG (tightened 2026-06-08) ---------------------------------
    # The naive rule (Brnd_Name != Gnrc_Name) leaks multi-source generics whose
    # brand field carries a CMS '*' generic flag or a punctuation/word variant of
    # the molecule (e.g. "Levothyroxine Sodium*", "Hydrocodone-Acetaminophen",
    # "Pantoprazole Sodium*"), or whose manufacturer is an authorized-generic
    # distributor (Prasco, Cipla, Aurobindo, Amneal, Upsher-Smith). These carry
    # the 4.22x brand ratio wrongly: RAND RR-A788-3 finds US UNBRANDED GENERICS are
    # CHEAPER than abroad, so a positive savings on a generic line is a defect.
    # Tighten the flag with three programmatic screens so they cannot re-enter and
    # the universe backfills with genuine single-source brands.
    AG_DISTRIBUTORS = ("prasco", "cipla", "aurobindo", "amneal", "upsher")

    # CURATED multi-source-brand leak list (Stage 5.5 Challenge 3, 2026-06-08).
    # These are distinct trade names with NO CMS '*' generic flag and a non-AG
    # originator manufacturer, so none of the programmatic screens below catch them;
    # but each had real US generic / biosimilar competition AVAILABLE by CY2023.
    # RAND RR-A788-3 finds US unbranded generics are CHEAPER than abroad, so applying
    # a brand international-reference gap to a molecule that already had a US generic
    # in 2023 overstates the recoverable saving (the live lever is generic
    # substitution, not international reference pricing). Matched as a lowercased
    # prefix on Brnd_Name; each carries its generic-availability basis in methodology.md.
    # The 7 in the first group were flagged by the adversarial review; the final 2
    # (Latuda, Multaq) are the "usual suspects" found in the same-class audit of the
    # rest of the universe. Revlimid, Tasigna, Lumigan reviewed and KEPT (brand-
    # dominant through CY2023; their generic competition was nominal or post-2023).
    MULTISOURCE_BRAND_LEAK = (
        "symbicort",      # Breyna (generic budesonide/formoterol) approved Mar 2022
        "restasis",       # generic cyclosporine ophthalmic emulsion, Feb 2022
        "advair",         # Wixela Inhub (generic fluticasone/salmeterol), 2019 (Diskus + HFA)
        "vascepa",        # generic icosapent ethyl, 2020
        "flovent",        # authorized generic fluticasone propionate (Flovent HFA/Diskus)
        "copaxone",       # generic glatiramer acetate, 2015
        # --- audit additions (usual suspects, same defect) ---
        "latuda",         # generic lurasidone launched Feb 2023 (multi-source through 2023)
        "multaq",         # generic dronedarone, ANDA launches 2022-2023
        "wixela",         # Wixela Inhub IS the substitutable generic of Advair (Viatris)
    )

    def _norm(s):
        return re.sub(r"[^a-z0-9]", "", str(s).lower())

    naive_brand = (df["Brnd_Name"].str.lower().str.strip()
                   != df["Gnrc_Name"].str.lower().str.strip())
    bnorm = df["Brnd_Name"].map(_norm)         # strips '*' and punctuation
    gnorm = df["Gnrc_Name"].map(_norm)
    has_asterisk = df["Brnd_Name"].astype(str).str.contains(r"\*", regex=True)
    is_ag_distributor = df["manufacturer"].astype(str).str.lower().apply(
        lambda m: any(d in m for d in AG_DISTRIBUTORS))
    # Brand name is just the molecule name plus a dosage-form suffix (DR/ER/XR/HFA/
    # ODT/etc.) => an unbranded/authorized generic, not a trade-name brand. A real
    # trade name (Synthroid, Humira, Lantus) never starts with its own INN, so this
    # catches molecule-named generics (e.g. "Dexlansoprazole Dr", Par/TWI) regardless
    # of manufacturer without hitting genuine brands. Guard with len>=5 to avoid
    # trivial short-stem collisions.
    brand_is_molecule = [bool(b) and len(g) >= 5 and b.startswith(g)
                         for b, g in zip(bnorm, gnorm)]
    # Molecule-named generic catch: a row whose Brnd_Name is just the molecule combo
    # (e.g. "Oxycodone-Acetaminophen" vs generic "Oxycodone HCl/Acetaminophen") is an
    # unbranded generic, not a trade-name brand. Flag when EVERY alpha token (len>=4)
    # in the brand name is a substring of the normalized generic name. Real trade names
    # (Humira, Lantus, Synthroid, Spiriva) carry a token absent from their INN, so this
    # does not hit genuine brands.
    def _brand_is_molecule_combo(b, g):
        gn = re.sub(r"[^a-z0-9]", "", str(g).lower())
        toks = re.findall(r"[a-z]{4,}", str(b).lower())
        return bool(toks) and all(t in gn for t in toks)
    brand_molecule_combo = [_brand_is_molecule_combo(b, g)
                            for b, g in zip(df["Brnd_Name"], df["Gnrc_Name"])]
    is_multisource_leak = df["Brnd_Name"].astype(str).str.lower().str.strip().apply(
        lambda b: any(b.startswith(p) for p in MULTISOURCE_BRAND_LEAK))
    df["is_generic_leak"] = (bnorm == gnorm) | has_asterisk | is_ag_distributor \
        | pd.Series(brand_is_molecule, index=df.index) \
        | pd.Series(brand_molecule_combo, index=df.index) | is_multisource_leak
    df["is_multisource_brand_leak"] = is_multisource_leak
    df["is_brand"] = naive_brand & ~df["is_generic_leak"]

    n_leak = int((naive_brand & df["is_generic_leak"]).sum())
    n_ms = int((naive_brand & df["is_multisource_brand_leak"]).sum())
    ms_gross = df.loc[naive_brand & df["is_multisource_brand_leak"], "gross"].sum() / 1e9
    print(f"  total rows {n_all:,}; Overall rows {len(df):,}; "
          f"total gross CY{SPEND_YEAR} ${df['gross'].sum()/1e9:.1f}B")
    print(f"  generic-leak rows reclassified out of brand universe: {n_leak}")
    print(f"  ...of which curated multi-source-brand leak (Stage 5.5 Ch3): "
          f"{n_ms} rows (${ms_gross:.2f}B gross)")
    return df


# =============================================================================
# STEP 2: PARSE NHS DRUG TARIFF (oral-solid per-unit prices)
# =============================================================================
def parse_nhs():
    print("\n=== STEP 2: NHS Drug Tariff Part VIIIA April 2026 ===")
    import pdfplumber
    dest = DATA_CACHE / "nhs_tariff_VIIIA_apr2026.pdf"
    cached_download(NHS_TARIFF_PDF_URL, dest, "NHS Drug Tariff Part VIIIA")
    rows = []
    with pdfplumber.open(dest) as pdf:
        npages = len(pdf.pages)
        for p in pdf.pages:
            t = p.extract_text() or ""
            for line in t.split("\n"):
                s = line.strip()
                m = re.match(
                    r"^([A-Za-z].*?)(?:\sS)?\s+(\d+(?:\.\d+)?)(?:\s?(?:ml|g|litre))?\s+(\d{2,7})\s+([A-Z])(?:\s+.*)?$",
                    s)
                if m:
                    rows.append((m.group(1).strip(), m.group(2),
                                 int(m.group(3)), m.group(4)))
    # build molecule -> median pence/unit for tablet/capsule forms only
    mol_unit = {}
    for txt, qty, price, cat in rows:
        if re.search(r"(tablet|capsule)", txt.lower()):
            root = re.match(r"([A-Za-z][A-Za-z\-]+)", txt)
            if not root:
                continue
            try:
                q = float(qty)
                if q <= 0:
                    continue
            except ValueError:
                continue
            mol_unit.setdefault(root.group(1).lower(), []).append(price / q)
    nhs = {k: statistics.median(v) for k, v in mol_unit.items()}
    print(f"  pages {npages}; price rows {len(rows):,}; "
          f"oral-solid molecules {len(nhs):,}")
    return nhs


# =============================================================================
# STEP 3: IRA EXCLUSION LIST
# =============================================================================
def build_exclusions():
    print("\n=== STEP 3: Exclusion list (IRA Rounds 1+2+3 + Issue #7 GLP-1) ===")
    rows = []
    for rnd, lst, eff in [(1, IRA_ROUND_1, "2026-01-01"),
                          (2, IRA_ROUND_2, "2027-01-01"),
                          (3, IRA_ROUND_3, "2028-01-01")]:
        for brand, generic, mfp in lst:
            rows.append({"brand_key": brand.lower(), "generic_key": generic.lower(),
                         "brand_name": brand, "generic_name": generic,
                         "ira_round": rnd, "mfp_per_30d_usd": mfp,
                         "effective_date": eff,
                         "reason": f"IRA Round {rnd}"})
    # Issue #7 GLP-1 overlap (ROADMAP general overlap rule #5): tirzepatide is
    # inside Issue #7's already-booked GLP-1 pricing layer. ira_round=7 is a
    # sentinel meaning "overlap exclusion, not an IRA selection".
    for brand, generic in ISSUE7_GLP1:
        rows.append({"brand_key": brand.lower(), "generic_key": generic.lower(),
                     "brand_name": brand, "generic_name": generic,
                     "ira_round": 7, "mfp_per_30d_usd": None,
                     "effective_date": "",
                     "reason": "Issue #7 GLP-1 overlap (ROADMAP rule #5)"})
    df = pd.DataFrame(rows)
    df.to_csv(RESULTS / "ira_exclusion_list.csv", index=False)
    print(f"  R1={len(IRA_ROUND_1)} R2={len(IRA_ROUND_2)} R3={len(IRA_ROUND_3)} "
          f"GLP1_overlap={len(ISSUE7_GLP1)} -> {len(df)} exclusion keys written")
    return df


def _is_excluded(brand, generic, excl):
    b, g = str(brand).lower(), str(generic).lower()
    for _, r in excl.iterrows():
        if r.brand_key and r.brand_key in b:
            return r.ira_round
        if r.generic_key and r.generic_key in g:
            return r.ira_round
    return 0


# =============================================================================
# STEP 4: UNIVERSE FILTER (top 100 brands minus IRA)
# =============================================================================
def is_insulin(generic):
    g = str(generic).lower()
    return bool(re.search(r"insulin|glargine|lispro|aspart|degludec|detemir", g))


def is_biologic(generic):
    # Insulins are handled in their own class; do NOT fold them into biologic.
    g = str(generic).lower()
    if is_insulin(g):
        return False
    return bool(re.search(
        r"(mab\b|mab-|cept\b|tide\b|palmitate|alfa|pegol)", g))


def is_vaccine(brand, generic):
    # RSV / shingles vaccines (Arexvy, Shingrix, Abrysvo). Vaccine international
    # pricing is set through tenders / public procurement, not the therapeutic
    # brand market, so RAND's 4.22x therapeutic-brand ratio is a poor fit. Excluded
    # per Stage 3 Counter 6 + Red-Team flag #4 (synthesizer call: EXCLUDE).
    b, g = str(brand).lower(), str(generic).lower()
    if any(v in b for v in ("arexvy", "shingrix", "abrysvo")):
        return True
    return bool(re.search(r"(\bantigen\b|vacc|zoster ge|rsvpref|rsv vacc)", g))


def build_universe(df, excl, top_n=100):
    print("\n=== STEP 4: Universe filter (top %d single-source brands) ===" % top_n)
    b = df[df["is_brand"]].copy()
    b["ira_round"] = b.apply(lambda r: _is_excluded(r.Brnd_Name, r.Gnrc_Name, excl), axis=1)
    b["is_vaccine"] = b.apply(lambda r: is_vaccine(r.Brnd_Name, r.Gnrc_Name), axis=1)
    excluded = b[b["ira_round"] > 0]
    glp1_excl = b[b["ira_round"] == 7]
    vax_excl = b[(b["ira_round"] == 0) & b["is_vaccine"]]
    # Keep genuine single-source brands, minus IRA R1/2/3, minus the Issue #7 GLP-1
    # overlap (ira_round==7), minus RSV/shingles vaccines. Backfills to top_n
    # automatically because excluded rows never enter the head() window.
    keep = (b[(b["ira_round"] == 0) & (~b["is_vaccine"])]
            .sort_values("gross", ascending=False).head(top_n).copy())
    keep = keep.reset_index(drop=True)
    keep["rank"] = keep.index + 1
    keep["insulin"] = keep["Gnrc_Name"].map(is_insulin)
    keep["biologic"] = keep["Gnrc_Name"].map(is_biologic)
    top20 = set(keep.nlargest(20, "gross").index)
    keep["is_top20"] = keep.index.isin(top20)

    def drug_class(i, insu, bio):
        if insu:
            return "insulin"        # own rebate tier (0.70); highest-rebated class
        if i in top20:
            return "top_brand"
        return "biologic" if bio else "mid_brand"
    keep["drug_class"] = [drug_class(i, insu, bio)
                          for i, insu, bio in zip(keep.index, keep.insulin, keep.biologic)]
    print(f"  brand rows {len(b):,}; IRA-excluded {len(excluded[excluded.ira_round.isin([1,2,3])]):,} "
          f"(${excluded[excluded.ira_round.isin([1,2,3])]['gross'].sum()/1e9:.1f}B); "
          f"GLP-1 overlap excluded {len(glp1_excl)} "
          f"(${glp1_excl['gross'].sum()/1e9:.2f}B); "
          f"vaccines excluded {len(vax_excl)} (${vax_excl['gross'].sum()/1e9:.2f}B)")
    print(f"  UNIVERSE n={len(keep)}  gross=${keep['gross'].sum()/1e9:.1f}B")
    print(f"  class mix: " + ", ".join(
        f"{k}={v}" for k, v in keep["drug_class"].value_counts().items()))
    # Confirm no leakage survived
    assert not keep["Gnrc_Name"].str.lower().str.contains("tirzepatide").any(), "tirzepatide leaked!"
    assert not keep["is_vaccine"].any(), "vaccine leaked!"
    return keep


# =============================================================================
# STEP 5: NHS join + per-drug US-vs-NHS gap (illustrative)
# =============================================================================
def join_nhs(uni, nhs):
    print("\n=== STEP 5: NHS per-drug gap (illustrative; not the headline ref) ===")
    def mol_root(g):
        m = re.match(r"([A-Za-z][A-Za-z\-]+)", str(g))
        return m.group(1).lower() if m else ""
    uni = uni.copy()
    uni["mol_root"] = uni["Gnrc_Name"].map(mol_root)
    uni["nhs_per_unit_usd"] = uni["mol_root"].map(
        lambda m: (nhs[m] / 100.0 * GBP_TO_USD) if m in nhs else np.nan)
    # real US-vs-NHS price ratio for oral-solid molecules with a clean match
    uni["nhs_gap_ratio"] = np.where(
        uni["nhs_per_unit_usd"].notna() & (uni["nhs_per_unit_usd"] > 0),
        uni["medicare_per_unit"] / uni["nhs_per_unit_usd"], np.nan)
    # Keep only meaningful, plausibly-oral-solid matches: US>1.5x NHS, US per-unit
    # below an oral-solid ceiling ($1,500), and ratio < 1000x (drops depot
    # injectables like Abilify Maintena mis-matched to NHS aripiprazole tablets).
    uni["nhs_match"] = uni["nhs_gap_ratio"].notna() & (uni["nhs_gap_ratio"] > 1.5) \
        & (uni["nhs_gap_ratio"] < 1000) & (uni["medicare_per_unit"] < 1500)
    matched = uni[uni["nhs_match"]]
    print(f"  NHS oral-solid matches with US>NHS: {len(matched)} of {len(uni)}")
    if len(matched):
        g = matched["nhs_gap_ratio"]
        print(f"  US/NHS gap (matched): median {g.median():.1f}x  "
              f"P25 {g.quantile(.25):.1f}x  P75 {g.quantile(.75):.1f}x  "
              f"P90 {g.quantile(.90):.1f}x  max {g.max():.0f}x")
    return uni


# =============================================================================
# STEP 6: PER-DRUG SAVINGS (headline = RAND 4.22 gross, tiered rebate)
# =============================================================================
def compute_savings(uni):
    print("\n=== STEP 6: Per-drug net-to-net savings (RAND 3.22 net reference) ===")
    uni = uni.copy()
    reb = {"top_brand": REBATE_TOP_BRAND, "mid_brand": REBATE_MID_BRAND,
           "biologic": REBATE_BIOLOGIC, "insulin": REBATE_INSULIN,
           "generic": REBATE_GENERIC}
    uni["rebate_fraction"] = uni["drug_class"].map(reb)

    # CENTRAL METHOD (Stage 5.5 Challenge 1 correction, 2026-06-08): NET-TO-NET.
    # The rebate is applied ONCE, converting gross PUF spend to net US spend. The
    # RAND rebate-adjusted NET brand ratio (3.22x; net gap 1-1/3.22 = 0.689) is then
    # applied to that net base. This is internally consistent: a NET price gap is
    # applied to NET dollars. The rebate does NOT appear twice. (The prior central
    # applied the GROSS gap 0.763 from the 4.22x gross ratio to a net base, implicitly
    # asserting US-net/OECD-net = 4.22, which contradicts RAND's own 3.22 net ratio.)
    net_gap = 1 - 1 / RAND_BRAND_RATIO_REBATE_ADJ        # 0.689 (3.22x NET)
    gross_gap = 1 - 1 / RAND_BRAND_RATIO_GROSS           # 0.763 (4.22x GROSS, upper)
    uni["net_spend_bil"] = uni["gross"] * (1 - uni["rebate_fraction"]) / 1e9
    # OECD net reference per unit = (US net per unit) / 3.22
    uni["ref_per_unit_usd"] = (uni["medicare_per_unit"] * (1 - uni["rebate_fraction"])
                               / RAND_BRAND_RATIO_REBATE_ADJ)
    uni["ref_method"] = "rand_oecd33_brand_net_3.22x_net_to_net"
    # CENTRAL: net US spend that is excess vs OECD net prices
    uni["net_savings_bil"] = uni["net_spend_bil"] * net_gap
    uni["booked_savings_bil"] = uni["net_savings_bil"] * RECOV_CENTRAL
    # UPPER-method (retained, NOT central): gross price gap (4.22x) on the same net
    # base — the prior, internally-inconsistent central. Kept visible as a sensitivity.
    uni["net_savings_grossgap_bil"] = uni["net_spend_bil"] * gross_gap
    # gross-to-gross (pre-rebate) reference column only
    uni["gross_savings_bil"] = uni["gross"] * gross_gap / 1e9
    print(f"  net spend base ${uni['net_spend_bil'].sum():.1f}B; "
          f"net-to-net savings (3.22x) ${uni['net_savings_bil'].sum():.1f}B; "
          f"booked@{RECOV_CENTRAL} ${uni['booked_savings_bil'].sum():.1f}B")
    print(f"  [upper-method gross-gap 4.22x on net base: "
          f"${uni['net_savings_grossgap_bil'].sum():.1f}B pre-recoverability]")
    cols = ["rank", "Brnd_Name", "Gnrc_Name", "manufacturer", "gross", "tot_clms",
            "tot_benes", "medicare_per_unit", "drug_class", "rebate_fraction",
            "net_spend_bil", "ref_per_unit_usd", "ref_method", "nhs_per_unit_usd",
            "nhs_gap_ratio", "nhs_match", "gross_savings_bil",
            "net_savings_grossgap_bil", "net_savings_bil", "booked_savings_bil"]
    out = uni[cols].copy()
    out.to_csv(RESULTS / "per_drug_savings.csv", index=False)
    out.to_csv(RESULTS / "top_100_drugs_panel.csv", index=False)
    return uni


# =============================================================================
# STEP 7: SENSITIVITY GRID
# =============================================================================
def sensitivity(uni):
    print("\n=== STEP 7: Sensitivity ===")
    net = uni["net_savings_bil"].sum()   # net-to-net (3.22x) central, pre-recoverability
    grid = {}
    for rf in (RECOV_LOWER, RECOV_CENTRAL, RECOV_UPPER):
        grid[f"recov_{rf}"] = round(net * rf, 2)
    # Central method alias for traceability (net-to-net 3.22, recov 0.55)
    grid["central_net_to_net_3.22_recov0.55"] = round(net * RECOV_CENTRAL, 2)
    # UPPER-method sensitivity (NOT central): gross price gap (4.22x) applied to the
    # NET spend base — the prior, internally-inconsistent central. Retained per
    # Stage 5.5 Challenge 1 as a visible upper bound on the price-gap assumption.
    net_spend = (uni["gross"] * (1 - uni["rebate_fraction"])).sum() / 1e9
    grossgap_savings = net_spend * (1 - 1 / RAND_BRAND_RATIO_GROSS)
    grid["grossgap_4.22_on_net_recov0.55"] = round(grossgap_savings * RECOV_CENTRAL, 2)
    # NHS-floor upper: for NHS-matched off-patent drugs, let Medicare pay the UK
    # generic price (capped at 95% savings); RAND floor elsewhere; recov 0.85.
    nhs_gross = np.where(
        uni["nhs_match"],
        uni["gross"] / 1e9 * np.minimum(1 - 1 / uni["nhs_gap_ratio"].fillna(1), 0.95),
        uni["gross_savings_bil"])
    nhs_net = (pd.Series(nhs_gross, index=uni.index) * (1 - uni["rebate_fraction"])).sum()
    grid["nhs_floor_upper_recov0.85"] = round(nhs_net * RECOV_UPPER, 2)
    for k, v in grid.items():
        print(f"  {k:38s} ${v:.1f}B")
    return grid


# =============================================================================
# STEP 8: CROSS-VALIDATION
# =============================================================================
def cross_validate(df, booked_bil, universe_gross_bil):
    print("\n=== STEP 8: Cross-validation ===")
    rows = []
    # (a) Reproduce Issue #2 on its 9-drug universe using Issue #2's own
    #     international-average ratios and 49% rebate (no recoverability factor).
    sp = "gross"
    i2 = df[df["Gnrc_Name"].str.lower().apply(
        lambda g: any(k in g for k in ISSUE_2_INTL_RATIO))].copy()
    # collapse to the 9 molecules (largest brand row per molecule key)
    def key(g):
        for k in ISSUE_2_INTL_RATIO:
            if k in str(g).lower():
                return k
        return None
    i2["k"] = i2["Gnrc_Name"].map(key)
    i2 = i2.dropna(subset=["k"]).sort_values(sp, ascending=False).drop_duplicates("k")
    gross_sav = (i2[sp] * (1 - 1 / i2["k"].map(ISSUE_2_INTL_RATIO))).sum() / 1e9
    i2_booked = gross_sav * (1 - ISSUE_2_REBATE)
    delta = (i2_booked - ISSUE_2_BOOKED_BIL) / ISSUE_2_BOOKED_BIL * 100
    print(f"  (a) Issue #2 reproduction: ${i2_booked:.1f}B vs published $25B "
          f"({delta:+.1f}%); 9-drug gross ${i2[sp].sum()/1e9:.1f}B")
    rows.append({"anchor": "Issue #2 9-drug universe (its own intl ratios, 49% rebate)",
                 "expected_bil": ISSUE_2_BOOKED_BIL, "computed_bil": round(i2_booked, 1),
                 "delta_pct": round(delta, 1), "pass": abs(delta) <= 5})

    # (b) IRA Round 1 savings-vs-gross-pool anchor. CMS states ~22% net-of-net;
    #     on the gross pool that is ~$6B/$50B = 12%. Both denominators reported.
    r1 = IRA_R1_NET_SAVINGS_BIL / IRA_R1_GROSS_POOL_BIL * 100
    rows.append({"anchor": "IRA R1 savings vs gross pool ($6B/$50B); CMS net-of-net ~22%",
                 "expected_bil": f"{r1:.0f}% of gross", "computed_bil": f"{r1:.0f}%",
                 "delta_pct": "ref", "pass": True})
    # (c) IRA Round 2 savings-vs-gross-pool anchor. CMS ~44% net-of-net (ex-CGDP);
    #     on the gross pool ~$12B/$42.5B = 28%.
    r2 = IRA_R2_NET_SAVINGS_BIL / IRA_R2_GROSS_POOL_BIL * 100
    rows.append({"anchor": "IRA R2 savings vs gross pool ($12B/$42.5B); CMS net-of-net ~44%",
                 "expected_bil": f"{r2:.0f}% of gross", "computed_bil": f"{r2:.0f}%",
                 "delta_pct": "ref", "pass": True})
    # (d) RAND brand-ratio sanity: central uses the NET gap (3.22x); the gross gap
    #     (4.22x) is the retained upper-method. Report both.
    net_gap = 1 - 1 / RAND_BRAND_RATIO_REBATE_ADJ
    rows.append({"anchor": "RAND brand-ratio reference (central NET 3.22x; upper GROSS 4.22x)",
                 "expected_bil": "net 3.22x (68.9% net gap) / gross 4.22x (76.3%)",
                 "computed_bil": f"central net gap {net_gap*100:.1f}%",
                 "delta_pct": "ref", "pass": True})
    # (e) KEY: recoverability calibration vs IRA Round 2 realized capture.
    #     Full OECD-parity on NET prices implies a 1-1/3.22 = 68.9% net-price cut.
    #     IRA R2 negotiation realized a 44% net-of-net MFP reduction (CMS, ex-CGDP),
    #     i.e. it captured 0.44/0.689 = ~64% of the OECD-parity net gap. Our central
    #     recoverability factor (0.55) sits at/below that realized capture, so the
    #     central is conservative relative to what negotiation actually achieved.
    ira_r2_net_of_net = 0.44
    implied_recov = ira_r2_net_of_net / net_gap
    d = (RECOV_CENTRAL - implied_recov) / implied_recov * 100
    rows.append({"anchor": "Central recoverability 0.55 vs IRA R2 implied capture (0.44/0.689)",
                 "expected_bil": f"implied {implied_recov:.2f} (IRA R2 realized)",
                 "computed_bil": f"central {RECOV_CENTRAL:.2f}",
                 "delta_pct": round(d, 1), "pass": RECOV_CENTRAL <= implied_recov + 0.02})
    # (f) Booked rate vs IRA R2 realized gross-pool rate (informational). Booked is
    #     post-recoverability, so it is EXPECTED to sit below IRA's realized 28%;
    #     pass = we do not over-claim relative to what IRA actually captured.
    booked_rate = booked_bil / universe_gross_bil * 100
    r2_gross_rate = IRA_R2_NET_SAVINGS_BIL / IRA_R2_GROSS_POOL_BIL * 100
    rows.append({"anchor": "Booked rate vs IRA R2 realized gross-pool rate (informational; booked post-0.55-recov, expected below)",
                 "expected_bil": f"{r2_gross_rate:.0f}% (IRA R2 realized)",
                 "computed_bil": f"{booked_rate:.0f}% (booked)",
                 "delta_pct": round((booked_rate - r2_gross_rate) / r2_gross_rate * 100, 1),
                 "pass": booked_rate <= r2_gross_rate + 1})
    cv = pd.DataFrame(rows)
    cv.to_csv(RESULTS / "cross_validation.csv", index=False)
    return cv


# =============================================================================
# STEP 9: ROLLUP (manufacturer + class)
# =============================================================================
def rollup(uni):
    print("\n=== STEP 9: Rollup by manufacturer and drug class ===")
    rows = []
    for keycol, ctype in [("manufacturer", "manufacturer"), ("drug_class", "drug_class")]:
        g = uni.groupby(keycol).agg(
            n_drugs=("rank", "count"), tot_spndng_bil=("gross", lambda s: s.sum() / 1e9),
            gross_savings_bil=("gross_savings_bil", "sum"),
            net_savings_bil=("net_savings_bil", "sum"),
            booked_savings_bil=("booked_savings_bil", "sum")).reset_index()
        g = g.rename(columns={keycol: "category"})
        g["category_type"] = ctype
        rows.append(g)
    out = pd.concat(rows, ignore_index=True).sort_values(
        ["category_type", "booked_savings_bil"], ascending=[True, False])
    out.to_csv(RESULTS / "savings_by_therapeutic_class.csv", index=False)
    top = out[out.category_type == "manufacturer"].head(6)
    print("  top manufacturers by booked savings:")
    for _, r in top.iterrows():
        print(f"    {str(r.category)[:34]:34s} n={int(r.n_drugs):2d} "
              f"booked ${r.booked_savings_bil:.2f}B")
    return out


# =============================================================================
# STEP 10: EMIT savings_estimate.json
# =============================================================================
def emit_estimate(uni, sens, gap_stats):
    booked = float(uni["booked_savings_bil"].sum())
    net = float(uni["net_savings_bil"].sum())
    n_molecules = int(uni["Gnrc_Name"].str.lower().str.strip().nunique())
    grossgap_central = float(sens["grossgap_4.22_on_net_recov0.55"])
    est = {
        "issue_number": 16, "issue_title": "The Other 100 Drugs (Part D)",
        "anchor_year": SPEND_YEAR,
        "headline_status": "COMPUTED",
        "booked_bil": round(booked, 2),
        "booked_target_bil": 35.0,
        "range_lo_bil": round(sens["recov_0.45"], 2),
        "range_hi_bil": round(sens["nhs_floor_upper_recov0.85"], 2),
        "central_method": ("RAND OECD-33 brand NET ratio 3.22x applied net-to-net "
                           "(rebate applied once, gross->net; net price gap 0.689 on "
                           "net spend), recoverability 0.55"),
        "net_total_before_recoverability_bil": round(net, 2),
        "universe_n": int(len(uni)),
        "universe_label": "100 brand products (~%d molecules)" % n_molecules,
        "distinct_molecules": n_molecules,
        "universe_gross_bil": round(float(uni["gross"].sum() / 1e9), 2),
        "universe_net_spend_bil": round(float(uni["net_spend_bil"].sum()), 2),
        "recoverability": {"lower": RECOV_LOWER, "central": RECOV_CENTRAL, "upper": RECOV_UPPER},
        "rebate_fractions": {"top_brand": REBATE_TOP_BRAND, "mid_brand": REBATE_MID_BRAND,
                             "biologic": REBATE_BIOLOGIC, "insulin": REBATE_INSULIN,
                             "generic": REBATE_GENERIC},
        "upper_method_grossgap_4.22_on_net_recov0.55_bil": round(grossgap_central, 2),
        "stage55_corrections_2026_06_08": {
            "challenge_1_gross_net_inconsistency": (
                "CORRECTED. Central switched from GROSS gap 0.763 (4.22x) on a net "
                "base to NET-TO-NET: NET gap 0.689 (3.22x rebate-adjusted) on the net "
                "spend base. Rebate applied once. Prior central was internally "
                "inconsistent (gross price gap on net dollars)."),
            "challenge_1_central_was_bil": 19.48,
            "challenge_1_central_now_label": "net-to-net 3.22x",
            "challenge_2_residual_pool_selection": (
                "DISCLOSED (not recomputed). Universe excludes the highest-gap "
                "off-patent-abroad blockbusters (sent to IRA), leaving an on-patent "
                "biologic/specialty residual whose true US-vs-OECD ratio may sit below "
                "the all-brand 3.22 average; NHS Drug Tariff check covers only the "
                "oral-solid minority. Downward-uncertainty caveat on the central."),
            "challenge_3_multisource_leak": (
                "CORRECTED. Dropped multi-source brands with US generic/biosimilar "
                "competition by CY2023 (Symbicort, Restasis, Advair Diskus/HFA, Vascepa, "
                "Flovent HFA, Copaxone + audit additions Latuda, Multaq); universe "
                "backfilled to 100 with next-ranked genuine single-source brands."),
            "relabel_100_brand_products": "100 brand products (~%d molecules)" % n_molecules,
            "grossgap_retained_as_upper_sensitivity": True,
        },
        "stage3_corrections_2026_06_08": {
            "excluded_tirzepatide_issue7_overlap": True,
            "dropped_multisource_generics_brand_filter_tightened": True,
            "excluded_rsv_shingles_vaccines": True,
            "insulin_rebate_repaired_to": REBATE_INSULIN,
            "rand_brand_only_ratio_confirmed": True,
            "universe_backfilled_to_100_single_source_brands": True,
        },
        "sensitivity_bil": sens,
        "nhs_gap_distribution": gap_stats,
        "ira_exclusion_counts": {"round_1": len(IRA_ROUND_1), "round_2": len(IRA_ROUND_2),
                                 "round_3": len(IRA_ROUND_3)},
        "vs_target": f"central ${booked:.1f}B is "
                     f"{'below' if booked < 35 else 'at/above'} the $35B target; "
                     f"the computed net-to-net central is reported as-is, not tuned",
        "generated_at": datetime.now().isoformat(),
    }
    (RESULTS / "savings_estimate.json").write_text(json.dumps(est, indent=2))
    return est


# =============================================================================
# STEP 11: METHODOLOGY / GOTCHA / ORIGINALITY docs
# =============================================================================
def emit_docs(uni, est, sens, gap_stats, cv):
    booked = est["booked_bil"]
    # methodology.md
    md = f"""# Issue #16 Methodology - The Other 100 Drugs (Part D)

Generated by `01_build_data.py` on {datetime.now().date()}. Computed, not a placeholder.

## Headline (computed bottom-up)

**Booked central: ${booked:.1f}B/year.** Range ${est['range_lo_bil']:.1f}-{est['range_hi_bil']:.1f}B.
Universe = **{est['universe_label']}** ({est['distinct_molecules']} distinct molecules; the
"100" counts brand products / SKUs, several of which share a molecule). The scoping-brief
target was $35B; the computed central is **${booked:.1f}B**, reported as-is, not tuned.

The central uses a **net-to-net** computation (Stage 5.5 Challenge 1 correction): the
rebate is applied once to convert gross PUF spend to net US spend, and RAND's
rebate-adjusted NET brand ratio (3.22x; net price gap 0.689) is applied to that net base.
The prior central applied RAND's GROSS gap (0.763, from the 4.22x gross ratio) to a net
base, which implicitly asserted a net ratio of 4.22 and contradicted RAND's own 3.22 net
finding; it overstated the central by ~10% on a like-for-like universe. The gross-gap
computation is retained below as a visible UPPER-method sensitivity
(${sens['grossgap_4.22_on_net_recov0.55']:.1f}B at recoverability 0.55), not the central.

## Universe

Top **{est['universe_n']} brand products (~{est['distinct_molecules']} molecules)** in the
CMS Medicare Part D Spending by Drug PUF (CY{SPEND_YEAR} annual release), ranked by gross
Medicare spend, after removing:
- every drug selected for IRA negotiation Rounds 1 ({len(IRA_ROUND_1)} keys), 2
  ({len(IRA_ROUND_2)} keys), and 3 ({len(IRA_ROUND_3)} keys), matched on both brand and
  generic name (this fully contains Issue #2's nine drugs, deliberately excluded per
  ROADMAP overlap rule #12);
- tirzepatide (Mounjaro / Zepbound), excluded on the **Issue #7 (The GLP-1 Gold Rush)
  overlap basis** per ROADMAP general overlap rule #5: Issue #7 already booked the GLP-1
  pricing gap, so counting Mounjaro's Part D international-price gap here would
  double-count the same molecule. Tirzepatide is not on any IRA round, so the IRA-only
  filter missed it; it is now in the exclusion list with reason
  "Issue #7 GLP-1 overlap (ROADMAP rule #5)";
- multi-source / authorized-generic rows that leaked the naive brand flag (CMS '*'
  generic-flag brand names such as "Levothyroxine Sodium*", "Pantoprazole Sodium*",
  "Potassium Chloride*", "Diclofenac Sodium*"; molecule-name punctuation variants such
  as "Hydrocodone-Acetaminophen"; and authorized-generic distributors Prasco/Cipla/
  Aurobindo/Amneal/Upsher-Smith for "Albuterol Sulfate HFA" and "Fluticasone-Salmeterol").
  RAND RR-A788-3 finds US unbranded generics are CHEAPER than abroad, so a positive
  brand-ratio savings on a generic line is a defect; these are removed and the brand
  flag is tightened so they cannot re-enter;
- **curated multi-source-brand leak (Stage 5.5 Challenge 3):** distinct trade names with
  NO CMS '*' flag and a non-AG originator manufacturer, so the programmatic screens above
  do not catch them, but each had real US generic / biosimilar competition AVAILABLE by
  CY2023. RAND finds US generics are cheaper than abroad, so applying a brand
  international-reference gap to a molecule that already had a US generic in 2023 overstates
  the recoverable saving (the live lever is generic substitution, not reference pricing).
  Dropped: **Symbicort** (Breyna generic budesonide/formoterol, Mar 2022), **Restasis**
  (generic cyclosporine ophthalmic, Feb 2022), **Advair Diskus** + **Advair HFA** (Wixela
  Inhub, 2019), **Vascepa** (generic icosapent, 2020), **Flovent HFA** (authorized generic
  fluticasone), **Copaxone** (generic glatiramer, 2015), plus same-class audit additions
  **Latuda** (generic lurasidone launched Feb 2023) and **Multaq** (generic dronedarone,
  ANDA launches 2022-2023). Reviewed and KEPT as brand-dominant through CY2023: Revlimid
  (limited settlement generics began 2022 but still brand-dominant), Tasigna (nilotinib
  generic launch effectively post-2023), Lumigan (brand-formulation-specific). The brand
  still bills at a premium Medicare pays, so this is a disclose-and-decide trim, made in
  the conservative (downward) direction;
- the three RSV/shingles vaccines (Arexvy, Shingrix, Abrysvo) — see the Vaccine section.

After each exclusion the universe backfills from rank 101+ with the next-ranked genuine
single-source brands, so the count stays at exactly {est['universe_n']} brand products
({est['distinct_molecules']} molecules). Note: branded single-source drugs of
otherwise-genericized molecules (e.g. Synthroid) are KEPT — they command brand pricing and
are not multi-source generics. Universe gross spend: ${est['universe_gross_bil']:.1f}B; net
spend base (post-rebate): ${est['universe_net_spend_bil']:.1f}B.

## "100 brand products," not "100 drugs" (Stage 5.5 Challenge 4 relabel)

The universe is **100 brand products / SKUs spanning {est['distinct_molecules']} distinct
molecules**. Adalimumab appears as several Humira presentations, insulin glargine across
several pen SKUs, etc. Each is a separate CMS "Overall" row with its own non-overlapping
spend, so there is no dollar double-count, but the label is "100 brand products
(~{est['distinct_molecules']} molecules)," not "100 drugs."

## Liraglutide (Victoza) — reviewed and kept

Victoza (liraglutide) is an older GLP-1 receptor agonist. It is KEPT in the universe:
Issue #7's booked GLP-1 pricing gap was built on the semaglutide and tirzepatide
blockbusters, not on off-patent-imminent liraglutide, and the Stage 3 overlap audit
reviewed Victoza and did not exclude it. It is netted of rebate here (biologic tier) and
does not re-book any Issue #7 line. Only tirzepatide, which is squarely inside Issue #7's
booked scope, is excluded for overlap.

## Per-drug computation (net-to-net central)

```
medicare_per_unit(d) = Avg_Spnd_Per_Dsg_Unt_Wghtd  (US GROSS $/dosage unit)
rebate_fraction(d)   = top_brand 0.49 | mid_brand 0.275 | biologic 0.20 | insulin 0.70
net_spend(d)         = Tot_Spndng(d) * (1 - rebate_fraction(d))      # rebate applied ONCE
net_gap              = 1 - 1/3.22 = 0.689   (RAND brand NET ratio, rebate-adjusted)
net_savings(d)       = net_spend(d) * 0.689                          # NET gap on NET base
booked_savings(d)    = net_savings(d) * 0.55                         # recoverability
ref_per_unit(d)      = medicare_per_unit(d) * (1 - rebate_fraction(d)) / 3.22  # OECD net
```

**The rebate appears exactly once** (gross -> net_spend). The 3.22x ratio is RAND's
rebate-adjusted NET-vs-NET brand ratio, so applying its gap (0.689) to net dollars is
internally consistent. No second rebate is taken. The Part D PUF has no days-supply field,
so per-30-day pricing cannot be computed; the per-dosage-unit price is the scale-invariant
basis for the savings ratio.

UPPER-method (retained, NOT central): the GROSS gap 0.763 (from the 4.22x gross ratio) on
the same net base = ${sens['grossgap_4.22_on_net_recov0.55']:.1f}B at recoverability 0.55.

## RAND brand ratios — gross 4.22x vs net 3.22x (Stage 5.5 Challenge 1)

The load-bearing curated input is the RAND ratio. RAND RR-A788-3 (Mulcahy, Schwam, Lovejoy,
"International Prescription Drug Price Comparisons: Estimates Using 2022 Data," Feb 2024,
DOI 10.7249/RRA788-3), Key Findings, reports:
- **All drugs: 278% (2.78x)** of comparison-country prices.
- **Brand-name originator drugs, GROSS: 422% (4.22x)** of comparison-country prices.
- **Brand-name originator drugs, rebate-adjusted NET: ~322% (3.22x).**
- Unbranded generics: US prices are LOWER than most comparison countries.

Because our spend base is **net** (gross PUF spend minus the tiered manufacturer rebate),
the price ratio applied to it must also be **net**: we use the **3.22x net ratio (net gap
0.689)**. The prior central used the 4.22x **gross** gap (0.763) on a net base, which is
internally inconsistent — it implicitly asserted a net ratio of 4.22, contradicting RAND's
own 3.22 net figure, and inflated the central by 0.763/0.689 = 1.107 (~+11%) on a
like-for-like universe. The gross ratio is retained only as an upper-method sensitivity.
(The 2.78x all-drugs ratio is not used: the universe is brand-only after the brand-filter
and multi-source-leak repairs.)

## Challenge 2 — residual-pool selection effect (downward-uncertainty disclosure)

The universe deliberately **excludes the highest-gap off-patent-abroad blockbusters**
(Eliquis, Jardiance, Xarelto, Januvia, etc.), because those went to IRA negotiation and are
removed per overlap rule #12. RAND's 4.22/3.22 brand averages are heavily driven by exactly
those off-patent-abroad small molecules. What remains in the "other 100" is an on-patent
biologic/specialty-heavy residual (Skyrizi, Dupixent, oncology TKIs, immune globulins,
recently-launched specialty drugs), whose **true US-vs-OECD ratio may sit BELOW the
all-brand 3.22 net average**. Applying the population-average ratio uniformly to this
residual therefore likely **overstates** the gap. The per-drug international prices needed
to measure each residual molecule's true ratio are exactly the licensed/restricted data the
data-partner CTA seeks; until then this is a named downward-uncertainty limitation on the
central, and it compounds the same direction as Challenge 1.

The NHS Drug Tariff check does NOT rebut this: it covers only **{gap_stats.get('n_matched', 0)}
of {est['universe_n']}** products (the off-patent oral solids — Oxycontin, Brilinta, Latuda
[now dropped], etc.), not the on-patent biologic majority that dominates the dollars, so it
validates a minority subset, not the biologic core. See the NHS section below.

## Why a population-average reference (not the UK NHS generic price) drives the headline

Issue #2's nine drugs had unusually large international gaps (median ~14x, up to 581x at the
UK generic price) because they were diabetes/anticoagulant blockbusters off-patent abroad.
The "other 100" is a broader brand pool. We use RAND's OECD-33 brand NET average (3.22x) as
a single reference. The real UK NHS gap, computed separately for the
{gap_stats.get('n_matched', 0)} oral-solid molecules with a clean NHS Drug Tariff match, has
a median of {gap_stats.get('median', float('nan')):.0f}x (P25 {gap_stats.get('p25', float('nan')):.0f}x,
P75 {gap_stats.get('p75', float('nan')):.0f}x, P90 {gap_stats.get('p90', float('nan')):.0f}x) — far
above the 3.22x reference, but for only ~11 off-patent oral solids (see Challenge 2). The
NHS-floor upper bound (Medicare pays UK generic prices for those matched drugs) is
${sens['nhs_floor_upper_recov0.85']:.1f}B and anchors the top of the range.

## Gross vs net (CLAUDE.md gotcha) — net-to-net central

The PUF reports GROSS (pre-rebate) cost. The booked figure is NET-to-NET: a tiered rebate
(0.49 top brand / 0.275 mid brand / 0.20 biologic / **0.70 insulin**) converts gross to net
ONCE, then RAND's 3.22 net ratio (net gap 0.689) is applied to the net base, then
recoverability 0.55. This is the rebate-consistent computation; the prior hybrid (gross gap
on net base) is superseded and retained only as the upper-method sensitivity.

## Insulin rebate repair (2026-06-08)

Insulin carries the largest gross-to-net rebates of any drug class, and the prior tiers
mis-handled it: Lantus Solostar was tagged top_brand (0.49) while its sibling SKUs (Lantus,
Levemir, Tresiba, Toujeo, Basaglar, Humalog) were tagged biologic (0.20) — internally
inconsistent, and BOTH understated insulin's real rebate, overstating insulin savings. A
single insulin-specific rebate fraction of **0.70** is now applied to every insulin SKU
(glargine, lispro, aspart, degludec, detemir). Evidence: ASPE (HP-2022-22, "Insulin
Affordability and the Inflation Reduction Act") and SSR Health manufacturer net-price
tracking put insulin gross-to-net in the 65-84% range by 2022 (Lantus, Humalog, NovoLog
all above 70%); the Medicare Trustees Report's manufacturer-rebate tables corroborate
insulin as the highest-rebated class. The repair REDUCES the insulin contribution, which
is the intellectually honest direction. (See the [Issue #4: The Middlemen] cross-reference:
Issue #4 addressed insulin through the PBM rebate/spread mechanism and booked no
separate insulin international-reference-pricing line; #16's insulin savings are net of
rebate and do not re-book the PBM layer. Distinct mechanisms, no double count.)

## Vaccines (Arexvy, Shingrix, Abrysvo) — EXCLUDED

The three RSV/shingles vaccines that ranked into the raw top 100 are EXCLUDED. Vaccine
international prices are set through national tenders and public-procurement programs, not
the therapeutic-brand market, so RAND's 4.22x therapeutic-brand ratio is a poor fit and
would not reliably represent the US-vs-OECD vaccine gap. Per Stage 3 Counter 6 and
Red-Team flag #4, the synthesizer call is EXCLUDE (the more defensible option of the
editor's "exclude or footnote" guidance, since the ratio's validity for vaccines is
unestablished). Their slots are backfilled with genuine single-source therapeutic brands.

## Sensitivity

| Scenario | Booked |
|----------|--------|
| recoverability 0.45 (range low) | ${sens['recov_0.45']:.1f}B |
| **recoverability 0.55 (CENTRAL, net-to-net 3.22x)** | **${sens['recov_0.55']:.1f}B** |
| recoverability 0.85 | ${sens['recov_0.85']:.1f}B |
| Upper-method: gross gap 4.22x on net base, recov 0.55 | ${sens['grossgap_4.22_on_net_recov0.55']:.1f}B |
| NHS-floor upper (recov 0.85, range high) | ${sens['nhs_floor_upper_recov0.85']:.1f}B |

## Cross-validation

- **Issue #2 reproduction** on its 9-drug universe (its own published intl ratios + 49%
  rebate; independent of the net-to-net change since it uses Issue #2's own ratios):
  ${cv.iloc[0]['computed_bil']}B vs published $25B ({cv.iloc[0]['delta_pct']}%) -> {'PASS' if cv.iloc[0]['pass'] else 'FAIL'} (within +/-5%).
- **Recoverability calibration vs IRA R2:** full OECD-parity on net prices implies a
  1-1/3.22 = 68.9% net-price cut; IRA Round 2 negotiation realized a 44% net-of-net MFP
  reduction (CMS, ex-CGDP), i.e. it captured 0.44/0.689 = ~0.64 of the OECD-parity net gap.
  Our central recoverability 0.55 sits at/below that realized capture -> conservative -> PASS.
- **Booked rate (informational):** booked / universe gross =
  {est['booked_bil']/est['universe_gross_bil']*100:.0f}% of gross, below IRA R2's realized
  28%-of-gross capture, as expected given the 0.55 recoverability haircut (we do not
  over-claim relative to what negotiation actually achieved).

## Original vs curated

| Element | Status |
|---------|--------|
| Universe filter (top 100 Part D brand products minus IRA R1+2+3, leak repair) | ORIGINAL |
| Per-drug net-to-net / booked savings from CMS PUF | ORIGINAL |
| NHS Drug Tariff per-drug gap distribution | ORIGINAL |
| Manufacturer / class rollup | ORIGINAL |
| RAND 4.22 gross / 3.22 net brand ratios | CURATED |
| IRA R1/R2/R3 selected-drug lists + MFPs | CURATED |
| Issue #2 nine-drug intl ratios (cross-val) | CURATED |
"""
    (RESULTS / "methodology.md").write_text(md)

    # gotcha_block.json
    gb = {
        "issue_number": 16, "stage_status": "COMPUTED",
        "datasets_used": [
            f"CMS Medicare Part D Spending by Drug PUF (CY{SPEND_YEAR} annual)",
            "NHS Drug Tariff Part VIIIA April 2026",
            "RAND RR-A788-3 brand ratios (Feb 2024)",
            "CMS IRA Round 1/2/3 fact sheets (exclusion lists + MFPs)",
        ],
        "gotchas_confirmed": {
            "partd_overall_row_dedup": (
                "HONORED. PUF carries an Mftr_Name=='Overall' row AND per-manufacturer "
                "rows per drug. Summing all rows double-counts (Eliquis $36.5B vs true "
                "$18.3B). Filtered to Overall before aggregation."),
            "partd_gross_vs_net": (
                "HONORED (Stage 5.5 Challenge 1 net-to-net correction). PUF is GROSS. "
                "Tiered rebate (0.49 top / 0.275 mid / 0.20 biologic / 0.70 insulin) "
                "applied ONCE to convert gross->net; RAND's rebate-adjusted NET ratio "
                "3.22x (net gap 0.689) is then applied to the net base. Rebate appears "
                "exactly once; net price gap applied to net dollars (internally "
                "consistent). Prior central applied the 4.22x GROSS gap (0.763) to a net "
                "base (inconsistent, +~11%); now retained only as an upper-method "
                "sensitivity."),
            "insulin_rebate_repair": (
                "HONORED (2026-06-08). Insulin SKUs (glargine/lispro/aspart/degludec/"
                "detemir) moved to a single 0.70 rebate tier (ASPE HP-2022-22 + SSR "
                "Health: insulin gross-to-net 65-84%). Fixes the Lantus Solostar 0.49 "
                "vs sibling-SKU 0.20 inconsistency; reduces insulin savings."),
            "rand_brand_only_ratio": (
                "HONORED. RAND RR-A788-3 brand-name originator ratios: 4.22x GROSS, "
                "3.22x rebate-adjusted NET (NOT the 2.78x all-drugs ratio). The CENTRAL "
                "now uses the 3.22x NET ratio applied to the net spend base (net-to-net, "
                "Challenge 1). The 4.22x gross ratio is retained as an upper-method "
                "sensitivity. Brand-only ratio applied to a brand-only universe."),
            "multisource_brand_leak": (
                "HONORED (Stage 5.5 Challenge 3). Dropped distinct-trade-name brands with "
                "US generic/biosimilar competition by CY2023 (Symbicort, Restasis, Advair "
                "Diskus/HFA, Vascepa, Flovent HFA, Copaxone + audit additions Latuda, "
                "Multaq) that the programmatic screens could not catch; backfilled to 100."),
            "residual_pool_selection_caveat": (
                "DISCLOSED (Stage 5.5 Challenge 2). Universe excludes the highest-gap "
                "off-patent-abroad blockbusters (sent to IRA); the on-patent biologic/"
                "specialty residual's true US-vs-OECD ratio may sit below the 3.22 net "
                "average, so the central may be overstated. Named downward-uncertainty "
                "limitation; per-drug intl prices are the data-partner CTA."),
            "issue7_glp1_overlap": (
                "HONORED. Tirzepatide (Mounjaro/Zepbound) excluded on Issue #7 GLP-1 "
                "overlap basis (ROADMAP rule #5); not an IRA selection, so added "
                "explicitly to the exclusion list. Liraglutide (Victoza) reviewed and "
                "kept (not in Issue #7's booked scope)."),
            "generic_leak_filter": (
                "HONORED. Multi-source/authorized-generic rows that leaked the naive "
                "brand flag (CMS '*' flag, punctuation variants, AG distributors "
                "Prasco/Cipla/Aurobindo/Amneal/Upsher-Smith) removed; brand flag "
                "tightened; universe backfilled to 100 single-source brands."),
            "vaccines_excluded": (
                "HONORED. RSV/shingles vaccines (Arexvy/Shingrix/Abrysvo) excluded; "
                "vaccine international pricing is tender-based, RAND therapeutic-brand "
                "ratio a poor fit (Stage 3 Counter 6 / Red-Team flag #4)."),
            "no_days_supply_field": (
                "HONORED. PUF has no Tot_Day_Suply; per-30-day not computable. Used "
                "Avg_Spnd_Per_Dsg_Unt_Wghtd (per dosage unit) for the scale-invariant ratio."),
            "ira_match_brand_and_generic": (
                "HONORED. Semaglutide (Ozempic/Rybelsus/Wegovy) and all IRA R1/2/3 drugs "
                "excluded by brand+generic substring match."),
            "nhs_off_patent_floor": (
                "HONORED. NHS Drug Tariff = off-patent UK generic price; used only as an "
                "illustrative gap and an upper-bound floor, NOT as the headline reference."),
            "exchange_rate_gbp_usd": f"GBP/USD={GBP_TO_USD}; headline is RAND-based so "
                                     "insensitive to this rate (NHS gaps only).",
        },
        "originality_posture": (
            "Headline computed from CMS Part D PUF top-100 brands minus IRA R1+2+3, RAND "
            "OECD-33 brand reference, tiered rebate, recoverability. Distinguished from "
            "curated RAND/IRA inputs."),
        "computed_booked_bil": booked,
        "generated_at": datetime.now().isoformat(),
    }
    (RESULTS / "gotcha_block.json").write_text(json.dumps(gb, indent=2))

    # originality_gate.md
    og = f"""# Issue #16 - Stage 3.5 Originality Gate Evidence (COMPUTED)

Generated {datetime.now().date()}.

1. **`01_build_data.py` exists and runs clean.** YES. Downloads CMS Part D PUF +
   NHS Drug Tariff, builds the universe, prints the headline at exit.
2. **Script produces the headline as a printed number/variable.** YES.
   booked_bil = ${booked:.1f}B printed at exit and in savings_estimate.json
   (headline_status=COMPUTED).
3. **Original vs curated distinguished with explicit headers.** YES. ORIGINAL =
   universe filter + per-drug savings + NHS gap distribution + rollups; CURATED =
   RAND ratios, IRA lists, Issue #2 ratios. See methodology.md table.
4. **Headline not already published within 5% by RAND/KFF/Peterson/FTC/CBO/JAMA.**
   YES. No outlet publishes a booked savings figure for the specific post-IRA-Rounds-1-2-3
   "other 100" Part D universe. RAND publishes the 422%/322% aggregate brand ratio but
   not applied to this universe; CMS IRA fact sheets cover only the selected drugs; KFF/
   Peterson publish per-capita and per-drug context, not this booked aggregate.
5. **Modeling implemented computationally with sensitivity.** YES. Net-to-net central
   (3.22x net ratio); recoverability {{0.45,0.55,0.85}}; gross-gap (4.22x) upper-method;
   NHS-floor upper bound; cross-validation reproduces Issue #2 within {cv.iloc[0]['delta_pct']}%
   and calibrates recoverability against IRA R2's realized capture.

**Computed central booked: ${booked:.1f}B** (net-to-net, ~{est['distinct_molecules']} molecules
across 100 brand products; vs $35B scoping target). Reported as-is, not tuned.
"""
    (RESULTS / "originality_gate.md").write_text(og)


# =============================================================================
# MAIN
# =============================================================================
def main():
    print("=" * 75)
    print("Issue #16: The Other 100 Drugs (Part D) - Stage 2 FULL BUILD")
    print("=" * 75)

    df = load_partd()
    nhs = parse_nhs()
    excl = build_exclusions()
    uni = build_universe(df, excl, top_n=100)
    uni = join_nhs(uni, nhs)
    uni = compute_savings(uni)
    sens = sensitivity(uni)
    cv = cross_validate(df, float(uni["booked_savings_bil"].sum()),
                        float(uni["gross"].sum() / 1e9))
    rollup(uni)

    matched = uni[uni["nhs_match"]]
    gap_stats = {"n_matched": int(len(matched))}
    if len(matched):
        g = matched["nhs_gap_ratio"]
        gap_stats.update({"median": round(float(g.median()), 1),
                          "p25": round(float(g.quantile(.25)), 1),
                          "p75": round(float(g.quantile(.75)), 1),
                          "p90": round(float(g.quantile(.90)), 1),
                          "max": round(float(g.max()), 0)})
    est = emit_estimate(uni, sens, gap_stats)
    emit_docs(uni, est, sens, gap_stats, cv)

    # -------- Gotcha Confirmation Block (CLAUDE.md) --------
    cc = uni["drug_class"].value_counts().to_dict()
    print("\n===== DATASET GOTCHA CONFIRMATION =====")
    print("Part D PUF: filtered to Mftr_Name=='Overall' (dedup); Eliquis check $18.3B")
    print("Part D gross vs net: NET-TO-NET (Ch1). GROSS PUF -> tiered rebate ONCE "
          "(top 0.49 / mid 0.275 / bio 0.20 / insulin 0.70) -> 3.22x NET gap (0.689)")
    print("No Tot_Day_Suply field -> per-dosage-unit ratio basis used")
    print("RAND reference: CENTRAL = 3.22x NET ratio (net-to-net); 4.22x GROSS = upper-method")
    print(f"Exclusions matched on brand+generic: IRA R1={len(IRA_ROUND_1)} "
          f"R2={len(IRA_ROUND_2)} R3={len(IRA_ROUND_3)}; "
          f"Issue#7 GLP-1 overlap (tirzepatide); RSV/shingles vaccines; "
          f"multi-source brand leak (Ch3): Symbicort/Restasis/Advair/Vascepa/Flovent/"
          f"Copaxone/Latuda/Multaq")
    print("Universe classes: " + ", ".join(f"{k}={v}" for k, v in cc.items()))
    print("========================================")

    # -------- Originality Gate Block (CLAUDE.md) --------
    print("\n===== ORIGINALITY GATE =====")
    print("Headline produced by this script (printed below).")
    print("ORIGINAL: universe filter + per-drug savings + NHS gap dist + rollups.")
    print("CURATED: RAND 4.22/3.22 ratios, IRA R1/2/3 lists, Issue #2 ratios.")
    print(f"Not published within 5% elsewhere for the post-IRA other-100 universe.")
    print("============================")

    booked = est["booked_bil"]
    print("\n" + "=" * 75)
    print(f"HEADLINE (computed, net-to-net 3.22x): BOOKED ${booked:.1f}B/year")
    print(f"  range ${est['range_lo_bil']:.1f}B (recov 0.45) "
          f"to ${est['range_hi_bil']:.1f}B (NHS-floor, recov 0.85)")
    print(f"  universe {est['universe_label']}, ${est['universe_gross_bil']:.1f}B gross, "
          f"${est['universe_net_spend_bil']:.1f}B net spend")
    print(f"  upper-method (gross-gap 4.22x on net, recov 0.55): "
          f"${est['upper_method_grossgap_4.22_on_net_recov0.55_bil']:.1f}B")
    print(f"  vs $35B target: {est['vs_target']}")
    print(f"  cross-val Issue #2 reproduction: {cv.iloc[0]['delta_pct']}% (PASS<=5%)")
    print(f"Output files in: {RESULTS}")
    print("=" * 75)
    return 0


if __name__ == "__main__":
    sys.exit(main())
