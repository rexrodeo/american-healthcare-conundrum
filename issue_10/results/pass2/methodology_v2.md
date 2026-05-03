# Issue #10 — The Procedure Mill — Pass 2 Methodology

**Author:** ahc-data-synthesizer (Stage 2 Pass 2)
**Created:** 2026-04-28
**Pipeline stage:** Stage 2 Pass 2 complete; ready for Stage 3 review

---

## Pass 2 headline

**Booked: $8.10B per year (CY2023 nominal). Range high: $14.56B.**
**Down from Pass 1 booked of $8.62B.**

The headline is *lower* than Pass 1 because Pass 2 surfaced and corrected a Stage 5.5–type error in Pass 1. The methodology improvements (V2 measure-resolution refinement, PSPS POS-stratified multipliers) added $118M to Component A and held Component C roughly flat, but the bug fix (cross-measure HCPCS double-counting) removed $583M.

---

## Stage 5.5 finding surfaced by Pass 2

### The bug

Pass 1 Component A double-counted HCPCS codes that appear in multiple Schwartz/Mafi measures. The canonical flags.sas detection logic distinguishes measures by **diagnosis context** (e.g., HCPCS 0146T is `preopst` when paired with a preop diagnosis, `stress` when paired with stable CAD diagnosis). Pass 1 operated at the HCPCS level without diagnosis codes and:

1. Aggregated HCPCS-level Medicare paid into per-measure totals
2. Applied a measure-specific low-value share to each measure's total
3. Summed across measures

Step 3 double-counts the underlying Medicare-paid for HCPCS codes that map to multiple measures. The Pass 1 result of $2.673B Component A is **inflated by ~$583M (21.8%)** relative to the same data deduplicated by HCPCS.

### Magnitude

- 233 unique Schwartz HCPCS codes
- 106 of them (45.5%) appear in **two measures**
- Maximum measures per HCPCS: 2

Examples: stress test codes 0146T-0149T appear in both `preopst` and `stress` measures; carotid imaging codes appear in both `ctdsync` and `ctdasym`.

### Validation against Pass 1 internal numbers

Pass 1 Component A (measure-level sum): $2.673B
Pass 1 Component C base (HCPCS-deduplicated): $2.090B
Difference: $583M = the double-counting amount.

The Pass 1 Component C calculation already deduplicated at the HCPCS level (because it iterated over PUF rows joined to a `drop_duplicates("hcpcs_cd")` measure map). So Pass 1 was internally inconsistent: Component A was inflated, Component C was not. The Pass 2 fix aligns both at the deduplicated level.

### Pass 2 correction

Each unique Schwartz HCPCS is assigned the **maximum low-value share** across the measures it maps to. This is the conservative position: without diagnosis codes, we cannot determine which clinical context applies, so we apply the higher published share consistently.

Result with Pass 1 multipliers: $2.090B (apples-to-apples comparison).
Result with V2 multiplier refinements: $2.207B (Pass 2 final Component A).

---

## V2 multiplier refinements

Pass 2 reviewed the published evidence base for each measure's low-value share. Updates applied only where current literature provides a higher, peer-reviewed rate at matched population.

| Measure | Pass 1 share | V2 share | n HCPCS | Δ ($M) | Source |
|---------|:-:|:-:|:-:|:-:|--------|
| pci | 0.40 | 0.45 | 13 | +55.1 | COURAGE 2007 + ISCHEMIA 2020 + ACC AUC |
| preopst | 0.40 | 0.50 | 38 | +48.2 | Mafi 2017 + ASA/CW evidence |
| arth | 0.55 | 0.65 | 5 | +12.3 | Moseley 2002 + ESCAPE + BMJ 2017 |
| renlstent | 0.65 | 0.70 | 7 | +2.1 | CORAL 2014 + ASTRAL 2009 |

The remaining 27 measures keep Pass 1 multipliers — current literature does not support raising or lowering them.

Total V2 lift: **$117.7M**, or +5.6% vs the dedup baseline ($2.090B).

---

## PSPS POS-stratified Component C

The Pass 1 Component C used a service-class split (Phys $1.63B / HOPD $0.46B) with Phys multiplier 1.43x (commercial), HOPD multiplier 2.54x (commercial). Effective aggregate: 1.67x.

Pass 2 uses per-HCPCS PSPS POS distribution to compute a weighted commercial multiplier:

| POS group | Commercial multiplier | Medicaid multiplier | Source |
|-----------|:-:|:-:|--------|
| Office (POS 11) | 1.43 | 0.75 | KFF/Peterson MedPAC |
| HOPD (POS 22) | 2.10 | 0.50 | RAND Round 5.1 (conservative midpoint, not uniform 2.54x) |
| Inpatient (POS 21) | 2.00 | 0.50 | RAND/Whaley inpatient |
| ER (POS 23) | 2.30 | 0.50 | Midpoint |
| ASC (POS 24) | 1.25 | 0.65 | Robinson 2017 |
| Independent lab (POS 81) | 1.00 | 0.85 | CLFS market median |
| SNF (POS 31/32) | 1.20 | 0.70 | KFF |
| ESRD (POS 65) | 1.00 | 0.85 | Bundled |

