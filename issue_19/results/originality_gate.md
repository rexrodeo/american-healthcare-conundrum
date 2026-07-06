# Issue #19 - Stage 3.5 Originality Gate Evidence

Generated: 2026-06-10T21:07:33.574639

1. **`01_build_data.py` exists and runs clean.** CONFIRMED - this script runs
   end-to-end and emits the booked figure.

2. **Produces the headline as a print/variable.** CONFIRMED - booked central
   $10.33B printed at exit; saved to savings_estimate.json (booked_bil).

3. **Distinguishes ORIGINAL from CURATED.** CONFIRMED - explicit banners in the
   script; "what is original here" table in methodology.md. Original: the
   per-DSH-hospital panel, CCN facility scrub, allocation + allocation-proxy
   sensitivity, WAC-basis spread/CP-fee netting, two-series charity join, the
   aggregate spread-vs-charity sign test, and the COMPUTED #13/#17 overlaps.
   Curated: Drug Channels totals, IQVIA WAC, entity-type shares, ceiling
   discount, academic anchors, AIR340B.

4. **Not published within 5% by RAND/KFF/Peterson/FTC/CBO/JAMA.** CONFIRMED.
   Drug Channels publishes program totals ($81.4B) and IQVIA the WAC gap
   ($66.4B), but no per-entity spread-to-charity gap. AIR340B published a
   2022 DSH profit-vs-charity comparison ($44.1B vs $18.5B) on the SELL side;
   our buy-side per-DSH-hospital spread-minus-charity gap with overlap
   accounting against #13/#17/#4 and an allocation-robustness floor is distinct.
   Booked $10.33B is original.

5. **Modeling implemented computationally with sensitivity.** CONFIRMED - full
   3-scenario sensitivity grid (discount x cp_fee x charity-scope x DSH-share x
   recoverability) plus the first-class allocation-proxy sensitivity; cross-
   validation against Cassidy, IQVIA WAC, Drug Channels, AHA, AIR340B, and #17.

## Allocation robustness (the Stage 5.5 decisive question)

Aggregate net spread $49.61B > aggregate charity $16.18B, so
the gap is not a pure allocation artifact. See allocation_sensitivity.csv.

## Status: PASS (Stage 5.5 corrections applied; pending Stage 6 editor)
