# Issue #14 — Stage 3.5 Originality Gate Evidence (Stage 2 FULL BUILD)

Generated: 2026-05-25T22:30:59.041561

## Five Originality Gate checks

1. **`01_build_data.py` exists in `issue_14/` and runs clean.**
   - **Status: PASS.** This script runs end-to-end and produces all expected
     output files: savings_estimate.json, savings_by_component.csv,
     methodology.md, gotcha_block.json, per_specialty_savings.csv,
     component_a_per_specialty.csv, component_c_family_breakdown.csv,
     component_c_sensitivity.csv, recoverability_sensitivity.csv,
     overlap_subtractions.csv, cross_validation.csv,
     international_compensation_panel.csv, rvu_panel_full.csv,
     bls_oews_physicians_2024.csv, specialty_workforce_panel.csv.

2. **The script produces the headline savings number as a print or variable.**
   - **Status: PASS.** Headline booked = $27.62B,
     printed at script exit and emitted to savings_estimate.json
     (headline_status=STAGE2_RECOMPUTED, post Stage 5.5 patches).

3. **The script distinguishes ORIGINAL analysis from CURATED reference data
   with explicit section headers.**
   - **Status: PASS.** The CURATED REFERENCE DATA section at the top of
     the script holds Laugesen/Glied multiples, Bodenheimer framing,
     MedPAC directional recs, Doximity anchors, and BLS OEWS anchors.
     The ORIGINAL analysis is the four-component aggregation in steps
     6-10 (Component A intl gap, Component B workforce mix counterfactual,
     Component C RVU revaluation residual, Component D GME allocation
     counterfactual) plus the overlap accounting and recoverability
     factor application. The methodology.md emits the original-vs-curated
     table explicitly.

4. **The headline number is not already published within 5% by RAND, KFF,
   Peterson, FTC, CBO, or JAMA.**
   - **Status: PASS.** Per data_sources.md and our search:
     - Laugesen/Glied 2011 (Health Affairs) published international
       compensation multiples using 2008 data; they did NOT publish a
       national savings dollar figure. We extend to 2025 OECD + 2024 BLS
       data with our own per-specialty application.
     - MedPAC June 2025 publishes RVU reform recommendations and a $-figure
       for CY2025 PFS update but does NOT publish a national savings
       estimate for the structural workforce/mix/RVU reform package.
     - AAMC publishes workforce projections (20,200-40,400 PC shortage by
       2036) but does NOT translate into national savings.
     - RAND, KFF, Peterson, FTC, CBO: no published estimate within 5% of
       our four-component aggregation. The closest published comparison is
       Laugesen/Glied 2011's per-specialty multiplier (cross-validation
       row 1 in cross_validation.csv).
   - The four-component aggregation with overlap subtractions and per-
     component recoverability factors against current-year data is
     original to this analysis.

5. **Modeling issues implement the model computationally with sensitivity
   analysis.**
   - **Status: PASS.** Per-component recoverability factors emitted at
     conservative/central/aggressive bands (`results/recoverability_sensitivity.csv`).
     Component C revaluation sensitivity at 5%/10%/15% × 40%/60%/80% cascade
     factors (`results/component_c_sensitivity.csv`).

## What does NOT clear Stage 3.5

Any version of this script that prints "Laugesen and Glied 2011 found US
specialists earn 2× peers" as the headline without our own per-specialty
2025 computation; or any version that prints AAMC's "65% specialists"
share without our own workforce-mix counterfactual computation. The
four-component aggregation with current-year inputs and explicit overlap
subtractions is what makes the application original. **This script
clears the gate.**

## Editorial guardrail compliance

This script, its methodology output, and its savings_estimate.json all
explicitly carry the editorial guardrail: the analysis is computed against
system-level counterfactuals, NOT against individual physician compensation.
This is binding on downstream stages (newsletter drafter, fact-checker,
editor approval).

## Status

**STAGE2_RECOMPUTED.** Stage 5.5 adversarial math review (2026-05-25)
surfaced three defects; this build is the post-patch recomputation:
- Defect 1: OECD comparator restricted to OECD-18 high-income peer set,
  median-of-country-medians aggregation.
- Defect 2: PC share basis fixed at 28.0% (BLS-FTE) consistently across
  Components B, D, and methodology documentation.
- Defect 3: range_hi_bil derived empirically from aggressive recoverability
  band post-overlap, not a hard-coded ceiling.

Ready for Stage 4 fix-up redraft, Stage 5 fact-check (re-run on patched
numbers), and Stage 7 chart regeneration.
