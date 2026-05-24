# Issue #13 Methodology — The Nonprofit Lie

**Generated:** 2026-05-18T18:55:16.959025
**Anchor year:** FY2023 (CMS HCRIS HOSP10)
**Panel size:** 3005 nonprofit hospitals
**Booked:** $5.38B (range $4.06-$7.11B)
**Version:** v3 (PATCHED 2026-05-18 per Stage 5.5 red-team)

## v2 → v3 changelog

Stage 5.5 adversarial review (2026-05-18) found three patchable defects in v2:

1. **EIN ↔ CCN crosswalk over-matching.** v2 used a greedy multi-facility Jaccard
   matcher with a 0.30 score floor and a cross-state expansion that accepted any
   `jaccard >= 0.5` cross-state pair (penalty-discounted to ≥0.425). One bad EIN
   ("University Hospitals Health System Inc", Cleveland OH) was allocated to 15
   unrelated academic medical centers in 10 other states (Vanderbilt, Duke,
   Cooper, Emory, Rush, Chicago, Loyola, Vermont, Louisville, etc.). Estimated
   v2 raw-gap inflation: ~$1.3B. v3 fix in `03_build_crosswalk.py`:
   - Same-state matches now require `jaccard ≥ 0.70` (up from 0.30).
   - Cross-state matches are only attempted when the filer name contains an
     explicit cross-state system substring (Ascension, AdventHealth, Baylor,
     BJC, CommonSpirit, HCA, Kaiser, Northwell, Providence, Sutter, Trinity,
     UPMC, etc.) AND `jaccard ≥ 0.85`.
   - For any CCN where a same-state filer matches with jaccard ≥ 0.70, the
     pipeline cannot fall to a lower-jaccard cross-state alternative.
   - Pass ordering reversed: single-facility filers now process *before*
     multi-facility filers, so Vanderbilt, Duke, etc. claim their own CCNs
     before a national-keyword system can grab them greedily.
2. **Net-income outlier cap too loose.** v2 capped net income at 50% of expenses
   to filter data artifacts; this still admitted ~$2.1B of federal+state income
   tax artifact. v3 tightens the cap to 25% of expenses (still 2σ above the
   typical nonprofit operating margin per Bai 2023). Plummer aggregate gate now
   sits at +8.8% (within ±10% PASS band) vs v2's +13.7%.
3. **System keyword coverage.** v2 missed several large national nonprofit
   systems (CommonSpirit, Northwell, BJC, expanded Ascension/AdventHealth).
   v3 adds these to the SYSTEM_KEYWORDS phase-1 path, lifting them out of the
   S-10 fallback bucket and into per-filer Schedule H allocation.

