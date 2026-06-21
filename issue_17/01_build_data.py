"""
01_build_data.py - Issue #17: The Part B Pharmacy Premium

The American Healthcare Conundrum
International reference pricing applied to Medicare Part B physician-administered
drugs (oncology biologics, infused / injected monoclonal antibodies, ophthalmology
biologics, immunology infusions), identified by HCPCS J-codes, paid at Average
Sales Price (ASP) + 6 percent.

============================================================================
STAGE 2 FULL BUILD (computed; replaces the 2026-05-09 skeleton)
============================================================================
This script downloads the real CMS Medicare Part B Spending by Drug PUF (CY2023,
release year 2025, "DYT23"), builds the single-source brand/biologic Part B
universe with an auditable exclusion waterfall, and computes a bottom-up
recoverable savings figure. The headline is COMPUTED, not reverse-engineered to
the $15B scoping target. If the honest number lands at $9B or $22B, that is the
number.

RUN:
    pip install --break-system-packages pandas numpy
    python3 01_build_data.py
Network required on first run (~0.3MB PUF cached to data_cache/).

============================================================================
METHOD (what we actually do) — STAGE 5.5 CORRECTED (2026-06-09)
============================================================================
THE INTERNATIONAL RATIO (Stage 5.5 Challenge 1 — CORRECTED). The central ratio is
the Part-B-channel-appropriate published figure: MedPAC June 2019 / ASPE 2018
EX-MANUFACTURER 1.8x (19 high-income OECD). RAND RR-A788-3's 3.22x is NOT used as
the central, because it is US-net / international-GROSS (RAND nets only the US side,
and only the retail channel: RAND explicitly applied its invoice-to-net reduction
"to retail-dispensed brand-name drugs only ... because drugs dispensed through other
channels — for example, physician-administered drugs — appear to be less likely to
have any rebates"). Part B is exactly that "other channel," so 3.22x is the wrong
ratio for it. There is NO symmetric net-to-net international ratio published for
Part B biologics (the US ASP side is near-net for this channel; the international
net side is confidential) — that absence is the lead data-partner CTA. 3.22x is
retained ONLY as the aggressive ceiling (justified only if one accepts the
US-net/intl-gross asymmetry as a genuine recoverable gap). 1.5x is the conservative
stress floor (below the published 1.8x).

THE SPEND BASE (Stage 5.5 Challenge 2 — REBUTTED, disclosure added). spend_d is the
ASP+6% ALLOWED CHARGE (Medicare program payment + beneficiary liability), realized
at ~ASP+4% post-sequester (empirically Tot_Spndng ~= payment_allowance x 0.98 ~=
1.039 x bare_ASP). The international ratio is an EX-MANUFACTURER (ingredient) ratio.
We do NOT deflate the base to bare ASP, because the ASP+6% add-on is PROPORTIONAL:
under international reference pricing the same statutory add-on rides down with the
ingredient price, so the gap fraction g applied to the payment base yields the
correct SYSTEM saving. Algebra (per unit):
    S_now = k*ASP ;  under ref pricing ASP -> ASP/ratio ;  add-on % k unchanged
    S_ref = k*(ASP/ratio)
    saving = S_now - S_ref = k*ASP*(1 - 1/ratio) = S_now * g = Tot_Spndng * g
The reduction in the add-on dollars (from 0.039*ASP to 0.039*ASP/ratio) is a real
system saving, so keeping the whole payment base is correct, NOT an over-recovery.
We pair the base with the EX-MANUFACTURER 1.8x (not the payment-rate 2.05x) so the
ratio stays an ingredient ratio and the add-on is not double-counted.

NET-TO-NET caveat (honest, post-correction). The US side (ASP) is already net by
statute (SSA 1847A(c)(3)) and EXCLUDES Medicaid 1927 rebates and 340B prices. The
international side at 1.8x (MedPAC/ASPE ex-manufacturer) is the published Part-B
channel ratio; a true per-molecule net-to-net comparison is not possible from public
data (the data-partner ask). We do NOT apply any Part-D-style rebate haircut on top
of ASP (that would double-net the US side, the inverse of Issue #16's error).

For each Part B drug d in the universe:
    spend_d        = Tot_Spndng_2023        (ASP+6% allowed charge; payment base)
    intl_ratio_d   = US ex-manufacturer / international ex-manufacturer (default =
                     MedPAC/ASPE 1.8x; per-molecule override where a credible net
                     source exists)
    gap_fraction_d = 1 - (1 / intl_ratio_d)  (1.8 -> 0.4444)
                     * HALVED for genuinely-biosimilar-competed-by-CY2023 originators
                       (Challenge 3); ZEROED for true generics, Q5xxx biosimilar
                       products, and non-Q5 follow-ons (tbo-filgrastim).

    BOOKED = recoverability x SUM_d [ spend_d x gap_fraction_d x non340B_share_d ]

Where:
- non340B_share removes the 340B-acquired volume's international-gap dollars and
  reserves them for Issue #19 (the domestic 340B acquisition spread). Per the
  Stage 0 brief Section 3 Option (b): #17 = international net price gap on
  NON-340B-acquired Part B drug spend; #19 = domestic 340B acquisition spread on
  340B-acquired Part B drug spend. Different counterfactuals, different reference
  prices, additive.
- recoverability is the policy-friction haircut; central 0.55 (Issue #16
  precedent, Andrew's prior call), sensitivity 0.40-0.70.

EXCLUSIONS (each a named, printed step with dollars, so the waterfall from the
$50.79B total to the universe is auditable):
  1. Skin substitutes (Q4xxx) — not internationally-priced pharmacy biologics; a
     distinct policy story; no clean international comparator.
  2. Vaccines (90xxx / 91xxx CPT, and RSV/zoster brands) — set through CDC/public
     tender, not the buy-and-bill therapeutic-brand market.
  3. Immune globulins and blood/plasma products — dual-benefit commodities with
     poor international net matching; excluded on data-quality grounds.
  4. GLP-1s (asserted empty in Part B; Issue #7 overlap) — none present.
  5. Biosimilar-AVAILABLE ORIGINATOR reference lines are NOT excluded wholesale: ASP
     is the real blended price paid and already reflects biosimilar competition, so
     keeping the actual ASP and letting the RAND brand ratio under-apply where ASP
     is already low is the more honest treatment. We FLAG biosimilar-available
     originators and report their spend separately. BUT products that are THEMSELVES
     biosimilars (the Q5xxx HCPCS code block) are the cheaper competitor, not the
     brand originator, so the RAND brand-originator gap is ZEROED for them (kept in
     the panel, zero booked contribution). The screen is the Q5xxx prefix, NOT the
     FDA 4-letter suffix (novel originators like Darzalex Faspro / Vabysmo / Ultomiris
     / Enhertu carry suffixes but are not Q5 and keep the full gap). (methodology.md.)

============================================================================
DATASET GOTCHAS HONORED (CLAUDE.md / data_sources.md)
============================================================================
- "Total Spending" = the full value of the product (Medicare program payment +
  beneficiary liability). It is an ASP-derived allowed-charge base, NOT a charge
  or a cost. Nominal CY2023 dollars.
- ASP (Avg_DY23_ASP_Price) is already NET of commercial rebates/discounts by
  statute; it EXCLUDES 340B prices (so the published ASP is the non-340B net
  price) and is NOT compressed by IRA inflation rebates (those cut beneficiary
  coinsurance only, not the payment limit). => No Part-D rebate haircut on the US
  base. NOTE (Stage 5.5): there is NO symmetric net-to-net international ratio for
  Part B; the US side is near-net for this physician-administered channel, but the
  international NET side is confidential, so we anchor on the MedPAC/ASPE
  EX-MANUFACTURER 1.8x channel ratio (central) and disclose the asymmetry as the
  lead data-partner CTA. The spend base is the ASP+6% allowed charge (payment base);
  the add-on is proportional, so the ex-manufacturer gap on the payment base yields
  the correct system saving (Challenge 2 rebuttal).
- IRA Part B negotiation (IPAY 2028, first-ever Part B drugs) is post-dated to
  2028; the CY2023 pre-negotiation ASP is the correct present-day baseline. Any
  universe drug that is an IPAY-2028 selection is KEPT (the gap exists now) and
  FLAGGED, with a sensitivity line showing the booked number if excluded.

Author: The American Healthcare Conundrum, built 2026-06-09.
"""

import json
import re
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

SPEND_YEAR = 2023  # most recent annual Part B PUF coverage year (DYT23, RY25)

PARTB_ANNUAL_CSV_URL = (
    "https://data.cms.gov/sites/default/files/2025-05/"
    "f52d5fcd-8d93-481d-9173-6219813e4efb/"
    "DSD_PTB_RY25_P06_V10_DYT23_HCPCS-%20250430.csv"
)

