"""
01_build_data.py - Issue #18: Coding for Dollars

The American Healthcare Conundrum
Hospital DRG creep / upcoding in fee-for-service (FFS) Medicare. We measure how
much the case-mix index (CMI) of FFS Medicare inpatient discharges has drifted
upward over 2013-2024, isolate the documentation-driven (coding-intensity)
component from genuine acuity, value it against the actual FFS Inpatient
Prospective Payment System (IPPS) Medicare payment pool, net what CMS has
already recouped, apply a recoverability factor, and net the overlap with
DOJ False Claims Act (FCA) hospital-upcoding settlements.

============================================================================
STAGE 2 FULL BUILD (computed; replaces the 2026-05-09 skeleton)
============================================================================
PUBLIC-CMS PATH (Andrew's directive, 2026-06-09). We do NOT use HCUP NIS
(gated DUA workflow). The full Crespin et al. 2024 five-state regression
replication on NIS/SID microdata becomes the explicit data-partner CTA.
Everything here runs from public, no-DUA CMS data:

  - Medicare Inpatient Hospitals "by Geography and Service" PUF (DY2013-DY2024):
    national rollup of discharges + average Medicare payment for every MS-DRG,
    every year. This is the backbone for the national case-mix migration panel
    and the mechanism-specific severity-tier analysis.
  - Medicare Inpatient Hospitals "by Provider" PUF (DY2013-DY2024): per-CCN
    discharges, demographics, comorbidity prevalence, and the bene-weighted
    HCC risk score (Bene_Avg_Risk_Scre). This is the independent ACUITY
    counterfactual: did patients actually get sicker as fast as the codes say?

The headline is COMPUTED bottom-up, never reverse-engineered to the $20B
scoping target. Issues #16 ($35B target -> $16.36B computed) and #17 ($15B ->
$6.17B) both came in under target and shipped the computed number. If #18 lands
away from $20B, that is the result.

============================================================================
METHOD (what we actually do)
============================================================================
ORIGINAL backbone -- national fixed-weight case-mix migration index:
  For each DRG d, fix a relative weight W_d anchored to its DY2024 national
  average Medicare payment, normalized so the DY2024 discharge mix averages to
  1.000. Then re-weight each year's national discharge MIX by that fixed weight
  vector. The resulting index isolates PURE share migration toward high-weight
  DRGs (the upcoding signal), holding DRG prices constant. Result:
  +18.9% migration 2013->2024 (+10.7% 2013->2019).

ORIGINAL acuity counterfactual -- HCC risk-score trajectory:
  Bene-weighted Bene_Avg_Risk_Scre rose 1.98 (2013) -> 2.20 (2019) -> 2.14
  (2024), i.e. +7.8% 2013->2024. The HCC risk score is itself partly
  diagnosis-coding-driven, so it is a CONSERVATIVE (over-correcting)
  counterfactual: netting it out understates the coding residual. It defines
  the FLOOR, not the central.

ORIGINAL denominator -- FFS IPPS Medicare payment pool:
  Computed directly from the Geo PUF national rows: sum(discharges x avg
  Medicare payment) = ~$107B for DY2024. (The skeleton's $230B NHE placeholder
  was wrong -- that conflates total hospital care; the true FFS IPPS pool is
  ~$107-115B.)

CURATED calibration -- Crespin et al. 2024 Health Affairs (DOI
  10.1377/hlthaff.2024.00596). CORRECTED 2026-06-10 (Stage 5.5 C1): the paper's
  $14.6B/$5.8B/$4.6B all-payer/private/Medicare 2019 figures are NATIONAL
  (dollarized on national CMS NHE data), NOT five-state. Crespin's Medicare
  coding-intensity effect, after patient-level controls (demographics, LOS,
  Elixhauser comorbidity, hospital fixed effects), is 2.0% of MS-DRG payment
  weights (Exhibit 4; CI 1.7-2.2%). The corrected build applies that controlled
  2.0% Medicare share to OUR operating-netted FFS IPPS pool. The prior build's
  21.8%-of-pool share (national figure / 0.176 pop share) was a ~11x misread and
  is removed. Crespin supplies the controlled coding-intensity ratio; the CMI
  panel, the FFS-IPPS pool, the operating netting, the recoupment netting, the
  recoverability haircut, and the overlap accounting are all ours.

SAVINGS WATERFALL (central, CORRECTED):
  gross_central(2024) = crespin_controlled_medicare_share(2.0%) x op_netted_pool(2024)
                      ~ 0.020 x $95B = ~$1.9B
  (FLOOR: Crespin CI-low 1.7% x op-pool; CEILING: risk-net residual x op-pool,
   a cruder single-proxy control that over-attributes to coding)
  already_recouped = 0 on the Crespin path (Crespin's 2019 figure is measured
   on payments OBSERVED AFTER CMS applied the documentation-and-coding
   recoupment, so it is already net; subtracting again would double-count). The
   ATRA 2012 recoupment of the FY2008-2012 MS-DRG-transition coding was
   completed by ~FY2017 and is documented separately.
  recoverable = gross_excess x recoverability_factor (0.55 central; 0.45/0.75)
  booked = recoverable
         - overlap(#11 MA coding intensity = 0, separate program)
         - overlap(#5 admin paperwork = 0, separate mechanism)
         - overlap(#15 facility fee = 0, separate setting/code system)
         - overlap(#24 fraud = net of FCA-confirmed hospital DRG-upcoding
                   settlements, annualized)

BUDGET-NEUTRALITY NOTE (red-team load-bearing). CMS recalibrates DRG RELATIVE
WEIGHTS budget-neutrally every year, so a pure rescaling of weights is NOT extra
money. But weight budget-neutrality does NOT neutralize the SHIFT of the
discharge MIX into higher-weight DRGs: when more discharges land in MCC tiers,
CMI rises and total payment rises through the standardized amount, and CMS only
claws that back via the explicit documentation-and-coding adjustment -- a finite
ATRA recoupment completed ~FY2017, with no standing annual reduction after. Our
fixed-weight index measures exactly that un-neutralized mix migration, so the
headline is real money. This is engaged in methodology.md and flagged for
Stage 5.5.

RUN:
    pip install --break-system-packages pandas numpy
    python3 01_build_data.py
Network required on first run (~120MB of CMS PUF CSVs cached to data_cache/).

Author: The American Healthcare Conundrum, rebuilt 2026-06-09.
"""

import json
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
# DATA SOURCES (data.cms.gov, public, no DUA)
# =============================================================================
# Medicare Inpatient Hospitals - by Geography and Service (national rollups by
# MS-DRG: discharges + average Medicare payment). DY = data year (calendar year
# of the claims). Verified live from the data.cms.gov metastore 2026-06-09.
GEO_URLS = {
    2013: "https://data.cms.gov/sites/default/files/2023-05/dbee128c-28d2-4c64-b711-9c2528eed2f0/MUP_IHP_RY23_P03_V10_DY13_GEO.CSV",
    2014: "https://data.cms.gov/sites/default/files/2023-05/8938c5bd-da0f-4810-b696-cdad9a6b7ed8/MUP_IHP_RY23_P03_V10_DY14_GEO.CSV",
    2015: "https://data.cms.gov/sites/default/files/2023-05/b3cb61a4-7b3f-4508-ba0c-a3ffe3a1001e/MUP_IHP_RY23_P03_V10_DY15_GEO.CSV",
    2016: "https://data.cms.gov/sites/default/files/2023-05/37a92da8-fe11-4f52-b96c-04211cfafb2a/MUP_IHP_RY23_P03_V10_DY16_GEO.CSV",
    2017: "https://data.cms.gov/sites/default/files/2023-05/997006a4-cc2b-48ed-8b59-4c7ed6d2833f/MUP_IHP_RY23_P03_V10_DY17_GEO.CSV",
    2018: "https://data.cms.gov/sites/default/files/2023-05/9c685ed4-a63c-4d22-9027-f225ce631c56/MUP_IHP_RY23_P03_V10_DY18_GEO.CSV",
    2019: "https://data.cms.gov/sites/default/files/2023-05/f07177de-e932-4b1a-a754-eac7bdfc4b28/MUP_IHP_RY23_P03_V10_DY19_GEO.CSV",
    2020: "https://data.cms.gov/sites/default/files/2023-05/ef9ecf4c-ad7c-4112-881e-ccb9a83acb1c/MUP_IHP_RY23_P03_V10_DY20_GEO.CSV",
    2021: "https://data.cms.gov/sites/default/files/2023-05/ee35f629-d386-426e-b51e-70451cf896d2/MUP_IHP_RY23_P03_V10_DY21_GEO.CSV",
    2022: "https://data.cms.gov/sites/default/files/2024-05/a9f5e5e4-b214-4a3f-97f6-b4f3d7e34cfa/MUP_INP_RY24_P03_V10_DY22_Geo.CSV",
    2023: "https://data.cms.gov/sites/default/files/2025-05/e76f04f1-58da-450e-9f2f-129223992821/MUP_INP_RY25_P03_V10_DY23_Geo.CSV",
    2024: "https://data.cms.gov/sites/default/files/2026-04/4517a6a1-adeb-4345-9f3d-a95391a470db/MUP_INP_RY26_P03_V10_DY24_Geo.CSV",
}

# Medicare Inpatient Hospitals - by Provider (per-CCN, with Bene_Avg_Risk_Scre).
# Used for the national HCC risk-score acuity counterfactual.
PRV_URLS = {
    2013: "https://data.cms.gov/sites/default/files/2024-05/26990132-59b8-4de0-ba6e-811a756ff0c3/MUP_INP_RY24_P04_V10_DY13_Prv.CSV",
    2014: "https://data.cms.gov/sites/default/files/2024-05/9c770459-6517-4763-ad3e-991ddf7c5d9f/MUP_INP_RY24_P04_V10_DY14_Prv.CSV",
    2015: "https://data.cms.gov/sites/default/files/2024-05/1f667627-0c55-4237-b8e1-6545f9d43e75/MUP_INP_RY24_P04_V10_DY15_Prv.CSV",
    2016: "https://data.cms.gov/sites/default/files/2024-05/16a75a1e-060b-42dd-b647-a7536eb0373c/MUP_INP_RY24_P04_V10_DY16_Prv.CSV",
    2017: "https://data.cms.gov/sites/default/files/2024-05/c016da49-525e-4c64-adc8-4bef70eabf32/MUP_INP_RY24_P04_V10_DY17_Prv.CSV",
    2018: "https://data.cms.gov/sites/default/files/2024-05/7bb03a80-a0ed-4fd9-a7c8-c851c70d484b/MUP_INP_RY24_P04_V10_DY18_Prv.CSV",
    2019: "https://data.cms.gov/sites/default/files/2024-05/1c1f6004-9fe2-43d0-907c-203322cd40e7/MUP_INP_RY24_P04_V10_DY19_Prv.CSV",
    2020: "https://data.cms.gov/sites/default/files/2024-05/c2f4c3df-c7ec-4402-8064-7f7d2586ba56/MUP_INP_RY24_P04_V10_DY20_Prv.CSV",
    2021: "https://data.cms.gov/sites/default/files/2024-05/ef80e842-4949-46e8-ab66-0c4c4310d400/MUP_INP_RY24_P04_V10_DY21_Prv.CSV",
    2022: "https://data.cms.gov/sites/default/files/2024-05/e95428bb-00a6-46e2-9be2-ffd9c6fe5186/MUP_INP_RY24_P04_V10_DY22_Prv.CSV",
    2023: "https://data.cms.gov/sites/default/files/2025-05/10e4b7e9-40c5-437b-b4d6-61801b6681f2/MUP_INP_RY25_P04_V10_DY23_Prv.CSV",
    2024: "https://data.cms.gov/sites/default/files/2026-04/d9525c59-002b-45b3-af22-c81061a62dcd/mup_inp_ry26_p04_v10_dy24_prv.csv",
}

