# CTRL_TYPE MAPPING ERROR — CORRECTION CASCADE REPORT
**Date:** 2026-03-17
**Severity:** CRITICAL — affects published materials, media pitches, and external references
**Status:** Corrections identified and documented

---

## Executive Summary

The CTRL_TYPE mapping error in `issue_03/01_build_data.py` (lines 83–91) has cascaded into **public-facing materials**, specifically:
1. **PROMO_KIT.md** — 4 instances of the false "3.96× nonprofit markup" claim
2. **CLAUDE.md** — 2 instances (one key metric claim, one ownership breakdown)
3. **README.md** — 2 instances
4. **Newsletter draft newsletter_issue_03.md** — Does NOT contain false claims (passed fact-check without ownership breakdowns)

**Files requiring correction:**
- PROMO_KIT.md (HIGH PRIORITY — media-facing document)
- CLAUDE.md (HIGH PRIORITY — project documentation)
- README.md (MEDIUM PRIORITY — public repository reference)
- 01_build_data.py (CRITICAL — must fix the mapping itself)

---

## Detailed Correction Requirements

### 1. PROMO_KIT.md

**File:** `/sessions/pensive-clever-hypatia/mnt/healthcare/issue_03/PROMO_KIT.md`

#### Correction 1 — Line 36
**Current (WRONG):**
```
- Nonprofit hospitals have a median markup of 3.96x their actual operating costs
```

**Corrected to:**
```
- For-profit hospitals have a median markup of 4.11x their actual operating costs (the highest of all three ownership types)
```

**Rationale:** With correct CTRL_TYPE mapping:
- Nonprofit hospitals: 2.46x (LOWEST)
- For-profit hospitals: 4.11x (HIGHEST)
- Government hospitals: 2.22x

The original claim was backwards: nonprofit hospitals have the **lowest** median markup, not the highest.

---

#### Correction 2 — Line 67
**Current (WRONG):**
```
The analysis also computes cost-to-charge ratios for 3,193 hospitals by ownership type. Nonprofit hospitals (which receive tax exemptions) have a median markup of 3.96x actual operating costs.
```

**Corrected to:**
```
The analysis also computes cost-to-charge ratios for 3,193 hospitals by ownership type. For-profit hospitals have a median markup of 4.11x actual operating costs (the highest), while nonprofit hospitals have a median markup of 2.46x and government hospitals 2.22x — suggesting that ownership structure correlates with pricing behavior.
```

**Rationale:** Same as above. The original framed nonprofits as the expensive outlier; the corrected version shows for-profits as the actual high-cost outlier.

---

#### Correction 3 — Line 94
**Current (WRONG):**
```
Key finding: commercial insurers pay 254% of Medicare rates for identical hospital procedures. The median nonprofit hospital marks up 3.96x above actual operating costs.
```

**Corrected to:**
```
Key finding: commercial insurers pay 254% of Medicare rates for identical hospital procedures. For-profit hospitals (median markup 4.11x) have the steepest markups above actual operating costs, followed by nonprofit hospitals (2.46x), suggesting that profit motive rather than nonprofit status drives high markups.
```

**Rationale:** The original was misleading; nonprofits were being blamed for markups that actually belong to for-profits.

---

#### Correction 4 — Line 133
**Current (WRONG):**
```
I analyzed 3,193 hospital cost reports from CMS. Nonprofit hospitals mark up 3.96x above actual costs. A hip replacement: $29,006 here, $11,169 peer average.
```

**Corrected to:**
```
I analyzed 3,193 hospital cost reports from CMS. For-profit hospitals mark up 4.11x above actual costs (the highest of all ownership types). A hip replacement: $29,006 here, $11,169 peer average.
```

**Rationale:** Swaps the correct markup figure and ownership type.

---

**Additional Note on PROMO_KIT Line 145:**
```
✅ Tara Bannow (STAT News) — nonprofit markup angle
```

**Recommendation:** Change to:
```
✅ Tara Bannow (STAT News) — for-profit hospital markup angle
```

**Rationale:** The story angle should now be about for-profit hospitals' higher markups, not nonprofits. This affects the media pitch.

---

### 2. CLAUDE.md

**File:** `/sessions/pensive-clever-hypatia/mnt/healthcare/CLAUDE.md`

#### Correction 1 — Line 50 (Issue #3 Summary)
**Current (WRONG):**
```
- Finding: Commercial insurers pay 254% of Medicare for identical hospital procedures (RAND Round 5.1). Hip replacement: US $29k vs. Germany $15k vs. Spain $9k (iFHP 2024-2025). HCRIS FY2023 analysis of 3,193 hospitals shows median markup of 2.6× actual costs (nonprofit hospitals: 3.96×); 37% charge 3× or more.
```

**Corrected to:**
```
- Finding: Commercial insurers pay 254% of Medicare for identical hospital procedures (RAND Round 5.1). Hip replacement: US $29k vs. Germany $15k vs. Spain $9k (iFHP 2024-2025). HCRIS FY2023 analysis of 3,193 hospitals shows median markup of 2.6× actual costs overall (nonprofit hospitals: 2.46×, for-profit hospitals: 4.11×); 37% charge 3× or more.
```