# =============================================================================
# CURATED REFERENCE CONSTANTS  (inputs, NOT the headline)
# =============================================================================
# ----------------------------------------------------------------------------
# INTERNATIONAL RATIO LADDER (Stage 5.5 Challenge 1 corrected, 2026-06-09)
# ----------------------------------------------------------------------------
# CENTRAL = MedPAC June 2019 Ch.3 / ASPE 2018 EX-MANUFACTURER 1.8x (19 OECD), the
# Part-B-channel-appropriate published ratio, confirmed twice on this exact channel.
# Paired with the ASP+6% payment base via the proportional-add-on algebra (the ratio
# is an EX-MANUFACTURER ratio, so the add-on rides down proportionally and is not
# double-counted; that is why we use 1.8x ex-mfr, NOT the 2.05x payment-rate ratio).
PARTB_RATIO_CENTRAL = 1.8         # MedPAC/ASPE ex-manufacturer  <- CENTRAL
PARTB_RATIO_CONSERVATIVE = 1.5    # downside stress floor (below published 1.8x)

# RAND RR-A788-3 (Mulcahy/Schwam/Lovejoy, Feb 1, 2024), 2022 data: brand-originator
# US = 422% gross; "over three times as high" (~322%) AFTER a US-side rebate
# adjustment that RAND applied to RETAIL-dispensed drugs only and that nets ONLY the
# US side (international stays gross list). For Part B (a physician-administered
# channel RAND says lacks those rebates, and an asymmetric US-net/intl-gross ratio),
# 3.22x OVERSTATES the gap. Retained ONLY as the aggressive ceiling.
RAND_BRAND_RATIO_NET = 3.22       # US-net / intl-GROSS, retail-calibrated -> AGGRESSIVE CEILING
RAND_BRAND_RATIO_GROSS = 4.22     # 422% list (gross) — extreme upper reference only

# MedPAC June 2019: Part B payment (106% ASP) = 2.05x avg of 19 high-income OECD;
# ex-manufacturer 1.8x. ASPE 2018: 1.8x. The 2.05x PAYMENT-RATE ratio is NOT used
# against the payment base (it would double-count the add-on); carried for the
# sensitivity table only. 1.8x EX-MANUFACTURER is the central.
MEDPAC_2019_RATIO = 2.05          # payment-rate ratio (with add-on), 19 OECD — sensitivity only
MEDPAC_2019_EXMFR_RATIO = 1.8     # ex-manufacturer ratio — CENTRAL anchor
ASPE_2018_RATIO = 1.8

# 340B share of separately-paid Part B drug spend. MedPAC's OPPS-remedy analysis
# put the average minimum 340B discount at 22.5% of ASP (a 2020 acquisition survey
# found ASP-28.7%); CMS would have spent ~$4B less in CY2024 paying 340B-acquired
# Part B drugs at acquisition cost. The 340B-acquired SHARE of separately-paid Part
# B drug spend (the volume fraction we must remove and reserve for #19) is large but
# not precisely public at the J-code level (needs JG/TB-modifier claims, restricted).
# We use a defensible central share with sensitivity; the precise per-drug 340B share
# is the data-partner ask. Literature anchors: 340B DSH hospitals administer a large
# and growing fraction of HOPD separately-paid Part B drugs; GAO/MedPAC analyses put
# the 340B-acquired share of separately-paid Part B (Medicare) drug spend in the
# ~28-45% range depending on year and definition. Central 0.35.
SHARE_340B_CENTRAL = 0.35         # 340B-acquired share of separately-paid Part B spend
SHARE_340B_LOWER = 0.25           # -> non340B 0.75 (more spend stays in #17)
SHARE_340B_UPPER = 0.45           # -> non340B 0.55 (more reserved for #19)

# Recoverability (political/industry/operational friction on international ref pricing).
# This factor is the SINGLE home for the buy-and-bill / add-on political friction
# (Stage 5.5 Challenge 2/5): the base is kept whole (not /1.06), so the friction on
# the least-recoverable add-on dollars is carried here once, not double-counted.
RECOV_CENTRAL = 0.55
RECOV_LOWER = 0.40
RECOV_UPPER = 0.70

# ----------------------------------------------------------------------------
# BIOSIMILAR-COMPETED-BY-CY2023 ORIGINATORS (Stage 5.5 Challenge 3 corrected)
# ----------------------------------------------------------------------------
# Molecules with MATURE US biosimilar competition in or before the CY2023 anchor
# year. For these ORIGINATOR lines the US ASP is already biosimilar-depressed AND the
# international price has also fallen with biosimilar competition, so the US-vs-intl
# RATIO is below the monopoly average. We apply a HALF-GAP (gap x BIOSIM_GAP_FACTOR)
# to their originator reference lines. CRITICAL: this is restricted to molecules
# genuinely competed by CY2023 — it EXCLUDES substring false positives that the old
# `biosimilar_avail` flag caught:
#   - novel ADCs/combos matched by substring (Enhertu/fam-trastuzumab-deruxtecan,
#     Kadcyla/ado-trastuzumab, Phesgo/pertuzumab-trastuzumab) — no biosimilar, full gap
#   - originators whose biosimilars launched AFTER CY2023 (Eylea/aflibercept 2024-25,
#     Prolia/denosumab 2025, Soliris/eculizumab 2025) — monopoly in the anchor year,
#     full gap.
BIOSIM_COMPETED_CY2023 = {
    "rituximab", "bevacizumab", "trastuzumab", "pegfilgrastim", "filgrastim",
    "tbo-filgrastim", "epoetin", "darbepoetin", "ranibizumab", "infliximab",
}
BIOSIM_GAP_FACTOR = 0.5           # half-gap for competed originators (sensitivity 0.0-1.0)

# Non-Q5 follow-on biosimilars / 351(a) copies billed under J-codes that the Q5xxx
# prefix screen misses (Stage 5.5 Challenge 4). These are cheaper competitors, not
# monopoly originators, so their brand gap is ZEROED. Keyed on the generic-name root.
NON_Q5_FOLLOWON_GENERICS = {"tbo-filgrastim"}

# CURATED prior published Part B international-gap figures (Originality landmines)
# MFN 2020: ASPE estimated $87.8B government savings over the 7-year model performance
# period (NOT 10 years — fact-checker correction 2026-06-09). Rescinded Dec 2021.
MFN_2020_GOV_SAVINGS_7YR_BIL = 87.8    # CMS/ASPE MFN IFR 2020, 7-year period (rescinded Dec 2021)
MFN_2020_PERIOD_YEARS = 7
MFN_2020_REDUCTION_PCT = 65            # ~65% reduction vs ASP+6% when fully phased
GLOBE_2025_NET_SAVINGS_7YR_BIL = 11.9  # CMS GLOBE Model (Dec 19, 2025), Part B, 7yr

# =============================================================================
# IPAY 2028 NEGOTIATION SELECTIONS (CMS press release Jan 27, 2026) — flag, keep
# =============================================================================
# 15 selected (Part D + first-ever Part B) + Tradjenta renegotiation. The
# Part-B-administered members that can appear in the Part B PUF as J-codes:
# Botox (J0585), Orencia (J0129), Entyvio (J3380), Cimzia, Xolair, Cosentyx (some
# self-inject), Kisqali/Lenvima/Verzenio/Erleada/Rexulti/Anoro/Biktarvy/Xeljanz/
# Trulicity are predominantly Part D oral/self-inject. We match on brand substring
# and flag any hit; the CY2023 pre-negotiation ASP stays the baseline (gap is real
# now), with a sensitivity line for exclusion.
IPAY_2028_SELECTED = [
    "Anoro", "Biktarvy", "Botox", "Cimzia", "Cosentyx", "Entyvio", "Erleada",
    "Kisqali", "Lenvima", "Orencia", "Rexulti", "Trulicity", "Verzenio",
    "Xeljanz", "Xolair", "Tradjenta",
]