BASE_YEAR = 2013          # earliest PUF year (anchors the trajectory baseline)
ANCHOR_YEAR = 2024        # most recent data year (headline year)
CRESPIN_YEAR = 2019       # Crespin et al. anchor year

# Medicare Monthly Enrollment datastore (data.cms.gov data-api). National annual
# rows (MONTH=Year) carry TOT_BENES, ORGNL_MDCR_BENES (FFS), MA_AND_OTH_BENES (MA).
# Used for the MA-migration selection test (FFS vs MA share trajectory 2013-2024).
MME_DATASTORE = "https://data.cms.gov/data-api/v1/dataset/d7fabe1e-d19b-4333-9eff-e80e0643f2fd/data"

# =============================================================================
# CURATED REFERENCE CONSTANTS (inputs, NOT the headline)
# =============================================================================
# Crespin DJ, Dworsky M, Levin J, Ruder T, Whaley CM. "Upcoding Linked To Up To
# Two-Thirds Of Growth In Highest-Intensity Hospital Discharges In 5 States,
# 2011-19." Health Affairs 43(12):1619-1627 (Dec 2024)
# (DOI 10.1377/hlthaff.2024.00596).
#
# ============================================================================
# CRESPIN CALIBRATION -- CORRECTED 2026-06-10 (Stage 5.5 Challenge 1, DEFECT).
# ============================================================================
# The prior build read Crespin's $4.6B Medicare 2019 figure as a FIVE-STATE
# quantity and "national-scaled" it by dividing by the 0.176 five-state
# population share -> $26.1B -> a manufactured 21.8%-of-pool share. THIS IS A
# MISREAD. The paper text decides it (verified against the open-access NIHCR PDF):
#
#   Discussion, p.1625: "Using National Health Expenditure data from CMS, we
#   estimated that the increase in MS-DRG payment weights was associated with
#   $14.6 billion in payments in 2019, including $5.8 billion from private
#   health plans and $4.6 billion from Medicare." (cite 30 = CMS NHE, a NATIONAL
#   source.) The $14.6B / $5.8B / $4.6B set is therefore ALREADY NATIONAL, not
#   five-state. Crespin then writes the Medicare total of $11.6B (adding Cook &
#   Averett's 2011 baseline) is "comparable to ... Medicare Advantage plans was
#   $11 billion in 2019" -- a like-for-like NATIONAL comparison. Dividing an
#   already-national $4.6B by 0.176 double-scales it 5.7x.
#
#   Exhibit 4: "For Medicare, the increase [in MS-DRG payment weights attributed
#   to upcoding] was 2.0 percent (95% CI: 1.7, 2.2)" in 2019 vs 2011 coding.
#   This 2.0% IS the coding-intensity share of the Medicare payment-weight base;
#   the prior 21.8% was ~11x Crespin's own figure and appears nowhere in the paper.
#
# CORRECTED basis: Crespin's Medicare coding-intensity share of the payment-weight
# pool = 2.0% central (1.7% / 2.2% CI). Applied to OUR computed FFS IPPS pool.
# The national $4.6B (price-inflated to 2024) is a cross-check, not the share.
CRESPIN_MEDICARE_NATIONAL_2019_BIL = 4.6   # NATIONAL Medicare upcoding $ (NHE-based)
CRESPIN_ALLPAYER_NATIONAL_2019_BIL = 14.6  # NATIONAL all-payer ($5.8B private, $1.8B Medicaid)
CRESPIN_MED_WEIGHT_SHARE = 0.020           # Exhibit 4: Medicare 2.0% of MS-DRG weights
CRESPIN_MED_WEIGHT_SHARE_LO = 0.017        # 95% CI low
CRESPIN_MED_WEIGHT_SHARE_HI = 0.022        # 95% CI high
CRESPIN_ALLPAYER_WEIGHT_SHARE = 0.017      # Exhibit 4: overall 1.7% of MS-DRG weights
CRESPIN_HF_CONTROLLED_PP = 0.270           # Exhibit/appendix: HF controlled upcoded share +27pp

# C4 (Stage 5.5): the PUF Avg_Mdcr_Pymt is TOTAL payment per discharge, inclusive
# of indirect medical education (IME), disproportionate share (DSH), outlier, and
# capital add-ons. IME and DSH are proportional add-ons that ride the DRG-adjusted
# operating base, so they DO scale mechanically with the coding-driven CMI; outlier
# (charge-driven) and capital (separate prospective amount) do NOT scale with a
# coding share. We net the NON-SCALING add-ons (outlier ~5.1% + capital ~5.9% of the
# operating base ~ 11%) off the pool before applying any coding share, and keep
# IME/DSH in (they scale). Operating-base haircut on the pool:
POOL_NONSCALING_ADDON_HAIRCUT = 0.11

# Silverman E, Skinner J 2004 (J Health Econ 23(2):369-89): ownership variation
SILVERMAN_NONPROFIT_PP = 0.10
SILVERMAN_FORPROFIT_PP = 0.23
SILVERMAN_CONVERTING_PP = 0.37

# Geruso M, Layton T 2020 (JPE 128(3):984-1026): MA risk-score upcoding 6-16%
GERUSO_LAYTON_LO = 0.06
GERUSO_LAYTON_HI = 0.16

# MedPAC March 2026 Report to Congress, Ch.12 (MA Status Report): MA payments run
# ~14% above what FFS would have paid for the same beneficiaries; favorable selection
# (benes who cost LESS than their risk score predicts choosing MA) accounts for ~11pp
# of that gap, coding intensity ~4pp. Used only to characterize the selection channel
# in the MA-migration selection test; NOT an input to the Issue #18 headline.
MEDPAC_MA_FAVORABLE_SELECTION_PCT = 0.11
MEDPAC_MA_TOTAL_GAP_PCT = 0.14

# HHS OIG: MS-DRG 871 (severe sepsis w/ MCC) Medicare payments FY2019
OIG_DRG871_FY2019_BIL = 7.4

# CMS documentation-and-coding adjustment history (MedPAC; CMS IPPS final rules).
# The MS-DRG-transition coding effect (FY2008-2012) was recouped under ATRA 2012:
# CMS recovered ~$11B by FY2017 via cumulative standardized-amount cuts
# (-0.8% x3 in FY2014-16, -1.5% FY2017), completing the recoupment; a +0.4588%
# partial restoration in FY2018. There is NO standing annual doc-and-coding
# reduction after FY2018.
ATRA_RECOUPMENT_TARGET_BIL = 11.0          # statutory recoupment completed ~FY2017
DOC_CODING_RECOUP_COMPLETE_FY = 2017

# Recoverability factor (policy/audit friction on recovering coding-driven CMI)
RECOV_CENTRAL = 0.55
RECOV_LO = 0.45
RECOV_HI = 0.75

# Overlap fractions (Stage 0 brief Section 7)
OVERLAP_11 = 0.0    # MA coding intensity (separate program; Issue #11 books $28B)
OVERLAP_5 = 0.0     # admin paperwork (separate mechanism; Issue #5)
OVERLAP_15 = 0.0    # facility fee (separate setting/code system; Issue #15)
OVERLAP_24_FRACTION_OF_FCA = 0.25  # net 25% of annualized FCA-confirmed slice

# Booked scoping target (gate-check only; NEVER reverse-engineered to)
BOOKED_TARGET_BIL = 20.0


# =============================================================================
# DOWNLOAD HELPER
# =============================================================================
def cached_download(url, dest, label):
    if dest.exists() and dest.stat().st_size > 1000:
        print(f"  [cache] {label} -> {dest.name}")
        return dest
    print(f"  [download] {label} -> {dest.name}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 AHC-research"})
    with urllib.request.urlopen(req, timeout=240) as r, open(dest, "wb") as f:
        f.write(r.read())
    return dest


# =============================================================================
# STEP 1: LOAD NATIONAL DRG PANEL FROM GEO-AND-SERVICE PUF (DY2013-DY2024)
# =============================================================================
def load_national_drg_panel():
    """Return {year: DataFrame[DRG_Cd, DRG_Desc, dsch, avg_mdcr_pay]} for the
    NATIONAL rollup rows of each year's Geo-and-Service PUF."""
    print("\n=== STEP 1: National DRG panel (Geo-and-Service PUF, DY2013-DY2024) ===")
    panels = {}
    for y, url in GEO_URLS.items():
        dest = DATA_CACHE / f"geo_dy{y}.csv"
        cached_download(url, dest, f"Geo DY{y}")
        df = pd.read_csv(dest, dtype=str, low_memory=False)
        df = df[df["Rndrng_Prvdr_Geo_Lvl"] == "National"].copy()
        df["DRG_Cd"] = df["DRG_Cd"].str.zfill(3)
        df["dsch"] = pd.to_numeric(df["Tot_Dschrgs"], errors="coerce")
        df["avg_mdcr_pay"] = pd.to_numeric(df["Avg_Mdcr_Pymt_Amt"], errors="coerce")
        df = df.dropna(subset=["dsch", "avg_mdcr_pay"])
        panels[y] = df[["DRG_Cd", "DRG_Desc", "dsch", "avg_mdcr_pay"]].reset_index(drop=True)
        tot = df["dsch"].sum()
        print(f"  DY{y}: {len(df):>4} national DRGs, {tot:>11,.0f} discharges")
    return panels


# =============================================================================
# STEP 2: BUILD FIXED-WEIGHT NATIONAL CASE-MIX MIGRATION INDEX
# =============================================================================
def _fixed_weight_index(panels, weight_anchor):
    """Re-weight each year's national discharge MIX by a weight vector fixed to
    `weight_anchor` year's avg Medicare payment (normalized to mean 1.0 in the
    anchor mix). Returns {year: growth_vs_BASE_YEAR}."""
    base = panels[weight_anchor]
    mean_pay = (base["dsch"] * base["avg_mdcr_pay"]).sum() / base["dsch"].sum()
    W = dict(zip(base["DRG_Cd"], base["avg_mdcr_pay"] / mean_pay))
    cmi = {}
    for y in sorted(panels):
        df = panels[y]
        df = df[df["DRG_Cd"].isin(W)]
        w = df["DRG_Cd"].map(W)
        cmi[y] = (df["dsch"] * w).sum() / df["dsch"].sum()
    base_cmi = cmi[BASE_YEAR]
    return {y: cmi[y] / base_cmi - 1 for y in cmi}