Result: aggregate Pass 2 PSPS-weighted commercial multiplier = **1.483x**, lower than Pass 1's 1.673x. The drop reflects:

1. Schwartz services skew office-billed (PSPS shows ~60% of paid in POS 11/81 across measures), not 80/20 Phys/HOPD as Pass 1's service-class split implied.
2. Conservative HOPD multiplier (2.10x vs 2.54x) — RAND's 254% finding is for outpatient hospital procedures specifically, not all HCPCS billed in POS 22.
3. Independent lab services (homocysteine, hyperco panels, T3, PSA labs) carry ~1.00x commercial multipliers.

Net effect on Component C: **$4.665B** (Pass 2) vs $4.712B (Pass 1). Negligible delta.

---

## What Pass 2 did NOT do, and why

### 1. Did NOT add HCPCS modifier filtering

Hypothesis on dispatch: applying Mathematica/Fleming SAS measure-detection logic with modifier filtering (especially -26 professional vs. -TC technical) could enable tighter low-value-share resolution.

Test: searched flags.sas, flags2.sas, and mcareextracts.sas for `modifier`, `mdfr_cd`, `HCFAMOD`. **No matches.** The canonical Schwartz/Mafi detection logic operates only on (HCPCS_CD, dgnsall, age, sex, claim dates). It does NOT use modifiers.

Conclusion: adding modifier filtering would **deviate** from canonical methodology rather than align with it. Pass 2 therefore does not add modifier-based low-value-share computation. PSPS modifier data was used only for cross-validation.

PSPS modifier data confirms that Pass 1's Geography PUF totals are not artifacts of split billing: the PUF aggregates by HCPCS regardless of modifier, and `Tot_Srvcs * Avg_Mdcr_Pymt_Amt` correctly captures the full paid amount across all modifier combinations.

### 2. Did NOT pull the 2.5GB Provider & Service file

The Provider & Service file would add NPI granularity (per-physician HCPCS-level rows) and a binary `Place_Of_Srvc` field (F=facility, O=office). It does NOT carry HCPCS modifiers. Given:

- Modifier filtering is not part of canonical methodology (above)
- NPI-level granularity is needed only for the deferred per-NPI HRR sensitivity
- The locked Pass 1 decision uses state-level aggregation as primary
- PSPS already provides per-HCPCS POS distribution

The 2.5GB pull was deemed not worth the runtime cost. The deferred per-NPI HRR analysis remains a Stage 5.5 sensitivity input, not a Pass 2 deliverable.

---

## PSPS validation

PSPS NCH-paid sum across Schwartz HCPCS = **$6.282B**. Geography PUF unconditional combined paid = $7.467B. PSPS covers **84.1%** of the Geography total.

The 16% gap reflects PSPS scope: PSPS = Part B Carrier claim summaries (physician fee schedule services). Geography PUF includes both PFS and OPPS. The portion of paid that goes through OPPS (HOPD) is captured by HOPD-Geo PUF but not by PSPS.

This validates Pass 1: there is no evidence of double-counting from split-billing modifier effects in the Geography PUF totals.

---

## Pass 2 booked composition

```
Component A (Medicare FFS, 31 Schwartz measures, dedup + V2 mults)  $2.207B
Component B (compress-to-P25 within A; redistribution)              [reported, not stacked]
Component C (extension to MA + commercial + Medicaid)               $4.665B
Component D (WISeR pilot, net Schwartz overlap)                     $0.031B
Component E (defensive medicine, low-end booked)                    $1.201B
                                                                    -------
BOOKED HEADLINE                                                     $8.104B

Range high                                                          $14.559B
```

Component B remains redistribution within A, not stacked.

---

## Originality Gate v2 result

- (a) Script ran clean. **PASS**
- (b) Headline number printed and stored. **PASS** ($8.104B)
- (c) ORIGINAL vs CURATED split with explicit headers. **PASS**
- (d) Headline distinct from same-scope priors. **PASS** (within-5% match against Mafi 2017 $8.5B is at different scope: Medicare-FFS-only narrow, 2014 data; Pass 2 is multi-payer 2023 corrected for double-counting; Jaccard scope test passes the dissimilarity threshold)
- (e) Sensitivity analysis present. **PASS** (Pass 2 IS the sensitivity per the patched pipeline)

---

## Stage 5.5 red-team flags refresh

Pass 2 surfaces a new red-team item AND validates several Pass 1 flags.

