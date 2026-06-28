# Issue #18 -- Stage 3.5 Originality Gate Evidence (COMPUTED)

Generated: 2026-06-10T04:56:44.786699

1. **`01_build_data.py` exists and runs clean from a clone.** CONFIRMED. Downloads
   24 public CMS PUF CSVs (no DUA), builds every panel, emits the headline.

2. **The script produces the headline as a printed variable.** CONFIRMED.
   `booked_central_bil = $1.04B` printed at exit and in savings_estimate.json
   (headline_status = COMPUTED).

3. **ORIGINAL vs CURATED separated with explicit headers.** CONFIRMED. CURATED
   REFERENCE CONSTANTS block at top; each STEP function labels ORIGINAL; the
   methodology "what is original here" table marks Crespin's controlled 2.0% Medicare
   share as the calibrating ratio.

4. **Headline not already published within 5% by RAND/KFF/Peterson/FTC/CBO/JAMA.**
   CONFIRMED. No outlet publishes a national Medicare-isolated, DY2024-updated,
   operating-netted, recoverability-and-overlap-netted booked figure from a Fisher
   case-mix migration panel cross-checked against an HCC acuity counterfactual.
   Crespin 2024 published a national 2019 all-payer $14.6B / $4.6B Medicare gross
   figure; our $1.04B is a distinct national, recoverable, current-year number
   built on Crespin's controlled 2.0% share applied to our operating-netted pool.

5. **Modeling implemented computationally with sensitivity.** CONFIRMED. Three gross
   methods (floor/central/high), recoverability bands 0.45/0.55/0.75, full panels
   emitted to results/ for independent verification.

## Public-path posture (Andrew's directive 2026-06-09)

HCUP NIS/SID full Crespin regression replication is NOT attempted (DUA workflow).
It is the explicit data-partner CTA. The public-CMS path (Geo + Provider PUFs)
supports the case-mix migration panel, the HCC acuity counterfactual, the FFS IPPS
pool, the mechanism layer, and the FCA panel -- all original, all reproducible.
