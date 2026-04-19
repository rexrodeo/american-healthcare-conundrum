# Issue #8 — The Denial Machine

Original extraction of per-contract prior authorization data from CMS-0057-F transparency disclosures, combined with insurer 10-K filings, KFF reporting data, and peer-reviewed literature, to quantify how insurance companies use claim denials as a profit tool.

**Published:** April 19, 2026
**Newsletter:** [`newsletter_issue_08.md`](newsletter_issue_08.md)
**Savings identified:** $32 billion per year (range $22–37B)

## Pipeline

```bash
# 1. Build the analysis dataset from raw CMS and SEC inputs.
#    Downloads CMS-0057-F disclosures, MA enrollment files, 10-K extracts,
#    and produces the results/ directory used by every chart.
python 01_build_data.py

# 2. Generate all charts into figures/.
#    Wipes figures/*.png first to avoid orphan stale images.
python generate_all_charts.py
```

## Outputs

- `results/` — Per-contract denial rates, appeal analysis, national extrapolation, component-level savings model, sensitivity tables.
- `figures/` — Chart 1 (per-contract denial variance), Chart 2 (appeal gap), Chart 3 (savings components, $32B stacked), Chart 4 (running savings tracker, $428.6B cumulative), plus `hero_cover.png`.
- `newsletter_issue_08.md` — Published newsletter.
- `METHODOLOGY.md` — Methodology notes: data sources, derivation of each component, overlap accounting with Issues #3, #4, #5.

## Headline findings

- **UnitedHealthcare volume-weighted denial rate: 13.5%** (vs. public "95.4% approved" claim).
- **Per-contract variance: 0.7% to 25.2%** across 61 UHC MA contracts (36× spread).
- **Appeal overturn rates: 57.9% (UHC), 64.7% (Humana).** Yet <1% of denied patients appeal.
- **National extrapolation: ~3 million MA patients** denied entitled care every year.
- **$32B/year booked savings** from four components: Care Suppression ($13.7B mid), Vertical Integration Arbitrage ($10.3B mid), AI Denial Escalation ($5.7B mid), Risk Adjustment ($0.3B).
- MLR Gaming ($11.8–20.7B) documented but excluded from booked.
- Component D (Deductible-Delay Extraction): described in the MRI vignette but excluded from the booked total. A rigorous estimate requires matched patient-level claims + deductible-exposure data. The newsletter's open-data CTA solicits partnerships to close this gap.

## Data sources

| Source | Description |
|---|---|
| CMS-0057-F Prior Authorization Transparency Rule (April 2026) | Per-contract PA decisions for MA plans |
| CMS Monthly Enrollment by Plan (March 2026) | Contract-to-enrollment mapping (970 unique contracts, 61.1M beneficiaries) |
| UnitedHealth Group 10-K FY2024 | Revenue, operating margins, Optum segment |
| Humana, CVS Health, Elevance, Cigna 10-K filings | Insurer financials and MA enrollment |
| Health Affairs (Nov 2025) | Optum vertical integration premium: 17% (61% in concentrated markets) |
| Stanford npj Digital Medicine (Jan 2026) | AI increases denial rates 5–8 percentage points |
| AMA Physician Survey on Prior Authorization (2024) | 93% say PA delays care; 8% say PA contributed to death/disability |
| KFF CY2024 Part C PA Reporting Data | MA prior authorization volumes and outcomes |
| KFF ACA Marketplace 2024 Working File | 70% of 75.9M denials are administrative (374M claims, 2,540 plans) |

## Reproducibility notes

- `01_build_data.py` uses relative paths (`Path(__file__).resolve().parent`) and can be run from a clean clone after `pip install` of the dependencies declared at the top of the script.
- Raw CMS files cached in `raw_data/` are **not** committed (>2 GB). The build script downloads them on first run.
- Chart scripts read exclusively from `results/`; they do not hit the network.
- `02_component_d.py` is preserved as a reference implementation of the deductible-delay extraction model, but its outputs are not used in the booked total. See methodology notes.

## Companion disclosures

Full Who Profits sidebar data (revenue, operating margin, CEO compensation, buybacks, lobbying) is embedded in the newsletter and cited to SEC EDGAR 10-K / DEF 14A proxy filings and OpenSecrets.org federal lobbying data.
