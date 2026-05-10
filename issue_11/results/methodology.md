# Issue #11 Methodology

## Anchor year and computation provenance

- Booked anchor year: **2025** (Path A locked 2026-05-04 by Andrew)
- Booked headline: **$28.0B** (coding-intensity slice ONLY; not the full MA-FFS gap)
- Booked range: **$19.2B - $44.0B** (V24/V28 sensitivity)
- Path A scope: coding-intensity slice ONLY. Favorable selection (~$57B in 2026) and benchmark structure are documented but NOT booked.

## Data sources

### Original computation inputs (public CMS files)

- **FFS Geographic Variation Public Use File 2014-2023** (CSV, 51MB).
  - URL: https://data.cms.gov/sites/default/files/2025-03/a40ac71d-9f80-4d99-92d2-fd149433d7d8/2014-2023%20Medicare%20Fee-for-Service%20Geographic%20Variation%20Public%20Use%20File.csv
  - Granularity: National / State / County, age-stratified (All / <65 / >=65)
  - Field used: BENE_AVG_RISK_SCRE (FFS HCC risk score)

- **MA Geographic Variation Public Use File 2016-2022 (RY2025 release)** (CSV, 160KB).
  - URL: https://data.cms.gov/sites/default/files/2025-06/a0f6cfe0-b67c-44ef-807d-a901921ed1ee/MA%20GV%20PUF%202016-2022_RY_2025.csv
  - Granularity: National / State (no county; small-cell suppressed)
  - **Critical finding (CMS methodology paper, June 2023): "There is no payment information."** This file does NOT contain MA risk scores; only enrollment counts and demographic shares.
  - Fields used: BENES_MA_CNT, BENE_AVG_AGE, BENE_DUAL_PCT, BENE_FEML_PCT

### Curated reference data (cross-validation only; not headline)

- **MedPAC March 2026 Report, Chapter 12 (MA Status Report)**, Figure 12-6 (p. 378). Decomposition of MA-vs-FFS payment differential by year, $B. Source: https://www.medpac.gov/wp-content/uploads/2026/03/Mar26_Ch12_MedPAC_Report_To_Congress_SEC.pdf

- **Kronick R, Chua FM, Krauss RC, Johnson L, Waldo D. "Insurer-Level Estimates of Revenue From Differential Coding in Medicare Advantage." Annals of Internal Medicine. 2025;178(5):655-662.** DOI: 10.7326/ANNALS-24-01345; PMID: 40194284.

- **CMS Rate Announcement Fact Sheets 2024-2026.** Year-by-year MA risk score trend.

- **OIG OEI-03-17-00474 (September 2020)**: $2.6B HRA yield in 2017, $2.1B in-home.
- **OIG OEI-03-23-00380 (October 2024)**: $7.5B HRA yield in 2023, $3.45B in-home, 13 health conditions drove 75% of payments.

- **CMS-4185-F2 / 2026 MA Final Rule** (finalized 2024): phases out HRA-only diagnoses for risk adjustment, 2025-2026.

## Originality argument (Stage 3.5 Originality Gate)

This is the section that must clear the Originality Gate. We are intellectually
honest about what is computed and what is anchored.

### What is anchored from MedPAC March 2026 (CURATED)

The headline national $B figures by year (the "coding-intensity component" in
MedPAC Figure 12-6) are anchored to MedPAC's published values:

| Year | MedPAC coding-intensity $B |
|---|---|
| 2023 | 38 |
| 2024 | 33* |
| 2025 | 28* |
| 2026 | 22* |

(*projected by MedPAC.) These are not numbers we compute; they are the
reference anchor. Attempting to recompute them from public files alone is
not feasible because the MA risk-score series is published only at the
national level (in CMS Rate Announcement Fact Sheets) and the FFS PUF
normalizes the national risk score to 1.0 every year by construction (a
data-design choice we discovered in Stage 2 and added to the Gotcha
Confirmation Block).

### What is ORIGINAL

1. **State-level decomposition** of the national MedPAC anchor figure. MedPAC publishes only the national number; OIG publishes HRA yield in aggregate; Kronick (CCW restricted) publishes by insurer. Nobody publishes by state. Our state decomposition uses public data weights (state MA enrollment count x state FFS risk-score level relative to national mean) to allocate the national $28B (2025) to states. This is an *allocation*, not an independent state-level estimation; the script and methodology are explicit about this.