# =============================================================================
# PER-MOLECULE INTERNATIONAL NET OVERRIDES (sensitivity layer, NOT the headline)
# =============================================================================
# Where data_sources.md found a credible NET international price for a specific
# molecule, override the RAND class ratio. Honest verdict from Stage 1: the patented
# biologics that dominate Part B spend have NO public international NET price (eMIT
# is generics-only with framework prices redacted; EURIPID/AMNOG are gross list;
# IFHP is commercial-billed). We therefore carry NO confident per-molecule net
# override for the patented biologics and disclose this as the data-partner CTA.
# The dict below is intentionally empty; it is the hook for a future data partner.
# (Leaving it empty means EVERY universe drug uses the RAND class proxy, which we
# report transparently as the share of spend covered by the class proxy = 100%.)
INTL_NET_OVERRIDE = {
    # "molecule_root_lower": intl_ratio (US ASP net / intl net), source noted in methodology
}


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
# STEP 1: LOAD PART B PUF
# =============================================================================
def load_partb():
    print("\n=== STEP 1: CMS Part B Spending by Drug PUF (CY%d annual, DYT23) ===" % SPEND_YEAR)
    dest = DATA_CACHE / "partb_annual_DYT23.csv"
    cached_download(PARTB_ANNUAL_CSV_URL, dest, "Part B PUF annual")
    df = pd.read_csv(dest, low_memory=False)
    n_all = len(df)
    sp = f"Tot_Spndng_{SPEND_YEAR}"
    du = f"Tot_Dsg_Unts_{SPEND_YEAR}"
    cl = f"Tot_Clms_{SPEND_YEAR}"
    be = f"Tot_Benes_{SPEND_YEAR}"
    asp = "Avg_DY23_ASP_Price"
    for c in (sp, du, cl, be, asp):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=[sp]).copy()
    df = df.rename(columns={sp: "spend", du: "dsg_units", cl: "tot_clms",
                            be: "tot_benes", asp: "asp_per_unit"})
    df["HCPCS_Cd"] = df["HCPCS_Cd"].astype(str)
    print(f"  total rows {n_all:,}; rows with {SPEND_YEAR} spend {len(df):,}; "
          f"TOTAL separately-paid Part B spend CY{SPEND_YEAR} ${df['spend'].sum()/1e9:.2f}B")
    return df


# =============================================================================
# STEP 2: UNIVERSE DEFINITION + EXCLUSION WATERFALL  (ORIGINAL ANALYSIS)
# =============================================================================
def is_skin_substitute(hcpcs, gnrc):
    # Q4xxx skin substitutes / cellular & tissue products
    return str(hcpcs).upper().startswith("Q4")


def is_vaccine(hcpcs, brand, gnrc):
    h = str(hcpcs)
    b = str(brand).lower()
    g = str(gnrc).lower()
    # CPT vaccine codes 90xxx / 91xxx
    if re.match(r"^9[01]\d{3}$", h):
        return True
    # therapeutic vaccine brands billed under J/Q codes (RSV, zoster, pneumococcal)
    if any(v in b for v in ("arexvy", "shingrix", "abrysvo", "prevnar", "spikevax",
                            "comirnaty", "fluzone", "flublok", "mresvia")):
        return True
    if re.search(r"(vacc|zoster ge|rsvpref|rsv vacc|pneumococcal|influenza)", g):
        return True
    return False


def is_immune_globulin_or_blood(hcpcs, brand, gnrc):
    # Immune globulins (plasma-derived), blood products, clotting factors.
    g = str(gnrc).lower()
    if re.search(r"glob(ulin)?\b|globg|globul|\bigg\b|gamma\(", g):
        return True
    if re.search(r"(factor (viii|ix|vii|x|xiii)|\bvon willebrand|albumin\b|"
                 r"antihemophilic|prothrombin complex|fibrinogen|plasma)", g):
        return True
    return False


def is_glp1(brand, gnrc):
    b = str(brand).lower()
    g = str(gnrc).lower()
    return bool(re.search(r"semaglutide|tirzepatide|dulaglutide|liraglutide|"
                          r"exenatide|lixisenatide", g) or
                re.search(r"ozempic|wegovy|mounjaro|zepbound|trulicity|victoza|"
                          r"rybelsus|byetta|bydureon", b))


def is_true_generic(brand, gnrc):
    """Flag TRUE unbranded generics: the brand name IS the molecule name (modulo the
    CMS multi-source '*' suffix and punctuation). These are the lines where the RAND
    brand-originator international gap MUST NOT be applied — RAND RR-A788-3 finds US
    UNBRANDED GENERICS are CHEAPER than abroad, so a positive brand-ratio savings on a
    generic line is the exact defect Issue #16's red-team caught. We KEEP them in the
    panel (transparency) but zero their booked gap.

    Note: a bare CMS '*' on a TRADE name (Orencia*, Botox*, Fasenra*, Abraxane*) is a
    blended/multi-HCPCS indicator, NOT generic availability — those stay branded. The
    test is strictly normalized(brand) == normalized(generic), which only fires on
    genuinely unbranded molecule lines (Lanreotide Acetate, Formoterol Fumarate,
    Infliximab* biosimilar-blend, etc.)."""
    bn = re.sub(r"[^a-z0-9]", "", str(brand).lower())
    gn = re.sub(r"[^a-z0-9]", "", str(gnrc).lower())
    return bool(bn) and bn == gn


def is_biosimilar_available(brand, gnrc):
    """Flag molecules with marketed US biosimilars (reference product whose ASP is
    blended down by biosimilar competition). KEPT in the universe (ASP is the real
    price) but flagged so we can report their spend and apply the RAND ratio honestly
    (where ASP is already low, the gap the ratio implies is correspondingly small)."""
    g = str(gnrc).lower()
    biosim_molecules = (
        "rituximab", "trastuzumab", "bevacizumab", "infliximab", "adalimumab",
        "filgrastim", "pegfilgrastim", "epoetin", "darbepoetin", "ranibizumab",
        "aflibercept", "tocilizumab", "natalizumab", "denosumab", "ustekinumab",
        "eculizumab",
    )
    return any(m in g for m in biosim_molecules)


def is_biosimilar_product(hcpcs, brand, gnrc):
    """Flag rows that are THEMSELVES biosimilar PRODUCTS (the cheaper competitor), not
    the branded originator reference line.

    Screen: HCPCS codes in the Q5xxx block are the definitive biosimilar code series
    (Truxima, Mvasi, Zirabev, Ruxience, Riabni, Cimerli, Byooviz, Renflexis, Inflectra,
    Avsola, Zarxio, Nivestym, Releuko, Fulphila, Udenyca, Ziextenzo, Nyvepria, Fylnetra,
    Stimufend, Retacrit, etc.). For these PRODUCTS the RAND brand-ORIGINATOR international
    net gap (3.22x -> 0.689) must NOT be applied: a biosimilar is the generic-equivalent
    competitor, and RAND finds US generics/biosimilars are at rough international parity
    or cheaper, so a positive brand-originator gap on a biosimilar line is the exact defect
    Issue #16's red-team caught. We KEEP these rows in the panel (transparency) but zero
    their booked gap (conservative central; exposed as a sensitivity row).

    CRITICAL: the screen is the Q5xxx HCPCS PREFIX, the biosimilar code block, NOT the
    4-letter nonproprietary suffix. The FDA 4-letter suffix (e.g., -aamt, -svoa, -cwvz,
    -nxki) is now standard on ALL new biologics, so NOVEL ORIGINATOR biologics that carry a
    suffix (Darzalex Faspro / daratumumab-hyaluronidase J9144, Vabysmo / faricimab-svoa
    J2777, Ultomiris / ravulizumab-cwvz J1303, Enhertu / fam-trastuzumab-deruxtecan J9358,
    Reblozyl / luspatercept-aamt, Evenity / romosozumab-aqqg) are NOT biosimilars and KEEP
    the full originator gap. They are not in the Q5 block, so the prefix screen leaves them
    untouched by construction."""
    return str(hcpcs).upper().startswith("Q5")


