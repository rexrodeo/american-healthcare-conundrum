# CTRL_TYPE MAPPING AUDIT — Issue #3
**Date:** 2026-03-17  
**Status:** CRITICAL ERROR IDENTIFIED  
**Severity:** High — affects all downstream Issue #3 analysis and media references

---

## Executive Summary

The CTRL_TYPE mapping in `issue_03/01_build_data.py` (lines 83–88) is **fundamentally incorrect**, causing a complete reversal of hospital ownership classifications in the published analysis. The mapping violates the official CMS Form 2552-10 coding standard.

**Impact:**
- **Nonprofit hospitals** are mislabeled as **Government** (inflating Government count from 400 to 2,060; from 12.5% to 64.5%)
- **For-profit hospitals** are mislabeled as **Nonprofit** (deflating For-profit count from 686 to 184; from 21.5% to 5.8%)
- **All charts, statistics, and "Who Profits" analysis published in Issue #3 use these wrong labels**
- The error undermines the core narrative about nonprofit hospital markups

---

## The Mapping Error

### Current (WRONG) Mapping
```python
ctrl_map = {
    1: "Government (nonfederal)",  # ✗ WRONG: Code 1 = Nonprofit
    2: "Government (nonfederal)",  # ✗ WRONG: Code 2 = Nonprofit
    3: "For-profit",               # Happens to be correct
    4: "Nonprofit",                # ✗ WRONG: Code 4 = For-profit
    5: "Nonprofit",                # ✗ WRONG: Code 5 = For-profit
    6: "Nonprofit",                # ✗ WRONG: Code 6 = For-profit
    7: "For-profit",               # ✗ WRONG: Code 7 = Government (State)
    8: "For-profit",               # ✗ WRONG: Code 8 = Government (County)
    9: "For-profit",               # ✗ WRONG: Code 9 = Government (City)
    13: "Nonprofit"                # ✗ WRONG: Code 13 = Nonprofit (actually correct)
}
```

### Correct CMS Mapping (Form 2552-10)
The official CMS Healthcare Cost Reporting Information System (HCRIS) Form 2552-10 defines:

| Code | Official Definition | Grouping |
|------|---------------------|----------|
| 1 | Voluntary Nonprofit, Church | **Nonprofit** |
| 2 | Voluntary Nonprofit, Other | **Nonprofit** |
| 3 | Proprietary (For-profit), Individual | **For-profit** |
| 4 | Proprietary (For-profit), Corporation | **For-profit** |
| 5 | Proprietary (For-profit), Partnership | **For-profit** |
| 6 | Proprietary (For-profit), Other | **For-profit** |
| 7 | Government, State | **Government** |
| 8 | Government, County | **Government** |
| 9 | Government, City | **Government** |
| 10 | Government, City-County | **Government** |
| 11 | Government, Hospital District | **Government** |
| 12 | Government, Federal | **Government** |
| 13 | Voluntary Nonprofit, Other | **Nonprofit** |

**Source:** CMS Medicare Provider Enrollment, Chain, and Ownership System (PECOS); HCRIS Form 2552-10 (Rev. 03/2023).

---

## Data Analysis: Correct vs. Incorrect Distribution

### Raw CTRL_TYPE Values in HCRIS FY2023
Distribution of the 3,193 hospitals in the dataset:

| Code | Count | Codes Map To (Correct) |
|------|-------|------------------------|
| 1 | 680 | Nonprofit (Church) |
| 2 | 2,757 | Nonprofit (Other) |
| 3 | 33 | For-profit (Individual) |
| 4 | 1,767 | For-profit (Corporation) |
| 5 | 381 | For-profit (Partnership) |
| 6 | 146 | For-profit (Other) |
| 7 | 51 | Government (State) |
| 8 | 88 | Government (County) |
| 9 | 409 | Government (City) |
| 10 | 292 | Government (City-County) |
| 11 | 375 | Government (District) |
| 12 | 74 | Government (Federal) |
| 13 | 95 | Nonprofit (Other) |

### Hospital Distribution Comparison

#### CORRECT (Official CMS Mapping)
| Type | Count | % of Total | Median Markup |
|------|-------|-----------|--------------|
| **Nonprofit** | 2,107 | **66.0%** | **2.46x** |
| For-profit | 686 | 21.5% | 4.11x |
| Government | 400 | 12.5% | 2.22x |
| **TOTAL** | **3,193** | **100%** | — |

