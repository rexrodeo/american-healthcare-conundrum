# Issue #15 - Stage 3.5 Originality Gate (Computed, post-C1 recompute 2026-06-01)

Generated: 2026-06-01T14:54:11.123044

## Five checks

1. **`01_build_data.py` exists and runs clean.** CONFIRMED. Downloads CMS OPPS
   Addendum B, PFS RVU25D, Physician PUF DY2023; computes and writes results.

2. **Script produces the headline as a variable/print.** CONFIRMED. Medicare
   BOOKED base (clinic visits + minor procedures) = $1.967B;
   booked total = $2.550B printed at exit and written to
   savings_estimate.json (headline_status = STAGE2_COMPUTED).

3. **ORIGINAL vs CURATED distinguished with headers.** CONFIRMED. See the CURATED
   REFERENCE DATA block in the script and the original-vs-curated table in
   methodology.md.

4. **Headline not already published within 5% by RAND/KFF/Peterson/FTC/CBO/JAMA.**
   CONFIRMED. No outlet publishes a per-HCPCS clinic-visit + minor-procedure
   site-of-service savings figure built from CY2025 OPPS Addendum B + RVU25D +
   DY2023 POS=F utilization with the corrected mod-26 professional-fee treatment,
   the clinic-visit-via-E/M-plus-G0463 computation, and the booked/range/overlap
   framework. MedPAC publishes a broader aggregate (~$6.6B)
   that INCLUDES imaging and drug administration; our booked base
   ($1.967B) is a conservative SUBSET of that scope and is
   cross-validated against the CBO clinic-visit-only score order of magnitude,
   which it matches. We neither copy nor reverse-engineer to the MedPAC figure.

5. **Modeling implemented computationally with sensitivity.** CONFIRMED.
   Sensitivity over commercial multiplier (1.5x vs 2.54x) and recoverability
   (50/60/70%) emitted; range $0.93-$4.13B.

## Verdict: CLEARS Stage 3.5.

The booked per-HCPCS computation is genuine per-code math (HOPD_volume x
differential) on the two cleanly computable categories (clinic visits, minor
procedures). Diagnostic imaging (unbooked gross ~$4.68B) and
drug administration are honestly excluded from the booked figure -- imaging
because the public POS=F flag cannot isolate HOPD-outpatient volume from
inpatient/ER/ASC (Stage 5.5 defect C1), drug administration because it is C-APC
packaged -- and both are offered as the data-partner CTA. No category is booked on
a contaminated population, and the booked number is not inflated to cover the gap.