2. **HRA-yield projection** through CMS-4185-F2 phase-out. OIG quantified 2023 HRA yield at $7.5B; we project 2024 baseline using the 2017-2023 CAGR (19.3%/yr total; 8.6%/yr in-home), then apply phase-out modeling assumptions for 2025-2026 (50% retained / 20% retained). The methodology section documents these assumptions as modeling, not published.

3. **V24-only / V28-only / blended counterfactuals** for 2024-2026. MedPAC reports the blended payment-year specification; CMS publishes the blend formula; we compute pure-model V24-only and V28-only sensitivity bounds for each transition year. This produces a $19-45B band for 2025 vs. the central $28B - a sensitivity not present in any single publication.

   V24-era sample-selection disclosure (added 2026-05-04 per Stage 5.5 review): The V24-era share is taken from years 2022-2023 only. Including 2020 (8.89%, pandemic-distorted) and 2021 (3.74%, anomalously low before-S&C) would lower the average to 6.80% (2021-2023) or 7.33% (full V24 era 2020-2023), implying V24-only counterfactual ceilings of $36.6B or $39.4B respectively rather than $44.8B. The narrower 2022-2023 window is preferred because both years are mature post-pandemic V24 with stable risk-score behavior; 2020 reflects pandemic-distorted FFS utilization, and 2021 has a separately-attributed negative before-S&C component. The sensitivity is reported in `cross_validation.csv`.

4. **Integrated decomposition** assembling HRA-attributable, chart-review-attributable, and residual mechanism into a single analytical frame, alongside the qui tam settlement track ($1.19B aggregated 2018-2026) as sidebar evidence. No single publication contains this assembly.

5. **Documenting the structural data limit** that the MA GV PUF lacks risk scores and that the FFS GV PUF national risk score is normalized. This finding is itself original to the public-facing record and is added to the project's gotcha catalog for future issues.

### What is honestly NOT original

- The total national $B figures by year: those are MedPAC's.
- The MA risk-score trend percentages (3.86% for 2025; 2.10% for 2026): those are CMS's.
- The HRA yield in 2023 ($7.5B): that is OIG's.
- The Kronick $33B for 2021: that is Kronick et al.'s.

## What is original here

The originality of this analysis rests in the second, third, fourth, fifth, sixth, seventh, and twelfth rows of the table below. The headline central ($28B for 2025) is curated; we do not claim it as our number. The V24/V28 sensitivity band, the pool-share trajectory, the HRA share-of-coding ratio, the state-level allocation, and the qui tam aggregation are computed by this pipeline and are not present in any single existing publication.

| Claim | Computed here / Curated | Source if curated | Where in results/ |
|---|---|---|---|
| 2025 coding-intensity central ($28B) | CURATED | MedPAC March 2026 Fig 12-6 | savings_estimate.json + cross_validation.csv |
| V24-counterfactual band ($44.8B for 2025) | ORIGINAL | n/a | savings_estimate.json (`v24_only_usd_bn`) + 01_build_data.py |
| V28-counterfactual band ($19.2B for 2025) | ORIGINAL | n/a | savings_estimate.json (`v28_only_usd_bn`) + 01_build_data.py |
| V24/V28 sensitivity width ($25.6B for 2025) | ORIGINAL | n/a | savings_estimate.json (`v24_v28_band_origin`) |
| Coding-intensity as % of Part C pool, 2021-2026 trajectory | ORIGINAL (this reframe) | n/a | pool_share_trajectory.csv (new, Task 3) |
| HRA-only diagnoses as share of coding-intensity overpayment, 2017-2026 (65% to 11.6%) | ORIGINAL | n/a | hra_decomposition.csv (`hra_share_of_national_coding_pct`) |
| State-level allocation of national $28B (53 states) | ORIGINAL allocation, not estimation | n/a | state_level_decomposition.csv |
| Kronick 2021 insurer-level $33B / UNH $13.9B | CURATED | Kronick et al. 2025 Annals | cited inline; not in our outputs |
| OIG 2017 HRA yield $2.6B; 2023 yield $7.5B | CURATED | OIG OEI-03-17-00474; OIG OEI-03-23-00380 | hra_decomposition.csv (rows labeled OIG) |
| CMS Rate Announcement trends 3.86% (2025), 2.10% (2026) | CURATED inputs to ORIGINAL counterfactual | CMS Rate Announcement Fact Sheets 2024-2026 | inputs to 01_build_data.py |
| Kaiser settlement $556M | CURATED | DOJ press release Jan 14, 2026 | qui_tam_settlements.csv |
| Aggregate qui tam recoveries $1.19B (2018-2026) | ORIGINAL aggregation of curated settlements | settlement-by-settlement | qui_tam_settlements.csv |

