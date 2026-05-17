# Issue #12 Methodology — Stage 2 Full Build (auto-generated)

Generated: 2026-05-12T12:42:53.614485

## Status

Stage 2 full build complete. Headline figure: **$13.03B booked** (Range $25.0-$50.0B per ROADMAP).

## What is original analysis vs curated reference

| Element | Status |
|---------|--------|
| Merger event panel 2018-2025 from CMS POS (8 annual snapshots) | ORIGINAL |
| HSA-level HHI panel computed from POS bed counts via Dartmouth ZIP-HSA crosswalk | ORIGINAL |
| Pre/post HHI shift per merger HSA-year (top-2 firm combination simulation) | ORIGINAL |
| Per-hospital commercial spend allocation from HCRIS Worksheet G-3 Net Patient Revenue with NHE-anchored uniform commercial share | ORIGINAL |
| National scaling to NHE 2024 private-insurance hospital anchor | ORIGINAL |
| Per-market booked savings table with overlap subtractions | ORIGINAL |
| Coefficient anchors (Cooper, Dafny/Ho/Lee, Brot-Goldberg, FTC Evanston) | CURATED |
| Industry-side counter-arguments | CURATED |

No outlet has published a per-HSA-year merger panel constructed from CMS POS files with Issue #3 / Issue #15 overlap accounting applied. The application of the curated coefficient to this panel is the originality claim.

## Data inputs

- **CMS Provider of Services (POS) annual snapshots, 2018-2025** (n=8 years).
  Source: data.cms.gov data.json catalog. Hospital subset (PRVDR_CTGRY_CD=01).
  Fields used: PRVDR_NUM, GNRL_CNTL_TYPE_CD, CHOW_DT, CHOW_PRIOR_DT, CHOW_CNT,
  CRTFD_BED_CNT, ZIP_CD, STATE_CD, FAC_NAME.
- **CMS HCRIS HOSP10 FY2023** (primary fiscal year anchor).
  Worksheet G-3 Line 3 Col 1 = Net Patient Revenue.
  Worksheet S-3 Pt 1 Line 14 Cols 2/3 = beds, bed-days-available. Payer-day columns are extracted as sanity-check fields but the brittle column encoding across HOSP10 years means the days-based commercial-share proxy is NOT used to drive the allocation. Per-hospital commercial revenue is computed as Net Patient Revenue * 0.40, with the national total reconciled to the NHE 2024 private-insurance hospital anchor via a small scale factor.
- **Dartmouth Atlas ZIP -> HSA -> HRR crosswalk (2019 release)**.
  3,436 HSAs, 306 HRRs.
- **CMS NHE 2024 final tables** (private-insurance hospital category = ~$595B; curated).

## Coefficient stack (CURATED REFERENCE)

| Anchor | Coefficient | Source |
|--------|-------------|--------|
| Cooper 2019 QJE | 15.3% monopoly differential | Cooper et al. 2019, QJE 134(1):51-107 |
| Dafny/Ho/Lee 2019 RAND J Econ | 7-9% cross-market merger effect | Dafny/Ho/Lee 2019, RAND J Econ 50(2):286-325 |
| FTC Evanston WP 307 | 11.1-17.9pp post-merger increase | FTC retrospective study |
| Brot-Goldberg/Cooper/Craig 2024 | post-2019 cohort, consistent with Cooper | NBER WP 32613 |
| Brot-Goldberg 2024 wage pass-through | 0.4% labor income decline per 1% price increase | NBER WP 32613, downstream |

Piecewise application:
- HHI_post >= 4000: Cooper coefficient (15.3%)
- 2500 <= HHI_post < 4000: blended 9.5% (between Dafny upper and Cooper)
- 1500 <= HHI_post < 2500: Dafny central 8%
- HHI_post < 1500: Dafny lower 7%

Coefficient is scaled by HHI shift intensity (shift / 200 points, capped at 1.0) to reflect the FTC merger-review threshold for presumed anticompetitive effects.

## Spending denominators

