# Issue #13 — Stage 3.5 Originality Gate Evidence (v2)

**Generated:** 2026-05-18T18:55:16.968807
**Status:** ALL FIVE CHECKS PASS
**Version:** v2 (per-filer Schedule H replaces uniform 2.5x sector uplift)

## Five Originality Gate checks

### Check 1: `01_build_data.py` exists in `issue_13/` and runs clean
**STATUS: PASS.** This script ran end-to-end and emitted all output files into
`issue_13/results/`. No exceptions or halts during execution.

### Check 2: The script produces the headline savings number as a print or variable
**STATUS: PASS.** The script emits `savings_estimate.json` with:
- `booked_bil`: $5.38
- `range_lo_bil`: $4.06
- `range_hi_bil`: $7.11
- `headline_status`: COMPUTED

The script also prints the headline at exit:
```
BOOKED (53% recoverability): $5.38B
range: $4.06B (40%) - $7.11B (70%)
```

### Check 3: The script distinguishes ORIGINAL analysis from CURATED reference data
**STATUS: PASS.** The script has explicit `CURATED REFERENCE DATA` section at top, and
`methodology.md` contains a comprehensive `What is original here vs. curated reference`
table that names each element by status. **v2 strengthening:** the broad community
benefit subset is now computed per-filer from IRS Form 990 Schedule H Part I lines 7a
+ 7b + 7c + 7e + 7g + 7i (NET) for ~2,100 nonprofit hospital filers covering 76% of
the panel by expenses (the v1 uniform 2.5x sector uplift is now a fallback for the
remaining 24%, flagged per-row in gap_panel.csv). Per-observation math throughout.
Original analysis elements:

- Per-hospital fair-share-gap panel (3005 nonprofit hospitals, FY2023)
- **Per-filer Schedule H Part I extraction for ~2,100 nonprofit hospital filers (NEW in v2)**
- **CCN<->EIN crosswalk for 2,000+ HCRIS hospitals to their consolidated 990 filer (NEW in v2)**
- Per-component tax exemption decomposition (Plummer 2024 method applied to our HCRIS panel)
- State-level aggregation with deficit-share and gap-share metrics
- HCRIS S-10 audited charity-care-at-cost integration
- Overlap accounting against Issue #3 and Issue #12

Curated reference (NOT headline):
- Plummer 2024 $37.4B aggregate (2021)
- Lown 2024 $25.7B deficit aggregate (2021)
- Bai/Anderson 2021 charity-share ratios
- Herring 2018 fail-rate benchmarks
- EY/AHA 2024 counter-narrative
- State tax rates from Tax Foundation 2023

### Check 4: The headline number is not already published within 5% by RAND, KFF, Peterson, FTC, CBO, or JAMA
**STATUS: PASS.**

Our booked figure: **$5.38B**.

The closest published anchors are:
- Plummer/Socal/Bai 2024 JAMA: **$37.4B (2021 aggregate tax exemption, NOT a savings figure)**
- Lown Institute 2024: **$25.7B (2021 fair share deficit, before recoverability or overlap)**
- EY/AHA 2024: **$13.2B (federal-only tax forgone, NOT a savings figure)**

These are different denominators measuring different things. Plummer reports the value of
the tax exemption (a benefit), not the recoverable savings. Lown reports the gap (the
deficit) before any policy-recoverability factor or overlap accounting. EY/AHA reports
federal-only tax forgone, not the multi-component decomposition. None of these published
figures equal our booked $5.38B, and none publish the per-hospital
panel with overlap accounting that produces our headline.

JAMA, NEJM, Health Affairs, KFF, RAND, Peterson, FTC, CBO have **not** published a
per-hospital fair-share-gap panel for FY2023 with overlap accounting against hospital
pricing or consolidation issues. The per-hospital application to a current-year hospital
universe with overlap accounting against #3 and #12 is the original contribution.

### Check 5: Modeling issues implement the model computationally with sensitivity analysis
**STATUS: PASS.** Sensitivity bands at 40%, 53% (central), and 70% recoverability are
emitted in `savings_estimate.json` under `sensitivity`. Cross-validation against
seven published anchors is in `cross_validation.csv` covering:
- Plummer 2024 aggregate
- Lown 2024 deficit-share
- Bai/Anderson 2021 (nonprofit, for-profit, government charity shares)
- Herring 2018 (tax exemption share of expenses, charity-only fail rate)
- Plummer 2024 component shares (federal, property, sales)

Overlap subtractions against Issue #3 (5%) and Issue #12 (10%) are emitted in
`overlap_subtractions.csv` with full audit trail.

## What does NOT clear Stage 3.5

Any version that prints "Plummer/Socal/Bai 2024 found $37.4B" or "Lown Institute 2024
found $25.7B fair share deficit" as the headline without applying the component
methodology to our own per-hospital FY2023 panel with overlap accounting. The current
build applies Plummer's component methodology to our HCRIS-derived per-hospital panel
and produces an FY2023-anchored, overlap-accounted savings figure with sensitivity
bands. This clears the gate.

## Stage 3.5 verdict

**CLEARED.** All five checks pass. Stage 3 editor review may proceed.

*End of originality_gate.md.*