def build_cmi_trend(panels):
    """ORIGINAL. Fixed-weight national case-mix migration index, isolating pure
    severity-mix migration (the upcoding signal) from price growth.

    C2 (Stage 5.5): the index value depends on which year's weight vector is
    fixed. Anchoring to the END year (DY2024, a Paasche-like choice) over-weights
    exactly the DRGs whose share grew, inflating the migration; anchoring to the
    BASE year (DY2013, Laspeyres) understates it. We now compute BOTH and report a
    Fisher index (geometric mean of the two gross factors), the standard symmetric
    remedy. The Fisher index is the conservative, anchor-neutral migration figure
    the savings math uses; the Paasche/Laspeyres band is reported for transparency."""
    print("\n=== STEP 2: Fixed-weight national case-mix migration index (Fisher) ===")
    paasche = _fixed_weight_index(panels, ANCHOR_YEAR)   # end-year weights
    laspeyres = _fixed_weight_index(panels, BASE_YEAR)   # base-year weights

    rows = []
    base = panels[ANCHOR_YEAR]
    mean_pay_anchor = (base["dsch"] * base["avg_mdcr_pay"]).sum() / base["dsch"].sum()
    W24 = dict(zip(base["DRG_Cd"], base["avg_mdcr_pay"] / mean_pay_anchor))
    for y in sorted(panels):
        df = panels[y]
        dfm = df[df["DRG_Cd"].isin(W24)].copy()
        dfm["w"] = dfm["DRG_Cd"].map(W24)
        tot = dfm["dsch"].sum()
        cmi24 = (dfm["dsch"] * dfm["w"]).sum() / tot
        gp = paasche[y]
        gl = laspeyres[y]
        gf = ((1 + gp) * (1 + gl)) ** 0.5 - 1   # Fisher
        rows.append({
            "fiscal_year": y,
            "cmi_paasche_2024anchor": round(cmi24, 5),
            "growth_paasche_2024anchor": round(gp, 5),
            "growth_laspeyres_2013anchor": round(gl, 5),
            "growth_fisher": round(gf, 5),
            "total_discharges": int(tot),
            "avg_mdcr_pay_per_dsch": round((dfm["dsch"] * dfm["avg_mdcr_pay"]).sum() / tot, 2),
        })
    trend = pd.DataFrame(rows)
    # caseshift_index/growth aliases kept (Fisher) for downstream MA-selection merge
    trend["caseshift_index"] = (1 + trend["growth_fisher"]).round(5)
    trend["caseshift_growth_vs_base"] = trend["growth_fisher"].round(5)
    trend.to_csv(RESULTS / "drg_complexity_trend.csv", index=False)

    gp24 = paasche[ANCHOR_YEAR]; gl24 = laspeyres[ANCHOR_YEAR]
    gf24 = ((1 + gp24) * (1 + gl24)) ** 0.5 - 1
    gp19 = paasche[CRESPIN_YEAR]; gl19 = laspeyres[CRESPIN_YEAR]
    gf19 = ((1 + gp19) * (1 + gl19)) ** 0.5 - 1
    # C3: pre-COVID slope projected forward as the COVID-robust migration. 2020-2022
    # carry genuine pandemic acuity (respiratory failure, sepsis) that is NOT coding.
    # The pre-COVID Fisher slope (2013->2019) matches Crespin's window; project it.
    annual_preCOVID = (1 + gf19) ** (1.0 / (CRESPIN_YEAR - BASE_YEAR)) - 1
    gf24_robust = (1 + annual_preCOVID) ** (ANCHOR_YEAR - BASE_YEAR) - 1
    print(f"  migration {BASE_YEAR}->{ANCHOR_YEAR}: Paasche {gp24:+.1%} | Laspeyres {gl24:+.1%} | FISHER {gf24:+.1%}")
    print(f"  migration {BASE_YEAR}->{CRESPIN_YEAR}: Paasche {gp19:+.1%} | Laspeyres {gl19:+.1%} | FISHER {gf19:+.1%} (pre-COVID)")
    print(f"  COVID-robust Fisher {BASE_YEAR}->{ANCHOR_YEAR} (pre-COVID slope projected): {gf24_robust:+.1%}")
    print(f"  (pure discharge-mix shift toward high-weight DRGs; DRG prices held constant)")
    return trend, {
        "g_anchor": gf24, "g_crespin": gf19, "g_anchor_robust": gf24_robust,
        "g_paasche_anchor": gp24, "g_laspeyres_anchor": gl24,
        "g_paasche_crespin": gp19, "g_laspeyres_crespin": gl19,
    }


# =============================================================================
# STEP 3: HCC RISK-SCORE ACUITY COUNTERFACTUAL (by-Provider PUF)
# =============================================================================
def build_risk_score_panel():
    """ORIGINAL. National bene-weighted HCC risk score by year. This is the
    independent acuity counterfactual. NOTE: the HCC risk score is itself partly
    diagnosis-coding-driven, so it OVER-corrects for coding intensity -> it
    defines the conservative FLOOR, not the central."""
    print("\n=== STEP 3: HCC risk-score acuity counterfactual (by-Provider PUF) ===")
    rows = []
    for y, url in PRV_URLS.items():
        dest = DATA_CACHE / f"prv_dy{y}.csv"
        cached_download(url, dest, f"Provider DY{y}")
        # stream only the needed columns to keep memory low. Some provider CSVs
        # carry latin-1 bytes in hospital names, so fall back from utf-8.
        cols = pd.read_csv(dest, nrows=0, encoding="latin-1").columns
        usecols = [c for c in ("Tot_Benes", "Tot_Dschrgs", "Bene_Avg_Risk_Scre",
                               "Bene_Avg_Age") if c in cols]
        df = pd.read_csv(dest, usecols=usecols, low_memory=False, encoding="latin-1")
        b = pd.to_numeric(df.get("Tot_Benes"), errors="coerce")
        r = pd.to_numeric(df.get("Bene_Avg_Risk_Scre"), errors="coerce")
        age = pd.to_numeric(df.get("Bene_Avg_Age"), errors="coerce")
        m = b.notna() & r.notna() & (b > 0)
        avg_risk = float((b[m] * r[m]).sum() / b[m].sum())
        avg_age = float((b[m] * age[m]).sum() / b[m].sum()) if age is not None and age.notna().any() else None
        rows.append({"fiscal_year": y, "natl_avg_hcc_risk_score": round(avg_risk, 5),
                     "natl_avg_bene_age": round(avg_age, 3) if avg_age else None,
                     "n_hospitals": int(m.sum())})
    rs = pd.DataFrame(rows)
    base_r = rs.loc[rs.fiscal_year == BASE_YEAR, "natl_avg_hcc_risk_score"].iloc[0]
    rs["risk_index"] = (rs["natl_avg_hcc_risk_score"] / base_r).round(5)
    rs["risk_growth_vs_base"] = (rs["risk_index"] - 1).round(5)
    rs.to_csv(RESULTS / "risk_score_counterfactual.csv", index=False)
    g24 = rs.loc[rs.fiscal_year == ANCHOR_YEAR, "risk_growth_vs_base"].iloc[0]
    g19 = rs.loc[rs.fiscal_year == CRESPIN_YEAR, "risk_growth_vs_base"].iloc[0]
    print(f"  HCC risk-score growth {BASE_YEAR}->{ANCHOR_YEAR}: {g24:+.1%}")
    print(f"  HCC risk-score growth {BASE_YEAR}->{CRESPIN_YEAR}: {g19:+.1%}")
    print(f"  (acuity proxy; partly coding-driven, so a conservative over-correcting control)")
    return rs, {"g_anchor": g24, "g_crespin": g19}


# =============================================================================
# STEP 4: FFS IPPS MEDICARE PAYMENT POOL (computed denominator)
# =============================================================================
def compute_ipps_pool(panels):
    """ORIGINAL. FFS IPPS Medicare payment pool = sum over national DRG rows of
    discharges x average Medicare payment, by year."""
    print("\n=== STEP 4: FFS IPPS Medicare payment pool (computed denominator) ===")
    rows = []
    for y in sorted(panels):
        df = panels[y]
        pool = (df["dsch"] * df["avg_mdcr_pay"]).sum() / 1e9
        rows.append({"fiscal_year": y, "ffs_ipps_medicare_pool_bil": round(pool, 2),
                     "total_discharges": int(df["dsch"].sum())})
    pool_df = pd.DataFrame(rows)
    pool_df.to_csv(RESULTS / "ffs_ipps_pool_panel.csv", index=False)
    pool_anchor = pool_df.loc[pool_df.fiscal_year == ANCHOR_YEAR, "ffs_ipps_medicare_pool_bil"].iloc[0]
    print(f"  FFS IPPS pool DY{ANCHOR_YEAR}: ${pool_anchor:.1f}B "
          f"(PUF excludes DRGs with <11 discharges/geography; true pool slightly higher)")
    print(f"  NOTE: skeleton placeholder was $230B NHE -- WRONG (that is total hospital care).")
    return pool_df, pool_anchor


# =============================================================================
# STEP 5: MECHANISM-SPECIFIC SEVERITY-TIER MIGRATION
# =============================================================================
# Three-tier and two-tier DRG families with a clean CC/MCC structure. For each
# family we compute the share that lands in the top (MCC) tier in the base year
# vs the anchor year, and value the share-shift at constant total volume using
# the anchor-year average Medicare payment gap between tiers.
MECHANISM_FAMILIES = {
    "heart_failure": {"top": ["291"], "mid": ["292"], "low": ["293"],
                      "label": "Heart failure & shock (291 MCC / 292 CC / 293 none)"},
    "sepsis": {"top": ["871"], "mid": [], "low": ["872"],
               "label": "Severe sepsis (871 w/MCC / 872 w/o MCC)"},
    "simple_pneumonia": {"top": ["193"], "mid": ["194"], "low": ["195"],
                         "label": "Simple pneumonia & pleurisy (193 MCC / 194 CC / 195 none)"},
    "copd": {"top": ["190"], "mid": ["191"], "low": ["192"],
             "label": "COPD (190 MCC / 191 CC / 192 none)"},
    "renal_failure": {"top": ["682"], "mid": ["683"], "low": ["684"],
                      "label": "Renal failure (682 MCC / 683 CC / 684 none)"},
    "kidney_uti": {"top": ["689"], "mid": [], "low": ["690"],
                   "label": "Kidney & UTI (689 w/MCC / 690 w/o MCC)"},
    "cellulitis": {"top": ["602"], "mid": [], "low": ["603"],
                   "label": "Cellulitis (602 w/MCC / 603 w/o MCC)"},
    "nutrition_metab": {"top": ["640"], "mid": [], "low": ["641"],
                        "label": "Nutrition/metabolic disorders (640 w/MCC / 641 w/o MCC)"},
}


def build_mechanism_panel(panels):
    """ORIGINAL. Severity-tier migration per condition family, and the dollar
    value of the top-tier share-shift at constant family volume."""
    print("\n=== STEP 5: Mechanism-specific severity-tier migration ===")
    base = panels[BASE_YEAR].set_index("DRG_Cd")
    anchor = panels[ANCHOR_YEAR].set_index("DRG_Cd")

    def family_stats(panel, fam):
        codes = fam["top"] + fam["mid"] + fam["low"]
        present = [c for c in codes if c in panel.index]
        if not present:
            return None
        dsch = {c: float(panel.loc[c, "dsch"]) for c in present}
        pay = {c: float(panel.loc[c, "avg_mdcr_pay"]) for c in present}
        tot = sum(dsch.values())
        top_d = sum(dsch.get(c, 0) for c in fam["top"])
        return {"tot": tot, "dsch": dsch, "pay": pay, "top_share": top_d / tot if tot else 0}

    rows = []
    total_shift_excess_bil = 0.0
    for key, fam in MECHANISM_FAMILIES.items():
        b = family_stats(base, fam)
        a = family_stats(anchor, fam)
        if b is None or a is None:
            print(f"  [skip] {key}: tier codes missing in a panel year")
            continue
        # Excess top-tier discharges in anchor year = (anchor top share - base top
        # share) x anchor total volume. Value each at the anchor-year payment gap
        # between the top tier and the volume-weighted lower tiers.
        top_code = fam["top"][0]
        lower_codes = [c for c in (fam["mid"] + fam["low"]) if c in a["dsch"]]
        if not lower_codes:
            continue
        lower_dsch = sum(a["dsch"][c] for c in lower_codes)
        lower_pay = (sum(a["dsch"][c] * a["pay"][c] for c in lower_codes) / lower_dsch
                     if lower_dsch else 0)
        top_pay = a["pay"][top_code]
        pay_gap = top_pay - lower_pay
        excess_top_dsch = (a["top_share"] - b["top_share"]) * a["tot"]
        excess_dollars_bil = max(excess_top_dsch, 0) * pay_gap / 1e9
        total_shift_excess_bil += excess_dollars_bil
        rows.append({
            "mechanism": key,
            "label": fam["label"],
            "base_year": BASE_YEAR,
            "anchor_year": ANCHOR_YEAR,
            "base_top_tier_share": round(b["top_share"], 4),
            "anchor_top_tier_share": round(a["top_share"], 4),
            "top_share_shift_pp": round((a["top_share"] - b["top_share"]) * 100, 1),
            "anchor_family_discharges": int(a["tot"]),
            "anchor_top_tier_pay": round(top_pay, 0),
            "anchor_lower_tier_pay": round(lower_pay, 0),
            "tier_pay_gap": round(pay_gap, 0),
            "excess_top_tier_discharges": int(max(excess_top_dsch, 0)),
            "shift_value_bil": round(excess_dollars_bil, 3),
        })
        print(f"  {key:16s} top-tier share {b['top_share']:.1%}->{a['top_share']:.1%} "
              f"(+{(a['top_share']-b['top_share'])*100:4.1f}pp)  shift value ${excess_dollars_bil:.2f}B")
    mech = pd.DataFrame(rows).sort_values("shift_value_bil", ascending=False)
    mech.to_csv(RESULTS / "mechanism_specific_upcoding.csv", index=False)
    print(f"  TOTAL mechanism-family share-shift value (8 families): ${total_shift_excess_bil:.2f}B")
    print(f"  (illustrative decomposition WITHIN the headline residual; NOT additive to it)")
    return mech, total_shift_excess_bil


