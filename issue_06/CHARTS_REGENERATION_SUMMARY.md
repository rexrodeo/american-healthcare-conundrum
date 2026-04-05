# Issue #6 Charts Regeneration — Complete

**Date:** 2026-03-31  
**Status:** All 6 charts generated and visually verified. No text overlaps.

## Charts Generated

### Chart 1: Hospital Supply Cost Variance by Bed Size (CMI-Adjusted)
**File:** `chart1_supply_variance.png` (104 KB)
**Type:** Horizontal range bar chart with P50 median markers
**Key Features:**
- Shows P25-P75 ranges (teal bars) with P50 median marked by red diamond
- Explicit positioning of P75/P25 ratio annotations (7.7×, 3.0×, 2.3×, 2.9×) to the right
- Hospital counts (N=) integrated into y-axis labels
- X-axis: $0–$3,500 per discharge
- **Fix from original:** Ratio annotations moved to fixed x-position with ample clearance; no overlap with bars

**Data Source:** HCRIS FY2023, 5,480 hospitals stratified by bed size

### Chart 2: Medical Surplus Nonprofits — Annual Revenue
**File:** `chart2_surplus_nonprofits.png` (96 KB)
**Type:** Horizontal bar chart with log scale
**Key Features:**
- Organizations ranked by revenue: Direct Relief ($2.27B) down to Afya Foundation ($11.6M)
- Log scale on x-axis ($10M–$1B) allows both large and small orgs to be visible and readable
- Value labels positioned inside large bars, outside small bars
- **Fix from original:** Removed overlapping annotation text at top; let the visual speak

**Data Source:** Form 990 tax filings (2023), ProPublica Nonprofit Explorer

### Chart 3: NEW — Supply Cost Decomposition ($170.9B)
**File:** `chart3_cost_decomposition.png` (110 KB)
**Type:** Horizontal stacked bar with segment labels
**Key Features:**
- Three segments: Medical Supplies ($40.4B, 23.6%), Implantable Devices ($48.7B, 28.5%), Drugs ($81.9B, 47.9%)
- Bold white labels centered inside each segment
- Total callout box highlighting $170.9B across 142.3M discharges
- Visual shows that drugs represent nearly half of hospital supply spending

**Data Source:** CMS HCRIS Worksheets A, S-2, S-3 (FY2023)

### Chart 4: NEW — Ownership Breakdown: Supply Cost Per Discharge
**File:** `chart4_ownership_breakdown.png` (132 KB)
**Type:** Two-panel bar chart (side-by-side)
**Left Panel:** Total spend by ownership
- For-Profit: $18.8B (N=1,576)
- Nonprofit: $128.9B (N=2,993)
- Government: $23.0B (N=911)

**Right Panel:** Median cost per discharge
- For-Profit: $236/DC
- Nonprofit: $1,270/DC
- Government: $1,332/DC

**Key Insight Box:** Explains that for-profit's low median reflects hospital mix (specialty/surgical centers) rather than efficiency

**Data Source:** CMS HCRIS FY2023

### Chart 5: NEW — Implant Price Variance (TKA)
**File:** `chart5_implant_variance.png` (104 KB)
**Type:** Grouped bar chart with variance and reduction annotations
**Key Features:**
- Three scenarios: Low cost ($1,797 teal), High cost ($12,093 red), High cost with reference pricing ($10,073 gold)
- 6.7× variance annotation with curved arrow connecting bars
- 16.7% reduction savings annotation showing $2,020 savings per implant
- Connects Robinson 2012 (variance) with Fang 2020 (reference pricing benefit)

**Data Source:** Robinson et al. 2012 (Health Affairs); Fang et al. 2020 (JBJS)

### Chart 6: Savings Tracker (Cumulative)
**File:** `chart6_savings_tracker.png` (163 KB)
**Type:** Two-panel cumulative bar chart
**Top Panel:** Full $3 Trillion scale
- Bars show cumulative savings: $0.6B → $356.6B across Issues #1-6
- Red dashed line at $3T target
- Progress indicator: "11.9% of $3T Target"

**Bottom Panel:** Zoomed $0–$500B window
- Same bars at larger scale to show individual issue contributions
- Individual savings labeled within segments where space allows

**Key Metrics:**
- Issue #1 (OTC): $0.6B
- Issue #2 (Drug Pricing): $25.0B
- Issue #3 (Hospital Pricing): $73.0B
- Issue #4 (PBMs): $30.0B
- Issue #5 (Admin Cost): $200.0B
- Issue #6 (Supply Waste): $28.5B
- **Running Total: $356.6B / $3T (11.9%)**

## Adherence to Chart Creation Rules

✓ **Rule 1 — Figure sizing:** All charts use `figsize=(10, 6)` at `dpi=100`, saved at `dpi=150`  
✓ **Rule 2 — Text overlap prevention:** ALL annotations use explicit `xytext` positioning. No reliance on matplotlib auto-placement.  
✓ **Rule 3 — Font minimums:** Smallest text (footnotes) at 6pt; minimum readable size 5.5pt  
✓ **Rule 4 — Layout spacing:** `gridspec_kw` used for multi-panel charts; `subplots_adjust` set appropriately  
✓ **Rule 6 — Testing:** Each PNG read and visually verified before sign-off. No overlapping text detected.  
✓ **Rule 8 — Memory management:** `plt.close(fig)` called after every `savefig()` to free memory

## Files Created

All Python scripts saved to `/sessions/blissful-optimistic-allen/mnt/healthcare/issue_06/`:
- `generate_chart1.py` — Supply variance by bed size
- `generate_chart2.py` — Surplus nonprofits
- `generate_chart3.py` — Cost decomposition (NEW)
- `generate_chart4.py` — Ownership breakdown (NEW)
- `generate_chart5.py` — Implant price variance (NEW)
- `generate_chart6.py` — Savings tracker

All PNG outputs in: `/sessions/blissful-optimistic-allen/mnt/healthcare/issue_06/figures/`

## Design Notes

**Brand consistency across all charts:**
- Navy (#1A1F2E): Backgrounds, axis labels, spines
- Teal (#0E8A72): Primary data series
- Red (#B7182A): Highlights, variance, targets
- Gold (#D4AF37): Secondary series, reference pricing
- White (#F8F8F6): Text on dark backgrounds

**Font:** DejaVu Sans throughout (system default, compatible with all platforms)

**Saving methodology:** 
- Source data compiled from HCRIS FY2023, academic literature (Robinson, Fang, Zygourakis), and Form 990 databases
- All numbers cited in RESEARCH_BRIEF.md
- Charts ready for Substack injection

---

**Quality Assurance:** All 6 charts visually verified. No text overlaps, no clipped labels, all readable at 1200px rendered width.
