"""
02_hrr_sensitivity.py - Issue #12: HRR-level sensitivity mini-run

Per Stage 3 editorial review (Refinement 3): the HSA market definition produces
~82% of merger markets at HHI_post >= 4000, which is partly a small-market
artifact. Stage 3 requires an HRR-level cross-validation BEFORE Stage 4 drafter
begins.

This script re-runs steps 6, 7, 8 of 01_build_data.py using HRR (Hospital
Referral Region, 306 nationally) as the market definition, instead of HSA
(Hospital Service Area, 3,436 nationally). Larger markets -> lower HHI -> lower
HHI shifts -> typically a more conservative booked figure.

Pass criterion: HRR-level booked within +/- 25% of HSA-level $31.95B
(i.e., between $24B and $40B). If outside that band, escalate.

Inputs reused from 01_build_data.py outputs:
- data_cache/_pos_annual_panel.csv
- results/merger_event_panel.csv
- data_cache/HOSP10FY2023.ZIP (extracted)
- data_cache/ZipHsaHrr19.csv

Outputs:
- results/hrr_sensitivity.csv
- results/hrr_sensitivity_summary.json
"""

import json
import zipfile
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA_CACHE = HERE / "data_cache"
RESULTS = HERE / "results"

# Reuse constants from 01_build_data.py
COOPER_2019_MONOPOLY_DIFFERENTIAL = 0.153
DAFNY_HO_LEE_2019_CROSS_MARKET_LO = 0.07
DAFNY_HO_LEE_2019_CENTRAL = 0.08
HHI_THRESHOLD_HIGHLY_CONCENTRATED = 2500
HHI_THRESHOLD_MODERATELY_CONCENTRATED = 1500
NHE_2024_PRIVATE_INSURANCE_HOSPITAL_SPEND_BIL = 595.0
OVERLAP_ADJ_3_FRACTION = 0.20
OVERLAP_ADJ_15_FRACTION = 0.05
HSA_BOOKED_REFERENCE_BIL = 13.03   # Updated 2026-05-12 post-NaN-fix patch
HSA_RAW_REFERENCE_BIL = 17.37      # Updated 2026-05-12 post-NaN-fix patch


def coef(pre_hhi, post_hhi):
    if post_hhi >= 4000:
        return COOPER_2019_MONOPOLY_DIFFERENTIAL
    elif post_hhi >= HHI_THRESHOLD_HIGHLY_CONCENTRATED:
        return 0.095
    elif post_hhi >= HHI_THRESHOLD_MODERATELY_CONCENTRATED:
        return DAFNY_HO_LEE_2019_CENTRAL
    else:
        return DAFNY_HO_LEE_2019_CROSS_MARKET_LO