- NHE 2024 private-insurance hospital spend: $595.0B (CMS NHE final 2024)
- Issue #3 commercial spend at risk: $528.0B (Issue #3 published)
- Issue #3 booked savings: $73.0B (Issue #3 published)

## Overlap accounting (ROADMAP rule #10)

- **Issue #3 (commercial-vs-Medicare gap)**: Issue #3 booked $73B by capping commercial hospital payments at 200% of Medicare on $528B commercial spend at risk. A fraction of #12's HHI-shift effect is already captured by that cap (hospitals charging well above 200% are dragged down). Conservative subtraction: **20% of #12 raw savings** ($20%).
- **Issue #15 (facility-fee differential)**: Vertical physician-practice acquisitions billed at HOPD rates are entirely #15's territory. The merger event panel flags vertical acquisitions as `tax_status_change` / `government_transition`; horizontal mergers stay in #12. Residual subtraction for any leakage: **5% of #12 raw savings**.

## Headline figures

| Metric | Value |
|--------|-------|
| Merger HSA-years detected | 409 |
| Hospitals in commercial spend allocation | 6,044 |
| Mean HHI shift per merger HSA-year | 2318.1 |
| Raw gross savings (pre-overlap) | $17.37B |
| Issue #3 overlap subtraction | -$3.47B |
| Issue #15 overlap subtraction | -$0.87B |
| **Booked Issue #12** | **$13.03B** |
| Range (per ROADMAP) | $25.0-$50.0B |
| Headline target status | OUT_OF_RANGE_NEEDS_REVIEW |

## Sensitivity

- Merger-market commercial spend total: $218.44B
- At a flat 5% blended uplift across that base (net of overlap): $8.19B
- At a flat 10% blended uplift: $16.38B
- The booked figure uses the HHI-piecewise coefficient, not a flat blend

## Booked target and range

- Booked: $13.03B
- Range: $25.0-$50.0B

## Known limitations (Stage 5.5 red-team hooks)

1. **POS bed-count market share is a proxy.** AHA Annual Survey (gated) would give verified system-affiliation flags; data-partner CTA in newsletter.
2. **Top-2 firm merger simulation is conservative.** Real horizontal mergers may combine non-top hospitals; some HHI shifts will be understated, others overstated. Net direction in expectation: small bias toward understatement (real mergers are sometimes between #1 and #3, which is closer to top-2 than to non-top combinations).
3. **HCRIS payer-days proxy for commercial share has measurement error.** Some hospitals' commercial revenue intensity (revenue per day) differs from Medicare/Medicaid. The reconciliation to NHE 2024 partially corrects for this at the national aggregate.
4. **Annual POS snapshots miss intra-year mergers.** Quarterly granularity is available but adds 4x data volume; annual captures ownership state at year-end which is the relevant year for the next year's price renegotiation.
5. **Coefficient is curated, not estimated from this panel.** Cooper 2019 used HCCI; Dafny used FAIR Health; both restricted-access. The originality is in the application to a public-data panel, not in re-estimating the coefficient from claims.

## Stage 5.5 pre-emptive rebuttals

1. **"Cooper 2019 is a level differential, not a merger event study."** Confirmed in Stage 1; the application here treats Cooper as the monopoly-equilibrium upper bound. The merger-event interpretation rests on Dafny/Ho/Lee and Brot-Goldberg, which the cross-validation table confirms.
2. **"Public bed counts are an inferior market-share proxy."** Confirmed limitation; the Petris Center commuting-zone HHI panel is the cross-validation target where available, and the data-partner CTA in the newsletter is explicit.
3. **"Mergers create efficiencies that offset price increases."** Beaulieu et al. 2020 NEJM: no measurable quality benefit; FTC retrospectives empirically falsify the efficiency hypothesis. Counter-script already in place.
4. **"The 30% upper bound was wrong."** Confirmed in Stage 1; Issue #11 tease was revised to 7-17% before publishing.
5. **"Per-transaction granularity is not feasible from public data."** Confirmed; the headline is per-market (HSA), with per-transaction granularity flagged as data-partner CTA (state APCDs, MarketScan, FAIR Health).