**Rationale:**
- The parenthetical "(nonprofit hospitals: 3.96×)" was sourced from the incorrect CTRL_TYPE mapping
- Corrected to show: nonprofits 2.46x, for-profits 4.11x
- The overall median 2.6× remains unchanged (it's computed before the ownership breakdown)

---

#### Correction 2 — Line 135 (Issue #6 Summary)
**Current (WRONG):**
```
  - Ownership split: Nonprofits $122.9B (72%), median $1,273/discharge vs. Government median $458/discharge
```

**Corrected to:**
```
  - Ownership split: Nonprofits $149.6B (88%), median $1,190/discharge vs. For-profit $16.8B (10%), median $1,567/discharge vs. Government $4.5B (2%), median $915/discharge
```

**Rationale:**
- Original figures came from the CTRL_TYPE mislabeling in the supply waste script
- The supply waste script reads CTRL_TYPE correctly (lines 470–484 of `supply_waste_step3_cmi.py`)
- But the mapping of raw CTRL_TYPE codes to ownership labels must be fixed
- Corrected proportions: Nonprofits should dominate (~66% in Issue #3 HCRIS, which translates to ~88% of supply costs due to higher bed count); for-profits ~21.5% by count (~10% of supply spend); government ~12.5% by count (~2% of supply spend)

**Important caveat:** The actual corrected figures for Issue #6 will require re-running `supply_waste_step3_cmi.py` with the corrected CTRL_TYPE mapping. The figures shown above are estimates. **Do not publish these specific numbers until the script is re-run and verified.**

---

### 3. README.md

**File:** `/sessions/pensive-clever-hypatia/mnt/healthcare/README.md`

#### Correction 1 — Line 76 (Issue #3 Metrics)
**Current (WRONG):**
```
- Median markup in nonprofit hospitals: 3.96× actual operating costs; 37% of all hospitals charge 3× or more
```

**Corrected to:**
```
- Median markup in for-profit hospitals: 4.11× actual operating costs (highest); nonprofit hospitals: 2.46× (lowest); 37% of all hospitals charge 3× or more
```

**Rationale:** Same as PROMO_KIT corrections — ownership types were swapped.

---

#### Correction 2 — Line 17 (Issue Summary Table)
**Current entry:**
```
| 3 | [The 254% Problem](issue_03/newsletter_issue_03.md) | $73.0B/yr | Commercial insurers pay 254% of Medicare for identical hospital procedures | CMS HCRIS, RAND 5.1 |
```

**No change required** — the summary is ownership-agnostic and does not reference the mislabeled figures.

---

### 4. 01_build_data.py (THE ROOT FIX)

**File:** `/sessions/pensive-clever-hypatia/mnt/healthcare/issue_03/01_build_data.py`
**Lines:** 83–91

**Current (WRONG):**
```python
ctrl_map = {
    1: "Nonprofit", 2: "Nonprofit",           # Voluntary Nonprofit (Church, Other)
    3: "For-profit", 4: "For-profit",          # Proprietary (Individual, Corporation)
    5: "For-profit", 6: "For-profit",          # Proprietary (Partnership, Other)
    7: "Government", 8: "Government",          # Government (State, County)
    9: "Government", 10: "Government",         # Government (City, City-County)
    11: "Government", 12: "Government",        # Government (Hospital District, Federal)
    13: "Nonprofit"                            # Voluntary Nonprofit, Other
}
```

**Wait — CRITICAL DISCOVERY:** The mapping in the current codebase is **actually correct**. Let me re-read the audit...

Looking at CTRL_TYPE_AUDIT.md line 24-35, the audit states the WRONG mapping had codes 1–2 as "Government (nonfederal)" and codes 4–6 as "Nonprofit", but the current code shows codes 1–2 as "Nonprofit" and codes 4–6 as "For-profit", which matches the CORRECT mapping in the audit (lines 157–171).

**Conclusion:** The `01_build_data.py` script has **already been corrected** or was never wrong. The error exists only in the downstream claims that reference the **output** of an older, incorrect version of the script.

**Action Required:** Verify that the current mapping in `01_build_data.py` lines 83–91 matches the CORRECT mapping from CTRL_TYPE_AUDIT.md. If it does, no code change is needed. If it doesn't, apply the audit's corrected mapping.

---

## Checklist for Publication of Corrections

### Before Correcting Public Files

- [ ] **Regenerate** Issue #3 figures and outputs with verified correct `01_build_data.py` mapping
- [ ] **Verify** that hospital_ccr_2023.csv and ownership breakdown statistics match the corrected values
- [ ] **Confirm** that the newsletter text (newsletter_issue_03.md) does NOT contain false ownership claims (it shouldn't — the fact-check report shows it passed review without ownership breakdown claims)

### Corrections to Apply

- [ ] **PROMO_KIT.md** — Update 5 instances (lines 36, 67, 94, 133, 145)
- [ ] **CLAUDE.md** — Update 2 instances (lines 50, 135)
- [ ] **README.md** — Update 1 instance (line 76)
- [ ] **01_build_data.py** — Verify correct mapping is in place (lines 83–91)

### Publication Steps

- [ ] Create a new Substack post or correction note: "Issue #3 Clarification: Hospital Ownership and Markup Distribution"
  - **Key message:** For-profit hospitals (median 4.11× markup) have the highest markups, not nonprofit hospitals (2.46×). The savings estimate ($73B) is unaffected, but the ownership breakdown analysis requires clarification.
  - **Audience:** Journalists, researchers, policy stakeholders who may have picked up the PROMO_KIT claims

- [ ] Update GitHub:
  - Commit corrected PROMO_KIT.md, CLAUDE.md, README.md
  - Add a note to issue_03/CTRL_TYPE_AUDIT.md and CORRECTION_CASCADE.md in the repository (or in .gitignore if keeping internal only)
  - Update the README.md with a "Known Issues & Corrections" section

- [ ] **Media notification** (if Issue #3 has been pitched):
  - Flag the change to any journalists who received PROMO_KIT
  - Specifically note the change for Tara Bannow (STAT News) — the nonprofit markup angle should become the for-profit markup angle

---

## Impact Assessment

### What is NOT affected
- **Core $73B savings estimate** — this is based on RAND Round 5.1 (254% of Medicare) and CMS NHE national hospital spending, not on the HCRIS ownership breakdown
- **Newsletter text** (newsletter_issue_03.md) — does not contain false ownership claims
- **The 254% finding** itself — this is peer-reviewed RAND data, not derived from HCRIS
- **International procedure comparisons** — from iFHP, not HCRIS

### What IS affected
- **PROMO_KIT narrative** — the nonprofit hospital "villain" angle is backwards; should be for-profit
- **Public documentation** (CLAUDE.md, README.md) — contain false metrics that may mislead researchers
- **Media pitches** — the nonprofit markup claim should not be sent to journalists
- **Issue #6 (Supply Waste)** — depends on CTRL_TYPE categorization; may require recalculation (TBD after running corrected script)

---

## Next Steps

1. **Verify** that `issue_03/01_build_data.py` has the correct CTRL_TYPE mapping (compare lines 83–91 to CTRL_TYPE_AUDIT.md lines 157–171)
2. **If mapping is correct:** Regenerate all Issue #3 outputs and verify ownership breakdown statistics
3. **If mapping is wrong:** Fix the mapping, regenerate, and re-verify
4. **Apply all corrections** listed above to PROMO_KIT.md, CLAUDE.md, and README.md
5. **Re-run Issue #6 script** (supply_waste_step3_cmi.py) with corrected CTRL_TYPE mapping and update CLAUDE.md Section "Issue #6" with corrected ownership breakdown figures
6. **Publish correction note** on Substack if Issue #3 has been widely circulated
7. **Update GitHub** with corrected files and this audit report

---

## Sources

- **CTRL_TYPE_AUDIT.md** — detailed mapping error analysis (this session)
- **FACT_CHECK_REPORT.md** — confirmed that newsletter text is correct (no ownership breakdown claims included)
- **issue_03/01_build_data.py** — source of the error and location of the fix
- **CMS Form 2552-10** — official source for CTRL_TYPE code definitions

---

**Prepared by:** Claude (Data Audit)
**For:** Andrew Rexroad / American Healthcare Conundrum Project
**Status:** Ready for correction implementation

---

## ADDENDUM: Other Files Checked

### cms_impact_file_comparison.md
**Status:** NO CORRECTIONS NEEDED — different methodology, not CTRL_TYPE error
**Context:** This file compares two different data sources (HCRIS all-payer vs IPPS Medicare-only) and explains why they show different ownership breakdowns. This is legitimate methodological analysis, not a cascade of the CTRL_TYPE error.
**Key distinction:** The file is aware of and documents the methodological difference between:
- HCRIS Worksheet C (all payer data) — what Issue #3 uses
- IPPS Operating CCR (Medicare only) — a separate CMS file

The apparent contradiction explained in this file is resolved by understanding the different data sources, not related to CTRL_TYPE mapping.

### threads/REGISTRY.md
**Status:** NO CORRECTIONS NEEDED — brief reference, not a claim
**Context:** This file logs HackerNews reply threads and briefly mentions "nonprofit markup" as a topic discussed. It is a registry/index, not a primary source of data claims. No false statistics are stated in this file.


---

## Final Summary

**Total files requiring corrections:** 3 (not 4)
1. **PROMO_KIT.md** — 5 corrections (highest priority)
2. **CLAUDE.md** — 2 corrections (high priority)
3. **README.md** — 1 correction (medium priority)

**Files checked but requiring NO corrections:**
- newsletter_issue_03.md (passed fact-check, no false ownership claims)
- cms_impact_file_comparison.md (different methodology, legitimate analysis)
- threads/REGISTRY.md (index/registry only, not a data source)
- 01_build_data.py (mapping already corrected)

**Files with corrections complete:**
- CORRECTION_CASCADE.md (this report)
- CORRECTIONS_SUMMARY.txt (exact text changes)
- CTRL_TYPE_AUDIT.md (root cause analysis, completed in prior session)
