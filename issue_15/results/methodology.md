# Issue #15 Methodology - Stage 2 Computed Build (post-C1 recompute, 2026-06-01)

Generated: 2026-06-01T14:54:11.121304

## Headline (computed, not targeted)

- Medicare site-neutral savings, BOOKED base (clinic visits + minor procedures,
  computed from raw CMS files): **$1.967B**
- Commercial extension (net of Issue #3 overlap): **$2.508B**
- Gross (Medicare + commercial net): **$4.474B**
- After Issue #12 overlap: **$4.251B**
- **Booked (x0.6 recoverability): $2.550B**
- Range: **$0.93B - $4.13B**

The booked Medicare base is **clinic visits + minor procedures only**. Diagnostic
imaging (unbooked gross ~$4.68B) and drug administration are
BOTH excluded from the booked figure and offered as the data-partner CTA, because
public per-HCPCS files cannot isolate HOPD-outpatient volume (see the analysis
limitation on imaging below). The $15B scoping target is NOT met by the cleanly
computable data; per the no-reverse-engineering rule, the computed figure is
reported as-is.

## Analysis limitation: why imaging is not in the booked figure

The HOPD-volume proxy available in public per-HCPCS files is the Medicare
Physician/Supplier PUF service count with Place_Of_Srvc=='F'. That field is a
**binary facility/non-facility payment flag** (it takes only two values, 'O' and
'F'), not a hospital-outpatient-department indicator. POS=F therefore aggregates
every facility setting: inpatient hospital, emergency department, ambulatory
surgical center, skilled nursing facility, and HOPD. For clinic visits and the
minor-procedure injection family this is a minor overstatement, but for diagnostic
imaging the inpatient/ER share is the *majority* of POS=F volume on the codes that
carry the most dollars. Chest X-ray 71045 shows 12.3M POS=F services against only
0.72M office (POS=O) services, a 0.945 facility share that is overwhelmingly
inpatient and emergency-department portable films; head CT 70450 is 0.952 facility
share, dominated by emergency stroke and trauma scans. These services are billed
in a facility because the facility is the place of service, but they are not
candidates for an office-equivalent payment.

The public data cannot separate the HOPD-outpatient-eligible fraction of imaging
volume from the inpatient/ER/ASC fraction. The Medicare Outpatient PUF, which
would carry a true HOPD setting, suppresses packaged imaging through
Comprehensive-APC bundling (G0463 itself shows only ~1,920 primary services). With
no defensible way to downweight the single largest line to its office-equivalent
share, this analysis reports the full imaging gross (~$4.68B)
as an unbooked figure and treats imaging as a data-partner recruitment ask
alongside drug administration. Closing it requires claims-level data with a true
HOPD-outpatient site flag (CMS LDS/VRDC, state APCD, MarketScan). This is the same
public-data-floor posture as Issue #8 Component D and Issue #9.

## What is original vs curated

| Element | Status |
|---------|--------|
| Per-HCPCS OPPS facility rate (Addendum B, CY2025 Jan) | ORIGINAL (from raw file) |
| Per-HCPCS PFS office / facility-prof rate (RVU25D, CY2025) | ORIGINAL (computed from RVUs x CF) |
| HOPD volume per HCPCS (Physician PUF POS=F, DY2023) | ORIGINAL (from raw file) |
| Per-HCPCS site-of-service differential and savings | ORIGINAL |
| Clinic-visit savings via HOPD E/M + G0463 vs office E/M | ORIGINAL |
| Site-neutral candidate categories + eligibility shares | CURATED (MedPAC framework) |
| MedPAC $6.6B aggregate (cross-validation) | CURATED |
| Issue #3 2.54x commercial ratio | CURATED |
| Capps/Dranove/Ody 14.1%, HA Feb 2026 Optum 11% | CURATED |

## Data sources and years

- OPPS Addendum B, CY2025 January release (HCPCS -> facility Payment Rate).
- PFS Relative Value File RVU25D (CY2025). CF read from file: 32.3465.
- Medicare Physician & Other Practitioners by Geography and Service, DY2023
  (most recent). National POS=F service counts = HOPD-setting volume.
- Medicare Outpatient Hospitals by Geography and Service, DY2023 (used only to
  document the comprehensive-APC volume-suppression blocker; not used for
  booked numbers).

Rate year (2025) and volume year (2023) differ because CMS utilization PUFs lag
~2 years. The differential is a 2025-rate counterfactual applied to 2023 volume;
documented as a limitation.

## Computation

For each candidate HCPCS code c:

    OPPS_rate(c)   = Addendum B Payment Rate (institutional facility fee)
    PFS_office(c)  = (work + non-facility PE + MP) RVU x 32.3465
    HOPD_prof(c)   = mod-26 professional rate if c has a prof/tech split (PCTC=1),
                     else facility-PE global rate
    HOPD_total(c)  = OPPS_rate(c) + HOPD_prof(c)
    differential(c)= HOPD_total(c) - PFS_office(c)
    savings(c)     = HOPD_volume(c) x differential(c) x eligibility_share(c)

Clinic visits: for office/outpatient E/M (99202-99215) billed POS=F (HOPD),
    HOPD_total = facility E/M professional fee + G0463 OPPS clinic-visit fee
    office     = non-facility E/M total
The HOPD E/M POS=F count is the clinic-visit volume.

### Methodology refinement vs the brief's sketch
The brief sketched differential = OPPS_rate - PFS_office. That omits the facility
professional fee still paid in the HOPD and double-counts the technical component
for imaging. The corrected differential = (OPPS facility fee + facility
professional fee) - office total. This matches MedPAC's total-payment-across-
settings approach.

## Savings by category (computed; booked column flags what enters the headline)

              codes    volume  savings_bil  booked
category                                          
clinic_visit      9  18530110        1.821    True
imaging         358  55348463        4.682   False
minor_proc        6    524871        0.146    True

Only categories with booked=True (clinic_visit, minor_proc) enter the booked
Medicare base. Imaging (booked=False) is computed for the unbooked CTA gross only.

## Why the booked number is what it is (categories NOT cleanly computable)

The Outpatient PUF reports CAPC_Srvcs = comprehensive-APC PRIMARY service counts only; packaged/secondary lines (most clinic visits, drug administration, packaged imaging) are not separately counted. G0463 shows only ~1,920 services here vs the tens of millions of actual HOPD clinic visits, confirming the suppression. This is why HOPD volume for the booked categories is taken from the Physician PUF POS=F counts instead, and why drug administration is not computable and becomes the data-partner CTA.

Two categories are excluded from the booked figure and offered as the
data-partner CTA:

1. **Diagnostic imaging** — POS=F volume is contaminated by inpatient/ER/ASC/SNF
   imaging (see the analysis-limitation section above). Unbooked gross
   ~$4.68B.
2. **Drug administration (96360-96549)** — MedPAC's largest single site-neutral
   category, but HOPD drug-admin volume is packaged into Comprehensive APCs and
   unavailable per-HCPCS in public files.

Both require claims-level data with a true HOPD-outpatient site flag (CMS
LDS/VRDC, state APCD, MarketScan), mirroring Issue #8 Component D and Issue #9.

## Commercial extension

Booked uses a conservative 1.5x blend
(not the full Issue #3 2.54x). Rationale: only part of commercial outpatient
spend is OPPS-benchmarked; commercial site-neutral adoption lags; the 254% figure
is an inpatient-weighted hospital-wide average not specific to the outpatient
site-of-service mechanism. The full 2.54x is the range ceiling.

## Overlap accounting (ROADMAP rule #10, scoping Section 7)

- Issue #3: 15% of the commercial extension.
- Issue #12: 5% of the full booked.
- Issue #14: 0% (distinct payment layer).

## Recoverability

Central 60% (range 50-70%), reflecting legislative/grandfathering friction.

## Limitations

1. Volume year (2023) lags rate year (2025): a 2025-rate counterfactual on 2023
   utilization.
2. **POS=F is a binary facility/non-facility flag, not an HOPD indicator.** For
   the booked categories (clinic visits, minor procedures) the inpatient/ER/ASC
   share of POS=F is modest and the booked clinic-visit volume (~18.5M) is itself
   a conservative subset of the full institutional G0463 universe (~75M), so the
   booked figure does not rely on POS=F being a clean HOPD proxy. For imaging the
   contamination is severe (majority of POS=F volume on the top codes is
   inpatient/ER), which is why imaging is excluded from the booked figure entirely
   (see the analysis-limitation section above) rather than included with a
   judgmental eligibility fraction.
3. Eligibility shares set to 1.0 for the two booked categories; MedPAC excludes
   clinically non-equivalent services, which is why the candidate set is narrow.
4. Commercial multiplier is the single largest source of range width.
5. The imaging candidate classifier already excludes interventional/cath-lab and
   radiation-oncology families that are not office-equivalent; even within the
   remaining diagnostic-imaging set, the POS=F contamination prevents a clean
   booked figure.
