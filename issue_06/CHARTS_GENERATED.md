# Issue #6 Charts — Generation Complete

**Date:** 2026-03-28
**Status:** All charts generated and verified. No text overlaps detected.

## Files Generated

### Issue #6 Figures (in `issue_06/figures/`)

1. **chart1_supply_variance.png** (103KB)
   - Type: Grouped bar chart
   - Data: CMI-adjusted per-discharge supply costs by hospital bed size
   - Shows: P25, P50, P75, P90 percentiles for 4 hospital size categories
   - Key insight: 7.7× variance between P25 and P75 for small hospitals
   - Includes: Hospital count annotations, variance ratio labels

2. **chart2_surplus_nonprofits.png** (108KB)
   - Type: Horizontal bar chart
   - Data: Annual in-kind donations to medical surplus nonprofits
   - Shows: 6 major organizations (Direct Relief, MAP International, Project C.U.R.E., MATTER, MedShare, Afya Foundation)
   - Key insight: >$3.3B annually flowing through surplus nonprofit ecosystem
   - Source: ProPublica Form 990 data (FY2023)

3. **chart3_savings_tracker.png** (96KB)
   - Type: Stacked horizontal bar
   - Data: Cumulative savings from Issues #1–#6
   - Shows: $356.6B total identified (11.9% of $3T target)
   - Breakdown: $0.6B + $25.0B + $73.0B + $30.0B + $200.0B + $28.0B
   - Includes: Running total annotations, target line

4. **hero_cover.png** (132KB)
   - Type: Hero image for Substack
   - Dimensions: 1456×1048px (14:10 aspect ratio)
   - Design: Navy background with subtle grid, brand colors
   - Key elements:
     - Series branding: "THE AMERICAN HEALTHCARE CONUNDRUM" (red) + "ISSUE #6" (gold)
     - Main hook: "$170.9 BILLION" (annual supply costs)
     - Supporting stat: "5,480 Hospitals. Up to 7.7× Variance"
     - Bottom stats: Three-column breakdown of waste layers and fixes

### Global Savings Tracker (in `figures/`)

- **savings_tracker.png** (94KB)
  - Updated with Issue #6 data
  - Shows all 6 issues with cumulative progress
  - Includes 11.9% progress marker toward $3T target

## Chart Specifications

All charts follow mandatory brand and quality standards:

- **Color palette:** Navy (#1A1F2E), Teal (#0E8A72), Red (#B7182A), Gold (#D4AF37), White (#F8F8F6)
- **Figure sizing:** figsize=(10, 6) at 100dpi, saved at 150dpi
- **Output dimensions:** ~1500×900px (150dpi)
- **Text overlap prevention:** All labels positioned with explicit xy/xytext coordinates
- **Font sizes:** Title 13–14pt, labels 10–11pt, annotations 7.5–9pt, footnotes 5.5–6.5pt
- **Grid spacing:** ≥40px minimum vertical clearance between adjacent labels

## Verification Results

✓ Chart 1: Clean, readable. Ratio labels positioned above P75 bars.
✓ Chart 2: Clean, readable. Value labels positioned to the right of bars.
✓ Chart 3: Clean, readable. Stacked bar with all labels visible and non-overlapping.
✓ Hero: Safe zone content centered (900×550px), all text readable.
✓ Global tracker: Updated successfully with Issue #6 contribution.

## Integration Notes

- Chart 1 replaces placeholder in newsletter_issue_06.md: *[Chart 1: Hospital Supply Cost Variance by Bed Size (CMI-Adjusted)]*
- Chart 2 replaces placeholder: *[Chart 2: Medical Surplus Nonprofits — Annual In-Kind Donations by Organization]*
- Chart 3 replaces placeholder: *[Chart 3: Savings Tracker - Full Breakdown by Issue]*
- Hero image ready for Substack social preview (1456×1048px, Substack crops to ~3:2 on homepage)
- Global tracker image updated at `/figures/savings_tracker.png` for any other future issues

## Data Sources

- **Chart 1:** CMS HCRIS FY2023, Worksheets A/S-2/S-3 (5,480 hospitals, 142.3M discharges)
- **Chart 2:** ProPublica Nonprofit Explorer, IRS Form 990 FY2023 (Schedule M extraction)
- **Chart 3:** Composite from Issues #1–#6 methodology documents
- **Hero:** Narrative elements from newsletter draft

All scripts saved to `issue_06/` directory for reproducibility.