def main():
    print("=" * 75)
    print("Issue #12: HRR-LEVEL SENSITIVITY MINI-RUN")
    print("=" * 75)

    # Load Dartmouth crosswalk
    dart = pd.read_csv(DATA_CACHE / "ZipHsaHrr19.csv", dtype=str)
    dart = dart.rename(columns={c: c.lower() for c in dart.columns})
    if "zipcode19" in dart.columns:
        dart = dart.rename(columns={"zipcode19": "zip5"})
    dart["zip5"] = dart["zip5"].str.zfill(5)
    dart["hrrnum"] = dart["hrrnum"].astype(str)
    print(f"Dartmouth crosswalk: {len(dart):,} ZIPs -> {dart['hrrnum'].nunique():,} HRRs")

    # Load POS annual panel
    pan = pd.read_csv(DATA_CACHE / "_pos_annual_panel.csv", dtype=str)
    pan["beds"] = pd.to_numeric(pan["beds"], errors="coerce").fillna(0)
    pan["year"] = pd.to_numeric(pan["year"], errors="coerce")
    pan["zip5"] = pan["zip5"].fillna("").str[:5].str.zfill(5)
    active = pan[pan["beds"] > 0].copy()
    active = active.merge(dart[["zip5", "hrrnum"]], on="zip5", how="left")
    matched = active["hrrnum"].notna().sum()
    print(f"ZIP->HRR join: {matched:,} of {len(active):,} ({100*matched/len(active):.1f}%)")

    # Compute HRR-year HHI from bed shares
    hhi_rows = []
    for (hrr, yr), grp in active[active["hrrnum"].notna()].groupby(["hrrnum", "year"]):
        total_beds = grp["beds"].sum()
        if total_beds <= 0:
            continue
        shares = grp["beds"] / total_beds
        hhi = float((shares ** 2).sum() * 10000)
        hhi_rows.append({"hrr": hrr, "year": int(yr), "n_hospitals": len(grp),
                          "total_beds": int(total_beds), "hhi": hhi})
    hhi_df = pd.DataFrame(hhi_rows)
    print(f"Computed HHI for {len(hhi_df):,} HRR-years across {hhi_df['hrr'].nunique():,} HRRs")
    print(f"HRR HHI 2023: median={hhi_df[hhi_df['year']==2023]['hhi'].median():.0f}, "
          f"P75={hhi_df[hhi_df['year']==2023]['hhi'].quantile(0.75):.0f}, "
          f"share>=2500 = {(hhi_df[hhi_df['year']==2023]['hhi']>=2500).mean()*100:.1f}%")

    # Load merger panel and join to HRR
    merger = pd.read_csv(RESULTS / "merger_event_panel.csv", dtype=str)
    merger = merger[merger["classified_layer"] == "consolidation_horizontal"].copy()
    merger["year"] = pd.to_numeric(merger["year"], errors="coerce")
    merger["zip5"] = merger["zip5"].fillna("").str[:5].str.zfill(5)
    merger = merger.merge(dart[["zip5", "hrrnum"]], on="zip5", how="left")
    print(f"Merger events with HRR match: {merger['hrrnum'].notna().sum():,} of {len(merger):,}")

    # Aggregate to HRR-year and compute pre/post HHI via top-2 simulation
    hrr_year_events = merger.dropna(subset=["hrrnum"]).groupby(["hrrnum", "year"]).size().reset_index(name="events")
    pre_post = []
    for _, ev in hrr_year_events.iterrows():
        hrr = ev["hrrnum"]
        yr = int(ev["year"])
        grp = active[(active["hrrnum"] == hrr) & (active["year"] == yr)]
        total_beds = grp["beds"].sum()
        if total_beds <= 0 or len(grp) < 2:
            continue
        shares = (grp["beds"].sort_values(ascending=False) / total_beds).reset_index(drop=True)
        hhi_pre = float((shares ** 2).sum() * 10000)
        new_share = shares.iloc[0] + shares.iloc[1]
        other = shares.iloc[2:].tolist()
        shares_post = [new_share] + other
        hhi_post = float(sum(s ** 2 for s in shares_post) * 10000)
        pre_post.append({
            "hrr": hrr, "year": yr, "n_hospitals": len(grp),
            "hhi_pre": hhi_pre, "hhi_post": hhi_post,
            "hhi_shift": hhi_post - hhi_pre,
            "concentrated_pre": hhi_pre >= HHI_THRESHOLD_HIGHLY_CONCENTRATED,
            "concentrated_post": hhi_post >= HHI_THRESHOLD_HIGHLY_CONCENTRATED,
        })
    hrr_panel = pd.DataFrame(pre_post)
    print(f"Computed HHI shift for {len(hrr_panel):,} merger HRR-years")
    print(f"Mean HHI shift: {hrr_panel['hhi_shift'].mean():.1f}")

    # Deduplicate to unique HRRs (largest shift retained)
    hrr_dedup = (hrr_panel.sort_values("hhi_shift", ascending=False)
                          .drop_duplicates("hrr", keep="first")
                          .reset_index(drop=True))
    print(f"HRR panel: {len(hrr_panel):,} HRR-years -> {len(hrr_dedup):,} unique merger HRRs")

    # Load spend allocation file (already carries hrrnum from 01_build_data.py)
    spend_hosp = pd.read_csv(RESULTS / "commercial_spend_at_risk.csv")
    spend_hosp["hrrnum"] = spend_hosp["hrrnum"].astype(str).str.replace(r"\.0$", "", regex=True)
    spend_by_hrr = spend_hosp[spend_hosp["hrrnum"].notna() & (spend_hosp["hrrnum"] != "nan")].groupby("hrrnum").agg(
        spend_at_risk_bil=("spend_at_risk_bil", "sum"),
        n_hospitals=("ccn", "count"),
    ).reset_index().rename(columns={"hrrnum": "hrr"})
    print(f"Spend by HRR: {len(spend_by_hrr)} HRRs, total ${spend_by_hrr['spend_at_risk_bil'].sum():.1f}B")
    # Coerce hrr key to string on both sides
    hrr_dedup["hrr"] = hrr_dedup["hrr"].astype(str)
    spend_by_hrr["hrr"] = spend_by_hrr["hrr"].astype(str)

    # Apply coefficient
    out = hrr_dedup.merge(spend_by_hrr, on="hrr", how="left")
    out["spend_at_risk_bil"] = out["spend_at_risk_bil"].fillna(0)
    out["raw_uplift"] = out.apply(lambda r: coef(r["hhi_pre"], r["hhi_post"]), axis=1)
    out["shift_intensity"] = (out["hhi_shift"] / 200.0).clip(lower=0, upper=1.0)
    out["blended_uplift"] = out["raw_uplift"] * out["shift_intensity"]
    out["raw_savings_bil"] = out["spend_at_risk_bil"] * out["blended_uplift"]

    raw_total = float(out["raw_savings_bil"].sum())
    overlap_3 = raw_total * OVERLAP_ADJ_3_FRACTION
    overlap_15 = raw_total * OVERLAP_ADJ_15_FRACTION
    booked_hrr = max(raw_total - overlap_3 - overlap_15, 0.0)

    print("")
    print("=" * 75)
    print("HRR-LEVEL RESULTS")
    print("=" * 75)
    print(f"Unique merger HRRs:        {len(out):,}")
    print(f"Merger-HRR commercial spend at risk: ${out['spend_at_risk_bil'].sum():.1f}B")
    print(f"Median uplift:             {out['blended_uplift'].median()*100:.2f}%")
    print(f"Raw gross savings (HRR):   ${raw_total:.2f}B")
    print(f"  Overlap #3 (-20%):       -${overlap_3:.2f}B")
    print(f"  Overlap #15 (-5%):       -${overlap_15:.2f}B")
    print(f"BOOKED (HRR):              ${booked_hrr:.2f}B")
    print("")
    print(f"HSA-LEVEL REFERENCE:")
    print(f"  Booked (HSA):            ${HSA_BOOKED_REFERENCE_BIL:.2f}B")
    print(f"  Raw gross (HSA):         ${HSA_RAW_REFERENCE_BIL:.2f}B")
    print("")
    delta_pct = (booked_hrr - HSA_BOOKED_REFERENCE_BIL) / HSA_BOOKED_REFERENCE_BIL
    print(f"DELTA HRR vs HSA:          {delta_pct*100:+.1f}%")
    pass_band = abs(delta_pct) <= 0.25
    print(f"WITHIN +/- 25% PASS BAND:  {'YES (proceed to Stage 4 drafter)' if pass_band else 'NO (escalate to Stage 5.5 first)'}")
    print("")
    print(f"Distribution of HRR HHI_post buckets in savings file:")
    print(pd.cut(out['hhi_post'], bins=[0,1500,2500,4000,10001]).value_counts().sort_index())

    # Write outputs
    out.to_csv(RESULTS / "hrr_sensitivity.csv", index=False)
    summary = {
        "stage": "2.5 (HRR sensitivity mini-run)",
        "hsa_reference_booked_bil": HSA_BOOKED_REFERENCE_BIL,
        "hsa_reference_raw_bil": HSA_RAW_REFERENCE_BIL,
        "hrr_unique_merger_markets": int(len(out)),
        "hrr_merger_market_spend_at_risk_bil": round(float(out["spend_at_risk_bil"].sum()), 2),
        "hrr_median_uplift_pct": round(float(out["blended_uplift"].median() * 100), 2),
        "hrr_raw_gross_bil": round(raw_total, 2),
        "hrr_overlap_3_bil": round(overlap_3, 2),
        "hrr_overlap_15_bil": round(overlap_15, 2),
        "hrr_booked_bil": round(booked_hrr, 2),
        "delta_pct_from_hsa": round(delta_pct * 100, 2),
        "pass_band_plus_minus_25pct": bool(pass_band),
        "interpretation": (
            "HRR (n=306) is larger than HSA (n=3,436). Same population of hospitals, "
            "fewer markets each with more hospitals. Pre-merger HHI is lower in HRRs. "
            "HHI shift from a top-2 merger is mechanically smaller. Booked figure "
            "should be lower at HRR level than HSA level by construction. The magnitude "
            "of the drop measures how much of the HSA result is small-market artifact "
            "versus how much is real consolidation pricing power. Delta within +/- 25% "
            "indicates the HSA result is not artifact-dominated."
        ),
        "generated_at": datetime.now().isoformat(),
    }
    (RESULTS / "hrr_sensitivity_summary.json").write_text(json.dumps(summary, indent=2))
    print(f"\nWrote results/hrr_sensitivity.csv and results/hrr_sensitivity_summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