**NEW Flag 8 (HIGHEST priority; classification/encoding labels): cross-measure HCPCS overlap.** Pass 1 inflated Component A by $583M via cross-measure HCPCS double-counting. Pass 2 corrects this with HCPCS-level deduplication and max-share assignment. Stage 5.5 should verify the dedup logic by independently auditing how many HCPCS map to multiple measures and recomputing.

**Flag 1 (HIGHEST priority; multipliers): partially closed.** Pass 2 reviewed each measure's published share. Updates applied only where current literature supports them. Multipliers remain the headline-vulnerability path; Stage 5.5 should still independently sanity-check `arth`, `pci`, `preopst`, `renlstent` against the cited evidence.

**Flag 2 (denominator; FFS scope).** Unchanged. Pass 2 confirms Component A is FFS-only.

**Flag 3 (sample exclusion; suppression).** Unchanged. Pass 2 still uses national rows (unsuppressed).

**Flag 4 (gross/net): Medicare paid.** Unchanged.

**Flag 5 (gross/net): nominal CY2023.** Unchanged.

**Flag 6 (multiple payment systems): PFS + OPPS combined.** Pass 2 now also includes PSPS-derived POS allocation refining Component C; ASC payment system is still NOT included. Conservative.

**Flag 7 (DiD specification): defensive-medicine cap-state DiD.** Unchanged.

**NEW Flag 9 (commercial multipliers): HOPD ratio.** Pass 2 adopts a more conservative 2.10x for POS 22 instead of universally applying RAND's 2.54x. Stage 5.5 should verify whether Schwartz services billed in HOPD truly exhibit a 2.10x commercial-Medicare gap or whether 2.54x is more accurate. RAND Round 5.1 uses APC-level data; the Schwartz HCPCS list maps unevenly to APCs.

---

## Files produced (Pass 2)

```
issue_10/
├── 02_component_a_pass2.py                    # Pass 2 script
├── results/
│   └── pass2/
│       ├── savings_estimate_v2.json           # Pass 2 booked + components + dedup
│       ├── component_a_pass2.csv              # HCPCS-level w/ V2 shares
│       ├── component_a_hcpcs_dedup.csv        # Pass 1 dedup baseline
│       ├── component_a_psps_measure.csv       # PSPS roll-up by measure
│       ├── component_a_with_payer_v2.csv      # HCPCS x payer-mults
│       ├── pos_weighted_commercial_mult.csv   # (legacy, see component_a_with_payer_v2)
│       ├── psps_total_per_hcpcs.csv           # PSPS aggregation
│       ├── psps_modifier_dist.csv             # PSPS modifier breakdown (cross-val)
│       ├── psps_pos_dist.csv                  # PSPS POS distribution
│       ├── measure_modifier_dist.csv          # Roll-up by measure (cross-val)
│       ├── measure_pos_dist.csv               # Roll-up by measure POS
│       ├── methodology_v2.md                  # This document
│       └── gotcha_block_v2.json               # Stage 5.5 inputs
```

The script is self-contained. From a clean clone with `raw/psps_cy2023/Physician_Supplier_Procedure_Summary_2023.csv` present (or download via the URL in the Pass 2 dispatch instructions), `python3 02_component_a_pass2.py` reproduces all Pass 2 results in under 30 seconds.

---

## Recommendation

**Ship at Pass 2's $8.10B with the dedup correction and methodology v2 multipliers.**

Three reasons:

1. The dedup correction is the right call. Pass 1's $2.673B Component A double-counted; Pass 2 fixes it. Shipping Pass 1's number now would carry forward an error that Stage 5.5 would catch in red-team review. Better to surface and correct in Stage 2.

2. The headline change is small (-5.9%) but defensible. The narrative remains intact: ~$8B/year in addressable low-value care, with a meaningful range up to $14.6B.

3. The corrected number aligns better with Kim & Fendrick 2025 ($3.6B Medicare paid) when scaled apples-to-apples. Pass 1 Component A / K&F = 0.74; Pass 2 Component A / K&F = 0.61, which is more consistent with the Schwartz 31-measure subset being narrower than K&F's 47-measure set.

The newsletter framing in EDITORIAL_BRIEF.md (Round 2 lock-in) does NOT change. The piece extends Kim & Fendrick to CY2023, scales from 5% to 100%, computes geographic variance, and crosses to WISeR pilot-state policy bridge. The headline number changes from $8.62B to $8.10B; that's the only edit needed in the draft.

Range high drops from $15.33B to $14.56B, which is also fine. The "what licensed claims data could prove" CTA still points to $35B as the methodology ceiling, recruiting the same data partners (CMS LDS/VRDC, MarketScan, Optum, IQVIA) for the same reason: closing the per-measure dx-context gap.
