# Issue #17 Methodology — The Part B Pharmacy Premium

Generated alongside `01_build_data.py`. Computed bottom-up, not a placeholder, not reverse-engineered to a target. **Revised 2026-06-09 after the Stage 5.5 adversarial math review** (full adjudication in `red_team_report.md`).

## Headline (computed)

**Booked central: $6.17B/year.** Range **$2.85–14.06B** (conservative–aggressive scenario bounds).

The scoping-brief target was $15B; the honest bottom-up computation lands at **$6.17B**, reported as-is. It came in below target for four structural reasons: (1) the triple exclusion (skin substitutes, vaccines, immune globulins/blood products) removes ~$9B of the $50.79B total Part B drug spend that has no clean international therapeutic-brand comparator; (2) the international price gap is anchored to the **Part-B-channel-appropriate 1.8x ex-manufacturer ratio** (MedPAC/ASPE), not a higher all-brand retail ratio; (3) the 340B-acquired share of the remaining spend (~35%) is reserved for Issue #19, not booked here; and (4) the gap is not applied to products that are themselves the cheaper competitor (true generics, Q5xxx biosimilars, non-Q5 follow-ons carry zero gap; biosimilar-competed originators carry a half-gap). The price gap on the part that is left, after the recoverability haircut, is $6.17B.

### What the Stage 5.5 review changed (summary)

The pre-review headline was $9.78B. The adversarial math review re-anchored three choices:

1. **The international ratio was the wrong ratio.** The earlier build used RAND RR-A788-3's all-brand "net" ratio of 3.22x as the central. That ratio nets only the US side and only the retail channel (RAND explicitly excludes physician-administered drugs from its rebate adjustment), so it is asymmetric (US-net vs. international-gross) and not Part-B-appropriate. The central is now the MedPAC June 2019 / ASPE 2018 **ex-manufacturer 1.8x** figure, published twice on this exact channel. RAND's 3.22x is retained only as the aggressive ceiling. This moved the central from $9.78B to $6.31B.
2. **The biosimilar-competed originator treatment was refined.** Genuinely-biosimilar-competed-by-CY2023 originator lines now carry a half-gap (their US ASP is already competed-down and international prices have also fallen). This trimmed $0.14B, to $6.17B.
3. **The payment-base concern was rebutted on algebra** (no number change; see "The base algebra" below).

## The ratio: there is no symmetric net-to-net international ratio for Part B

This is the central honest disclosure, and it is the lead data-partner ask.

The US side (Average Sales Price, ASP) is already net by statute (SSA 1847A(c)(3)): a volume-weighted average net of volume, prompt-pay, and cash discounts, chargebacks, and most rebates. For a **physician-administered** channel like Part B, ASP is close to the ingredient cost: RAND's own report notes that physician-administered drugs "appear to be less likely to have any rebates" than retail-dispensed drugs, so the US net price for Part B sits near gross.

The international side is the problem. Per-molecule international **net** prices for the patented biologics that dominate Part B (Keytruda, Eylea, Opdivo, Darzalex, Vabysmo) are confidential everywhere: NHS eMIT is generics-only with framework prices redacted; EURIPID and German AMNOG (Lauer-Taxe) publish gross list, not post-rebate net; IFHP is commercial-billed and short-listed. So a clean per-molecule net-to-net comparison is not possible from public data.

What **is** published, and what we use, is a channel-level **ex-manufacturer** ratio: MedPAC June 2019 (2018 data, 19 high-income OECD countries) found US Part B ex-manufacturer prices at **1.8x** the international average; ASPE 2018 independently found **1.8x**. Two federal analyses on the exact channel converge. We use 1.8x as the central. We do **not** use RAND's 3.22x as the central, because that figure (a) nets only the US side, leaving international gross, and (b) is built on a retail-channel rebate adjustment RAND says does not apply to Part B. RAND's 3.22x is the aggressive ceiling only — defensible solely if one treats the US-net/intl-gross asymmetry as a genuine recoverable gap.

### The ratio ladder