def build_universe(df):
    print("\n=== STEP 2: Universe definition + exclusion waterfall (ORIGINAL) ===")
    total = df["spend"].sum() / 1e9
    print(f"  [waterfall] TOTAL separately-paid Part B CY{SPEND_YEAR}: ${total:.2f}B "
          f"({len(df)} HCPCS)")

    df = df.copy()
    df["excl_skin"] = df.apply(lambda r: is_skin_substitute(r.HCPCS_Cd, r.Gnrc_Name), axis=1)
    df["excl_vaccine"] = df.apply(lambda r: is_vaccine(r.HCPCS_Cd, r.Brnd_Name, r.Gnrc_Name), axis=1)
    df["excl_ig_blood"] = df.apply(lambda r: is_immune_globulin_or_blood(r.HCPCS_Cd, r.Brnd_Name, r.Gnrc_Name), axis=1)
    df["excl_glp1"] = df.apply(lambda r: is_glp1(r.Brnd_Name, r.Gnrc_Name), axis=1)
    df["is_true_generic"] = df.apply(lambda r: is_true_generic(r.Brnd_Name, r.Gnrc_Name), axis=1)
    df["biosimilar_avail"] = df.apply(lambda r: is_biosimilar_available(r.Brnd_Name, r.Gnrc_Name), axis=1)
    df["is_biosimilar_product"] = df.apply(lambda r: is_biosimilar_product(r.HCPCS_Cd, r.Brnd_Name, r.Gnrc_Name), axis=1)

    # GLP-1 assertion (Issue #7 overlap; expected empty in Part B)
    n_glp1 = int(df["excl_glp1"].sum())
    print(f"  [exclude] GLP-1 (Issue #7 overlap): {n_glp1} rows "
          f"${df.loc[df['excl_glp1'],'spend'].sum()/1e9:.2f}B  (asserted ~empty)")
    assert n_glp1 == 0, f"Unexpected GLP-1 J-codes in Part B: {df.loc[df['excl_glp1'],'HCPCS_Cd'].tolist()}"

    # Waterfall: apply each exclusion in sequence, printing dollars removed.
    exclusions = []
    work = df.copy()

    def drop(mask, label):
        nonlocal work
        m = mask.reindex(work.index, fill_value=False)
        removed = work[m]
        amt = removed["spend"].sum() / 1e9
        n = len(removed)
        work = work[~m]
        exclusions.append({"step": label, "n_codes": n, "spend_removed_bil": round(amt, 3),
                           "remaining_bil": round(work["spend"].sum() / 1e9, 3)})
        print(f"  [exclude] {label:34s} -{n:3d} codes  -${amt:6.3f}B   "
              f"remaining ${work['spend'].sum()/1e9:.2f}B")

    drop(df["excl_skin"], "skin substitutes (Q4xxx)")
    drop(df["excl_vaccine"], "vaccines (90xxx/91xxx + brands)")
    drop(df["excl_ig_blood"], "immune globulins / blood products")
    drop(df["excl_glp1"], "GLP-1 (Issue #7 overlap)")

    # The retained working set is the "single-source brand/biologic Part B" universe.
    # We KEEP multi-source and biosimilar-available molecules (ASP is the real price),
    # but flag them. We additionally drop rows with zero spend.
    work = work[(work["spend"] > 0)].copy()
    universe = work.sort_values("spend", ascending=False).reset_index(drop=True).copy()
    universe["rank"] = universe.index + 1
    universe["ipay2028_flag"] = universe["Brnd_Name"].astype(str).str.lower().apply(
        lambda b: any(s.lower() in b for s in IPAY_2028_SELECTED))

    n_tg = int(universe["is_true_generic"].sum())
    tg_spend = universe.loc[universe["is_true_generic"], "spend"].sum() / 1e9
    n_bs = int(universe["biosimilar_avail"].sum())
    bs_spend = universe.loc[universe["biosimilar_avail"], "spend"].sum() / 1e9
    n_bsp = int(universe["is_biosimilar_product"].sum())
    bsp_spend = universe.loc[universe["is_biosimilar_product"], "spend"].sum() / 1e9
    n_ipay = int(universe["ipay2028_flag"].sum())
    ipay_spend = universe.loc[universe["ipay2028_flag"], "spend"].sum() / 1e9

    print(f"  [retain]  UNIVERSE n={len(universe)} codes  "
          f"spend base ${universe['spend'].sum()/1e9:.2f}B")
    print(f"            ...flagged TRUE unbranded generic (kept in panel, GAP ZEROED): "
          f"{n_tg} codes ${tg_spend:.2f}B")
    print(f"            ...flagged biosimilar PRODUCT (Q5xxx; kept in panel, GAP ZEROED): "
          f"{n_bsp} codes ${bsp_spend:.2f}B")
    print(f"            ...flagged biosimilar-available ORIGINATOR (kept, ASP=real blended): {n_bs} codes ${bs_spend:.2f}B")
    print(f"            ...flagged IPAY-2028 negotiation selection (kept, baseline=CY23 ASP): "
          f"{n_ipay} codes ${ipay_spend:.2f}B")

    excl_df = pd.DataFrame(exclusions)
    excl_df.loc[len(excl_df)] = {"step": "RETAINED UNIVERSE", "n_codes": int(len(universe)),
                                 "spend_removed_bil": float("nan"),
                                 "remaining_bil": round(universe["spend"].sum() / 1e9, 3)}
    excl_df.to_csv(RESULTS / "exclusions_accounting.csv", index=False)
    return universe, total


# =============================================================================
# STEP 3: PER-DRUG GAP + SAVINGS  (ORIGINAL ANALYSIS, NET-TO-NET)
# =============================================================================
def mol_root(g):
    m = re.match(r"([A-Za-z][A-Za-z\-]+)", str(g))
    return m.group(1).lower() if m else ""


def is_non_q5_followon(gnrc):
    """Non-Q5 follow-on biosimilars / 351(a) copies billed under J-codes (Granix /
    tbo-filgrastim J1447) that the Q5xxx prefix screen misses (Stage 5.5 Challenge 4)."""
    g = str(gnrc).lower()
    return any(root in g for root in NON_Q5_FOLLOWON_GENERICS)


def is_biosim_competed_originator(hcpcs, brand, gnrc):
    """Genuinely biosimilar-competed-by-CY2023 ORIGINATOR (Stage 5.5 Challenge 3).
    Restricted to molecules with mature US biosimilar competition in/before CY2023.
    The half-gap applies ONLY to the branded ORIGINATOR reference line, so we EXCLUDE:
      - Q5xxx biosimilar PRODUCTS (they are the competitor; their gap is zeroed separately)
      - true unbranded generics (gap zeroed separately)
      - novel ADCs/combos that merely contain a competed-molecule substring (Enhertu /
        fam-trastuzumab-deruxtecan [note CMS spells it 'deruxtecn'], Kadcyla /
        ado-trastuzumab emtansine, Phesgo / pertuzumab-trastuzumab) — no biosimilar, full gap.
    Post-2023-entrant originators (Eylea/aflibercept, Prolia/denosumab, Soliris/eculizumab)
    are excluded by construction: their molecules are NOT in BIOSIM_COMPETED_CY2023."""
    h = str(hcpcs).upper()
    g = str(gnrc).lower()
    if h.startswith("Q5"):                       # biosimilar product, not the originator
        return False
    # novel ADC / combo false positives (handle the CMS 'deruxtecn' misspelling)
    if re.search(r"deruxteca?n|emtansine|pertuzumab", g):
        return False
    # FDA 4-letter biosimilar suffix (e.g. -abbs, -awwb, -cbqv) marks a biosimilar PRODUCT
    # billed under a non-Q5 J-code in a few cases; those are competitors, not originators.
    if re.search(r"[a-z]+-[a-z]{4}\b", g) and re.search(r"-(abbs|awwb|bvzr|maly|adcd|pvvr|arrx|"
                  r"jmdb|cbqv|apgf|fpgk|pbbk|aafi|sndz|ayow|qyyp|anns|dkst|dttb|pkrb|nuna|"
                  r"eqrn|abda|dyyb|axxq)\b", g):
        return False
    if "tbo-filgrastim" in g:                    # non-Q5 follow-on, zeroed separately
        return False
    return any(m in g for m in BIOSIM_COMPETED_CY2023)