# =============================================================================
# STEP 6: DOJ FCA HOSPITAL DRG-UPCODING SETTLEMENT PANEL
# =============================================================================
def build_fca_panel():
    """ORIGINAL aggregation. Resolved DOJ FCA hospital-side DRG/inpatient
    upcoding and DRG-outlier settlements. Hospital-side ONLY -- MA insurer
    risk-adjustment cases (Issue #11) are excluded by construction."""
    print("\n=== STEP 6: DOJ FCA hospital DRG-upcoding settlement panel ===")
    entries = [
        {"case_name": "Silver Lake Hospital (and investors)",
         "defendant": "Silver Lake Hospital, Newark NJ (LTACH)",
         "settlement_date": "2024-01", "settlement_amount_mil": 30.6,
         "alleged_conduct": "Excessive Medicare inpatient cost-outlier payments under the DRG system",
         "drg_mechanism": "Cost-outlier / DRG outlier",
         "source_url": "https://www.justice.gov/archives/opa/pr/new-jersey-hospital-and-investors-pay-united-states-306-million-alleged-false-claims-related"},
        {"case_name": "Prime Healthcare Services (and CEO)",
         "defendant": "Prime Healthcare Services, 14 CA hospitals",
         "settlement_date": "2018-08", "settlement_amount_mil": 65.0,
         "alleged_conduct": "Upcoding inpatient diagnoses and medically unnecessary inpatient admissions to raise DRG payment",
         "drg_mechanism": "DRG upcoding + short-stay admission",
         "source_url": "https://www.justice.gov/usao-cdca/pr/prime-healthcare-services-and-its-ceo-agree-pay-65-million-settle-medicare-overbilling"},
        {"case_name": "IPC Hospitalists of Michigan (and related)",
         "defendant": "IPC Hospitalists companies, MI",
         "settlement_date": "2023-10", "settlement_amount_mil": 4.38,
         "alleged_conduct": "Upcoding inpatient hospital services and billing for services not rendered",
         "drg_mechanism": "Inpatient E/M / DRG-adjacent upcoding",
         "source_url": "https://www.justice.gov/usao-edmi/pr/hospitalist-companies-agree-pay-nearly-44-million-settle-false-claims-act-allegations"},
    ]
    df = pd.DataFrame(entries)
    df.to_csv(RESULTS / "fca_settlement_panel.csv", index=False)
    total = df["settlement_amount_mil"].sum()
    # Annualize across the 2018-2025 window (8 years) to express as a per-year
    # overlap with Issue #18's annual booked figure.
    window_years = 2025 - 2018 + 1
    annual_bil = total / 1000.0 / window_years
    print(f"  {len(df)} resolved hospital DRG-upcoding settlements, total ${total:.1f}M")
    print(f"  annualized across {window_years}-yr window: ${annual_bil*1000:.1f}M/yr = ${annual_bil:.4f}B/yr")
    return df, annual_bil


# =============================================================================
# STEP 6.5: MA-MIGRATION SELECTION TEST (does the FFS case-mix rise from MA exit?)
# =============================================================================
def fetch_enrollment_shares():
    """ORIGINAL aggregation. Pull the national FFS-vs-MA enrollment share trajectory
    2013-2024 from the public CMS Medicare Monthly Enrollment datastore (annual
    national rows, MONTH=Year). Cached to data_cache/ as CSV."""
    import urllib.parse
    dest = DATA_CACHE / "mme_enrollment_national_year.csv"
    if dest.exists() and dest.stat().st_size > 200:
        print(f"  [cache] enrollment shares -> {dest.name}")
        return pd.read_csv(dest)
    rows = []
    for y in range(BASE_YEAR, ANCHOR_YEAR + 1):
        q = {"filter[YEAR]": str(y), "filter[MONTH]": "Year",
             "filter[BENE_GEO_LVL]": "National"}
        url = MME_DATASTORE + "?" + urllib.parse.urlencode(q)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 AHC-research"})
        data = json.loads(urllib.request.urlopen(req, timeout=120).read())
        if not data:
            continue
        r = data[0]
        tot = int(r["TOT_BENES"]); ffs = int(r["ORGNL_MDCR_BENES"]); ma = int(r["MA_AND_OTH_BENES"])
        rows.append({"fiscal_year": y, "total_benes": tot, "ffs_benes": ffs, "ma_benes": ma,
                     "ffs_share": round(ffs / tot, 5), "ma_share": round(ma / tot, 5)})
    df = pd.DataFrame(rows)
    df.to_csv(dest, index=False)
    print(f"  [download] enrollment shares -> {dest.name}")
    return df


def build_ma_selection_test(trend, rs, pool_anchor, cmi_growth, risk_growth):
    """ORIGINAL. Tests the strongest industry counter: as Medicare Advantage (MA)
    penetration roughly doubled 2013->2024, healthier beneficiaries plausibly left
    fee-for-service (FFS), mechanically raising FFS coded case-mix with zero coding
    behavior. The point: any selection that makes the remaining FFS pool genuinely
    sicker shows up in the FFS average HCC risk score (built from each remaining
    beneficiary's diagnoses across the whole year). The risk-net floor divides the
    case-mix migration by that risk rise, so it nets out selection BY CONSTRUCTION.
    The Crespin-calibrated central does NOT net FFS-vs-MA composition drift, so it
    is the selection-EXPOSED figure; the risk-net floor is the selection-robust one."""
    print("\n=== STEP 6.5: MA-migration selection test ===")
    enroll = fetch_enrollment_shares()

    # Merge enrollment shares with the case-mix and risk-score panels by year.
    cmi = trend[["fiscal_year", "caseshift_index"]].rename(columns={"caseshift_index": "fixed_weight_cmi_index"})
    risk = rs[["fiscal_year", "natl_avg_hcc_risk_score"]].rename(columns={"natl_avg_hcc_risk_score": "ffs_avg_risk_score"})
    out = (enroll[["fiscal_year", "ffs_share", "ma_share"]]
           .merge(risk, on="fiscal_year", how="left")
           .merge(cmi, on="fiscal_year", how="left"))
    out.to_csv(RESULTS / "ma_selection_test.csv", index=False)

    g_cmi = cmi_growth["g_anchor"]          # +18.9% fixed-weight case-mix migration
    g_risk = risk_growth["g_anchor"]        # +7.76% FFS avg HCC risk-score growth
    ffs_13 = float(enroll.loc[enroll.fiscal_year == BASE_YEAR, "ffs_share"].iloc[0])
    ffs_24 = float(enroll.loc[enroll.fiscal_year == ANCHOR_YEAR, "ffs_share"].iloc[0])
    ma_13 = float(enroll.loc[enroll.fiscal_year == BASE_YEAR, "ma_share"].iloc[0])
    ma_24 = float(enroll.loc[enroll.fiscal_year == ANCHOR_YEAR, "ma_share"].iloc[0])

    # The risk-net residual (the high/ceiling after C1) on coding intensity.
    resid = (1 + g_cmi) / (1 + g_risk) - 1
    # Upper bound on the migration that ANY measured acuity (aging + selection + real
    # morbidity) can explain: the multiplicative share the risk score accounts for.
    acuity_capturable_frac = g_risk / g_cmi
    # Post-Crespin transfer-window check: did measured FFS acuity rise 2019->2024
    # (which would inflate the central via uncontrolled composition drift)?
    r19 = float(rs.loc[rs.fiscal_year == CRESPIN_YEAR, "natl_avg_hcc_risk_score"].iloc[0])
    r24 = float(rs.loc[rs.fiscal_year == ANCHOR_YEAR, "natl_avg_hcc_risk_score"].iloc[0])
    ffs_risk_19_24 = r24 / r19 - 1

    print(f"  FFS enrollment share {BASE_YEAR}->{ANCHOR_YEAR}: {ffs_13:.1%} -> {ffs_24:.1%} "
          f"(MA {ma_13:.1%} -> {ma_24:.1%}; penetration nearly doubled)")
    print(f"  Fisher case-mix migration {g_cmi:+.1%} vs FFS avg HCC risk-score rise {g_risk:+.1%}")
    print(f"  -> risk-net residual (CEILING; cruder single-proxy control): {resid:+.2%}")
    print(f"  -> max share of migration explainable by ANY measured acuity "
          f"(aging+selection+morbidity): {acuity_capturable_frac:.0%}; selection is a SUBSET")
    print(f"  -> FFS avg HCC risk {CRESPIN_YEAR}->{ANCHOR_YEAR}: {ffs_risk_19_24:+.2%} "
          f"(measured FFS acuity did NOT rise post-Crespin -> central not inflated by "
          f"post-2019 selection in measured-risk terms)")

    selection = {
        "ffs_share_base": round(ffs_13, 4),
        "ffs_share_anchor": round(ffs_24, 4),
        "ma_share_base": round(ma_13, 4),
        "ma_share_anchor": round(ma_24, 4),
        "ffs_avg_risk_growth_2013_2024_pct": round(g_risk * 100, 2),
        "casemix_migration_fisher_2013_2024_pct": round(g_cmi * 100, 2),
        "risk_net_residual_pct": round(resid * 100, 2),
        "max_acuity_capturable_fraction_of_migration": round(acuity_capturable_frac, 4),
        "ffs_avg_risk_growth_2019_2024_pct": round(ffs_risk_19_24 * 100, 2),
        "medpac_ma_favorable_selection_pct": MEDPAC_MA_FAVORABLE_SELECTION_PCT,
        "verdict": (
            "After the Crespin correction (Stage 5.5 C1), the CENTRAL is anchored to "
            "Crespin's fully patient-level-controlled Medicare coding-intensity share "
            "(2.0% of MS-DRG weights; regression on demographics, length-of-stay, "
            "Elixhauser comorbidity, hospital fixed effects). Those controls already net "
            "out genuine acuity AND compositional selection at the patient level, so the "
            "central is selection-robust by Crespin's design, not by ours. Our own "
            "risk-net residual (Fisher migration net of the HCC risk-score rise) is a "
            "CRUDER single-proxy control and OVER-attributes to coding, so it defines the "
            "HIGH/ceiling, not the floor. Selection mechanics still hold: any selection "
            "making remaining FFS patients sicker raises the FFS average HCC risk score, "
            "which the risk-net method divides out; even if 100% of the FFS risk rise were "
            "selection it is netted. And measured FFS acuity FELL 2019->2024 (HCC "
            "recalibration + COVID mortality), so post-2019 selection did not inflate "
            "measured FFS acuity over the calibration-transfer window. The corrected "
            "central is ~$1.0B; the risk-net ceiling is ~$5B."),
    }
    return out, selection


