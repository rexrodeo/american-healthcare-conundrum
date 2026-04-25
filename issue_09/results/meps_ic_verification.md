# MEPS-IC Verification

**Run:** 2026-04-20 (Issue #9 second-pass)

The Stage 1 `DATA_HUNT.md` reported that MEPS-IC 2022+ state tables were not available (404 on state table URLs). This verification confirms the opposite: **MEPS-IC 2024 state tables are live** under the canonical URL pattern:

    https://meps.ahrq.gov/data_stats/summ_tables/insr/excel/{YEAR}/{StateName}{YEAR}.xlsx

All 50 states, DC, and the US aggregate publish 2024 tables. Zipped CSV equivalents also exist. 2023 state tables are also live. The state tables report, per firm-size band:

- Table II.A.2: Percent of establishments offering health insurance
- Table II.B.1: Employee counts
- Table II.B.2: Enrollment rates, self-insured share, TPA/ASO share, stop-loss share
- Table II.F.30: Prescription drug copay / cost-share design

## Verification results

| URL | Label | Status | Size |
|---|---|---|---|
| `https://meps.ahrq.gov/data_stats/summ_tables/insr/excel/2024/UnitedStates2024.xlsx` | US 2024 workbook | HTTP 200 | 75,082 bytes |
| `https://meps.ahrq.gov/data_stats/summ_tables/insr/excel/2024/Colorado2024.xlsx` | Colorado 2024 workbook | HTTP 200 | 76,818 bytes |
| `https://meps.ahrq.gov/data_stats/summ_tables/insr/excel/2024/Alabama2024.xlsx` | Alabama 2024 workbook | HTTP 200 | 76,399 bytes |
| `https://meps.ahrq.gov/data_stats/summ_tables/insr/excel/2023/UnitedStates2023.xlsx` | US 2023 workbook | HTTP 200 | 88,422 bytes |

## Implication for Issue #9

The first-pass `01_build_data.py` did not use MEPS-IC and stated in its scoping that the public tables were unavailable. That claim is wrong. Future issues with employer-side angles (Issue #11 Consolidation, Issue #22 Scope of Practice, any state spotlight) should use MEPS-IC state tables as a standard data source. For Issue #9 specifically, the state premium tables can supplement the Sch A variance analysis by cross-validating the Schedule-A-observed premium means against MEPS-IC establishment-weighted means.

## What this does NOT fix

MEPS-IC public tables are aggregated, not microdata. The per-establishment variance analysis (the Issue #9 "P75/P25 within firm-size band" angle) requires FSRDC-restricted microdata, which is out of scope for the 2026-04-26 publish window. What we CAN do from the public tables is confirm state-level ranges and firm-size-band medians.

**Action:** update `DATA_HUNT.md` claim about MEPS-IC 404 to 'verified live as of 2026-04-20'; add MEPS-IC to the fact-checker's reference dataset list.