def compute_savings(uni, share_340b=SHARE_340B_CENTRAL, recov=RECOV_CENTRAL,
                    ratio_central=PARTB_RATIO_CENTRAL):
    uni = uni.copy()
    uni["mol_root"] = uni["Gnrc_Name"].map(mol_root)
    # gap_fraction per drug: default = MedPAC/ASPE ex-manufacturer 1.8x -> 0.4444
    # (Stage 5.5 Challenge 1 corrected); override where a credible per-molecule
    # international NET ratio exists (currently none).
    def ratio_for(row):
        r = INTL_NET_OVERRIDE.get(row["mol_root"])
        return r if r else ratio_central
    uni["intl_ratio"] = uni.apply(ratio_for, axis=1)
    uni["ratio_source"] = uni["mol_root"].apply(
        lambda m: "per_molecule_net_override" if m in INTL_NET_OVERRIDE
        else "medpac_aspe_exmfr_1.8x")
    uni["gap_fraction"] = 1.0 - 1.0 / uni["intl_ratio"]

    # Stage 5.5 Challenge 3: genuinely biosimilar-competed-by-CY2023 ORIGINATOR lines
    # get a HALF-GAP (US ASP already competed AND international price also fallen, so the
    # ratio is below the monopoly average). Applied BEFORE the zeroing rules so that
    # true generics / Q5 products / follow-ons (which overlap some of these molecules)
    # are then fully zeroed and take precedence.
    uni["biosim_competed_orig"] = uni.apply(
        lambda r: is_biosim_competed_originator(r.HCPCS_Cd, r.Brnd_Name, r.Gnrc_Name), axis=1)
    uni.loc[uni["biosim_competed_orig"], "gap_fraction"] *= BIOSIM_GAP_FACTOR
    uni.loc[uni["biosim_competed_orig"], "ratio_source"] = "biosim_competed_originator_half_gap"

    # TRUE unbranded generics: zero the brand gap (RAND finds US generics CHEAPER
    # abroad; applying a brand-originator gap to them is the Issue #16 red-team defect).
    if "is_true_generic" in uni.columns:
        uni.loc[uni["is_true_generic"], "gap_fraction"] = 0.0
        uni.loc[uni["is_true_generic"], "ratio_source"] = "true_generic_gap_zeroed"
    # Stage 5.5 Challenge 4: non-Q5 follow-on biosimilars (tbo-filgrastim / Granix)
    # billed under J-codes are cheaper competitors, not originators; zero their gap.
    uni["non_q5_followon"] = uni["Gnrc_Name"].apply(is_non_q5_followon)
    uni.loc[uni["non_q5_followon"], "gap_fraction"] = 0.0
    uni.loc[uni["non_q5_followon"], "ratio_source"] = "non_q5_followon_gap_zeroed"
    # BIOSIMILAR PRODUCTS (Q5xxx): zero the brand-ORIGINATOR gap. A biosimilar IS the
    # cheaper competitor, not the monopoly-priced originator; the brand gap cannot apply
    # to it (Issue #16 red-team defect, recurring). The originator reference lines
    # (Rituxan, Avastin, Herceptin, Neulasta, Lucentis, Eylea, Prolia) are NOT Q5 and
    # keep their gap (halved where genuinely competed by CY2023). NOTE: screened on the
    # Q5xxx HCPCS prefix only; novel originators with 4-letter suffixes (Darzalex Faspro,
    # Vabysmo, Ultomiris, Enhertu) are not Q5 and retain the full gap by construction.
    if "is_biosimilar_product" in uni.columns:
        uni.loc[uni["is_biosimilar_product"], "gap_fraction"] = 0.0
        uni.loc[uni["is_biosimilar_product"], "ratio_source"] = "biosimilar_product_gap_zeroed"
    uni["non340b_share"] = 1.0 - share_340b

    # spend is the ASP+6% allowed charge (payment base). gap_fraction is the
    # ex-manufacturer gap (1.8x central -> 0.4444); the proportional add-on rides down
    # under reference pricing so the gap applied to the payment base is the correct
    # system saving (Stage 5.5 Challenge 2 rebuttal). non340b_share removes 340B-acquired
    # volume's gap dollars (reserved for #19). recoverability is the policy-friction haircut.
    uni["gross_gap_savings_bil"] = uni["spend"] * uni["gap_fraction"] / 1e9
    uni["after_340b_savings_bil"] = uni["gross_gap_savings_bil"] * uni["non340b_share"]
    uni["booked_savings_bil"] = uni["after_340b_savings_bil"] * recov
    uni["savings_contribution_bil"] = uni["booked_savings_bil"]  # alias for export
    return uni


# =============================================================================
# STEP 4: SENSITIVITY GRID (gap_fraction x recoverability x 340B-share)
# =============================================================================
def sensitivity(uni):
    print("\n=== STEP 4: Sensitivity grid (ratio x 340B-share x recoverability) ===")
    # Per-line gap modifiers (Stage 5.5):
    #   - true generics, Q5xxx biosimilar products, non-Q5 follow-ons -> gap ZEROED
    #   - genuinely biosimilar-competed-by-CY2023 originators -> gap HALVED
    # The booked() helper recomputes the per-line gap at each scenario ratio so the
    # half-gap and zeroing ride correctly with the ratio (it does NOT apply a uniform
    # gap to a flat "gap-eligible" spend pool, which would mis-credit competed originators).
    zeroed = pd.Series(False, index=uni.index)
    if "is_true_generic" in uni.columns:
        zeroed |= uni["is_true_generic"]
    if "is_biosimilar_product" in uni.columns:
        zeroed |= uni["is_biosimilar_product"]
    if "non_q5_followon" in uni.columns:
        zeroed |= uni["non_q5_followon"]
    half = uni["biosim_competed_orig"] if "biosim_competed_orig" in uni.columns \
        else pd.Series(False, index=uni.index)
    half = half & ~zeroed  # zeroing takes precedence over halving
    spend = uni["spend"]
    grid = []

    def booked(ratio, share_340b, recov):
        gap = 1.0 - 1.0 / ratio
        line_gap = pd.Series(gap, index=uni.index)
        line_gap = line_gap.where(~half, gap * BIOSIM_GAP_FACTOR)
        line_gap = line_gap.where(~zeroed, 0.0)
        return float((spend * line_gap * (1 - share_340b) * recov).sum() / 1e9)

    scenarios = {
        "conservative": dict(ratio=PARTB_RATIO_CONSERVATIVE, share=SHARE_340B_UPPER, recov=RECOV_LOWER),
        "central":      dict(ratio=PARTB_RATIO_CENTRAL,      share=SHARE_340B_CENTRAL, recov=RECOV_CENTRAL),
        "aggressive":   dict(ratio=RAND_BRAND_RATIO_NET,     share=SHARE_340B_LOWER, recov=RECOV_UPPER),
    }
    for name, p in scenarios.items():
        b = booked(p["ratio"], p["share"], p["recov"])
        grid.append({"scenario": name, "intl_ratio": p["ratio"], "gap_fraction": round(1 - 1/p["ratio"], 4),
                     "share_340b": p["share"], "non340b_share": round(1 - p["share"], 4),
                     "recoverability": p["recov"], "booked_bil": round(b, 2)})
        print(f"  {name:12s} ratio={p['ratio']:.2f} (gap {1-1/p['ratio']:.3f})  "
              f"340B={p['share']:.2f}  recov={p['recov']:.2f}  -> ${b:.2f}B")

    # One-at-a-time sensitivity around central, for the methodology table.
    # intl_ratio axis spans the conservative stress (1.5x), the central (1.8x ex-mfr),
    # the payment-rate ratio (2.05x; shown for reference but NOT central — it would
    # double-count the add-on), and the aggressive RAND ceiling (3.22x).
    oat = []
    for ratio in (PARTB_RATIO_CONSERVATIVE, PARTB_RATIO_CENTRAL, MEDPAC_2019_RATIO, RAND_BRAND_RATIO_NET):
        oat.append({"vary": "intl_ratio", "value": ratio,
                    "booked_bil": round(booked(ratio, SHARE_340B_CENTRAL, RECOV_CENTRAL), 2)})
    for share in (SHARE_340B_LOWER, SHARE_340B_CENTRAL, SHARE_340B_UPPER):
        oat.append({"vary": "share_340b", "value": share,
                    "booked_bil": round(booked(PARTB_RATIO_CENTRAL, share, RECOV_CENTRAL), 2)})
    for recov in (RECOV_LOWER, RECOV_CENTRAL, RECOV_UPPER):
        oat.append({"vary": "recoverability", "value": recov,
                    "booked_bil": round(booked(PARTB_RATIO_CENTRAL, SHARE_340B_CENTRAL, recov), 2)})
    # biosimilar-competed-originator half-gap sensitivity (Challenge 3): show booked at
    # full-gap (1.0), half-gap (0.5, central), and zero-gap (0.0) for those lines.
    if "biosim_competed_orig" in uni.columns:
        for bf in (1.0, BIOSIM_GAP_FACTOR, 0.0):
            gap = 1.0 - 1.0 / PARTB_RATIO_CENTRAL
            lg = pd.Series(gap, index=uni.index)
            lg = lg.where(~half, gap * bf)
            lg = lg.where(~zeroed, 0.0)
            b = float((spend * lg * (1 - SHARE_340B_CENTRAL) * RECOV_CENTRAL).sum() / 1e9)
            oat.append({"vary": "biosim_competed_gap_factor", "value": bf, "booked_bil": round(b, 2)})

    # Biosimilar-product (Q5xxx) gap treatment sensitivity: central zeroes the gap on
    # biosimilar PRODUCTS. This row shows the booked figure if those products instead
    # RETAINED the full RAND brand-originator gap (the pre-patch, overstated treatment),
    # so the dollar magnitude of the Q5 adjustment is transparent.
    if "is_biosimilar_product" in uni.columns:
        bsp_mask = uni["is_biosimilar_product"]
        bsp_spend_bil = float(uni.loc[bsp_mask, "spend"].sum() / 1e9)
        # booked contribution IF biosimilar products kept the full brand gap, at the
        # CENTRAL 1.8x ratio (not the RAND ceiling) and central params.
        gap_full = 1.0 - 1.0 / PARTB_RATIO_CENTRAL
        bsp_booked_if_full = float(
            (uni.loc[bsp_mask, "spend"] * gap_full
             * (1 - SHARE_340B_CENTRAL) * RECOV_CENTRAL).sum() / 1e9)
        central_booked = booked(PARTB_RATIO_CENTRAL, SHARE_340B_CENTRAL, RECOV_CENTRAL)
        oat.append({"vary": "biosimilar_product_gap", "value": "zeroed (central)",
                    "booked_bil": round(central_booked, 2)})
        oat.append({"vary": "biosimilar_product_gap", "value": "full_brand_gap (pre-patch)",
                    "booked_bil": round(central_booked + bsp_booked_if_full, 2)})
        print(f"  [Q5 adjust] biosimilar PRODUCTS (Q5xxx): {int(bsp_mask.sum())} codes, "
              f"${bsp_spend_bil:.3f}B spend; gap ZEROED (central).")
        print(f"  [Q5 adjust] booked contribution removed by zeroing the Q5 gap: "
              f"-${bsp_booked_if_full:.3f}B "
              f"(pre-patch ${central_booked + bsp_booked_if_full:.2f}B -> patched ${central_booked:.2f}B)")

    grid_df = pd.DataFrame(grid)
    oat_df = pd.DataFrame(oat)
    pd.concat([grid_df.assign(kind="scenario"),
               oat_df.assign(kind="one_at_a_time")], ignore_index=True) \
        .to_csv(RESULTS / "sensitivity_grid.csv", index=False)
    return {s["scenario"]: s["booked_bil"] for s in grid}, grid_df, oat_df