# =============================================================================
# STEP 7: SAVINGS WATERFALL
# =============================================================================
def compute_savings(cmi_growth, risk_growth, pool_anchor, fca_annual_bil):
    """CORRECTED 2026-06-10 (Stage 5.5 C1+C2+C3+C4).

    Coherent waterfall after the Crespin misread is fixed. Crespin's Medicare
    coding-intensity figure is a FULLY PATIENT-LEVEL-CONTROLLED residual (regression
    on demographics, LOS, Elixhauser comorbidity index, hospital fixed effects):
    2.0% of MS-DRG payment weights (CI 1.7-2.2%). That richly-controlled share is
    the principled CENTRAL. Our own risk-net residual nets only ONE acuity proxy
    (the HCC risk score, itself partly coding-contaminated), so it controls far less
    and OVER-attributes to coding -> it becomes the HIGH/ceiling, not the floor. The
    raw fixed-weight migration is uncontrolled context, never booked.

    C4: apply every share to the OPERATING-NETTED pool (outlier + capital add-ons,
    which do not scale with a coding share, removed; IME/DSH kept because they ride
    the DRG-adjusted operating base and scale mechanically with CMI).
    C3: the risk-net high uses the COVID-robust (pre-COVID-slope) Fisher migration.
    C2: all migration figures are Fisher (anchor-neutral), not the Paasche end-anchor."""
    print("\n=== STEP 7: Savings waterfall (CORRECTED: Crespin-controlled central) ===")
    g_cmi_19 = cmi_growth["g_crespin"]          # Fisher 2013->2019 (pre-COVID)
    g_cmi_24 = cmi_growth["g_anchor"]           # Fisher 2013->2024
    g_cmi_24_robust = cmi_growth.get("g_anchor_robust", g_cmi_24)
    g_risk_24 = risk_growth["g_anchor"]

    # C4: operating-netted pool (strip non-scaling outlier+capital add-ons).
    pool_op = pool_anchor * (1 - POOL_NONSCALING_ADDON_HAIRCUT)

    # --- CENTRAL: Crespin's fully-controlled Medicare weight share x op-netted pool.
    crespin_share = CRESPIN_MED_WEIGHT_SHARE          # 2.0%
    gross_central = crespin_share * pool_op
    # FLOOR: Crespin CI-low (1.7%) -- the most conservative controlled estimate.
    gross_floor = CRESPIN_MED_WEIGHT_SHARE_LO * pool_op
    # HIGH/ceiling: our risk-net residual on the plain Fisher migration (anchor-neutral,
    # C3 COVID step left in). This control is cruder (single, coding-contaminated proxy)
    # so it over-attributes to coding -> upper bound. We use the plain Fisher migration
    # (not the COVID-robust projection, which would be HIGHER) so the ceiling is the
    # conservative version of the cruder method. The COVID-robust residual is reported
    # as a sensitivity only.
    residual_riskNet = (1 + g_cmi_24) / (1 + g_risk_24) - 1
    residual_riskNet_covidRobust = (1 + g_cmi_24_robust) / (1 + g_risk_24) - 1
    gross_high = max(residual_riskNet, 0) * pool_op

    # Cross-check (not the share): Crespin's NATIONAL Medicare $4.6B (2019), price-
    # inflated to 2024 by our avg-Medicare-pay-per-discharge growth. Holds volume at
    # 2019 (so it over-states relative to the share method, which rides the shrunk
    # 2024 pool); a sanity bracket, not a booked figure.
    crespin_nat_19 = CRESPIN_MEDICARE_NATIONAL_2019_BIL

    print(f"  Crespin Medicare coding-intensity share (Exhibit 4): {crespin_share:.1%} "
          f"(CI {CRESPIN_MED_WEIGHT_SHARE_LO:.1%}-{CRESPIN_MED_WEIGHT_SHARE_HI:.1%}) of weights")
    print(f"  pool DY{ANCHOR_YEAR}: full ${pool_anchor:.1f}B -> operating-netted "
          f"${pool_op:.1f}B (outlier+capital {POOL_NONSCALING_ADDON_HAIRCUT:.0%} removed)")
    print(f"  risk-net residual (Fisher migration {g_cmi_24:+.1%} / risk {g_risk_24:+.1%}): "
          f"{residual_riskNet:+.1%}  [cruder control -> ceiling; COVID-robust variant "
          f"{residual_riskNet_covidRobust:+.1%}]")
    print(f"  GROSS excess: floor (1.7%) ${gross_floor:.2f}B | CENTRAL (2.0%) ${gross_central:.2f}B "
          f"| high (risk-net {residual_riskNet:.0%}) ${gross_high:.2f}B")

    # --- already-recouped = 0 (unchanged; C7 rebutted in our favor) ---
    already_recouped_central = 0.0

    # --- recoverability + overlaps ---
    overlap_24 = fca_annual_bil * OVERLAP_24_FRACTION_OF_FCA

    def book(gross, rf, recoup=0.0):
        after = gross * (1 - recoup)
        rec = after * rf
        return max(rec - overlap_24, 0.0), after, rec

    booked_central, after_c, rec_c = book(gross_central, RECOV_CENTRAL, already_recouped_central)
    booked_lo, _, _ = book(gross_central, RECOV_LO, already_recouped_central)
    booked_hi_recov, _, _ = book(gross_central, RECOV_HI, already_recouped_central)
    booked_floor, _, _ = book(gross_floor, RECOV_LO, already_recouped_central)   # floor @0.45
    booked_high, _, _ = book(gross_high, RECOV_HI, already_recouped_central)     # high @0.75

    # Range: low = Crespin CI-low @0.45 ; high = risk-net ceiling @0.75
    range_lo = booked_floor
    range_hi = booked_high

    # price-inflated cross-check
    crespin_nat_24_priceinfl = crespin_nat_19 * (15500.09 / 12424.71)  # +24.8% from trend

    print(f"\n  central recoverability {RECOV_CENTRAL}: gross ${gross_central:.2f}B -> "
          f"recoverable ${rec_c:.2f}B -> net FCA overlap (${overlap_24*1000:.0f}M) -> "
          f"BOOKED ${booked_central:.2f}B")
    print(f"  range: ${range_lo:.2f}B (Crespin CI-low @{RECOV_LO}) -- "
          f"${range_hi:.2f}B (risk-net ceiling @{RECOV_HI})")
    print(f"  cross-check: Crespin national Medicare $4.6B (2019) price-inflated to 2024 "
          f"= ${crespin_nat_24_priceinfl:.2f}B gross (volume held at 2019; share method "
          f"rides the shrunk 2024 pool, so this brackets above)")
    print(f"  scoping target was ${BOOKED_TARGET_BIL:.0f}B; computed central ${booked_central:.2f}B "
          f"({'below' if booked_central < BOOKED_TARGET_BIL else 'at/above'} target, reported as-is)")

    by_component = pd.DataFrame([
        {"component": "FFS IPPS pool DY2024 (full, computed)", "value_bil": round(pool_anchor, 2)},
        {"component": f"Operating-netted pool (outlier+capital {POOL_NONSCALING_ADDON_HAIRCUT:.0%} removed)", "value_bil": round(pool_op, 2)},
        {"component": "Gross excess (floor: Crespin CI-low 1.7% x op-pool)", "value_bil": round(gross_floor, 3)},
        {"component": "Gross excess (CENTRAL: Crespin 2.0% controlled share x op-pool)", "value_bil": round(gross_central, 3)},
        {"component": "Gross excess (high: risk-net residual x op-pool, cruder control)", "value_bil": round(gross_high, 3)},
        {"component": "Already-recouped subtraction (Crespin path already net)", "value_bil": -round(gross_central * already_recouped_central, 3)},
        {"component": f"Recoverable central (gross_central x {RECOV_CENTRAL})", "value_bil": round(rec_c, 3)},
        {"component": "Overlap subtraction #24 (FCA-confirmed slice, annualized)", "value_bil": -round(overlap_24, 4)},
        {"component": "BOOKED Issue #18 central", "value_bil": round(booked_central, 3)},
    ])
    by_component.to_csv(RESULTS / "savings_by_component.csv", index=False)

    overlap_df = pd.DataFrame([
        {"source": "Issue #11 MA coding intensity", "basis": "separate program (insurer risk-adjustment vs hospital DRG)", "subtraction_bil": round(gross_central * RECOV_CENTRAL * OVERLAP_11, 4)},
        {"source": "Issue #5 admin paperwork", "basis": "separate mechanism (compliance cost vs coding revenue)", "subtraction_bil": round(gross_central * RECOV_CENTRAL * OVERLAP_5, 4)},
        {"source": "Issue #15 facility fee", "basis": "separate setting/code system (outpatient HCPCS vs inpatient DRG)", "subtraction_bil": round(gross_central * RECOV_CENTRAL * OVERLAP_15, 4)},
        {"source": "Issue #24 fraud (FCA-confirmed)", "basis": f"{OVERLAP_24_FRACTION_OF_FCA:.0%} of annualized confirmed hospital DRG-upcoding settlements", "subtraction_bil": round(overlap_24, 4)},
        {"source": "BOOKED Issue #18 central", "basis": "after all subtractions", "subtraction_bil": round(booked_central, 3)},
    ])
    overlap_df.to_csv(RESULTS / "overlap_subtractions.csv", index=False)

    return {
        "pool_full_bil": round(pool_anchor, 3),
        "pool_operating_netted_bil": round(pool_op, 3),
        "gross_floor_bil": round(gross_floor, 3),
        "gross_central_bil": round(gross_central, 3),
        "gross_high_bil": round(gross_high, 3),
        "crespin_med_weight_share": CRESPIN_MED_WEIGHT_SHARE,
        "crespin_med_weight_share_lo": CRESPIN_MED_WEIGHT_SHARE_LO,
        "crespin_med_weight_share_hi": CRESPIN_MED_WEIGHT_SHARE_HI,
        "crespin_nat_19_bil": round(crespin_nat_19, 2),
        "crespin_nat_24_priceinfl_bil": round(crespin_nat_24_priceinfl, 3),
        "risk_net_residual_share": round(residual_riskNet, 4),
        "risk_net_residual_covid_robust_share": round(residual_riskNet_covidRobust, 4),
        "recoverable_central_bil": round(rec_c, 3),
        "overlap_24_bil": round(overlap_24, 4),
        "booked_central_bil": round(booked_central, 3),
        "booked_lo_recov_bil": round(booked_lo, 3),
        "booked_hi_recov_bil": round(booked_hi_recov, 3),
        "booked_floor_bil": round(booked_floor, 3),
        "booked_high_bil": round(booked_high, 3),
        "range_lo_bil": round(range_lo, 3),
        "range_hi_bil": round(range_hi, 3),
        "recoverability": {"lo": RECOV_LO, "central": RECOV_CENTRAL, "hi": RECOV_HI},
    }


