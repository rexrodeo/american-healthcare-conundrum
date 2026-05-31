# Issue #14 Methodology — The Specialist Tax (Stage 2 FULL BUILD, Stage 5.5 patched)

Generated: 2026-05-25T22:30:59.039782

## Editorial guardrail (binding)

**This analysis is the project's most physician-sensitive issue.** The savings
estimate is computed against system-level counterfactuals (different RVU
schedule, different GME allocation, different workforce mix), NOT against any
individual physician's compensation level. The villain is the payment system,
not the people who chose medicine.

Physicians make enormous personal sacrifices in training, debt, time, and
family life. 11-15 years of post-college training, $200K+ median medical
school debt (AAMC 2024), 60-80 hour residency weeks at sub-minimum-wage
hourly rates when divided out, malpractice exposure, prior authorization
burden documented in Issue #8, and administrative burden documented in
Issue #5. The compensation gap measured here is a system output, not a
personal moral failure. See scoping_brief.md Section 1 for the full
editorial guardrail and CLAUDE.md "On physicians and healthcare workers"
for project-wide policy.

## Headline

**Booked: $27.6B/year. Range: $19.6-$35.5B.**

The range is derived empirically from conservative and aggressive
recoverability bands (post-overlap), not a hard-coded ceiling. See
`results/recoverability_sensitivity.csv`.

## Stage 5.5 patch note

Component A was recomputed against the OECD-18 high-income peer group after
Stage 5.5 adversarial review identified the full-OECD median as overly
influenced by lower-income members (Bulgaria, Mexico, Costa Rica, Colombia,
Poland, Slovakia, Czech Republic, Hungary, Estonia, Latvia, Lithuania,
Croatia, Slovenia, Portugal, Greece, Israel, Turkey, Chile). The patched
analysis uses a more defensible peer comparison. The aggregation method
also shifted to median-of-country-medians (each country one vote)
rather than pooling all observations. The two methodological choices are
applied jointly. PC-share basis is fixed at 28.0% (BLS-FTE) consistently.
Range ceiling is derived from the aggressive recoverability band rather
than a hard-coded value.

## What is original analysis vs curated reference

| Element | Status |
|---------|--------|
| Per-specialty US workforce panel from CMS PUF + BLS OEWS 2024 | ORIGINAL |
| Country-by-country compensation panel from OECD DF_REMUN 2025 | ORIGINAL |
| RVU revaluation residual from CMS PFS RVU CY2025 + Medicare Geo-Svc PUF CY2024 + MedPAC June 2025 directional reval | ORIGINAL |
| GME allocation counterfactual using BLS-anchored FTE + per-FTE comp deltas + COGME target | ORIGINAL |
| Four-component aggregation with overlap subtractions and per-component recoverability factors | ORIGINAL |
| Laugesen/Glied 2011 international compensation multiples | CURATED (cross-validation) |
| Bodenheimer 2007 RVU misvaluation framing | CURATED |
| GAO-15-434 RUC critique | CURATED |
| MedPAC June 2025 directional revaluation recommendations | CURATED (anchors corrected RVU benchmark) |
| Doximity 2025 / Medscape 2025 compensation reports | CURATED (cross-validation) |

## Components

### Component A — International compensation gap (productivity-normalized)

Formula:
```
intl_gap(s) = (us_comp_per_fte(s) - oecd_peer_median_comp_per_fte(s))
            × us_fte(s)
            × productivity_norm_factor
```

Where:
- `us_comp_per_fte(s)` = BLS OEWS May 2024 A_MEAN annual wage for the matching
  29-1xxx physician occupation code. BLS OEWS is the most defensible US anchor
  because it is an observed wage statistic (not a self-report survey) and is
  released annually.
- `oecd_peer_median_comp_per_fte(s)` = OECD DF_REMUN median across the
  OECD-18 high-income peer group (USD_PPP, latest year per country).
  Computed separately for specialist (EMPLSPMP) and general practitioner
  (EMPLGENP) categories. Aggregation: median-of-country-medians (per-country
  median first, then median across countries; each country gets one vote
  regardless of how many observation rows it contributes).
- `us_fte(s)` = BLS OEWS TOT_EMP May 2024 for each matching 29-1xxx
  occupation code.
- `productivity_norm_factor` = 2.7/3.5 = 0.7714. The US has 2.7 physicians per
  1,000 population vs OECD average 3.5; US physicians see more patients per
  FTE. This factor discounts the raw gap by ~23% to reflect productivity-
  adjusted compensation.