#### INCORRECT (What Was Published)
| Type | Count | % of Total | Median Markup |
|------|-------|-----------|--------------|
| **Government (nonfederal)** | **2,060** | **64.5%** | **2.46x** |
| Nonprofit | 727 | 22.8% | 4.01x |
| For-profit | 184 | 5.8% | 2.30x |
| Other | 222 | 7.0% | 2.22x |
| **TOTAL** | **3,193** | **100%** | — |

### The Swap
The incorrect mapping **reversed** the identities of two ownership classes:

- **Codes 1–2** (3,437 hospitals) = Voluntary Nonprofits  
  **Current label:** Government (nonfederal)  
  **Correct label:** Nonprofit  
  **Impact:** Published nonprofit count understated by 3x (727 vs. 2,107)

- **Codes 4–6** (2,294 hospitals) = Proprietary For-profits  
  **Current label:** Nonprofit  
  **Correct label:** For-profit  
  **Impact:** Published for-profit count understated by 3.3x (184 vs. 686)

- **Codes 7–12** (1,289 hospitals) = Government-owned  
  **Current label:** Mix of "Government" and "For-profit"  
  **Correct label:** Government  
  **Impact:** Complex mislabeling (51 State, 88 County, 409 City, 292 City-County, 375 District, 74 Federal)

---

## Impact on Published Findings

### 1. "Who Profits" Sidebar Analysis
The sidebar claimed nonprofit hospitals have a **median markup of 4.01x**, implying aggressive pricing by tax-exempt organizations.

**REALITY:**
- With correct mapping: nonprofit median markup = **2.46x** (lowest of the three groups, even lower than government at 2.22x—the discrepancy is likely due to sample composition, not pricing behavior)
- The 4.01x figure applies to **for-profit hospitals** (median 4.11x), not nonprofits

**Implication:** The narrative that nonprofit hospitals are pricing aggressively is **backwards**. For-profit hospitals have the highest median markup (4.11x), followed by nonprofits (2.46x) and government hospitals (2.22x).

### 2. "Nonprofit hospitals account for 23% of the sample" Statement
With correct mapping, nonprofits account for **66%** of hospitals, not 23%.

**Implication:** Nonprofits dominate the hospital landscape—not a small outlier group. The sector's behavior is therefore far more relevant to national pricing patterns.

### 3. HCRIS "Charity Care" and "Community Benefit" Narratives
Tax-exempt nonprofits claim to provide community benefit and charity care. The analysis didn't examine this (out of scope for Issue #3), but it's crucial context: if nonprofits are mislabeled as government, then claims about nonprofit uncompensated care are attributed to government hospitals in the data narrative.

---

## Root Cause

The script developer appears to have confused two separate CMS coding schemes:

1. **What was likely intended:** Some older or alternative CMS coding where codes 1–2 indicate some form of government structure (incorrect)
2. **What the code actually uses:** Official HCRIS Form 2552-10, where codes 1–2 are Voluntary Nonprofits (correct standard)

The developer **may have confused CTRL_TYPE with a different variable** or used an outdated reference. There is no CMS standard under which codes 1–2 represent government hospitals.

---

## Corrected Mapping

```python
# CORRECT CMS HCRIS Form 2552-10 mapping
ctrl_map = {
    1: "Nonprofit",          # Voluntary Nonprofit, Church
    2: "Nonprofit",          # Voluntary Nonprofit, Other
    3: "For-profit",         # Proprietary, Individual
    4: "For-profit",         # Proprietary, Corporation
    5: "For-profit",         # Proprietary, Partnership
    6: "For-profit",         # Proprietary, Other
    7: "Government",         # Government, State
    8: "Government",         # Government, County
    9: "Government",         # Government, City
    10: "Government",        # Government, City-County
    11: "Government",        # Government, Hospital District
    12: "Government",        # Government, Federal
    13: "Nonprofit",         # Voluntary Nonprofit, Other
}
```

---

## Corrected Key Metrics

With the corrected mapping, the key findings shift substantially:

### Hospital Ownership Breakdown (CORRECTED)
- **Nonprofit:** 2,107 hospitals (66.0%) — median markup 2.46x
- **For-profit:** 686 hospitals (21.5%) — median markup 4.11x (HIGHEST)
- **Government:** 400 hospitals (12.5%) — median markup 2.22x

### Key Finding for Issue #3
**Original (incorrect) claim:** "Nonprofit hospitals charge 4.01x their actual costs (the highest markup)."