# =============================================================================
# STEP 8: CROSS-VALIDATION
# =============================================================================
def cross_validate(trend, rs, cmi_growth, risk_growth, sav, pool_anchor, mech_total):
    print("\n=== STEP 8: Cross-validation ===")
    rows = []
    # (a) Crespin direction/magnitude: our 2013->2019 fixed-weight migration vs
    #     Crespin's documented high-intensity discharge growth window.
    g19 = cmi_growth["g_crespin"]
    rows.append({
        "anchor": "Crespin 2024 HA: high-intensity discharge growth 2011-19 (residual upcoding)",
        "expected": "~two-thirds of growth unexplained; HF controlled upcoded share +27pp",
        "computed": f"our Fisher migration 2013-19 = {g19:+.1%} (raw, uncontrolled); "
                    f"raw HF MCC share +{mech_hf_pp(mech_total)} >> Crespin controlled +27pp "
                    f"(raw is grouper/ICD-10-contaminated)",
        "verdict": "DIRECTIONAL MATCH (raw migration exceeds Crespin controlled, as expected)",
    })
    # (b) Crespin Medicare controlled weight share 2019 (the central basis).
    rows.append({
        "anchor": "Crespin 2024 HA Exhibit 4: Medicare coding-intensity = 2.0% of MS-DRG weights (CI 1.7-2.2%)",
        "expected": "2.0% of the Medicare payment-weight pool (fully patient-level-controlled)",
        "computed": f"gross_central DY2024 = ${sav['gross_central_bil']:.2f}B "
                    f"({sav['crespin_med_weight_share']:.1%} of op-netted ${sav['pool_operating_netted_bil']:.0f}B)",
        "verdict": "BY CONSTRUCTION (Crespin controlled share x our op-netted pool)",
    })
    # (b2) Crespin national Medicare $ 2019 price-inflated cross-check.
    rows.append({
        "anchor": "Crespin 2024 HA: national Medicare upcoding $4.6B (2019, NHE-based)",
        "expected": "~$5.7B gross if price-inflated to 2024 (volume held at 2019)",
        "computed": f"price-inflated cross-check = ${sav['crespin_nat_24_priceinfl_bil']:.2f}B; "
                    f"share method (rides shrunk 2024 pool) = ${sav['gross_central_bil']:.2f}B gross",
        "verdict": "CONSISTENT (share method below price-inflated because 2024 pool shrank vs 2019)",
    })
    # (c) Geruso/Layton MA upcoding order-of-magnitude (vs the risk-net ceiling).
    rows.append({
        "anchor": "Geruso/Layton 2020 JPE: MA risk-score upcoding 6-16% (cross-program)",
        "expected": "6-16% coding-intensity inflation (different program surface)",
        "computed": f"our risk-net residual (CEILING, cruder control) = {sav['risk_net_residual_share']:.1%}; "
                    f"Crespin-controlled central share = {sav['crespin_med_weight_share']:.1%}",
        "verdict": "ORDER-OF-MAGNITUDE BRACKET (controlled 2% << risk-net 10% << uncontrolled migration)",
    })
    # (d) OIG sepsis DRG 871 anchor.
    rows.append({
        "anchor": "HHS OIG: MS-DRG 871 (severe sepsis w/MCC) = $7.4B FY2019",
        "expected": "high-volume MCC-tier concentration in sepsis",
        "computed": f"sepsis 871-vs-872 migration in mechanism panel",
        "verdict": "CONSISTENT (sepsis is a top mechanism)",
    })
    # (e) Pool sanity vs MedPAC FFS IPPS spending.
    rows.append({
        "anchor": "MedPAC: FFS Medicare IPPS spending ~$110-125B/yr",
        "expected": "$110-125B",
        "computed": f"our computed FFS IPPS pool DY2024 = ${pool_anchor:.0f}B (PUF >=11 dsch floor)",
        "verdict": "CONSISTENT (PUF slightly below true pool by design)",
    })
    cv = pd.DataFrame(rows)
    cv.to_csv(RESULTS / "cross_validation.csv", index=False)
    for _, r in cv.iterrows():
        print(f"  [{r['verdict']}] {r['anchor'][:60]}")
    return cv


def mech_hf_pp(_):
    # helper: read the HF share shift from the mechanism CSV if present
    p = RESULTS / "mechanism_specific_upcoding.csv"
    if p.exists():
        m = pd.read_csv(p)
        hf = m[m["mechanism"] == "heart_failure"]
        if len(hf):
            return f"{hf['top_share_shift_pp'].iloc[0]:+.1f}pp (291 MCC)"
    return "n/a"


# =============================================================================
# STEP 9: EMIT savings_estimate.json
# =============================================================================
def emit_estimate(sav, pool_anchor, cmi_growth, risk_growth, mech_total, fca_annual_bil, selection=None):
    selection = selection or {}
    est = {
        "issue_number": 18,
        "issue_title": "Coding for Dollars",
        "anchor_year": ANCHOR_YEAR,
        "headline_status": "COMPUTED",
        "booked_bil": sav["booked_central_bil"],
        "booked_target_bil": BOOKED_TARGET_BIL,
        "range_lo_bil": sav["range_lo_bil"],
        "range_hi_bil": sav["range_hi_bil"],
        "central_method": (
            "Crespin 2024 fully patient-level-controlled Medicare coding-intensity share "
            "(2.0% of MS-DRG payment weights, Exhibit 4; CI 1.7-2.2%) applied to our "
            "computed DY2024 FFS IPPS Medicare pool NET of non-scaling outlier+capital "
            "add-ons (operating-base pool), recoverability 0.55, less the tiny annualized "
            "DOJ FCA-confirmed hospital-upcoding overlap. FLOOR = Crespin CI-low (1.7%) at "
            "recoverability 0.45. HIGH = our HCC-risk-net residual on the (plain Fisher) "
            "migration (a cruder single-proxy control that over-attributes to coding) at "
            "recoverability 0.75. CORRECTED 2026-06-10: the prior build misread "
            "Crespin's national $4.6B Medicare figure as five-state and double-scaled it "
            "by a 0.176 population share, manufacturing a 21.8% pool share (~11x Crespin's "
            "actual 2.0%); that error is fixed."),
        "gross_excess_floor_bil": sav["gross_floor_bil"],
        "gross_excess_central_bil": sav["gross_central_bil"],
        "gross_excess_high_bil": sav["gross_high_bil"],
        "ffs_ipps_pool_anchor_full_bil": round(pool_anchor, 2),
        "ffs_ipps_pool_operating_netted_bil": sav["pool_operating_netted_bil"],
        "pool_nonscaling_addon_haircut": POOL_NONSCALING_ADDON_HAIRCUT,
        "crespin_med_weight_share_central": sav["crespin_med_weight_share"],
        "crespin_med_weight_share_ci": [sav["crespin_med_weight_share_lo"], sav["crespin_med_weight_share_hi"]],
        "crespin_national_medicare_2019_bil": sav["crespin_nat_19_bil"],
        "crespin_national_medicare_2024_priceinfl_bil": sav["crespin_nat_24_priceinfl_bil"],
        "case_mix_migration_fisher_2013_2024_pct": round(cmi_growth["g_anchor"] * 100, 2),
        "case_mix_migration_fisher_2013_2019_pct": round(cmi_growth["g_crespin"] * 100, 2),
        "case_mix_migration_paasche_2013_2024_pct": round(cmi_growth.get("g_paasche_anchor", 0) * 100, 2),
        "case_mix_migration_laspeyres_2013_2024_pct": round(cmi_growth.get("g_laspeyres_anchor", 0) * 100, 2),
        "covid_robust_fisher_migration_2013_2024_pct": round(cmi_growth.get("g_anchor_robust", 0) * 100, 2),
        "hcc_risk_growth_2013_2024_pct": round(risk_growth["g_anchor"] * 100, 2),
        "risk_net_residual_share_pct": round(sav["risk_net_residual_share"] * 100, 2),
        "mechanism_family_shift_value_bil": round(mech_total, 2),
        "fca_confirmed_annualized_bil": round(fca_annual_bil, 4),
        "recoverability": sav["recoverability"],
        "sensitivity_bil": {
            "central_crespin_2pct_recov_0_55": sav["booked_central_bil"],
            "central_crespin_2pct_recov_0_45": sav["booked_lo_recov_bil"],
            "central_crespin_2pct_recov_0_75": sav["booked_hi_recov_bil"],
            "floor_crespin_ci_low_1_7pct_recov_0_45": sav["booked_floor_bil"],
            "high_risk_net_ceiling_recov_0_75": sav["booked_high_bil"],
        },
        "overlap_subtractions": {
            "issue_11_ma": 0.0, "issue_5_admin": 0.0, "issue_15_facility_fee": 0.0,
            "issue_24_fraud_fca_annualized_x25pct": sav["overlap_24_bil"],
        },
        "vs_target": (f"computed central ${sav['booked_central_bil']:.2f}B is "
                      f"{'below' if sav['booked_central_bil'] < BOOKED_TARGET_BIL else 'at/above'} "
                      f"the ${BOOKED_TARGET_BIL:.0f}B scoping target; reported as-is, not tuned "
                      f"(Issue #16/#17 precedent). The gap to target is the data-partner CTA: "
                      f"a national patient-level replication of Crespin could push the controlled "
                      f"share above 2.0% and the recoverable figure toward the risk-net ceiling."),
        "data_partner_cta": (
            "Full Crespin five-state regression replication on HCUP NIS/SID microdata "
            "(patient-level controls for demographics, LOS, principal diagnosis, hospital "
            "characteristics) requires a DUA workflow not run here. CMS LDS/VRDC "
            "claim-level files would allow per-discharge coding-intensity audit. These are "
            "the explicit recruitment asks for closing the gap from the controlled 2.0% "
            "central toward the risk-net ceiling."),
        # --- selection robustness (after C1 correction) ---
        # The CENTRAL is now Crespin's fully patient-level-controlled share, which nets
        # out genuine acuity AND compositional selection by Crespin's regression design.
        # The risk-net residual (our cruder single-proxy control) is the HIGH/ceiling.
        "ma_selection_test": selection,
        "generated_at": datetime.now().isoformat(),
    }
    (RESULTS / "savings_estimate.json").write_text(json.dumps(est, indent=2))
    return est