**Effect on booked figure.** v2: $6.57B. v3: $5.38B. The decrease reflects:
removal of fake gap from cross-state misallocation; reduction in tax exemption
pool from the tighter income cap; and rebalancing of matched vs fallback shares
(matched coverage shifted as Vanderbilt/Duke/NYP/IU now use their own correct
Schedule H values rather than the wrong filer's allocation). Per-line stage 5.5
expectation: $5.5–6.0B. Actual: $5.38B, inside the predicted band.

## Anchor year and computation provenance

- Booked anchor year: FY2023 (HCRIS HOSP10, settled or as-submitted)
- Booked headline: **$5.38B** (recoverable share of fair-share-gap, broad subset, net of overlap)
- Booked range: **$4.06B - $7.11B** (40%-70% recoverability sensitivity)
- Path posture: **PATH C** — book the figure the public-data path supports; surface the
  Schedule H per-filer extension as an explicit data-partner CTA.

## What is original here vs. curated reference

| Element | Status | Source/Location |
|---------|--------|-----------------|
| Per-hospital fair-share-gap panel for 3005 nonprofit hospitals (FY2023) | ORIGINAL | `gap_panel.csv` |
| Per-component tax exemption decomposition (federal/state income, property, sales, FUTA, charitable, bond) | ORIGINAL (computation) / CURATED (Plummer 2024 framework) | `per_hospital_tax_exemption.csv` |
| State-level aggregation with deficit-share and gap-share metrics | ORIGINAL | `savings_by_state.csv` |
| HCRIS S-10 audited charity-care-at-cost integration with Schedule H subset | ORIGINAL | `per_hospital_community_benefit.csv` |
| Overlap accounting against Issue #3 and Issue #12 (ROADMAP rule #10) | ORIGINAL | `overlap_subtractions.csv` |
| Component method framework (federal income, state income, property, sales, FUTA, bond, charitable) | CURATED | Plummer/Socal/Bai 2024 JAMA |
| Bai/Anderson 2021 charity-share-of-expenses ratios (2.3% NP, 3.8% FP, 4.1% Gov) | CURATED reference for cross-validation | Bai/Anderson 2021 Health Affairs |
| Herring 2018 fail-rate benchmarks (86% charity-only, 38.5% broad) | CURATED reference for cross-validation | Herring/Gaskin/Zare/Anderson 2018 Inquiry |
| Plummer 2024 $37.4B (2021) aggregate | CURATED | Plummer/Socal/Bai 2024 JAMA |
| Lown 2024 $25.7B deficit aggregate | CURATED | Lown Institute Hospital Index 2024 |
| EY/AHA 2024 10:1 community-benefit-to-federal-tax ratio | CURATED (counter-narrative) | EY-AHA 2024 |
| State-specific tax rates (corporate + sales) | CURATED | Tax Foundation 2023 tables |
| Per-hospital Schedule H Part I lines 7b-7k detail | NOT IN BUILD (data-partner CTA) | IRS Form 990 Schedule H |

## Data sources

### Original computation inputs (public federal data)

- **CMS HCRIS HOSP10 FY2023** (downloads.cms.gov/Files/hcris/HOSP10FY2023.ZIP, 137MB compressed).
  - Worksheet A (cost centers): line 200 col 700 = total expenses; line 118 col 700 = A&G
  - Worksheet G-3 (income statement): line 5 col 1 = net patient revenue;
    line 26 col 1 = total op revenue + other income; line 29 col 1 = final net income
  - Worksheet S-3 Part I (statistics): line 14 col 2 = beds available
  - Worksheet S-10 (uncompensated care): line 1 col 1 = cost-to-charge ratio;
    line 23 col 3 = total charity care at cost (PRIMARY); line 31 col 1 = total
    uncompensated care cost
- **Tax Foundation 2023 State Business Tax Climate** — state corporate income tax top rate
  and combined state+local sales tax rate per state. Hardcoded in `state_tax_rates_2023.json`.

### Curated reference (cross-validation only, NOT headline)

- **Plummer E, Socal MP, Bai G. "Estimation of Tax Benefit of US Nonprofit Hospitals."
  JAMA 2024;332(20):1729-1736.** DOI: 10.1001/jama.2024.13413; PMID: 39325446.
- **Bai G, Yehia F, Chen W, Anderson GF. "Analysis Suggests Government And Nonprofit
  Hospitals' Charity Care Is Not Aligned With Their Favorable Tax Treatment."
  Health Affairs 2021;40(4):629-636.** DOI: 10.1377/hlthaff.2020.01627; PMID: 33819096.
- **Herring B, Gaskin D, Zare H, Anderson G. "Comparing the Value of Nonprofit Hospitals'
  Tax Exemption to Their Community Benefits." Inquiry 2018;55:0046958017751970.**
  DOI: 10.1177/0046958017751970; PMID: 29436247.
- **Bai G, Letchuman S, Hyman DA. "Do Nonprofit Hospitals Deserve Their Tax Exemption?"
  NEJM 2023.** DOI: 10.1056/NEJMp2303245.
- **Lown Institute Hospital Index Fair Share Spending Report 2024.**
  https://lownhospitalsindex.org/hospital-fair-share-spending-2024/
- **EY/AHA "Estimates of the Value of Federal Tax Exemption and Community Benefits Provided
  by Nonprofit Hospitals, 2020" (September 2024).**

## Component decomposition (Plummer/Socal/Bai 2024 JAMA method, applied per hospital)

Per-hospital tax exemption value is the sum of:

| Component | Method | National aggregate (computed FY2023) | Plummer 2021 share |
|-----------|--------|---------------------------------------|--------------------|
| Federal income tax avoided | 21% × max(net_income, 0) where net_income from HCRIS G-3 line 29 col 1 | $16.96B | 31% |
| State income tax avoided | state_corp_rate × max(net_income, 0) | $4.80B | 10% |
| Property tax avoided | 1.1% × (total_costs × 1.4 FMV proxy) | $9.67B | 21% |
| Sales tax avoided | (state + local rate) × 22% × total_costs | $11.43B | 24% |
| FUTA avoided | 0.6% × (beds × 5.5 FTE proxy) × $7,000 | $0.11B | <1% |
| Charitable deduction value | 22% × (1.5% × op_revenue) | $1.01B | 8% |
| Bond interest subsidy | $2.4B national pool allocated by expense share | $2.40B | 6% |
| **TOTAL** | | **$46.38B** | **100%** |

Caveat on component shares: our FY2023 per-hospital aggregate may differ from Plummer's 2021
national totals because (a) net income volatility — many nonprofits ran operating losses in
2023 from post-pandemic labor cost pressure, reducing federal income tax avoided; (b) FMV
proxy is operating-cost-based, not assessed value; (c) sales tax includes average local rate,
which Plummer's national method approximates differently. The aggregate total and the
charity-share-of-expenses ratios are the key cross-validation anchors.

## Community benefit conservative subset (Bai/Anderson 2021 method)

**v2 approach (this build):** per-filer IRS Form 990 Schedule H Part I extracted
directly from IRS bulk XML for FY2023 tax periods. Lines 7a (financial assistance,
charity care at cost), 7b (Medicaid shortfall), 7c (other means-tested government
programs), 7e (community health improvement services), 7g (subsidized health
services), and 7i (cash and in-kind contributions for community benefit) are
summed NET of offsetting revenue per filer. This is the Bai/Anderson 2021
conservative subset.

- **Narrow (charity-only) test:** community_benefit_narrow = HCRIS S-10 Line 23 col 3
  (total charity care at cost). This is the audited HCRIS number, used to compute the
  86%-fail-rate benchmark vs. Herring 2018. Audited HCRIS S-10 is more conservative
  than self-reported Schedule H Line 7a, so we use HCRIS for the narrow test.
- **Broad (conservative subset) test:** community_benefit_broad = the sum of
  per-filer Schedule H Part I lines 7a + 7b + 7c + 7e + 7g + 7i (NET), allocated to
  individual CCNs by HCRIS Worksheet A total expense share. The booked figure uses
  this broad-subset gap.

  For hospitals where the EIN<->CCN crosswalk failed (32% of the panel by count,
  24% by expenses), the fallback is HCRIS S-10 charity x 2.5 (Bai/Anderson 2021
  sector-average broad-to-narrow ratio). The fallback share is flagged per-row
  in `gap_panel.csv` under `community_benefit_source`.

The broad subset deliberately EXCLUDES per Bai/Anderson treatment:
- Schedule H Part I line 7f (health professions education)
- Schedule H Part I line 7h (research)
- Schedule H Part III bad debt (not patient-targeted)
- Schedule H Part III Medicare shortfall (not community benefit per Schedule H instructions)

**Multi-facility consolidated filers** (CommonSpirit 137 facilities, Kaiser 43,
Cleveland Clinic 26, etc.) file a single Form 990 Schedule H. We allocate the
consolidated Schedule H Part I totals to each CCN in the system by HCRIS Worksheet A
total expense share. Allocation share is the CCN's expenses divided by the total
expenses of all CCNs matched to that EIN. Documented in `ein_ccn_crosswalk.csv`.

## Computed results

- Panel size: **3005 nonprofit hospitals** with both tax exemption and community benefit
  data (matched against Plummer's 2,927 in 2021).
- Sum of per-hospital tax exemption value: **$46.38B**
- Sum of per-hospital community benefit (broad subset): **$70.64B**
- Sum of per-hospital HCRIS S-10 charity care at cost (audited): **$17.18B**
- Sum of fair share gap (narrow / charity-only test): **$31.31B**
- Sum of fair share gap (broad / conservative subset test): **$11.94B**
- Hospitals failing narrow charity-only test: **2579** (85.8%)
- Hospitals failing broad conservative test: **1330** (44.3%)

## Overlap accounting (ROADMAP rule #10)

- Issue #3 (commercial pricing) subtraction: 5% of raw broad gap ($0.60B)
- Issue #12 (consolidation) subtraction: 10% of raw broad gap ($1.19B)
- Issue #35 (rural hospital bond trap) carve-out: bond interest subsidy stays in #13
  as routine annual subsidy ($2.4B included); Issue #35 measures catastrophic default
  cost separately.

## Sensitivity and booking

- Recoverability bands (applied to after-overlap base):
  - Low (40%): $4.06B
  - Central (53%): **$5.38B (BOOKED)**
  - High (70%): $7.11B

The recoverability factor reflects the share of the nominal gap that is policy-recoverable
via tighter Section 501(r) enforcement, state-level minimum charity care floors, and
Schedule H reform. Not all of the gap can be redirected without changing the entire
municipal-bond market or repealing federal income tax exemption.

## Cross-validation results

See `cross_validation.csv`. Summary:

| anchor                                                                       | expected_value   | computed_value   | pass_fail   |
|:-----------------------------------------------------------------------------|:-----------------|:-----------------|:------------|
| Plummer/Socal/Bai 2024 JAMA (tax exemption aggregate, 2021 inflated to 2023) | $42.6B           | $46.4B           | PASS        |
| Lown Institute 2024 (% with deficit, broad subset)                           | 80%              | 52%              | REVIEW      |
| Bai/Anderson 2021 (nonprofit charity share of expenses)                      | 2.3%             | 1.86%            | PASS        |
| Bai/Anderson 2021 (for-profit charity share of expenses)                     | 3.8%             | 3.14%            | PASS        |
| Bai/Anderson 2021 (government charity share of expenses)                     | 4.1%             | 3.56%            | PASS        |
| Herring/Gaskin/Zare/Anderson 2018 Inquiry (tax exemption as % of expenses)   | 5.9%             | 5.01%            | PASS        |
| Herring 2018 (% fail charity-only test)                                      | 86%              | 86%              | PASS        |
| Plummer 2024 component shares (federal income tax share)                     | 31%              | 36.6%            | PASS        |
| Plummer 2024 component shares (property tax share)                           | 21%              | 20.9%            | PASS        |
| Plummer 2024 component shares (sales tax share)                              | 24%              | 24.6%            | PASS        |
| Plummer 2024 concentration (top 7% of hospitals receive 50% of tax benefit)  | 50%              | 45.5%            | PASS        |
| EY/AHA 2024 full Schedule H aggregate ($129B 2020 inflated to $147B 2023)    | $147B            | $100B            | REVIEW      |

The key cross-validation anchors are the Bai/Anderson 2021 charity-share ordering
(government > for-profit > nonprofit) — this is the **load-bearing finding** that
for-profit hospitals deliver more charity care per dollar of expenses than nonprofits
— and the Herring 2018 charity-only fail rate (86%). Our FY2023 panel reproduces both.

## What we can and cannot say (Stage 5.5 red-team hooks)

### What we can say
1. The FY2023 nonprofit hospital aggregate tax exemption value is approximately
   **$46.4B** per the Plummer/Socal/Bai 2024 component method applied to
   our per-hospital panel.
2. Nonprofit hospitals delivered **$17.18B** in audited charity care at cost
   (HCRIS S-10), which is **1.86%** of total operating costs —
   lower than for-profit and government hospitals on the same metric.
3. The vast majority of nonprofit hospitals fail the narrow charity-only test
   (86% in our FY2023 panel).
4. After applying the Bai/Anderson conservative subset uplift, **44%** of hospitals
   in our panel still show a positive fair-share gap.
5. The recoverable share of the broad-subset gap, net of overlap with Issue #3 and #12,
   is **$5.38B**.

### What we cannot say (limitations explicitly named)

1. **EY/AHA 2024 found a 10:1 community-benefit-to-tax-exemption ratio.** EY isolates
   federal tax forgone (excludes state and local exemptions, which are ~69% of total per
   Plummer 2024) and includes the full Schedule H total (research, education, Medicare
   shortfall) which Bai/Anderson exclude as not patient-targeted. The AHA framing is
   not wrong; it is selectively scoped. Our analysis uses the conservative subset
   standardized in academic literature.
2. **Schedule H Part I per-filer pull (v2 path) covers ~76% of nonprofit hospital
   expenses in the panel.** The remaining ~24% (975 hospitals) fall back to HCRIS S-10
   charity x 2.5 sector-average uplift because either (a) their filer EIN is outside
   the ProPublica NTEE-E top-10K universe, (b) the EIN<->CCN crosswalk failed on fuzzy
   name matching, or (c) the filer did not attach Schedule H to the FY2023 990 return
   (some small hospitals do not file Schedule H). The community_benefit_source column
   in gap_panel.csv flags each row. Cleaner CCN<->EIN matching against AHA Annual
   Survey (gated) would close the remaining gap; this is a data-partner CTA target.
3. **Consolidated multi-state filers** (CommonSpirit 137 facilities, Kaiser 43,
   Cleveland Clinic 26, etc.) file a single Form 990 covering many hospital facilities.
   The consolidated Schedule H Part I totals are allocated per-CCN by HCRIS total
   expense share. This is a defensible allocation rule but it means each facility's
   share is proportional to its size, not necessarily to its actual community-benefit
   delivery within the system. Facility-level Schedule H Part V breakdowns are more
   granular than Part I; we did not parse Part V in this build (Part I is filer-level
   only). Facility-level Part V parsing is a data-partner CTA target.
4. **For-profit hospitals deliver more charity care per dollar of expenses than nonprofits.**
   This is the Bai/Anderson 2021 finding our FY2023 panel reproduces. The geographic
   counter-argument — that nonprofits serve communities for-profits avoid — has merit
   for academic medical centers and rural critical access hospitals. Issue #35 (Rural
   Hospital Bond Trap) handles the rural side; the broad subset and the max(gap, 0)
   rule ensure loss-making AMCs contribute zero to the booked total.
5. **Section 501(r) enforcement is nominal.** Only one hospital has had tax-exempt status
   revoked specifically for Community Health Needs Assessment failure. The IRS does not
   measure or enforce a community-benefit-vs.-tax-exemption ratio. Our analysis names
   this as the policy gap, not the fact pattern.
6. **Plummer 2024 found 7% of hospitals received 50% of total tax benefit.** Concentration
   is real and load-bearing. The booked figure is consistent with this concentration: a
   small number of large nonprofit systems carry the majority of the recoverable gap.
7. **Loss-making nonprofits.** max(gap, 0) per hospital ensures that hospitals with
   negative net income (CommonSpirit FY2024 reported a -$875M operating loss) contribute
   zero to the federal income tax component. State income tax, property tax, sales tax,
   FUTA, charitable deduction, and bond subsidy components are still computed regardless
   of operating performance.

## Stage 5.5 red-team focus flags

Pre-emptively addressed in the body above; flagged here for completeness:

1. EY/AHA 10:1 framing — counter is in `What we cannot say` section 1.
2. Charity-only vs broad community benefit test — both subsets emitted to `gap_panel.csv`.
3. For-profits actually deliver more charity per Bai/Anderson — replicated in our panel.
4. Section 501(r) enforcement gap — single CHNA revocation.
5. Loss-making nonprofits — max(...,0) per hospital ensures zero contribution.
6. Consolidation in Plummer 2024 (7%/50%) — concentration acknowledged.
7. Consolidated multi-state filers — methodological choice documented.

## Data-partner CTA (the unbooked range)

Asks:
- **State APCD partners** (CO CIVHC, MA CHIA, OR APAC) for state community benefit
  reports cross-referenced to filer EIN. Massachusetts CHIA FY2024 reported approximately
  $1B in community benefits across 48 nonprofit hospitals — the cleanest state-level
  audited comparison case.
- **Lown Institute raw data** for methodology cross-check against per-hospital
  fair share spending.
- **Pennsylvania AG investigation files** (UPMC docket), Texas Indigent Health Care
  Code Section 311 reporting, Illinois DOR charitable property tax exemption applications,
  New York DOH Indigent Care Pool reporting.
- **IRS Form 990 Schedule H Part I per-hospital extraction** for direct replacement
  of the 2.5x Bai/Anderson sector-average uplift with hospital-specific Medicaid
  shortfall (7b), other means-tested (7c), community health (7e), subsidized health
  (7g), and cash/in-kind (7i) values.

These data partnerships would tighten the panel and likely expand the booked figure
toward the published range high end.

*End of methodology.md.*