# =============================================================================
# STEP 5: CROSS-VALIDATION (distinct-from-published block)
# =============================================================================
def cross_validate(uni, booked_central):
    print("\n=== STEP 5: Cross-validation (distinct from published) ===")
    spend_base = uni["spend"].sum() / 1e9
    rows = []

    # (a) MedPAC 2019 2.05x applied naively to the universe spend (no 340B, no recov):
    #     a sanity anchor for the order of magnitude of the gross gap.
    medpac_naive_gap = 1 - 1 / MEDPAC_2019_RATIO
    medpac_naive = spend_base * medpac_naive_gap
    print(f"  (a) MedPAC 2019 2.05x naive gross gap on universe ${spend_base:.1f}B: "
          f"${medpac_naive:.1f}B (no 340B, no recoverability)")
    rows.append({"check": "MedPAC 2019 2.05x naive gross gap on universe",
                 "value_bil": round(medpac_naive, 2),
                 "note": "order-of-magnitude anchor; we are net-to-net + 340B-netted + recov-haircut"})

    # (b) GLOBE model $11.9B / 7yr Part B savings — annualized ~$1.7B/yr, partial
    #     utilization, phased rebate. Ours is full single-source biologic universe,
    #     one-year, net gap, 340B-netted. Must be larger / different by construction.
    globe_annual = GLOBE_2025_NET_SAVINGS_7YR_BIL / 7
    print(f"  (b) GLOBE $11.9B/7yr ~= ${globe_annual:.1f}B/yr (partial utilization, "
          f"phased intl-ref rebate). Ours booked central ${booked_central:.1f}B/yr "
          f"(full universe, one-year net gap, 340B-netted).")
    rows.append({"check": "CMS GLOBE Model $11.9B/7yr annualized",
                 "value_bil": round(globe_annual, 2),
                 "note": "different counterfactual: partial mandatory subset + phased rebate vs our full-universe one-year net gap"})

    # (c) MFN 2020 model: $87.8B gov savings / 7yr ~= $12.5B/yr, ~65% reduction on a
    #     ~top-50 universe with an index blend, GDP-adjusted intl. Different year,
    #     universe, exclusions, netting, and we book a one-year recoverable gap.
    #     (7-year period, NOT 10 — fact-checker correction 2026-06-09.)
    mfn_annual = MFN_2020_GOV_SAVINGS_7YR_BIL / MFN_2020_PERIOD_YEARS
    print(f"  (c) MFN 2020 $87.8B gov/7yr ~= ${mfn_annual:.1f}B/yr at ~65% reduction "
          f"(rescinded 2021). Different year/universe/netting; we update to CY2023.")
    rows.append({"check": "CMS MFN 2020 $87.8B gov/7yr annualized",
                 "value_bil": round(mfn_annual, 2),
                 "note": "2020 top-~50, index blend, GDP-adjusted; rescinded. We differ in year, exclusions, one-year"})

    # (d) Distinct-from-published assertion: our booked central must NOT be within 5%
    #     of GLOBE's annualized figure on a like scope (it should be larger).
    pct_vs_globe = abs(booked_central - globe_annual) / globe_annual * 100
    distinct = pct_vs_globe > 5
    print(f"  (d) Booked central ${booked_central:.1f}B vs GLOBE annualized ${globe_annual:.1f}B: "
          f"{pct_vs_globe:.0f}% apart -> {'DISTINCT' if distinct else 'TOO CLOSE — re-scope'}")
    rows.append({"check": "DISTINCT-FROM-PUBLISHED (booked vs GLOBE annualized, >5% apart)",
                 "value_bil": round(booked_central, 2),
                 "note": f"{pct_vs_globe:.0f}% apart from GLOBE annualized; {'PASS' if distinct else 'FAIL'}"})

    pd.DataFrame(rows).to_csv(RESULTS / "cross_validation.csv", index=False)
    return distinct


# =============================================================================
# STEP 6: MANUFACTURER ROLLUP (Who Profits)
# =============================================================================
def manufacturer_rollup(uni):
    print("\n=== STEP 6: Manufacturer / brand rollup (Who Profits) ===")
    # The Part B PUF has no manufacturer column; map the top brands to manufacturers
    # via a small CURATED lookup (confirm financials at draft time via SEC EDGAR).
    BRAND_MFR = {
        "keytruda": "Merck (MRK)", "eylea": "Regeneron (REGN)",
        "prolia": "Amgen (AMGN)", "darzalex": "Johnson & Johnson (JNJ)",
        "opdivo": "Bristol Myers Squibb (BMY)", "vabysmo": "Roche/Genentech",
        "orencia": "Bristol Myers Squibb (BMY)", "imfinzi": "AstraZeneca (AZN)",
        "entyvio": "Takeda (TAK)", "ocrevus": "Roche/Genentech",
        "tecentriq": "Roche/Genentech", "rituxan": "Roche/Genentech",
        "ultomiris": "AstraZeneca/Alexion (AZN)", "enhertu": "AstraZeneca/Daiichi (AZN)",
        "yervoy": "Bristol Myers Squibb (BMY)", "evenity": "Amgen (AMGN)",
        "reblozyl": "Bristol Myers Squibb (BMY)", "sandostatin": "Novartis (NVS)",
        "botox": "AbbVie (ABBV)", "xolair": "Roche/Genentech / Novartis",
    }
    uni = uni.copy()
    uni["mfr"] = uni["Brnd_Name"].astype(str).str.lower().apply(
        lambda b: next((v for k, v in BRAND_MFR.items() if k in b), "Other / unmapped"))
    g = uni.groupby("mfr").agg(
        n_codes=("rank", "count"),
        spend_bil=("spend", lambda s: s.sum() / 1e9),
        booked_savings_bil=("booked_savings_bil", "sum")).reset_index()
    g = g.sort_values("booked_savings_bil", ascending=False)
    g.to_csv(RESULTS / "manufacturer_rollup.csv", index=False)
    print("  top manufacturers by booked savings contribution:")
    for _, r in g.head(8).iterrows():
        print(f"    {str(r.mfr)[:34]:34s} n={int(r.n_codes):2d}  "
              f"spend ${r.spend_bil:5.2f}B  booked ${r.booked_savings_bil:.2f}B")
    return g


# =============================================================================
# STEP 7: EXPORT universe CSV + savings_estimate.json
# =============================================================================
def export_universe(uni):
    cols = ["rank", "HCPCS_Cd", "Brnd_Name", "Gnrc_Name", "mol_root", "spend",
            "asp_per_unit", "dsg_units", "tot_clms", "tot_benes",
            "is_true_generic", "is_biosimilar_product", "biosimilar_avail",
            "biosim_competed_orig", "non_q5_followon", "ipay2028_flag",
            "intl_ratio", "ratio_source", "gap_fraction", "non340b_share",
            "gross_gap_savings_bil", "after_340b_savings_bil",
            "booked_savings_bil", "savings_contribution_bil"]
    out = uni[cols].copy()
    out.to_csv(RESULTS / "universe_part_b_drugs.csv", index=False)
    return out