**OECD-18 peer comparator set:** AUS, AUT, BEL, CAN, CHE, DEU, DNK, FIN,
FRA, GBR, IRL, ISL, ITA, NLD, NOR, NZL, SWE, KOR. This is the standard
"high-income OECD" or "OECD-18" peer set used in international health
systems research. It excludes the US (the unit of analysis), low-income
OECD members (Mexico, Costa Rica, Colombia, Turkey, Chile), and post-Soviet
Eastern European states (Bulgaria, Poland, Slovakia, Czech Republic,
Hungary, Estonia, Latvia, Lithuania, Croatia, Slovenia) whose physician
compensation reflects different cost structures and is not a defensible
benchmark for the US. Japan would be included if it reported physician
remuneration via DF_REMUN; it does not.

**Peer countries actually present in the OECD DF_REMUN panel:**
- Specialist data: 18 of 18 countries — AUS, AUT, BEL, CAN, CHE, DEU, DNK, FIN, FRA, GBR, IRL, ISL, ITA, KOR, NLD, NOR, NZL, SWE
- GP data:         13 of 18 countries — AUS, AUT, BEL, CAN, CHE, DEU, FIN, GBR, IRL, ISL, KOR, NLD, SWE

**Important caveat:** OECD's DF_REMUN dataset does NOT include US
physician remuneration submissions. The US anchor uses BLS OEWS A_MEAN.
This is the best public-data path; tighter comparability would require US
submission to OECD.

**Computed values (OECD-18 peer median, country-median basis):**
- OECD-18 specialist median (USD_PPP, country-median basis): $176,673
- OECD-18 GP median (USD_PPP, country-median basis): $154,664
- Component A raw: $64.2B
- Component A recoverable (×0.55): $35.3B

**Reference (NOT used in headline):**
- Full-OECD pooled specialist median (all reporting countries, pooled observations): $148,562
- Full-OECD pooled GP median: $110,508

The difference between OECD-18 country-median ($176,673) and
full-OECD pooled ($148,562) reflects both the comparator-set restriction
(excluding lower-income members) and the aggregation choice (per-country
voting). See `cross_validation.csv` row 6 for the side-by-side comparison.

### Component B — Workforce-mix counterfactual

Holds US per-FTE compensation constant. Reallocates the US specialty mix
from the current 72.0% specialist / 28.0% primary care (BLS-FTE basis,
BLS OEWS May 2024) toward the COGME 45% primary care target.

**Note on PC share basis:** This analysis uses the BLS-FTE basis (28.0%)
consistently throughout Components B and D. The AAMC headcount figure
(34.2% primary care) is referenced in some public discussion but uses a
different denominator (active physician headcount including some categories
not in BLS clinical-practice employment). The BLS basis is the correct
denominator for per-FTE compensation analysis because BLS reports observed
employment in the 29-1xxx physician occupation series. The two are not
interchangeable; per-FTE savings computed on a headcount basis would
mix populations.

Formula:
```
spending_current = pc_fte × pc_comp_per_fte + sp_fte × sp_comp_per_fte
spending_cf      = (total_fte × target_pc_share) × pc_comp_per_fte
                 + (total_fte × target_sp_share) × sp_comp_per_fte
Component B = spending_current - spending_cf
```

**Editorial:** this is NOT a pay cut. It's a national workforce composition
counterfactual that plays out over residency throughput (7-15 years).

- Current PC share (BLS-FTE basis, CANONICAL): 28.0%
- AAMC headcount basis (reference, not used): 34.2%
- COGME target: 45%
- Gap to close (BLS-FTE basis): 17.0%
- Avg PC comp per FTE: $251,820
- Avg SP comp per FTE: $287,512
- Component B raw: $4.7B
- Component B recoverable (×0.55): $2.6B
- Sensitivity at OECD 50/50 target: $6.1B raw

### Component C — RVU misvaluation residual (MedPAC June 2025 directional)