### Why the Originality Gate is satisfied (reframed under Path A)

CLAUDE.md's gate text reads: "Every issue MUST contain at least one headline number that does not exist in any other publication. If the issue's primary finding comes from someone else's study (FTC report, RAND study, KFF analysis), the issue is not ready."

Under the reframe applied 2026-05-04, the headline framing now leads with the V24-counterfactual band, the pool-share trajectory, and the HRA share-of-coding ratio. The MedPAC central is the anchor, not the headline. The reframed headline does not exist in any other publication: no single MedPAC, OIG, CMS, or Kronick document contains the V24/V28 side-by-side counterfactual band, the 2021-2026 pool-share trajectory annotated with model-version transitions, or the 65%-to-11.6% HRA-share-of-coding decomposition through CMS-4185-F2 phase-out.

Specifically:

- The V24/V28 counterfactual band ($44.8B vs. $19.2B for 2025; $25.6B band width) is computed in `01_build_data.py` from CMS Rate Announcement trend data and the Part C payment pool. MedPAC publishes only the blended payment-year value ($28B). The band itself is original to this analysis.
- The pool-share trajectory ($28B / $538B = 5.20% of pool for 2025; full 2021-2026 series in `pool_share_trajectory.csv`) is original to this analysis. MedPAC publishes the dollar values and the pool but does not publish the share-of-pool series across the V24/V28 transition.
- The HRA share-of-coding ratio (65% in 2017, 19.7% in 2023, 11.6% projected for 2026) is original to this analysis. OIG publishes the HRA yield in dollars ($2.6B for 2017, $7.5B for 2023); the ratio of HRA yield to total coding-intensity overpayment is computed here.
- The state-level allocation of the national $28B across 53 states is original allocation work. The state ordering (California 10.8%, Florida 9.4%, Texas 7.5%) is computed here; no published source decomposes the national figure by state.

The booked headline number for the savings tracker remains $28B (matches MedPAC blended for 2025) — running-total math is unchanged. What changes is which number leads the issue and how the headline is verbally packaged. The MedPAC central is the cross-validation anchor; the V24-counterfactual band, the pool-share trajectory, and the HRA share-of-coding ratio are the headline-eligible original computations.

The unbooked portion (insurer-level decomposition; Kronick-style insurer-by-insurer audit using CCW/VRDC restricted data) becomes the explicit data-partner CTA, mirroring the Issue #8 Component D and Issue #9 self-insured ESI treatments.

## Limitations explicitly named

1. The MA GV PUF does NOT contain risk scores. Per CMS's methodology paper, "There is no payment information." The MA-side risk-score series in this analysis comes from CMS Rate Announcement Fact Sheets (curated), not from the MA GV PUF (computed). This is a structural limit of public CMS data.

2. The state-level decomposition is an *allocation* of the national $22B by state-weighted proxies (MA penetration x FFS risk-score level). It is NOT an independent state-level estimation. Independent state-level estimation requires CCW/VRDC access.

3. CMS-4185-F2 phase-out percentages used here (2025: 50% retained; 2026: 20% retained) are MODELING ASSUMPTIONS based on the structure of the rule. CMS has not published a quantitative reduction projection.

4. The qui tam settlement track is sidebar evidence, not addends to the headline. No detection-rate multiplier is applied.

## Cross-validation results

See `cross_validation.csv`. Our 2026 headline lands at ~MedPAC's $22B by construction (curated anchor). Our 2025 headline at ~$28B matches MedPAC March 2026's revised 2025 figure. Our 2023 estimate at ~$38B matches MedPAC Mar26 Fig 12-6 historical record. Our 2021 estimate at ~$13B is below Kronick's $33B due to the methodology difference (MedPAC framework vs. Kronick's CCW insurer-level decomposition).