def emit_estimate(uni, total_partb, scenarios, distinct):
    booked = float(uni["booked_savings_bil"].sum())
    spend_base = float(uni["spend"].sum() / 1e9)
    gross_gap = float(uni["gross_gap_savings_bil"].sum())
    after_340b = float(uni["after_340b_savings_bil"].sum())
    swr = float((uni["intl_ratio"] * uni["spend"]).sum() / uni["spend"].sum())
    # "class proxy" = lines priced off the MedPAC/ASPE 1.8x ex-manufacturer class ratio
    # (full or half gap), i.e. everything not on a per-molecule net override.
    class_proxy_sources = {"medpac_aspe_exmfr_1.8x", "biosim_competed_originator_half_gap"}
    pct_class_proxy = float(
        uni.loc[uni["ratio_source"].isin(class_proxy_sources), "spend"].sum()
        / uni["spend"].sum() * 100)

    ipay_booked_excluded = float(
        uni.loc[~uni["ipay2028_flag"], "booked_savings_bil"].sum())
    ipay_spend = float(uni.loc[uni["ipay2028_flag"], "spend"].sum() / 1e9)

    # Q5 biosimilar-product adjustment magnitude (booked dollars removed by zeroing the
    # brand-originator gap on Q5xxx biosimilar PRODUCTS).
    bsp_mask = uni["is_biosimilar_product"] if "is_biosimilar_product" in uni.columns \
        else pd.Series(False, index=uni.index)
    bsp_n = int(bsp_mask.sum())
    bsp_spend = float(uni.loc[bsp_mask, "spend"].sum() / 1e9)
    gap_full = 1.0 - 1.0 / PARTB_RATIO_CENTRAL
    bsp_booked_if_full = float(
        (uni.loc[bsp_mask, "spend"] * gap_full
         * (1 - SHARE_340B_CENTRAL) * RECOV_CENTRAL).sum() / 1e9)

    est = {
        "issue_number": 17, "issue_title": "The Part B Pharmacy Premium",
        "anchor_year": SPEND_YEAR,
        "headline_status": "COMPUTED",
        "booked_bil": round(booked, 2),
        "booked_target_bil": 15.0,
        "range_lo_bil": round(scenarios["conservative"], 2),
        "range_hi_bil": round(scenarios["aggressive"], 2),
        "central_method": (
            "MedPAC June 2019 / ASPE 2018 EX-MANUFACTURER 1.8x (Part-B-channel-appropriate "
            "published ratio) applied to the ASP+6% allowed-charge payment base via the "
            "proportional-add-on algebra (the statutory add-on rides down with the "
            "ingredient price, so the ex-manufacturer gap fraction on the payment base "
            "yields the correct system saving). 340B-acquired volume removed (non340B "
            f"share {1-SHARE_340B_CENTRAL:.2f}; reserved for Issue #19), recoverability "
            f"{RECOV_CENTRAL}. RAND's 3.22x (US-net/intl-gross, retail-calibrated) is the "
            "aggressive ceiling only; 1.5x is the conservative stress floor. "
            "Biosimilar-competed-by-CY2023 originators carry a half-gap (Stage 5.5 "
            "Challenge 3); true generics, Q5xxx biosimilars, and non-Q5 follow-ons "
            "(tbo-filgrastim) carry zero gap."),
        "waterfall": {
            "total_partb_separately_paid_bil": round(total_partb, 2),
            "universe_spend_base_bil": round(spend_base, 2),
            "gross_intl_gap_savings_bil": round(gross_gap, 2),
            "after_340b_netting_bil": round(after_340b, 2),
            "after_recoverability_booked_bil": round(booked, 2),
        },
        "biosimilar_product_adjustment": {
            "screen": "HCPCS Q5xxx (biosimilar code block)",
            "n_codes": bsp_n,
            "spend_bil": round(bsp_spend, 3),
            "gap_treatment": "zeroed (biosimilar is the cheaper competitor, not the brand originator)",
            "booked_removed_bil": round(bsp_booked_if_full, 3),
            "note": ("Q5xxx biosimilar PRODUCTS keep zero brand-originator gap; the Issue #16 "
                     "red-team defect (brand-originator ratio on a biosimilar/generic line). "
                     "Novel originators with 4-letter suffixes (Darzalex Faspro, Vabysmo, "
                     "Ultomiris, Enhertu) are NOT Q5 and retain the full gap."),
        },
        "universe_n_codes": int(len(uni)),
        "spend_weighted_avg_ratio": round(swr, 3),
        "pct_spend_on_class_proxy": round(pct_class_proxy, 1),
        "pct_spend_per_molecule_override": round(100 - pct_class_proxy, 1),
        "params": {
            "intl_ratio_central": PARTB_RATIO_CENTRAL,
            "intl_ratio_conservative": PARTB_RATIO_CONSERVATIVE,
            "intl_ratio_aggressive_ceiling": RAND_BRAND_RATIO_NET,
            "medpac_2019_exmfr_ratio": MEDPAC_2019_EXMFR_RATIO,
            "aspe_2018_ratio": ASPE_2018_RATIO,
            "rand_brand_ratio_net": RAND_BRAND_RATIO_NET,
            "rand_brand_ratio_gross": RAND_BRAND_RATIO_GROSS,
            "biosim_competed_gap_factor": BIOSIM_GAP_FACTOR,
            "share_340b": {"lower": SHARE_340B_LOWER, "central": SHARE_340B_CENTRAL, "upper": SHARE_340B_UPPER},
            "recoverability": {"lower": RECOV_LOWER, "central": RECOV_CENTRAL, "upper": RECOV_UPPER},
        },
        "stage_5_5_corrections": {
            "challenge_1_intl_ratio": ("CORRECTED: central re-anchored from RAND 3.22x "
                "(US-net/intl-gross, retail-calibrated) to MedPAC/ASPE ex-manufacturer "
                "1.8x; 3.22x demoted to aggressive ceiling; 1.5x conservative floor."),
            "challenge_2_payment_base": ("REBUTTED: base is ASP+6% payment limit, but the "
                "add-on is proportional, so under reference pricing it rides down and the "
                "ex-manufacturer gap on the payment base is the correct system saving; "
                "base NOT deflated; paired with ex-mfr 1.8x (not payment-rate 2.05x)."),
            "challenge_3_biosim_originators": ("CORRECTED (partial): half-gap applied to "
                "genuinely biosimilar-competed-by-CY2023 originators; substring false "
                "positives (Enhertu/Kadcyla/Phesgo ADCs; Eylea/Prolia/Soliris post-2023 "
                "entrants) keep the full gap."),
            "challenge_4_non_q5_followon": ("CORRECTED (immaterial): tbo-filgrastim (Granix "
                "J1447) gap-zeroed; blended '*' codes correctly kept (multi-HCPCS marker)."),
            "challenge_5_additivity": ("REBUTTED for #17 (340B removal is conservative); "
                "#17/#19 additivity overlap caveat strengthened at project-tracker level."),
            "challenge_6_conservative_corner": ("CORRECTED: conservative corner now uses a "
                "genuine sub-central 1.5x ratio; range re-centered to $3.51-11.59B."),
        },
        "scenarios_bil": scenarios,
        "ipay2028": {
            "selections_in_universe_spend_bil": round(ipay_spend, 2),
            "booked_if_ipay2028_excluded_bil": round(ipay_booked_excluded, 2),
            "note": ("CY2023 pre-negotiation ASP is the correct present-day baseline; "
                     "IPAY-2028 Maximum Fair Prices take effect 2028 and would offset "
                     "part of this gap for the flagged drugs."),
        },
        "distinct_from_published": bool(distinct),
        "curated_priors_bil": {
            "mfn_2020_gov_7yr": MFN_2020_GOV_SAVINGS_7YR_BIL,
            "mfn_2020_period_years": MFN_2020_PERIOD_YEARS,
            "mfn_2020_annualized": round(MFN_2020_GOV_SAVINGS_7YR_BIL / MFN_2020_PERIOD_YEARS, 2),
            "globe_2025_7yr": GLOBE_2025_NET_SAVINGS_7YR_BIL,
            "globe_2025_annualized": round(GLOBE_2025_NET_SAVINGS_7YR_BIL / 7, 2),
            "medpac_2019_payment_ratio": MEDPAC_2019_RATIO,
            "medpac_2019_exmfr_ratio": MEDPAC_2019_EXMFR_RATIO,
            "aspe_2018_ratio": ASPE_2018_RATIO,
        },
        "data_partner_cta": (
            "No symmetric net-to-net international ratio is published for Part B "
            "biologics: the US ASP side is near-net for this physician-administered "
            "channel, but per-molecule international NET prices for patented biologics "
            "(Keytruda, Eylea, Opdivo, Darzalex, Vabysmo, etc.) are confidential. We "
            "use the MedPAC/ASPE ex-manufacturer 1.8x class ratio as the central. "
            "EURIPID full access, national procurement net prices (NHS commercial "
            "framework, German AMNOG post-rebate net), or licensed IQVIA MIDAS would "
            "let us compute per-molecule net gaps and replace the class ratio. The "
            "precise 340B-acquired share of our specific J-codes needs JG/TB-modifier "
            "claims (CMS RIF/LDS, restricted)."),
        "vs_target": (f"central ${booked:.1f}B is "
                      f"{'below' if booked < 15 else 'at/above'} the $15B scoping "
                      f"target; the computed central is reported as-is, not tuned "
                      f"(came in below target after the Stage 5.5 ratio re-anchoring "
                      f"to the Part-B-appropriate 1.8x ex-manufacturer figure)"),
        "generated_at": datetime.now().isoformat(),
    }
    (RESULTS / "savings_estimate.json").write_text(json.dumps(est, indent=2))
    return est