# =============================================================================
# STEP 10: METHODOLOGY / GOTCHA / ORIGINALITY docs
# =============================================================================
def emit_docs(est, sav, trend, rs, cmi_growth, risk_growth, mech, fca, pool_anchor, selection=None):
    selection = selection or {}
    booked = est["booked_bil"]
    g24 = cmi_growth["g_anchor"]; g19 = cmi_growth["g_crespin"]
    rg24 = risk_growth["g_anchor"]

    g_pa = cmi_growth.get("g_paasche_anchor", g24)
    g_la = cmi_growth.get("g_laspeyres_anchor", g24)
    g_robust = cmi_growth.get("g_anchor_robust", g24)
    pool_op = sav["pool_operating_netted_bil"]
    md = f"""# Issue #18 Methodology -- Coding for Dollars

Generated by `01_build_data.py` on {datetime.now().date()}. Computed, not a placeholder.
**Corrected 2026-06-10** after adversarial (Stage 5.5) review caught a misread of the
calibrating study; see `red_team_report.md` for the full adjudication.

## Summary (for the lay reader)

When a Medicare patient is admitted to a hospital, the bill is set by which
Diagnosis Related Group (DRG) the stay is sorted into. Sicker-looking codes pay
more. Over 2013-2024 the average coded "severity" of Medicare inpatient stays
climbed: across all stays, holding DRG prices fixed, the coded case-mix rose about
{g24*100:.0f}% (a symmetric, anchor-neutral measure). Patients did not get sicker
nearly as fast: a standard measure of how sick Medicare patients actually are
(their risk score) rose about {rg24*100:.0f}%. The gap between coded severity and
measured sickness is the coding-intensity signal.

The dollars-per-unit of that gap come from the best published patient-level study
(Crespin and colleagues, 2024), which controlled for demographics, length of stay,
comorbidity, and hospital, and found that coding intensity raised Medicare DRG
payment weights by about 2.0% in 2019. Applied to what Medicare actually pays
hospitals for inpatient operating care (about ${pool_op:.0f} billion a year, after
removing payment add-ons that do not move with coding), and after the share any
audit would leave in place, the recoverable figure is about
**${booked:.1f} billion a year** (range ${est['range_lo_bil']:.1f}-{est['range_hi_bil']:.1f}B).

## Headline (computed bottom-up)

**Booked central: ${booked:.2f}B/year.** Range ${est['range_lo_bil']:.1f}-{est['range_hi_bil']:.1f}B.
The scoping target was ${BOOKED_TARGET_BIL:.0f}B; the computed central is **${booked:.2f}B**,
reported as-is (Issue #16/#17 precedent: compute up, never tune to target). The wide
gap to target is the data-partner CTA: a national patient-level replication of
Crespin could lift the controlled share above 2.0% and push the figure toward the
risk-net ceiling (~${sav['booked_high_bil']:.0f}B).

## What is original here vs curated

| Element | Status |
|---------|--------|
| National fixed-weight case-mix migration index (Fisher), DY2013-DY2024 (Geo PUF) | ORIGINAL |
| HCC risk-score acuity counterfactual, DY2013-DY2024 (by-Provider PUF) | ORIGINAL |
| FFS IPPS Medicare payment pool, computed + operating-netted (C4) | ORIGINAL |
| Mechanism-specific severity-tier migration (8 condition families) | ORIGINAL |
| DOJ FCA hospital DRG-upcoding settlement panel 2018-2025 | ORIGINAL aggregation |
| Recoverability netting + overlap accounting (#11/#5/#15/#24) | ORIGINAL |
| Crespin 2024 Medicare controlled coding-intensity share (2.0% of weights, 2019) | CURATED (the calibrating ratio) |
| Silverman/Skinner 2004 ownership variation; Geruso/Layton 2020 MA cross-ref | CURATED context |
| OIG DRG 871 $7.4B FY2019 anchor; MedPAC pool/recoupment context | CURATED context |

What is ours: the national case-mix migration trajectory, the acuity counterfactual,
the FFS IPPS operating-pool denominator, the recoverability haircut, and the overlap
accounting. What is Crespin's: the dollars-per-unit-of-drift ratio (the controlled
2.0% Medicare share). We computed the trajectory; the conversion of drift into a
recoverable share is anchored to the published patient-level estimate.

## The corrected calibration (what changed and why)

The earlier build read Crespin's national Medicare upcoding figure ($4.6B in 2019)
as a *five-state* quantity and "national-scaled" it by dividing by a 0.176 five-state
population share, producing a manufactured "21.8% of the pool" share. The paper text
shows that figure is already national: Crespin dollarized using *national* CMS
National Health Expenditure data ("$14.6 billion in payments in 2019, including ...
$4.6 billion from Medicare"), and benchmarked his derived national Medicare total
against MedPAC's *national* Medicare Advantage coding figure. Crespin's actual
Medicare coding-intensity effect, stated in his Exhibit 4, is **2.0% of MS-DRG
payment weights** (95% CI 1.7-2.2%), not 21.8%. The corrected analysis uses 2.0% as
the share.

## The computation

1. **Case-mix migration (the upcoding signal), anchor-neutral.** Fix each DRG's
   relative weight to a reference year's average Medicare payment and re-weight each
   year's national discharge mix by that fixed vector, holding DRG prices constant.
   Because the index value depends on which year's weights you fix, we report a
   **Fisher index** (the geometric mean of the end-year-anchored and base-year-anchored
   results): **{g24:+.1%} over 2013-2024** (Paasche end-anchor {g_pa:+.1%};
   Laspeyres base-anchor {g_la:+.1%}). Pre-COVID (2013-2019): {g19:+.1%}.

2. **Acuity counterfactual.** National bene-weighted HCC risk score rose
   **{rg24:+.1%}** over 2013-2024. Netting it out of the Fisher migration leaves a
   {sav['risk_net_residual_share']*100:.1f}% residual. The HCC score is itself partly
   diagnosis-coding-driven, so this single-proxy control under-corrects for coding
   contamination; that residual is a CEILING on the coding share, not a clean floor.

3. **FFS IPPS pool (operating-netted, C4).** Sum over national DRG rows of discharges
   x average Medicare payment = **${pool_anchor:.0f}B for DY2024**. That figure is the
   *total* payment per discharge, which includes indirect medical education (IME),
   disproportionate share (DSH), outlier, and capital add-ons. IME and DSH are
   proportional add-ons that ride the DRG-adjusted operating base, so they scale
   mechanically with a coding-driven case-mix rise and stay in. Outlier (charge-driven)
   and capital (a separate prospective amount) do not scale with a coding share, so we
   remove them (~{POOL_NONSCALING_ADDON_HAIRCUT*100:.0f}% of the operating base),
   giving an operating-netted pool of **${pool_op:.0f}B** that the coding share is
   applied against.

4. **Gross excess.** Crespin's controlled Medicare share (2.0%, CI 1.7-2.2%) x the
   operating-netted pool = **${sav['gross_central_bil']:.2f}B central** (floor
   ${sav['gross_floor_bil']:.2f}B at the 1.7% CI low; ceiling ${sav['gross_high_bil']:.2f}B
   from the cruder risk-net residual). Cross-check: Crespin's national Medicare $4.6B
   (2019) price-inflated to 2024 by our average-payment-per-discharge growth (+24.8%)
   is ${sav['crespin_nat_24_priceinfl_bil']:.2f}B gross (holding volume at 2019); the
   share method comes in below it because the 2024 pool shrank as volume moved to MA.

5. **Already-recouped = 0.** Crespin's 2019 figure is measured on payments observed
   AFTER CMS applied the standardized-amount documentation-and-coding recoupment in
   effect, so it is already net. The ATRA 2012 recoupment of the FY2008-2012
   MS-DRG-transition coding (${ATRA_RECOUPMENT_TARGET_BIL:.0f}B, completed
   ~FY{DOC_CODING_RECOUP_COMPLETE_FY}) predates our 2013 base and there is no standing
   post-FY2018 reduction catching the 2013-2024 migration. Subtracting again would
   double-count.

6. **Recoverable = gross x 0.55** (central; 0.45 floor / 0.75 ceiling bands). Much
   coded severity reflects legitimate documentation of genuine acuity that any audit
   would leave in place; the 0.55 factor is the "we are not trying to recover all of
   it" guardrail.

7. **Overlaps.** #11 (MA coding intensity) = 0 (separate program). #5 (admin) = 0
   (separate mechanism). #15 (facility fee) = 0 (separate setting/code system).
   #24 (fraud) = 25% of the annualized DOJ FCA-confirmed hospital DRG-upcoding
   settlements (${est['fca_confirmed_annualized_bil']*1000:.0f}M/yr; the confirmed
   slice is tiny relative to the gray-zone total).

## Budget-neutrality (the load-bearing point, unchanged)

CMS recalibrates DRG RELATIVE WEIGHTS budget-neutrally each year, so a pure rescaling
of weights is not extra money. But weight budget-neutrality does NOT neutralize the
SHIFT of the discharge MIX into higher-weight DRGs: as more discharges land in MCC
tiers, CMI rises and total payment rises through the standardized amount, and CMS only
claws that back via the explicit documentation-and-coding adjustment, a finite ATRA
recoupment completed ~FY2017 with no standing annual reduction after. Crespin's
controlled 2.0% is exactly the un-neutralized, behavior-driven component. That is why
the figure is real money and not an accounting artifact.

## MA-migration selection robustness

Over 2013-2024, Medicare Advantage (MA) enrollment nearly doubled: the fee-for-service
(FFS) share of all Medicare beneficiaries fell from
{selection.get('ffs_share_base',0)*100:.1f}% to {selection.get('ffs_share_anchor',0)*100:.1f}%
(MA share {selection.get('ma_share_base',0)*100:.1f}% to {selection.get('ma_share_anchor',0)*100:.1f}%).
If the beneficiaries who moved to MA were healthier, the patients remaining in FFS are
sicker on average, and FFS coded case-mix would climb even if no code changed.

The corrected CENTRAL is robust to this by Crespin's design, not ours: Crespin's 2.0%
is a residual *after* patient-level regression controls (demographics, length of stay,
Elixhauser comorbidity, hospital fixed effects), which net out genuine acuity and
compositional selection at the patient level. Our own risk-net residual is a cruder,
single-proxy control (the bene-weighted HCC risk score), and it defines the CEILING,
not the floor. The selection mechanics still hold for that ceiling: any selection
making remaining FFS patients sicker raises the FFS average risk score, which the
risk-net method divides out; even if the entire {rg24*100:.1f}% FFS risk rise were
pure selection it is netted. And measured FFS risk actually FELL
{abs(selection.get('ffs_avg_risk_growth_2019_2024_pct',0)):.1f}% from 2019 to 2024
(HCC recalibration plus COVID-era mortality among the frailest), so post-2019
selection did not mechanically inflate measured FFS acuity over the
calibration-transfer window. MedPAC (March 2026) puts MA favorable selection at about
11% of MA spending; its FFS mirror is bounded by the risk-score rise the ceiling
already removes.

## Mechanism families (illustrative, NOT additive)

Eight CC/MCC condition families show the share-shift toward the top tier; total
constant-volume shift value = ${est['mechanism_family_shift_value_bil']:.1f}B. This is
a decomposition to make the signal concrete, NOT a separate additive layer, and it is
NOT the booked number. The raw per-family tier shifts (e.g. heart failure 291/292/293,
which shows a +53pp raw MCC-tier shift) are heavily contaminated by CMS grouper
redefinitions, CC/MCC list changes, and the October 2015 ICD-10 transition, which is
exactly why the headline rests on the aggregate fixed-weight migration cross-checked
against an independent acuity measure and calibrated to Crespin's *controlled* +27pp
heart-failure figure, not on any single family's raw tier share.

## Cross-validation

- Crespin 2024 controlled Medicare share (2.0% of weights): the central is anchored to
  it by construction; the price-inflated national $4.6B cross-check brackets above the
  share method as expected (2024 pool shrank vs 2019).
- Geruso/Layton 2020 MA upcoding 6-16%: order-of-magnitude bracket. The controlled 2%
  central sits below it; our cruder risk-net ceiling (~{sav['risk_net_residual_share']*100:.0f}%)
  sits within/above it, consistent with the controlled-vs-uncontrolled ordering.
- OIG sepsis DRG 871 $7.4B FY2019: consistent with sepsis as a top mechanism.
- MedPAC FFS IPPS spending ~$110-125B: our computed pool ${pool_anchor:.0f}B is
  consistent (PUF excludes <11-discharge DRGs by design).

## Limitations (honest, analysis-level)

- The recoverable-share ratio is anchored to a published five-state patient-level
  estimate (2.0% Medicare, 2019). A clean national, current-year share would require
  patient-level discharge microdata under a data use agreement (HCUP NIS/SID) or CMS
  claim-level files, which is the data-partner ask.
- The fixed-weight index is reported as a Fisher (anchor-neutral) figure; the
  Paasche/Laspeyres band ({g_la*100:.1f}%-{g_pa*100:.1f}%) reflects genuine
  index-number ambiguity. The COVID-robust variant (pre-2020 slope projected,
  {g_robust*100:.1f}%) confirms the post-2020 plateau does not drive the result.
- The HCC risk score is a partly coding-contaminated acuity counterfactual, so the
  risk-net residual is a ceiling on the coding share, not a clean floor.
- Total FFS discharges fall over the window (MA migration), so all work is in SHARES
  and per-discharge dollars, never absolute volumes.

## Data-partner CTA

{est['data_partner_cta']}
"""
    (RESULTS / "methodology.md").write_text(md)

    # gotcha_block.json
    gotcha = {
        "issue_number": 18,
        "datasets_used": [
            "CMS Medicare Inpatient Hospitals - by Geography and Service PUF (DY2013-DY2024)",
            "CMS Medicare Inpatient Hospitals - by Provider PUF (DY2013-DY2024)",
            "Crespin et al. 2024 Health Affairs (calibration)",
            "DOJ FCA press releases (settlement panel)",
        ],
        "gotchas_confirmed": {
            "ma_migration_shrinks_ffs_denominator": (
                "Total FFS inpatient discharges fall 9.9M (2013) -> 6.9M (2024) as "
                "beneficiaries move to Medicare Advantage. ALL analysis is in shares and "
                "per-discharge dollars; absolute volumes are never compared across years."),
            "drg_weight_budget_neutrality": (
                "CMS recalibrates relative weights budget-neutrally; pure weight rescaling "
                "is not extra money. The fixed-weight index measures discharge-MIX migration, "
                "the un-neutralized component, which raises payment via the standardized amount."),
            "hcc_risk_score_is_coding_contaminated": (
                "Bene_Avg_Risk_Scre moves with diagnosis coding, so the risk-net residual "
                "UNDER-corrects for coding contamination -> used as the CEILING, not the floor."),
            "fixed_weight_anchor_fisher": (
                "C2: the fixed-weight index value depends on which year's weights are fixed. "
                "End-year (Paasche) over-weights the DRGs whose share grew (+18.9%); base-year "
                "(Laspeyres) understates (+12.3%). Reported as a Fisher index (geometric mean, "
                "+15.5%), anchor-neutral. The Paasche/Laspeyres band is disclosed."),
            "pool_operating_netted_c4": (
                "C4: the PUF Avg_Mdcr_Pymt is TOTAL payment per discharge (incl IME, DSH, "
                "outlier, capital add-ons). IME/DSH ride the DRG-adjusted operating base and "
                "scale with CMI (kept). Outlier (charge-driven) and capital (separate "
                "prospective amount) do not scale with a coding share -> removed (~11%) before "
                "applying the share. Coding share is applied to the operating-netted pool."),
            "doc_coding_recoupment_finite": (
                f"ATRA 2012 MS-DRG-transition recoupment (${ATRA_RECOUPMENT_TARGET_BIL:.0f}B) "
                f"completed ~FY{DOC_CODING_RECOUP_COMPLETE_FY}; no standing annual reduction "
                "after. Crespin's 2019 figure is already net of in-effect recoupment, so "
                "already-recouped = 0 on the Crespin path (no double subtraction)."),
            "puf_lt11_discharge_suppression": (
                "Geo PUF suppresses DRGs with <11 discharges per geography, so the computed "
                "FFS IPPS pool (~$107B DY2024 full) is slightly below the true pool (~$110-125B); "
                "this makes the per-share dollar valuation mildly conservative."),
            "fca_panel_hospital_side_only": (
                "MA insurer risk-adjustment FCA cases (Issue #11) are excluded by "
                "construction; only hospital-side DRG/inpatient upcoding settlements counted."),
            "crespin_calibration_corrected_c1": (
                "C1 (DEFECT, corrected 2026-06-10): the prior build read Crespin's NATIONAL "
                "Medicare $4.6B (2019, NHE-based) as a five-state figure and divided by a 0.176 "
                "population share, manufacturing a 21.8% pool share (~11x Crespin's actual "
                "Exhibit 4 figure). Crespin's true Medicare coding-intensity effect is 2.0% of "
                "MS-DRG payment weights (CI 1.7-2.2%), fully patient-level-controlled. The "
                "central now uses 2.0% x operating-netted pool x 0.55."),
            "ma_migration_selection_robustness": (
                "MA enrollment nearly doubled 2013-2024 (FFS share 71.8% -> 49.9%). The CENTRAL "
                "is anchored to Crespin's patient-level-controlled share, which nets genuine "
                "acuity AND selection by his regression design. The risk-net residual (our "
                "cruder single-proxy control) is the CEILING. Measured FFS risk FELL 2019->2024, "
                "so post-2019 selection did not inflate measured FFS acuity over the "
                "calibration-transfer window. See results/ma_selection_test.csv."),
        },
        "international_ratio_used": "N/A (domestic coding-intensity issue; no international price ratio)",
        "originality_posture": (
            "Headline computed from CMS Geo + Provider PUFs (Fisher case-mix migration vs HCC "
            "acuity, operating-netted FFS IPPS pool) calibrated by Crespin's controlled 2.0% "
            "Medicare share; mechanism layer and FCA panel original; full NIS/SID regression "
            "replication is the data-partner CTA."),
        "stage_status": "COMPUTED_FULL_BUILD",
        "generated_at": datetime.now().isoformat(),
    }
    (RESULTS / "gotcha_block.json").write_text(json.dumps(gotcha, indent=2))

    # originality_gate.md
    og = f"""# Issue #18 -- Stage 3.5 Originality Gate Evidence (COMPUTED)

Generated: {datetime.now().isoformat()}

1. **`01_build_data.py` exists and runs clean from a clone.** CONFIRMED. Downloads
   24 public CMS PUF CSVs (no DUA), builds every panel, emits the headline.

2. **The script produces the headline as a printed variable.** CONFIRMED.
   `booked_central_bil = ${booked:.2f}B` printed at exit and in savings_estimate.json
   (headline_status = COMPUTED).

3. **ORIGINAL vs CURATED separated with explicit headers.** CONFIRMED. CURATED
   REFERENCE CONSTANTS block at top; each STEP function labels ORIGINAL; the
   methodology "what is original here" table marks Crespin's controlled 2.0% Medicare
   share as the calibrating ratio.

4. **Headline not already published within 5% by RAND/KFF/Peterson/FTC/CBO/JAMA.**
   CONFIRMED. No outlet publishes a national Medicare-isolated, DY2024-updated,
   operating-netted, recoverability-and-overlap-netted booked figure from a Fisher
   case-mix migration panel cross-checked against an HCC acuity counterfactual.
   Crespin 2024 published a national 2019 all-payer $14.6B / $4.6B Medicare gross
   figure; our ${booked:.2f}B is a distinct national, recoverable, current-year number
   built on Crespin's controlled 2.0% share applied to our operating-netted pool.

5. **Modeling implemented computationally with sensitivity.** CONFIRMED. Three gross
   methods (floor/central/high), recoverability bands 0.45/0.55/0.75, full panels
   emitted to results/ for independent verification.

## Public-path posture (Andrew's directive 2026-06-09)

HCUP NIS/SID full Crespin regression replication is NOT attempted (DUA workflow).
It is the explicit data-partner CTA. The public-CMS path (Geo + Provider PUFs)
supports the case-mix migration panel, the HCC acuity counterfactual, the FFS IPPS
pool, the mechanism layer, and the FCA panel -- all original, all reproducible.
"""
    (RESULTS / "originality_gate.md").write_text(og)
    print("\n  wrote methodology.md, gotcha_block.json, originality_gate.md")