- **Central: 1.8x** (gap fraction 0.4444). MedPAC June 2019 / ASPE 2018 ex-manufacturer.
- **Conservative floor: 1.5x** (gap 0.3333). A downside stress below the published 1.8x, recognizing that international *list* prices in some comparisons overstate the gap, and that the highest-spend Part B molecules may sit below the all-OECD average.
- **Aggressive ceiling: 3.22x** (gap 0.6894). RAND RR-A788-3 all-brand net ratio (US-net/intl-gross), the optimistic case.

The MedPAC **payment-rate** ratio (2.05x, which bakes in the ASP+6% add-on) is carried in the sensitivity table for reference but is **not** the central, because pairing a payment-rate ratio with a payment base would double-count the add-on. We pair the **ex-manufacturer** 1.8x with the payment base so the add-on rides correctly (see the algebra below).

## The base algebra: why the ASP+6% payment base is correct (Stage 5.5 Challenge 2 rebuttal)

The spend base is `Tot_Spndng_2023` = the full value of the product (Medicare program payment + beneficiary liability), which is the **ASP+6% allowed charge**, realized at about ASP+4% after the 2% sequester. Verified empirically against the PUF: the realized spend per dosage unit runs at ~0.98 of the `Avg_DY23_ASP_Price` payment-allowance column (median 0.982 across 734 codes; e.g., Keytruda $53.95 realized vs. $55.14 allowance). So the base is a **payment** base, not a bare-ingredient base.

The red-team asked whether applying an ingredient-price gap to a payment base over-recovers the ~6% add-on. It does not, because the add-on is **proportional** and rides down with the ingredient price under reference pricing. Per unit:

```
S_now = k · ASP            (current spend; k ≈ 1.039, the post-sequester ASP+6% multiplier)
Under reference pricing the ingredient falls: ASP → ASP / ratio, k unchanged (same statutory ASP+6%)
S_ref = k · (ASP / ratio)
saving = S_now − S_ref = k·ASP·(1 − 1/ratio) = S_now · g = Tot_Spndng · g
```

The reduction in the add-on dollars (from `0.039·ASP` to `0.039·ASP/ratio`) is itself a real system saving: Medicare really does pay fewer add-on dollars when the ingredient is cheaper. So the ex-manufacturer gap fraction `g` applied to the whole payment base yields the correct **system** saving. Deflating the base by /1.06 would *understate* the saving by discarding the legitimate add-on reduction. The base is kept whole; the political friction on the (least-recoverable) add-on dollars is carried once, in the recoverability factor, not double-counted.

## The formula

For each Part B drug d in the universe:

```
spend_d        = Tot_Spndng_2023            (ASP+6% allowed charge; payment base)
intl_ratio_d   = US ex-manufacturer / international ex-manufacturer   (central = 1.8x)
gap_fraction_d = 1 − (1 / intl_ratio_d)     (1.8x → 0.4444)
                 × 0.5 for biosimilar-competed-by-CY2023 originators
                 → 0 for true generics, Q5xxx biosimilar products, non-Q5 follow-ons
non340B_share  = 1 − 340B-acquired share    (central 0.65; reserves 340B for #19)

BOOKED = recoverability × SUM_d [ spend_d × gap_fraction_d × non340B_share_d ]
```

**Central parameters:** ex-manufacturer ratio **1.8x** (gap 0.4444); 340B share **0.35** (non340B 0.65); recoverability **0.55**.

## The waterfall (auditable, every step printed)