# =============================================================================
# GOTCHA + ORIGINALITY BLOCKS
# =============================================================================
def print_gotcha_block(uni, total_partb):
    print("\n===== DATASET GOTCHA CONFIRMATION =====")
    print("Dataset: CMS Medicare Part B Spending by Drug PUF, CY2023 (RY25, DYT23).")
    print(f"'Total Spending' = full value of product (Medicare program payment + "
          f"beneficiary liability); ASP-derived ALLOWED CHARGES, NOT charges or costs. "
          f"Nominal CY{SPEND_YEAR} dollars.")
    print(f"  Total separately-paid Part B CY{SPEND_YEAR}: ${total_partb:.2f}B; "
          f"retained universe ${uni['spend'].sum()/1e9:.2f}B.")
    print("ASP netting: ASP is ALREADY NET by statute (SSA 1847A(c)(3)) — net of "
          "volume/prompt-pay/cash discounts, chargebacks, most rebates.")
    print("  ASP EXCLUDES Medicaid 1927 rebates AND 340B prices => published ASP is "
          "the NON-340B net price; 340B spread reserved for Issue #19.")
    print("  ASP is NOT compressed by IRA Part B inflation rebates (those reduce "
          "beneficiary coinsurance only, NOT the payment limit) => gap not pre-closed.")
    print("RATIO BASIS (Stage 5.5 Challenge 1/2): US base = ASP+6% allowed charge "
          "(payment base). International comparator = MedPAC/ASPE EX-MANUFACTURER 1.8x "
          "(Part-B-channel ratio). The add-on is proportional, so the ex-mfr gap on the "
          "payment base = correct system saving (base NOT deflated; Challenge 2 rebuttal). "
          "NO Part-D-style rebate haircut on ASP. RAND 3.22x (US-net/intl-gross) is the "
          "AGGRESSIVE CEILING only, not the central; no symmetric net-to-net Part B ratio "
          "is public (data-partner CTA).")
    print("GLP-1 (Issue #7 overlap): asserted EMPTY in Part B PUF (0 J-codes).")
    print("Exclusions removed (skin substitutes Q4xxx; vaccines 90xxx/91xxx; immune "
          "globulins / blood products) — see results/exclusions_accounting.csv.")
    print("========================================")


def print_originality_block(est):
    print("\n===== ORIGINALITY GATE =====")
    print(f"HEADLINE (booked central): ${est['booked_bil']:.2f}B/year "
          f"(range ${est['range_lo_bil']:.2f}-{est['range_hi_bil']:.2f}B).")
    print("WHAT IS ORIGINAL (computed in this script from CY2023 Part B PUF):")
    print("  - The CY2023 single-source-brand/biologic Part B universe with the "
          "triple exclusion (skin substitutes, vaccines, immune globulins/blood) and "
          "GLP-1 assertion.")
    print("  - The per-J-code spend aggregation, the spend-weighted average ratio, "
          "and the international-gap savings net of 340B-acquired volume.")
    print("  - The 340B-netting boundary (non-340B Part B spend for #17; 340B spread "
          "reserved for #19), the biosimilar-competed-originator half-gap, and the "
          "sensitivity grid over ratio x 340B-share x recoverability. This exact "
          "aggregation (CY2023 + triple exclusion + 340B netting) has not been published.")
    print("WHAT IS CURATED (reference inputs / cross-validation, NOT the headline):")
    print(f"  - CENTRAL ratio: MedPAC 2019 / ASPE 2018 EX-MANUFACTURER "
          f"{MEDPAC_2019_EXMFR_RATIO}x (the Part-B-channel-appropriate published ratio). "
          f"Conservative {PARTB_RATIO_CONSERVATIVE}x stress floor; RAND "
          f"{RAND_BRAND_RATIO_NET}x (US-net/intl-gross) aggressive ceiling only.")
    print(f"  - MFN 2020 (${est['curated_priors_bil']['mfn_2020_gov_7yr']}B gov/7yr, "
          f"~{MFN_2020_REDUCTION_PCT}% reduction); GLOBE 2025 "
          f"(${est['curated_priors_bil']['globe_2025_7yr']}B/7yr); MedPAC 2019 "
          f"({MEDPAC_2019_RATIO}x payment-rate, {MEDPAC_2019_EXMFR_RATIO}x ex-mfr); "
          f"ASPE 2018 ({ASPE_2018_RATIO}x).")
    print(f"DISTINCT-FROM-PUBLISHED: {'PASS' if est['distinct_from_published'] else 'FAIL'} "
          f"(booked central differs from GLOBE annualized by >5%; different year, "
          f"universe, exclusions, net-to-net, one-year recoverable).")
    print("============================")


# =============================================================================
# MAIN
# =============================================================================
def main():
    print("=" * 76)
    print("ISSUE #17 — THE PART B PHARMACY PREMIUM — Stage 2 full build")
    print("=" * 76)

    df = load_partb()
    universe, total_partb = build_universe(df)
    universe = compute_savings(universe, SHARE_340B_CENTRAL, RECOV_CENTRAL)
    export_universe(universe)

    scenarios, grid_df, oat_df = sensitivity(universe)
    booked_central = float(universe["booked_savings_bil"].sum())
    distinct = cross_validate(universe, booked_central)
    manufacturer_rollup(universe)
    est = emit_estimate(universe, total_partb, scenarios, distinct)

    # Top 10 by savings contribution
    print("\n=== TOP 10 DRUGS BY BOOKED SAVINGS CONTRIBUTION ===")
    top10 = universe.sort_values("booked_savings_bil", ascending=False).head(10)
    for _, r in top10.iterrows():
        flags = []
        if r["is_true_generic"]: flags.append("gen-zeroed")
        if r["is_biosimilar_product"]: flags.append("Q5-zeroed")
        if r["biosimilar_avail"]: flags.append("biosim")
        if r["ipay2028_flag"]: flags.append("IPAY28")
        fl = (" [" + ",".join(flags) + "]") if flags else ""
        print(f"  {r['HCPCS_Cd']:7s} {str(r['Brnd_Name'])[:22]:22s} "
              f"{str(r['Gnrc_Name'])[:26]:26s} spend ${r['spend']/1e9:5.2f}B  "
              f"booked ${r['booked_savings_bil']:.3f}B{fl}")

    print_gotcha_block(universe, total_partb)
    print_originality_block(est)

    print("\n" + "=" * 76)
    print(f"BOOKED CENTRAL: ${est['booked_bil']:.2f}B/year  "
          f"(range ${est['range_lo_bil']:.2f}-{est['range_hi_bil']:.2f}B)")
    bspa = est["biosimilar_product_adjustment"]
    print(f"Q5 biosimilar-product adjustment: {bspa['n_codes']} Q5xxx codes "
          f"(${bspa['spend_bil']:.3f}B spend) gap ZEROED -> "
          f"-${bspa['booked_removed_bil']:.3f}B booked removed vs the pre-patch full-gap treatment.")
    print(f"Waterfall: total ${total_partb:.2f}B -> universe "
          f"${est['waterfall']['universe_spend_base_bil']:.2f}B -> gross gap "
          f"${est['waterfall']['gross_intl_gap_savings_bil']:.2f}B -> after 340B "
          f"${est['waterfall']['after_340b_netting_bil']:.2f}B -> booked "
          f"${est['waterfall']['after_recoverability_booked_bil']:.2f}B")
    print(f"Results written to {RESULTS}/")
    print("=" * 76)
    return est


if __name__ == "__main__":
    main()