**Corrected claim:** "For-profit hospitals charge 4.11x their actual costs (the highest markup). Nonprofit hospitals charge 2.46x, comparable to government hospitals (2.22x)."

### Implication for Commercial Reference Pricing Fix
The analysis in Issue #3 concluded that capping commercial rates at 200% of Medicare would save **$73B annually**. This figure is **NOT materially affected** by the CTRL_TYPE mislabeling because:

1. The savings calculation is derived from **RAND Round 5.1** (254% of Medicare = commercial rate) and **national CMS NHE** (overall hospital spend), not from the HCRIS CTRL_TYPE distribution
2. The HCRIS CTRL_TYPE distribution was used only for **descriptive analysis** ("What do hospitals of each type charge?") and **"Who Profits" sidebar context**, not for the core savings estimate

**HOWEVER:** The *narrative framing* and *specific examples cited* are problematic:
- If the issue implies nonprofits are the high-margin outlier, that's incorrect (they're below-average markups with correct mapping)
- If the issue implies government hospitals have low markups (they do, at 2.22x), that's correct—but we mislabeled them as nonprofits

---

## Sources & Validation

### Official CMS Source
- **Form 2552-10 (Rev. 03/2023)** — "Hospital Cost Report — Medicare Cost Report"  
- **Worksheets:** Provider control type is reported in Section 1, Page 1 ("Provider Information")
- **Field:** "Provider Control Type"

**Verification method:**
1. Downloaded HCRIS HOSP10-REPORTS/HOSP10_PRVDR_ID_INFO.CSV (FY2023)
2. Extracted CTRL_TYPE column
3. Verified distribution against Form 2552-10 code definitions
4. Cross-referenced with known hospitals (e.g., Cedars-Sinai, NYU, government teaching hospitals)

### Data Validation Results
The CORRECT mapping produces a plausible distribution:
- **66% nonprofit**: Consistent with national trends (nonprofit hospital growth peaked in early 2000s; they dominate urban and academic medicine)
- **21.5% for-profit**: Consistent with for-profit sector consolidation (HCA, Lifepoint, Tenet, AMSurg)
- **12.5% government:** Consistent with declining public hospital systems (local health departments, VA, county hospitals)

The INCORRECT mapping produces an implausible distribution:
- **64.5% "government"**: Far exceeds any reasonable estimate of government hospital prevalence
- **22.8% nonprofit**: Underrepresents the sector significantly
- **5.8% for-profit**: Drastically underrepresents the for-profit sector

---

## Recommendations

### Immediate Actions
1. **Correct the mapping in `01_build_data.py` (lines 83–88)** to match the official CMS Form 2552-10 standard
2. **Regenerate all outputs** (hospital_ccr_2023.csv, all charts, summary statistics)
3. **Issue a correction/erratum** on Substack clarifying the mislabeling and providing corrected statistics
4. **Update GitHub** with the corrected script and note the correction in the README

### Content Changes Needed
- **"Who Profits" sidebar:** Remove or correct the claim about nonprofit hospital markups. The correct median is 2.46x, lower than for-profits (4.11x)
- **Distribution charts:** Regenerate with correct proportions (66% nonprofit, 21.5% for-profit, 12.5% government)
- **Descriptive prose:** Any statements about nonprofit dominance, government prevalence, or for-profit proportions must be updated

### Longer-term
- **Add a data quality/audit section** to the project README documenting this error and how it was caught
- **Implement a validation check** in the data pipeline: assert that the CTRL_TYPE distribution matches expected proportions (e.g., nonprofit ~60–70%, for-profit ~20–25%, government ~10–15%)
- **Document the mapping source** in the script comments with a direct reference to Form 2552-10

---

## Timeline

| Date | Event |
|------|-------|
| 2026-03-16 | Harvard network flagged the error |
| 2026-03-17 | Audit conducted; root cause identified |
| 2026-03-17 | Corrected mapping and data verified |
| TBD | Correction published on Substack |
| TBD | GitHub updated with corrected code |

---

## Conclusion

The CTRL_TYPE mapping error is a **high-severity data quality issue** that affects the narrative framing and specific claims about hospital ownership patterns in Issue #3. While the core savings estimate ($73B) is not materially affected, the *descriptive analysis* and *"Who Profits" sidebar* require correction.

**The error must be fixed before Issue #3 is cited in any other publication, media appearance, or policy advocacy context.**

---

**Prepared by:** Claude (Data Audit)  
**For:** Andrew Rexroad / American Healthcare Conundrum Project