The MedPAC June 2025 Report Chapter 1 ("Reforming Physician Fee Schedule
Updates and Improving the Accuracy of Relative Payment Rates") recommends
that Congress direct the Secretary to collect and use timely cost data
for relative-value revaluation. MedPAC's qualitative finding: procedural
codes (cardiology, gastroenterology, orthopedics, ophthalmology) are
overvalued; evaluation and management (E&M) codes are undervalued.
MedPAC does NOT publish a numerical corrected-RVU table.

**Key statutory constraint:** The Medicare PFS is BUDGET-NEUTRAL by
statute (Sec. 1848(c)(2)(B) SSA). Any intra-Medicare RVU revaluation
above $20M threshold triggers a uniform conversion-factor adjustment to
hold total Medicare PFS spending constant. So Medicare-only savings from
revaluation = $0 by statute.

**Where the savings come from:** the commercial cascade. Commercial
insurers benchmark physician rates as multiples of Medicare PFS, and the
commercial premium over Medicare is much higher for procedural codes
(2.8-3.5x Medicare per Pelech 2023 MedPAC Brief, KFF Peterson Tracker)
than for E&M codes (~1.4x). When Medicare's RELATIVE weights shift
toward E&M, the COMMERCIAL absolute price for procedures drops (~3.2x
multiplier × Medicare unit value drop) while the commercial absolute
price for E&M rises by less (~1.4x × Medicare unit value rise). The
net commercial-side savings drives Component C.

Operationalization (computed in `component_c_family_breakdown.csv`):
- Procedural-family Medicare allowed (CY2024 national): $14.3B
- E&M-family Medicare allowed (CY2024 national): $42.1B
- Procedural-family commercial spending estimate: $70.2B
- E&M-family commercial spending estimate: $41.2B
- Central revaluation: 10% downward on procedural, 10% upward on E&M
- Medicare net savings: $0.00B (statutory budget neutrality)
- Commercial procedural savings: $7.02B
- Commercial E&M cost: $4.12B
- Commercial net savings: $2.89B
- Component C recoverable (×0.8): $2.32B

Sensitivity table at `results/component_c_sensitivity.csv` covers
5%/10%/15% procedural reval × 5%/10%/15% E&M reval.

### Component D — GME allocation counterfactual

The downstream physician-spending implication of reallocating federal GME
slots toward the COGME 45% primary care target.

Model:
```
gap = cogme_target_pc - current_pc_share
delta_fte_to_pc = gap × total_fte_steady_state
per_fte_delta = avg_specialty_comp - avg_primary_care_comp
raw_savings_per_year = delta_fte_to_pc × per_fte_delta
amortization_share = 0.50  (50% of mix shift over 10-year horizon,
                           per residency-throughput constraint)
Component D raw = raw_savings × amortization_share
```

- Current PC share (BLS-FTE basis, CANONICAL): 28.0%
- COGME target: 45%
- Gap share (BLS-FTE basis): 0.170
- Delta FTE to PC under COGME: 132,289
- Per-FTE specialty-to-PC comp delta: $35,692
- Raw steady-state savings: $4.72B
- Amortized 10-year (×0.5): $2.36B
- Component D recoverable (×0.6): $1.42B

**Editorial:** The savings here are NOT "spend less on GME"; they are
downstream physician-spending savings from a different workforce
composition over the rotation horizon. COGME has recommended this
allocation since the 1990s. The 2024 Medicare-supported residency
expansion already allocated 70% of new slots to primary care and
psychiatry — precedent that reallocation is feasible.

## Overlap accounting

| Source | Fraction | Subtraction ($B) |
|--------|---------:|-----------------:|
| Issue #3 hospital labor flow-through (×pre-overlap recoverable sum) | 15% | $6.24B |
| Issue #10 Procedure Mill physician-labor (×#10 booked) | 20% | $1.52B |
| Issue #11 MA coding intensity (×pre-overlap recoverable sum) | 5% | $2.08B |
| Issue #12 consolidation flow-through (×pre-overlap recoverable sum) | 10% | $4.16B |
| **TOTAL overlap subtractions** | | **$14.01B** |

## Recoverability factors

- Component A (international comp gap): 0.55
- Component B (workforce-mix counterfactual): 0.55
- Component C (RVU revaluation residual): 0.8
- Component D (GME allocation counterfactual): 0.6

These factors are JUDGMENTS about the political-economic horizon for
structural reform, not mathematical certainties. See
`results/recoverability_sensitivity.csv` for conservative/central/aggressive
bands per component.

## Booked vs raw

- Sum of recoverable components (pre-overlap): $41.63B
- Total overlap subtractions: -$14.01B
- **BOOKED (central): $27.62B**

### Sensitivity bands (post-overlap, see `recoverability_sensitivity.csv`)

| Band | Recoverability factors (A/B/C/D) | Booked post-overlap |
|------|----------------------------------|---------------------|
| Conservative | 0.40 / 0.40 / 0.60 / 0.40 | $19.65B |
| Central | 0.55 / 0.55 / 0.80 / 0.60 | $27.62B |
| Aggressive | 0.70 / 0.70 / 0.95 / 0.80 | $35.49B |

Reported range: **$19.6-$35.5B** (conservative to aggressive
recoverability). This is a defensible derivable range; prior versions cited
an unsupported ceiling.

## Anchor data

- CMS PFS Relative Value File CY2025 (RVU25D, released 2025-09-11)
- Medicare Physician & Other Practitioners by Geography and Service PUF,
  service year 2024 (release date 2026-05)
- Medicare Physician & Other Practitioners by Provider PUF, service year
  2024 (release date 2026-05)
- BLS Occupational Employment and Wage Statistics May 2024 (29-1xxx series)
- OECD Health at a Glance 2025 DF_REMUN dataset (USD_PPP, latest year
  per country, 2020-2023)
- MedPAC June 2025 Report Chapter 1
- CMS-1807-F Final Rule (CY2025 PFS) and CMS-1832-F Final Rule (CY2026 PFS)

## CMS PFS conversion factor

- CY2023: $33.89
- CY2024: $33.29
- CY2025: $32.35 (-2.83% from CY2024; per CMS-1807-F Final Rule and per
  RVU25D file)

## Stage 5.5 red-team hooks

The following challenges are pre-emptively addressed:

1. **OECD comparability** (gross vs net of social contributions): the OECD
   median computed here uses USD_PPP per the OECD's published comparability
   adjustments and is restricted to the OECD-18 high-income peer set with
   per-country-median aggregation (Stage 5.5 patch). The OECD does not
   collect US data via DF_REMUN; the US anchor uses BLS OEWS A_MEAN (an
   observed wage statistic, not a self-report). The productivity normalization
   factor (0.77) discounts the headline gap to account for US physicians'
   higher per-FTE patient load.

2. **US physician debt, training, malpractice, admin burden** justify
   compensation: the fix is consistent with this argument. The proposed
   levers (RVU revaluation toward primary care, GME slot reallocation,
   debt restructuring) address debt and admin burden BEFORE compensation
   level. The booked savings come from system-level mix/structure shifts,
   not from absolute compensation cuts.

3. **RUC reform has been tried and failed**: this is true and is the case
   FOR structural reform. The fix proposes a CMS independent revaluation
   unit (MedPAC's June 2025 recommendation). The 2024 Medicare GME
   expansion (70% to primary care) is precedent that reallocation is
   feasible. The recoverability factors (55-80%) explicitly account for
   political-economic friction.

4. **Component B confounds compositional shifts with population-level
   demographic drivers**: Component B holds total US physician FTE
   constant and reallocates the mix only. It does not assume the absolute
   number of physicians changes. Demographic drivers (aging, chronic
   disease) affect demand for both PC and specialty care; the mix shift
   does not preclude meeting demand because total FTE is held constant.

5. **Cross-cascade overlap with Issue #15 (facility fee) on physician
   acquisitions is not cleanly separable**: per ROADMAP rule #10, #15
   owns the HOPD-vs-office site-of-service differential; #14 owns the
   underlying RVU misvaluation regardless of billing setting. Component C
   operates on work-RVU + practice-expense-RVU + malpractice-RVU values,
   which are constant across settings; the facility-fee differential is
   in the practice-expense-RVU component but the cross-setting differential
   belongs to #15.

6. **The Laugesen/Glied 2011 2× multiplier is from 2008 data**: we
   compute the current 2025 multiplier directly from BLS OEWS May 2024
   vs OECD DF_REMUN 2022-2023. See `cross_validation.csv` row 1 for the
   updated multiplier.

7. **"Drozda 2024 JAMA" citation**: replaced with JAMA Network Open 2020
   trends paper (Wiltshire et al.) plus Doximity 2025 and Medscape 2025
   industry reports as cross-validation anchors.

## Data-partner CTA for unbooked tail

The booked figure reflects the public-data path with conservative
recoverability factors. Tightening the analysis beyond the central booked
would require partner data:

- MGMA Physician Compensation Survey microdata ($1,500-3,000 license, or
  via WRDS): true production-adjusted compensation by specialty and region;
  would let us decompose the BLS "Physicians, all other" (315K FTE)
  aggregate that drives a large share of Component A.
- AHA Annual Survey physician-employment flag: hospital-employed vs
  independent physician composition for Component A flow-through to #12
- Sullivan Cotter executive compensation database: hospital-employed
  physician system-level compensation
- IRS Form 990 Schedule J non-cash compensation: nonprofit hospital
  employer-side data
- AMA Physician Practice Benchmark Survey: would let us correct the
  BLS A_MEAN downward bias from excluding self-employed practice owners
- US submission to OECD DF_REMUN: would let us replace BLS-vs-OECD
  comparison with apples-to-apples OECD-format US data

## Editorial guardrail compliance check

This methodology document explicitly:
- Frames the analysis as system-level counterfactual (RVU, GME, mix), not
  individual compensation reduction.
- Names the structural drivers (RUC composition, GME formula, debt
  structure, malpractice environment, admin burden).
- Acknowledges physician sacrifices (training, debt, hours, malpractice,
  admin burden documented in Issues #5 and #8).
- Decomposes savings by policy lever rather than aggregating to a single
  per-specialty number.
- Documents the recoverability factors as judgments about political-
  economic horizon for structural reform, not mathematical certainties.

The methodology is consistent with the editorial guardrail. Downstream
stages (newsletter drafter, fact-checker, editor approval) inherit this
framing.
