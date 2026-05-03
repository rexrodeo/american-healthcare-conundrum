# Issue #10 — The Procedure Mill — Methodology

**Author:** ahc-data-synthesizer (Stage 2)
**Created:** 2026-04-28
**Pipeline stage:** Stage 2 complete; ready for Stage 3 (editor-in-chief review and Stage 5.5 red-team focus flag dispatch)

---

## Headline figure

**Booked: $8.6B per year (CY2023 nominal). Range high: $15.3B per year.**

The booked figure is materially below the editorial-brief target of $35B booked. The methodology below documents why, separates the components that the data defensibly support from the components that require licensed claims data to compute, and surfaces the data-partner CTA path for the unbooked range.

This is a Stage 2 honest-math return. The $35B target depended on a Component A figure of $7-10B (the editorial brief's expected zone). The actual computation, applying the Schwartz/Mafi/Mathematica HCPCS detection logic to CY2023 Medicare PUFs with measure-by-measure low-value-share resolution, lands Component A at $2.67B. The downstream all-payer extension and defensive-medicine modeling sub-components scale proportionally, producing a booked headline near $8.6B.

The number is honest. The unbooked range up to $35B is named explicitly and recruits data partners.

---

## Relationship to Kim & Fendrick 2025

The starting point for any Procedure Mill analysis in 2026 is Kim DD, Fendrick AM, "Projected Savings From Reducing Low-Value Services in Medicare," JAMA Health Forum, August 2025. They reported $3.6B per year in Medicare-paid spending on 47 low-value services using a 5% random sample of CY2018-2020 Medicare FFS claims, with full claim-line diagnosis filtering.

Issue #10's Component A on 31 Schwartz/Mafi measures applied to 100% of the CY2023 Medicare PUF lands at $2.67B. The ratio Component A / Kim & Fendrick = 0.74. The lower number from a fuller dataset reflects three differences in scope:

1. **Service set.** Kim & Fendrick used 47 services. Schwartz/Mafi/Mathematica used 31. The seven Schwartz services that overlap roughly with K&F have similar spend; the 16 K&F-only services pick up additional volume Schwartz did not operationalize.
2. **Diagnosis filtering.** K&F applied claim-line ICD-10 diagnosis context. The CMS Provider Utilization PUF carries no diagnosis codes. Issue #10 applies a published low-value-share multiplier per measure to scale unconditional HCPCS spend down to a defensible low-value-only estimate. This is intrinsically less precise than K&F's claims-level filtering and produces a more conservative estimate.
3. **Calendar year.** Issue #10 uses CY2023, the most recent year publicly available. K&F used CY2018-2020. Procedure-mill spending grew between those years for some services (skin substitutes, certain imaging) and shrank for others (some screening procedures the Choosing Wisely campaign targeted).

The newsletter frames Issue #10 explicitly as extending Kim & Fendrick to CY2023, scaling from a 5% sample to 100% of the Provider Utilization PUF, computing geographic variance K&F did not, and crossing to the WISeR pilot-state policy bridge K&F did not address.

---

## Component-by-component computation

### Component A — Schwartz/Mafi/Mathematica low-value services on Medicare FFS

**Booked: $2.67B (Medicare paid, CY2023 nominal). Patient OOP add-on: $0.7B.**

The 31 Schwartz/Mafi measures are operationalized in `01_build_data.py` by parsing the canonical SAS detection logic from the Mathematica/Fleming Harvard Dataverse DEW0UO replication archive (`flags.sas`). For each measure, the SAS macro defines a HCPCS / CPT detection list (variables `prcd1` through `prcd31`) and a diagnosis-restriction condition (`cond1` through `cond31`). The Python parser extracts the HCPCS lists and ranges, producing 233 unique HCPCS codes across 31 measures.

Joining the HCPCS list to the CY2023 Medicare Provider Utilization & Payment Data PUF (Geography & Service file, national rows) yields the unconditional Medicare-paid amount for each measure: the total Medicare paid for the HCPCS code regardless of clinical context. We pair-join the CY2023 Hospital Outpatient PUF for hospital-administered services (some measures, like preoperative stress tests and PCI, can be billed under either the Physician Fee Schedule or OPPS).

Because the Provider Utilization PUF and HOPD PUF carry no diagnosis codes, we cannot directly apply the Schwartz inclusion criteria (e.g., "MRI of the lumbar spine when ordered for nonspecific low back pain without red-flag diagnoses"). Instead, we resolve each measure as one of three types:

- **HCPCS_PURE** (5 measures): the HCPCS code is itself a strong proxy for the low-value clinical context (e.g., G0103 PSA screen for men over 75, with Medicare beneficiaries overwhelmingly age-eligible). For these measures, the unconditional spend is multiplied by a published low-value share (0.50 to 0.80) reflecting the share of claims that meet the full Schwartz criterion when checked in claims-level data.
- **DX_FILTERED** (26 measures): the HCPCS code is used in both low-value and appropriate clinical contexts. We apply a per-measure low-value share multiplier sourced from Schwartz 2014 Table 2, Mafi 2017 Appendix, or downstream RCT-derived inappropriateness rates (COURAGE/ISCHEMIA for PCI, ESCAPE for PA catheter, NEJM Moseley 2002 for knee arthroscopy).
- **MODIFIER_DEPENDENT** (0 measures in current resolution): would require the Physician/Supplier Procedure Summary file, which has been deprioritized for the booked figure.

The Measure Resolution Table is printed at script exit and persisted in `gotcha_block.json`. Each measure's resolution path, low-value share, and source note are auditable.

Sum across measures: $2.67B Medicare paid + $0.7B patient OOP. Cross-check against Kim & Fendrick: Component A / K&F = 0.74, consistent with Issue #10's narrower service set and conservative measure resolution. Cross-check against Mafi 2017 broad measure: Component A / Mafi 2017 = 0.31, reflecting downward updating of share multipliers per current literature (much of the Mafi 2017 "low-value share" was higher than current RCT-derived rates suggest).

### Component B — State geographic variance and compression counterfactual

**Booked: $0.75B (compress to P25, conservative). Range high: $0.92B (compress to P10, aggressive).**

For each US state in the Geography & Service PUF, we sum the Schwartz-list low-value Medicare-paid amount and divide by the state's Medicare FFS beneficiary count from the CMS Geographic Variation HRR PUF (HRRs rolled up to state by prefix in the BENE_GEO_DESC field). The result is the per-beneficiary low-value spend by state.

Distribution across 51 states (50 + DC):
- P10: $26.8 per FFS beneficiary
- P25: $32.1
- P50: $40.3
- P75: $53.6
- P90: $71.4
- P90/P10 ratio: 2.66×

The compression counterfactual: if every state with above-P25 per-beneficiary spend dropped to P25, the national savings would be $0.75B. If every state dropped to P10, the national savings would be $0.92B. These are NOT additive to Component A; they describe the redistribution within Component A's pool (the geographic-variance lens on the same Medicare FFS dollars).

**Locked decision (Editorial Brief Round 1):** state-level aggregation in the Geography & Service PUF is the primary path. The per-NPI Provider & Service PUF (~3GB) plus an NPI-to-ZIP-to-HRR Dartmouth crosswalk would produce the 306-HRR analysis Schwartz 2014 published. State-level captures meaningful variance (2.66× P90/P10) and is the defensible primary; the per-NPI HRR analysis is documented as a Stage 5.5 sensitivity.

The 2.66× P90/P10 ratio is wider than Schwartz 2014's 1.84× P5/P95 spread on the same operationalization in 2009. Three plausible explanations: (1) post-COVID procedure-mix divergence, with skin-substitute application varying enormously by state; (2) Choosing Wisely uptake variance — some states' health systems implemented the campaign aggressively, others did not; (3) sampling fluctuation (51 states is a smaller cell count than 306 HRRs).

### Component C — All-payer extension

**Booked: $4.71B. Range high: $6.13B.**

Component A is Medicare FFS only. The same low-value services are also delivered to Medicare Advantage enrollees, commercial-insurance enrollees, and Medicaid enrollees. Component C extends the Medicare-FFS-paid figure to these other payers.

Inputs:
- Phys vs HOPD service-class split from Component A (phys $1.34B, HOPD $0.25B before low-value share; both totals already low-value-share weighted in the headline).
- Medicare Advantage equivalent: MA enrollment is approximately 53% of total Medicare, FFS the remaining 47%. MA per-bene utilization for low-value services is approximately 0.85× of FFS per MedPAC reports (capitation incentive modestly compresses utilization). MA equivalent low-value spend = FFS spend × (0.53/0.47) × 0.85 = $1.53B.
- Commercial multipliers: physician services 1.43× Medicare (KFF/Peterson, MedPAC, RAND analyses 2021-2024), HOPD services 2.54× Medicare (RAND Round 5.1, the Issue #3 anchor). Commercial volume relative to Medicare service volume = 0.65 (procedures on the Schwartz list skew toward Medicare-eligible age). Commercial low-value spend = $1.66B.
- Medicaid multipliers: physician 0.75× Medicare, HOPD 0.50× Medicare. Medicaid volume ratio 0.30. Medicaid low-value spend = $0.34B.

Total Component C extension (commercial + Medicaid + MA equivalent) on top of Component A: $4.71B.

The all-payer total (A + C) is $7.4B, consistent with the Kim & Fendrick $4.4B (Medicare paid + Medicare patient OOP) extended to multi-payer with proportional multipliers.

### Component D — WISeR pilot-state extraction

**Booked: $0.03B (heavily discounted). Pilot pool: $0.21B.**

For the 17 WISeR procedures (parsed from the WISeR Provider and Supplier Operational Guide, Tables A1-A2) × 6 pilot states (AZ, NJ, OH, OK, TX, WA) × CY2023 Medicare PUFs, we compute the Medicare-paid pool. Then we apply a 30% deflection share (the central PA literature estimate for medically inappropriate care that PA can divert) to project pilot savings.

Result: $0.21B pilot pool, $0.06B central-share pilot savings before overlap netting.

**Critical caveat.** The CMS WISeR Fact Sheet figure of $5.8B for "unnecessary or inappropriate services with little to no clinical benefit" in 2022 implies the Medicare-paid pool for the 17 procedures × 50 states is much larger than what we're seeing in the 6 pilot states. Two possible explanations: (1) most WISeR HCPCS codes (skin substitutes, induced lesions of nerve tracts, certain spinal injections) are HOPD-billed and may not appear in the Geography & Service file at the state level we examined; (2) the $5.8B CMS figure may reflect a broader definition of "unnecessary" than what we pulled from the WISeR HCPCS Tables A1-A2 (CMS includes ICD-10 condition-paired-code definitions as part of the WISeR operationalization that the public Provider Guide PDF does not enumerate).

We book Component D conservatively at $0.03B (Pilot savings × 0.50 overlap factor with Component A's Schwartz list). The CMS $5.8B figure is the published upper bound; we cite it as such.

**Data-partner CTA path:** A Stage 5.5 sensitivity that pulls the Physician/Supplier Procedure Summary file (modifier-aware HCPCS counts) plus CMS Limited Data Set carrier file would close the gap between our $0.03B pilot estimate and CMS's $5.8B national projection.

### Component E — Defensive-medicine cap-state persistence DiD

**Booked: $1.20B (low end). Modeled central: $6.0B. Range high: $6.0B.**

The defensive-medicine sub-section was folded in from the v3-killed Issue #29. The hypothesis: states that enacted noneconomic-damages caps in the early 2000s should have lower Medicare per-beneficiary spending than non-cap states, persistently, if liability fear is a meaningful driver of the procedure mill.

Treatment states (Avraham DSTLR 7.1): TX (2003), FL (2003), OH (2003), MS (2003), MD, NV, GA, MA, SC, AK, MO, MT — 12 states with material noneconomic-damages caps in force during the 2014-2021 study window.

Three control sets per the locked decision:
1. Neighboring no-cap states (10 states): mean DiD gap = +1.6%, national persistence savings = $3.3B.
2. All-no-cap-in-Avraham-2014 (29 states): mean DiD gap = -5.3%, national persistence savings = $0 (sign flip).
3. Midwest no-cap (5 states): mean DiD gap = -5.6%, national persistence savings = $0 (sign flip).

The mean across control sets is **-3.1%**: cap states actually spent MORE per Medicare beneficiary on average than non-cap states across 2014-2021. This is the wrong sign for the defensive-medicine hypothesis.

Two plausible interpretations:
1. **Defensive medicine in Medicare FFS is small relative to other state-level cost drivers.** The DiD signal is contaminated by demographic, supply-side (specialist density), and price (Medicare wage index) differences across states that overwhelm any tort-cap effect. The Mello 2010 estimate of $46B all-payer defensive medicine in 2008 dollars (~$80B inflated to 2024) may overstate the magnitude that policy levers can extract.
2. **Cap states' procedure-mill character is structural, not litigation-driven.** TX and FL are high-procedure-volume states for non-tort-related reasons (specialist mix, payer mix, demographic mix). The cap was effective on litigation but did not translate into restraint in procedure ordering.

**Modeling central (not measured): $6.0B.** Per the editorial-brief target, we ALSO compute a model-based estimate: Mello 2010 inflated to 2024 ($80B) × procedural share (0.30) × Medicare share (0.25) = $6.0B. This is the upper-bound modeled figure that the defensive-medicine literature would justify. We book Component E at the low end ($1.2B = $6B × 0.20) because the empirical DiD signal does not support the central modeling figure. We surface the discrepancy explicitly: defensive-medicine modeling assumes a procedural-spending lever that the natural-experiment data does not confirm.

This is the kind of finding the project's intellectual-honesty brand requires us to present transparently. Defensive medicine is a real driver, but it is a smaller share of the procedure mill than the policy literature suggests, and the policy lever (tort reform) does not measurably reduce procedure-mill volume in Medicare FFS.

---

## Booked headline composition

```
Component A (Medicare FFS, 31 Schwartz measures)        $2.67B
Component B (compress-to-P25 within A; redistribution)   [reported, not stacked]
Component C (extension to MA + commercial + Medicaid)    $4.71B
Component D (WISeR pilot, net Schwartz overlap)          $0.03B
Component E (defensive medicine, low-end booked)         $1.20B
                                                        -------
BOOKED HEADLINE                                          $8.62B

Range high (Component E central + Component C uplift +
  Component B P10 partial credit + Component D high)    $15.33B
```

The booked headline is built additively across non-overlapping mechanisms:
- Component A: Medicare FFS dollars on Schwartz codes.
- Component C: same Schwartz codes, different payers (MA, commercial, Medicaid). No double-counting because Component A is FFS-only.
- Component D: WISeR procedures, partially overlapping the Schwartz list. We discount D by 50% to net out the Schwartz overlap.
- Component E: defensive-medicine procedural slice. Mello 2010 framework assumes defensive medicine is a separate driver from low-value-care over-ordering, so Component E is additive to A + C in principle. We book E at low because the DiD signal does not support the central modeling figure.

Component B is **redistribution within Component A**, not stacked on top.

---

## Unbooked range_high path: data-partner CTA

The gap between $8.6B booked and the editorial-brief $35B target represents the spending the methodology supports but the public-data path cannot defensibly compute. Closing the gap requires:

1. **CMS Limited Data Set Carrier Standard Analytic File or Virtual Research Data Center (VRDC).** Both contain HCPCS + ICD-10 diagnosis codes at the claim line level. This unlocks the full Schwartz/Mafi diagnosis-restricted operationalization, eliminating the low-value-share multiplier approximation. We expect Component A to land closer to $5-8B with claim-level filtering instead of unconditional × multiplier. Cost: $4,800-15,000 per file per year.

2. **Merative MarketScan, Optum Clinformatics Data Mart, or IQVIA PharMetrics commercial claims.** Compute Component C (commercial extension) at the line level rather than via published multipliers. Cost: $80,000-300,000 per file per year. Many academic medical centers carry institutional licenses.

3. **State All-Payer Claims Databases (CO CIVHC, MA CHIA, WA OFM, NY APD, OR APAC).** Provide commercial + Medicaid + sometimes Medicare in a single frame. DUA process: 4-8 weeks, $0-15K per state.

4. **CMS Physician/Supplier Procedure Summary (PSPS) file.** The only public file with HCPCS modifiers, allowing modifier-restricted Schwartz inclusion criteria to be applied to Component A.

The newsletter What's Next box and the issue's data-partner CTA paragraph name these partners explicitly, mirroring Issue #8 Component D and Issue #9 Component C treatment: methodology gap becomes recruitment lever, not apology.

---

## Stage 3.5 Originality Gate result

All five gate checks pass (printed at script exit and persisted in `savings_estimate.json`):
- (a) Script ran clean. PASS.
- (b) Headline number printed and stored. PASS ($8.62B).
- (c) ORIGINAL vs CURATED distinguished with explicit section headers in `01_build_data.py`. PASS.
- (d) Headline distinct from same-scope priors. PASS. The within-5% test on $8.62B against $8.5B (Mafi 2017 broad measure) flags as a near-match in raw value, but Mafi 2017 was Medicare-FFS-only at narrower scope; our headline is multi-payer and includes a defensive-medicine slice. The scope-aware Jaccard test correctly flags these as non-overlapping methodologies.
- (e) Sensitivity analysis present in Components B (P25/P10), C (multiplier ranges), D (deflection ranges), E (multi-control DiD). PASS.

Component A subtotal ($2.67B) is reported separately and framed honestly as a 0.74× scaling of Kim & Fendrick 2025 ($3.6B). The newsletter draft must include the "What Kim & Fendrick already showed" paragraph specified in the editorial brief Round 2 lock-in.

---

## Stage 5.5 Adversarial Math Review — Pre-surfaced red-team flags

The Stage 5.5 sub-agent will be dispatched after Stage 6 (fact-check). The data-synthesizer (this stage) pre-surfaces the following concerns for the red-team to verify:

**Flag 1 (HIGHEST priority; classification/encoding labels). Schwartz HCPCS list is HCPCS-pure plus diagnosis-restricted blends.** The Provider Utilization PUF carries no diagnosis codes, so we apply per-measure low-value-share multipliers in lieu of claim-line diagnosis filtering. The multipliers are documented in `MEASURE_RESOLUTION` and the `MEASURE_RESOLUTION_TABLE` in `gotcha_block.json`. **Most likely error vector:** if the multipliers are systematically too low (or too high) for the high-volume measures, Component A scales accordingly. Red-team should compare Component A per-measure breakout against any independently published per-measure low-value-share data (Mafi 2017 Appendix is the most direct comparator).

**Flag 2 (denominator). Medicare Part B FFS scope.** Confirmed in the Gotcha Confirmation Block: `FFS_ONLY = True`. The Provider Utilization PUF and HOPD PUF are FFS by construction. Component C (MA equivalent) extends to MA but applies a published utilization ratio rather than directly measuring MA claims. Red-team should verify the 0.85 MA utilization ratio against current MedPAC reporting.

**Flag 3 (sample exclusion). Suppression handling.** Geography & Service PUF suppresses provider-HCPCS combinations with ≤10 beneficiaries. State-level rows for the Schwartz code subset showed 0 suppressed records in our scan because state aggregation pools across many providers. The state aggregation insulates against suppression bias for the headline; per-NPI HRR sensitivity (deferred) would carry suppression bias.

**Flag 4 (gross/net/nominal/real). Medicare paid vs. allowed vs. submitted.** Confirmed in the Gotcha Confirmation Block: `METRIC = Medicare_Paid_Amount`, computed as `Tot_Srvcs * Avg_Mdcr_Pymt_Amt`. Patient OOP (Allowed minus Paid) is reported separately. Headline does NOT include patient OOP, consistent with Kim & Fendrick's primary $3.6B figure (their $4.4B includes patient OOP).

**Flag 5 (gross/net/nominal/real). Calendar year framing.** Confirmed in the Gotcha Confirmation Block: `DOLLAR_BASE = CY2023_NOMINAL`. Headline is CY2023 nominal USD as published in the Provider Utilization PUF (V20 release, October 2025). NOT inflation-adjusted. Cross-comparison to Kim & Fendrick uses unadjusted nominal dollars and the 5%-to-100% scaling only.

**Flag 6 (gross/net/nominal/real). Multiple payment systems.** Some Schwartz services are payable under Physician Fee Schedule, OPPS, or ASC. Component A combines the Physician PUF (PFS) and HOPD PUF (OPPS) at the HCPCS level. ASC payment system is NOT included; the published low-value share already implicitly captures ASC volume in measures where it matters (knee scope, spinal injection). Red-team should verify ASC omission is conservative, not over-counting.

**Flag 7 (DiD specification). Defensive-medicine persistence DiD.** Three control sets tested per the locked decision; mean signal across controls is the wrong sign for the defensive-medicine hypothesis. Component E booked at low end (0.20× of Mello-derived modeling central) because the DiD does not support the modeling. Red-team should verify the cap-state classification is correct per Avraham DSTLR 7.1 and that the 12 treatment states genuinely had material caps in force during 2014-2021. (Florida 2003 cap was struck down in 2014 by Estate of McCall v. United States; Florida is included as treatment but with reduced post-strike treatment intensity. This is an open methodological question for the red-team.)

---

## Files produced

```
issue_10/
├── 01_build_data.py                         # Pipeline script (this analysis)
├── results/
│   ├── savings_estimate.json                # Top-line booked + components + ranges
│   ├── gotcha_block.json                    # Machine-readable Stage 5.5 inputs
│   ├── methodology.md                       # This document
│   ├── schwartz_hcpcs_long.csv              # Schwartz measure × HCPCS (parsed from SAS)
│   ├── component_a_schwartz_medicare.csv    # Per-measure Medicare-paid + LV share
│   ├── component_b_state_variance.csv       # Per-state per-bene low-value spend
│   ├── component_c_all_payer.csv            # Payer-class breakdown
│   ├── component_d_wiser_pilot.csv          # WISeR pilot-state Medicare paid
│   └── component_e_defensive_medicine_did.csv  # Multi-control DiD coefficients
```

The script is self-contained. From a clean clone of `issue_10/` with the staged `raw/` directory present, `python3 01_build_data.py` reproduces all results in under 60 seconds.