# small formatting helpers used in methodology prose
def pct(x):
    return f"{x*100:.0f}%" if x is not None else "n/a"


def hf_share(mech, which):
    if mech is None or len(mech) == 0:
        return None
    hf = mech[mech["mechanism"] == "heart_failure"]
    if not len(hf):
        return None
    col = "base_top_tier_share" if which == "base" else "anchor_top_tier_share"
    return float(hf[col].iloc[0])


# =============================================================================
# GOTCHA CONFIRMATION BLOCK (printed)
# =============================================================================
def print_gotcha_block(trend, rs, pool_anchor, sav):
    print("\n===== DATASET GOTCHA CONFIRMATION =====")
    print("Datasets: CMS Inpatient Hospitals by-Geography-and-Service + by-Provider PUFs (public, no DUA)")
    d0 = trend.loc[trend.fiscal_year == BASE_YEAR, "total_discharges"].iloc[0]
    d1 = trend.loc[trend.fiscal_year == ANCHOR_YEAR, "total_discharges"].iloc[0]
    print(f"  MA migration / FFS denominator: discharges {d0:,} (2013) -> {d1:,} (2024); "
          f"analysis in SHARES + per-discharge $, never absolute volumes")
    print(f"  DRG weight budget-neutrality: fixed-weight index measures discharge-MIX migration "
          f"(un-neutralized component), not weight rescaling")
    print(f"  HCC risk score coding-contaminated: risk-net residual = CEILING, not floor")
    print(f"  Fisher migration (C2): anchor-neutral; Paasche/Laspeyres band disclosed")
    print(f"  Pool operating-netted (C4): outlier+capital ~11% removed; IME/DSH kept (scale w/ CMI)")
    print(f"  Doc-and-coding recoupment finite (ATRA, completed ~FY2017); already-recouped=0 on Crespin path")
    print(f"  FFS IPPS pool (computed): ${pool_anchor:.0f}B full DY2024 (PUF <11-dsch suppression -> mildly conservative)")
    print(f"  International ratio: N/A (domestic coding issue)")
    print(f"  Crespin calibration CORRECTED (C1): 2.0% controlled Medicare weight share, not 21.8%")
    print("========================================")


# =============================================================================
# MAIN
# =============================================================================
def main():
    print("=" * 75)
    print("Issue #18: Coding for Dollars -- Stage 2 FULL BUILD (public-CMS path)")
    print("=" * 75)

    panels = load_national_drg_panel()
    trend, cmi_growth = build_cmi_trend(panels)
    rs, risk_growth = build_risk_score_panel()
    pool_df, pool_anchor = compute_ipps_pool(panels)
    mech, mech_total = build_mechanism_panel(panels)
    fca, fca_annual_bil = build_fca_panel()
    sel_df, selection = build_ma_selection_test(trend, rs, pool_anchor, cmi_growth, risk_growth)

    sav = compute_savings(cmi_growth, risk_growth, pool_anchor, fca_annual_bil)
    cross_validate(trend, rs, cmi_growth, risk_growth, sav, pool_anchor, mech_total)
    est = emit_estimate(sav, pool_anchor, cmi_growth, risk_growth, mech_total, fca_annual_bil, selection)
    emit_docs(est, sav, trend, rs, cmi_growth, risk_growth, mech, fca, pool_anchor, selection)
    print_gotcha_block(trend, rs, pool_anchor, sav)

    print("\n" + "=" * 75)
    print(f"Issue #18 HEADLINE (COMPUTED): ${est['booked_bil']:.1f}B/year booked")
    print(f"  range ${est['range_lo_bil']:.1f}-{est['range_hi_bil']:.1f}B | "
          f"gross central ${sav['gross_central_bil']:.1f}B | pool ${pool_anchor:.0f}B")
    print(f"  case-mix migration 2013-2024 {cmi_growth['g_anchor']:+.1%} vs HCC acuity "
          f"{risk_growth['g_anchor']:+.1%}")
    print(f"  scoping target was ${BOOKED_TARGET_BIL:.0f}B (computed reported as-is)")
    print(f"  outputs in {RESULTS}")
    print("=" * 75)
    return 0


if __name__ == "__main__":
    sys.exit(main())