| Step | Spend |
|---|---|
| Total separately-paid Part B drug spend, CY2023 (734 HCPCS) | $50.79B |
| − skin substitutes (Q4xxx) | −$3.64B |
| − vaccines (90xxx/91xxx + brands) | −$2.50B |
| − immune globulins / blood products | −$2.86B |
| − GLP-1 (Issue #7 overlap; asserted empty) | −$0.00B |
| **= Universe spend base (597 codes)** | **$41.80B** |
| × international gap (spend-weighted 1.8x → 0.444; true generics + Q5 biosimilars + non-Q5 follow-ons zeroed; competed originators half-gap) | **$17.27B** gross gap |
| × non-340B share (0.65) | **$11.22B** after 340B netting |
| × recoverability (0.55) | **$6.17B booked** |

## Every parameter, with source

- **`spend_d` = Tot_Spndng_2023** — CMS Medicare Part B Spending by Drug PUF, CY2023 annual release (RY25, DYT23), dataset `76a714ad-3a2c-43ac-b76d-9dadf8f7d890`. "Total Spending" is the full value of the product: Medicare program payment + beneficiary liability, i.e., the **ASP+6% allowed charge** (realized ~ASP+4% post-sequester). Nominal CY2023 dollars. NOT a charge, NOT a cost.
- **`intl_ratio_d` = 1.8x (central)** — MedPAC June 2019 Report Ch.3 (2018 data, 19 high-income OECD) and ASPE 2018 ("Comparison of US and International Prices for Top Spending Part B Drugs"), both ex-manufacturer. This is the published Part-B-channel ratio; it pairs correctly with the payment base via the proportional-add-on algebra. RAND's 3.22x is the aggressive ceiling only (US-net/intl-gross, retail-calibrated). No symmetric net-to-net Part B ratio is public; that is the data-partner ask.
- **`gap_fraction_d`** — 1 − 1/intl_ratio. **Zeroed** for three kinds of line that are themselves the cheaper competitor rather than the monopoly-priced originator: (1) true unbranded generics (normalized brand == normalized generic); (2) Q5xxx biosimilar products; (3) non-Q5 follow-on biosimilars (tbo-filgrastim / Granix J1447). **Halved** for genuinely-biosimilar-competed-by-CY2023 originators (see below).
- **`non340B_share` = 0.65 (central)** — 340B-acquired share of separately-paid Part B drug spend estimated at 0.35. No single published figure pins this share directly. MedPAC's OPPS-340B-remedy analysis (April 2024) put the average minimum 340B discount at 22.5% of ASP (a 2020 acquisition survey found ASP−28.7%), and CMS estimated it would have spent ~$4B less in CY2024 paying 340B-acquired Part B drugs at acquisition cost. The **share** is derived from GAO/MedPAC HOPD drug-spending analyses, bounded to roughly 28–45%; central 0.35, sensitivity 0.25–0.45. The precise per-J-code share requires JG/TB-modifier-tagged claims (CMS RIF/LDS, restricted) and is the second data-partner ask.
- **`recoverability` = 0.55 (central)** — the share of the computed gap that realistic Part B reference-pricing policy could capture after political, industry, and operational friction. Anchored to the Part B reference-pricing context (the Most Favored Nation model was finalized November 2020, litigated, and rescinded December 2021 before taking effect; the Global and Bundled Effort, or GLOBE, model announced December 19, 2025 is a mandatory demonstration covering only a portion of Part B utilization; and buy-and-bill providers and 340B hospitals have a direct financial stake in resisting any change that compresses the price base their ASP+6% margin scales on). This factor is also the single home for the least-recoverable-add-on-dollar friction (the base is kept whole, so that friction is not double-counted). Sensitivity 0.40–0.70.

## Biosimilar treatment (Stage 5.5 Challenge 3/4 corrected)

Three different cases, handled differently:

**Biosimilar PRODUCTS (the cheaper competitor) — gap ZEROED.** A product that is itself a biosimilar (the Q5xxx HCPCS code block: Truxima, Mvasi, Zirabev, Ruxience, Cimerli, Renflexis, Inflectra, Zarxio, Fulphila, Udenyca, Retacrit, etc.) is the low-priced entrant. The brand-originator gap cannot apply to it. These 27 codes ($1.435B spend) are kept in the panel for transparency but carry zero gap; the Q5 zeroing removes $0.228B versus giving them the full 1.8x gap. **Plus** non-Q5 follow-ons billed under J-codes (tbo-filgrastim / Granix, J1447) are also zeroed — they are cheaper competitors the Q5 prefix screen misses.

**Biosimilar-COMPETED-by-CY2023 originators (the branded originator, with mature competition) — HALF-GAP.** Originator reference lines whose ASP was already biosimilar-depressed in the CY2023 anchor year AND whose international prices have also fallen with biosimilar competition (rituximab/Rituxan, bevacizumab/Avastin, trastuzumab/Herceptin, pegfilgrastim/Neulasta, filgrastim/Neupogen, epoetin/Epogen, darbepoetin/Aranesp, ranibizumab/Lucentis, infliximab) carry a **half-gap** (gap × 0.5): the US ASP is already competed and the US-vs-international ratio is below the monopoly average. This is 15 originator lines, $2.075B spend; the half-gap trims $0.14B (sensitivity: full $6.31B / half $6.17B / zero $6.04B).

**Critical false-positive exclusions.** The half-gap is restricted to genuinely-competed molecules. It explicitly **excludes**, keeping the full gap: (1) novel antibody-drug conjugates and combos matched only by molecule substring (Enhertu / fam-trastuzumab-deruxtecan J9358, Kadcyla / ado-trastuzumab emtansine J9354, Phesgo / pertuzumab-trastuzumab) — these are on-patent monopoly biologics with no biosimilar; and (2) originators whose biosimilars launched *after* CY2023 (Eylea/aflibercept, biosimilars May 2024 blocked by litigation; Prolia/denosumab 2025; Soliris/eculizumab 2025) — monopoly in the anchor year. The Q5xxx prefix screen leaves novel originators with 4-letter suffixes (Darzalex Faspro, Vabysmo, Ultomiris, Enhertu) untouched by construction.

## The 340B boundary with Issue #19

- **Issue #17 books the international price gap on NON-340B-acquired Part B drug spend.**
- **Issue #19 books the DOMESTIC 340B acquisition spread** (340B-discounted acquisition cost vs. ASP/commercial reimbursement) on 340B-acquired Part B drug spend.

These are different counterfactuals against different reference prices, so they are additive **in mechanism**. The 340B-acquired share's international-gap dollars are removed from #17 entirely and reserved for #19, which is conservative for #17 (it books none of them). **Overlap caveat at the project-tracker level (Stage 5.5 Challenge 5):** for a 340B-acquired unit, the international gap (~44% at 1.8x) and the domestic 340B spread (~22–30%) partly target the same overpayment dollars. #17 removes the international gap on those units (conservative); #19 books only the smaller domestic spread. So the project-level sum (#17 + #19) is **less than** the naive sum of each fully scoped — the running total carries this overlap caveat. Issue #19 publishes after #17; it is referenced as upcoming, not linked.

## IPAY-2028 negotiation flag

Five drugs in the universe ($2.90B spend) are IPAY-2028 negotiation selections (the first-ever Part B negotiation cycle; Maximum Fair Prices effective January 1, 2028). They are **kept in the base** — the CY2023 pre-negotiation ASP is the correct present-day baseline, and the gap exists today. Sensitivity: booked falls from $6.17B to **$5.71B** if the IPAY-2028 selections are excluded entirely (a ~7% effect; the gap is real for the 2023–2027 window regardless).

## The data-partner CTA (what's missing)

The single soft spot, disclosed openly (the same move as Issues #8, #9, #16):

1. **No symmetric net-to-net international ratio exists for Part B biologics.** The US ASP side is near-net for this physician-administered channel, but per-molecule international NET prices for patented biologics (Keytruda, Eylea, Opdivo, Darzalex, Vabysmo) are confidential. NHS eMIT is generics-only with framework prices redacted; EURIPID and German AMNOG (Lauer-Taxe) are gross *list*, not net; IFHP is commercial-billed. We therefore apply the MedPAC/ASPE ex-manufacturer 1.8x **class ratio** to 95.0% of universe spend. A data partner holding EURIPID full access, national procurement net prices (NHS commercial framework, German AMNOG post-rebate net), or a licensed IQVIA MIDAS international ex-manufacturer net dataset would let us compute per-molecule net gaps and replace the class ratio.
2. **The precise 340B-acquired share of our specific J-codes** needs JG/TB-modifier-tagged Part B claims (CMS RIF/LDS, restricted). We estimate the aggregate share from MedPAC/GAO; the per-drug share is the ask.

## Sensitivity grid

| Scenario | ratio | gap | 340B share | recov | booked |
|---|---|---|---|---|---|
| Conservative | 1.5x | 0.333 | 0.45 | 0.40 | **$2.85B** |
| **Central** | **1.8x** | **0.444** | **0.35** | **0.55** | **$6.17B** |
| Aggressive | 3.22x | 0.689 | 0.25 | 0.70 | **$14.06B** |

One-at-a-time around the central:
- **Ratio:** 1.5x → $4.60B; 1.8x (central) → $6.17B; 2.05x (payment-rate, reference only) → $7.07B; 3.22x (RAND ceiling) → $9.52B.
- **340B share:** 0.25 → $7.08B; 0.35 (central) → $6.17B; 0.45 → $5.19B.
- **Recoverability:** 0.40 → $4.46B; 0.55 (central) → $6.17B; 0.70 → $7.81B.
- **Biosimilar-competed originator gap factor:** full (1.0) → $6.31B; half (0.5, central) → $6.17B; zero (0.0) → $6.04B.
- **Q5 biosimilar-product gap:** zeroed (central) → $6.17B; full brand gap (pre-patch) → $6.40B.

## "What is original here" table

| Element | Original or Curated |
|---|---|
| CY2023 single-source-brand/biologic Part B universe + triple exclusion + GLP-1 assertion | **ORIGINAL** (computed from the PUF) |
| Per-J-code spend aggregation, spend-weighted average ratio, concentration stats | **ORIGINAL** |
| International-gap savings net of 340B-acquired volume; the #17/#19 boundary | **ORIGINAL** |
| Proportional-add-on treatment of the ASP+6% payment base (no deflation) | **ORIGINAL** application + documented algebra |
| Biosimilar-competed-by-CY2023 originator half-gap (with ADC / post-2023 false-positive exclusions) | **ORIGINAL** treatment |
| Q5xxx + non-Q5-follow-on gap-zeroing (brand-originator gap not applied to competitors) | **ORIGINAL** treatment |
| Sensitivity grid (ratio × 340B-share × recoverability × biosim-gap-factor) | **ORIGINAL** |
| MedPAC 2019 / ASPE 2018 ex-manufacturer 1.8x ratio (central input) | CURATED (analytic input) |
| RAND RR-A788-3 net brand-originator ratio (3.22x; aggressive ceiling) | CURATED (analytic input) |
| MFN 2020 ($87.8B gov over 7 years), GLOBE 2025 ($11.9B/7yr), MedPAC 2019 (2.05x payment-rate) | CURATED (cross-validation / distinguished priors) |

**Distinct-from-published:** our booked central ($6.17B/yr) is 263% apart from GLOBE's annualized figure ($1.7B/yr) and differs from MFN/MedPAC/ASPE in year (CY2023), universe (triple exclusion), 340B netting, and counterfactual (full single-source biologic universe, one-year recoverable, 340B-netted vs. a phased mandatory-subset rebate model). It is not within 5% of any published Part B gap figure on the same scope. (Note: the MFN 2020 government-savings figure is **$87.8B over 7 years**, not 10 — corrected 2026-06-09; annualized ~$12.5B/yr.)

## Limitations

- The headline anchors on a single class-level ex-manufacturer ratio (1.8x) applied to 95.0% of universe spend, because per-molecule international net prices for patented biologics are not public. If the true Part-B-specific net gap is below the 1.8x ex-manufacturer figure, the central is overstated; if above, understated. This is the central uncertainty and the lead data-partner ask. The aggressive scenario (3.22x) shows the upper bound if the US-net/intl-gross asymmetry is treated as recoverable.
- The 340B-acquired share (0.35 central) is an aggregate estimate, not a per-J-code measurement. The sensitivity grid spans 0.25–0.45.
- Total Part B spend in the PUF is "separately paid" drug spend; packaged/bundled drugs (paid inside a procedure rate) are not in scope.
- Nominal CY2023 dollars throughout; no inflation adjustment is applied (single-year analysis).
