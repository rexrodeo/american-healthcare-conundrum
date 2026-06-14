# Issue #16 - Stage 3.5 Originality Gate Evidence (COMPUTED)

Generated 2026-06-08.

1. **`01_build_data.py` exists and runs clean.** YES. Downloads CMS Part D PUF +
   NHS Drug Tariff, builds the universe, prints the headline at exit.
2. **Script produces the headline as a printed number/variable.** YES.
   booked_bil = $16.4B printed at exit and in savings_estimate.json
   (headline_status=COMPUTED).
3. **Original vs curated distinguished with explicit headers.** YES. ORIGINAL =
   universe filter + per-drug savings + NHS gap distribution + rollups; CURATED =
   RAND ratios, IRA lists, Issue #2 ratios. See methodology.md table.
4. **Headline not already published within 5% by RAND/KFF/Peterson/FTC/CBO/JAMA.**
   YES. No outlet publishes a booked savings figure for the specific post-IRA-Rounds-1-2-3
   "other 100" Part D universe. RAND publishes the 422%/322% aggregate brand ratio but
   not applied to this universe; CMS IRA fact sheets cover only the selected drugs; KFF/
   Peterson publish per-capita and per-drug context, not this booked aggregate.
5. **Modeling implemented computationally with sensitivity.** YES. Net-to-net central
   (3.22x net ratio); recoverability {0.45,0.55,0.85}; gross-gap (4.22x) upper-method;
   NHS-floor upper bound; cross-validation reproduces Issue #2 within -0.2%
   and calibrates recoverability against IRA R2's realized capture.

**Computed central booked: $16.4B** (net-to-net, ~85 molecules
across 100 brand products; vs $35B scoping target). Reported as-is, not tuned.
