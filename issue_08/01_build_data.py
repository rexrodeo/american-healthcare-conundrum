#!/usr/bin/env python3
"""
Issue #8: The Denial Machine — Original Analysis Pipeline
The American Healthcare Conundrum

ORIGINAL ANALYSES (computed from raw federal/KFF data):
  - Analysis 1: MA Enrollment × Denial Rate → Wrongful Silent Denial Cost
    (CMS Monthly Enrollment + KFF MA Prior Auth Insurer data)
  - Analysis 2: ACA Marketplace Denial Reason Decomposition
    (KFF ACA Marketplace 2024 Working File, 2,540 plans)
  - Analysis 3: Prior Auth Trend & Excess Denials 2019-2024
    (KFF Historical Prior Auth data)

CURATED REFERENCE DATA (published sources, pending MLR PUF upgrade):
  - Component B: Vertical Integration Arbitrage (Health Affairs 2025)
  - Component D: MLR Gaming (pending CMS MLR PUF)
  - Component E: MA Risk Adjustment (OIG/MEDPAC)

Date: 2026-04-12
Data vintage: CMS enrollment March 2026, KFF data calendar year 2024
"""

import json
import pandas as pd
import numpy as np
import os
import sys
from pathlib import Path
from datetime import datetime

# ============================================================================
# CONFIGURATION & PATHS
# ============================================================================

SCRIPT_DIR = Path(__file__).parent
RAW_DATA_DIR = SCRIPT_DIR / "raw_data"
RESULTS_DIR = SCRIPT_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# Raw data file paths
KFF_MA_INSURER_PATH = RAW_DATA_DIR / "KFF_MA_PriorAuth_Insurer_2024.csv"
KFF_MA_HISTORICAL_PATH = RAW_DATA_DIR / "KFF_MA_PriorAuth_Historical_2019-2024.csv"
KFF_MA_JSON_PATH = RAW_DATA_DIR / "KFF_MA_PriorAuth_2024_Data.json"
ACA_EXCEL_PATH = RAW_DATA_DIR / "KFF_ACA_Marketplace_2024_Working_File.xlsx"

# CMS enrollment CSV — may be in a subdirectory from ZIP extraction or flat
CMS_ENROLLMENT_CANDIDATES = [
    RAW_DATA_DIR / "Monthly_Report_By_Plan_2026_03" / "Monthly_Report_By_Plan_2026_03.csv",
    RAW_DATA_DIR / "Monthly_Report_By_Plan_2026_03.csv",
]
CMS_ENROLLMENT_PATH = None
for p in CMS_ENROLLMENT_CANDIDATES:
    if p.exists():
        CMS_ENROLLMENT_PATH = p
        break

if CMS_ENROLLMENT_PATH is None:
    print("ERROR: CMS enrollment CSV not found. Tried:")
    for p in CMS_ENROLLMENT_CANDIDATES:
        print(f"  {p}")
    sys.exit(1)

# ============================================================================
# COST ASSUMPTIONS (documented, sourced)
# ============================================================================

# CMS NHE 2024: Total MA spending ~$462B (CMS Office of the Actuary)
# KFF 2024 MA enrollment: 33.0M (used for 2024 denominators)
# CMS Monthly Enrollment March 2026: 35.6M MA-only (used for current snapshot)
# Average MA spend per beneficiary: $462B / 33M = ~$14,000/year
# Average PA-targeted service cost: PA is disproportionately applied to
#   surgical, imaging, specialty referrals, and high-cost drugs.
#   Milliman 2023: average PA-targeted service cost $1,800-2,400
#   We use $1,500 (conservative), $2,000 (mid), $2,500 (aggressive)

PA_CLAIM_COST_CONSERVATIVE = 1_500
PA_CLAIM_COST_MID = 2_000
PA_CLAIM_COST_AGGRESSIVE = 2_500

# KFF aggregate 2024 MA PA data (for cross-validation)
KFF_TOTAL_PA_REQUESTS_2024 = 52_801_636
KFF_AGGREGATE_DENIAL_RATE_2024 = 0.077  # 7.7%
KFF_AGGREGATE_APPEAL_RATE = 0.115  # 11.5% of denials appealed
KFF_AGGREGATE_OVERTURN_RATE = 0.807  # 80.7% of appeals overturned
KFF_MA_ENROLLMENT_2024 = 33_000_000

print("=" * 80)
print("Issue #8: The Denial Machine — Original Analysis Pipeline")
print("=" * 80)

# ============================================================================
# STEP 0: Load CMS MA Enrollment (MA-only, filtered)
# ============================================================================

print("\n[STEP 0] Loading CMS MA Enrollment Data (MA-only filter)")
print("-" * 60)

cms_raw = pd.read_csv(CMS_ENROLLMENT_PATH, encoding='latin-1', on_bad_lines='skip')
print(f"  Raw CMS records: {len(cms_raw):,}")

# Convert enrollment to numeric (suppress "*" values per HIPAA)
cms_raw['Enrollment_num'] = pd.to_numeric(cms_raw['Enrollment'], errors='coerce')

# CRITICAL: Filter to Medicare Advantage plans only
# Exclude: standalone PDPs, PACE, Cost Plans, Employer-only PDPs
MA_PLAN_TYPES = ['HMO', 'HMOPOS', 'Local PPO', 'Regional PPO', 'PFFS', 'MSA', 'HMO/HMOPOS']
ma_plans = cms_raw[cms_raw['Plan Type'].isin(MA_PLAN_TYPES)].copy()
print(f"  MA-only plans: {len(ma_plans):,}")
print(f"  Total MA enrollment (March 2026): {ma_plans['Enrollment_num'].sum():,.0f}")

# Map parent organizations to KFF insurer names
PARENT_KEYWORDS = {
    'UnitedHealth Group': ['UNITEDHEALTH', 'UNITED HEALTH', 'UNITEDHEALTHCARE'],
    'Humana Inc.': ['HUMANA'],
    'CVS Health Corporation': ['CVS', 'AETNA'],
    'Elevance Health': ['ELEVANCE', 'ANTHEM', 'WELLPOINT'],
    'Kaiser Foundation Health Plan': ['KAISER'],
    'Centene Corporation': ['CENTENE', 'WELLCARE'],
}

def map_parent_to_insurer(parent_org):
    """Map CMS Parent Organization to KFF insurer name."""
    if pd.isna(parent_org):
        return 'Other Insurers'
    pu = parent_org.upper()
    for insurer, keywords in PARENT_KEYWORDS.items():
        for kw in keywords:
            if kw in pu:
                return insurer
    return 'Other Insurers'

ma_plans['Insurer'] = ma_plans['Parent Organization'].apply(map_parent_to_insurer)

# Aggregate MA enrollment by insurer
ma_enrollment_by_insurer = ma_plans.groupby('Insurer').agg(
    enrollment=('Enrollment_num', 'sum'),
    plan_count=('Enrollment_num', 'count')
).reset_index().sort_values('enrollment', ascending=False)

print("\n  MA Enrollment by Insurer (March 2026, from CMS data):")
for _, row in ma_enrollment_by_insurer.iterrows():
    print(f"    {row['Insurer']}: {row['enrollment']:,.0f} ({row['plan_count']} plans)")
total_ma = ma_enrollment_by_insurer['enrollment'].sum()
print(f"    TOTAL: {total_ma:,.0f}")

# ============================================================================
# ANALYSIS 1: MA Wrongful Silent Denial Cost (ORIGINAL)
# ============================================================================

print("\n[ANALYSIS 1] MA Wrongful Silent Denial Cost (ORIGINAL)")
print("=" * 80)
print("  Method: CMS enrollment × KFF PA requests/enrollee × denial rate")
print("          × (1 - appeal rate) × overturn rate = wrongful silent denials")
print("          × PA-targeted service cost = suppressed care value")

# Load KFF insurer-level denial data
insurer_kff = pd.read_csv(KFF_MA_INSURER_PATH)
print(f"\n  Loaded {len(insurer_kff)} insurers from KFF MA Prior Auth data")

# Merge with real CMS enrollment
analysis1 = insurer_kff.merge(
    ma_enrollment_by_insurer[['Insurer', 'enrollment']].rename(columns={'Insurer': 'insurer', 'enrollment': 'cms_ma_enrollment'}),
    on='insurer',
    how='left'
)

# For "Other Insurers", use the CMS "Other" bucket
other_enrollment = ma_enrollment_by_insurer.loc[
    ma_enrollment_by_insurer['Insurer'] == 'Other Insurers', 'enrollment'
]
if len(other_enrollment) > 0:
    analysis1.loc[analysis1['insurer'] == 'Other Insurers', 'cms_ma_enrollment'] = other_enrollment.values[0]

# Fill any remaining NaN with 0
analysis1['cms_ma_enrollment'] = analysis1['cms_ma_enrollment'].fillna(0)

# Compute insurer-by-insurer denial costs
analysis1['total_pa_requests'] = analysis1['cms_ma_enrollment'] * analysis1['requests_per_enrollee']
analysis1['total_denials'] = analysis1['total_pa_requests'] * (analysis1['denial_rate'] / 100.0)
analysis1['appealed_denials'] = analysis1['total_denials'] * (analysis1['appeal_rate'] / 100.0)
analysis1['silent_denials'] = analysis1['total_denials'] - analysis1['appealed_denials']

# Key assumption: if X% of appealed denials are overturned (wrongful),
# approximately X% of silent denials were also wrongful.
# This is conservative: silent denials likely include MORE wrongful ones
# (patients who couldn't navigate the appeals process).
analysis1['wrongful_silent_denials'] = analysis1['silent_denials'] * (analysis1['appeals_overturned'] / 100.0)

# Dollar value of suppressed care
analysis1['cost_conservative'] = analysis1['wrongful_silent_denials'] * PA_CLAIM_COST_CONSERVATIVE
analysis1['cost_mid'] = analysis1['wrongful_silent_denials'] * PA_CLAIM_COST_MID
analysis1['cost_aggressive'] = analysis1['wrongful_silent_denials'] * PA_CLAIM_COST_AGGRESSIVE

# Sort by mid cost descending
analysis1 = analysis1.sort_values('cost_mid', ascending=False)

# Compute totals
total_row = pd.DataFrame([{
    'insurer': 'TOTAL',
    'cms_ma_enrollment': analysis1['cms_ma_enrollment'].sum(),
    'requests_per_enrollee': np.nan,
    'denial_rate': np.nan,
    'appeal_rate': np.nan,
    'appeals_overturned': np.nan,
    'total_pa_requests': analysis1['total_pa_requests'].sum(),
    'total_denials': analysis1['total_denials'].sum(),
    'appealed_denials': analysis1['appealed_denials'].sum(),
    'silent_denials': analysis1['silent_denials'].sum(),
    'wrongful_silent_denials': analysis1['wrongful_silent_denials'].sum(),
    'cost_conservative': analysis1['cost_conservative'].sum(),
    'cost_mid': analysis1['cost_mid'].sum(),
    'cost_aggressive': analysis1['cost_aggressive'].sum(),
}])
analysis1_with_total = pd.concat([analysis1, total_row], ignore_index=True)

# Save
a1_path = RESULTS_DIR / "analysis1_silent_denials.csv"
analysis1_with_total.to_csv(a1_path, index=False, float_format='%.0f')

# Print results
print("\n  Insurer-by-Insurer Wrongful Silent Denial Cost:")
for _, row in analysis1.iterrows():
    print(f"    {row['insurer']}: {row['cms_ma_enrollment']:,.0f} enrollees, "
          f"{row['total_denials']:,.0f} denials, "
          f"{row['wrongful_silent_denials']:,.0f} wrongful silent, "
          f"${row['cost_mid']/1e9:.2f}B suppressed care")

totals = analysis1_with_total[analysis1_with_total['insurer'] == 'TOTAL'].iloc[0]
print(f"\n  TOTALS:")
print(f"    MA enrollment (from CMS): {totals['cms_ma_enrollment']:,.0f}")
print(f"    Total PA requests: {totals['total_pa_requests']:,.0f}")
print(f"    Total denials: {totals['total_denials']:,.0f}")
print(f"    Silent denials (never appealed): {totals['silent_denials']:,.0f}")
print(f"    Wrongful silent denials: {totals['wrongful_silent_denials']:,.0f}")
print(f"    Suppressed care (conservative): ${totals['cost_conservative']/1e9:.2f}B")
print(f"    Suppressed care (mid): ${totals['cost_mid']/1e9:.2f}B")
print(f"    Suppressed care (aggressive): ${totals['cost_aggressive']/1e9:.2f}B")

# Cross-validation against KFF aggregates
print(f"\n  Cross-validation:")
print(f"    Our total PA requests: {totals['total_pa_requests']:,.0f}")
print(f"    KFF reported total: {KFF_TOTAL_PA_REQUESTS_2024:,}")
ratio = totals['total_pa_requests'] / KFF_TOTAL_PA_REQUESTS_2024
print(f"    Ratio: {ratio:.2f}x (>1 means our CMS enrollment is slightly higher than KFF's 2024 base)")

# ============================================================================
# ANALYSIS 2: ACA Marketplace Denial Reason Decomposition (ORIGINAL)
# ============================================================================

print("\n[ANALYSIS 2] ACA Marketplace Denial Reason Decomposition (ORIGINAL)")
print("=" * 80)

# Load plan-level ACA data
plans_df = pd.read_excel(ACA_EXCEL_PATH, sheet_name='Medical Plans')
print(f"  Loaded {len(plans_df)} plans from ACA Marketplace data")

# Clean numeric columns
for col in plans_df.columns:
    if 'Claims' in col or 'Denied' in col or 'Appeals' in col or 'Enrollment' in col:
        plans_df[col] = pd.to_numeric(plans_df[col], errors='coerce')

plans_with_data = plans_df[plans_df['Plan_Claims_Denied'].fillna(0) > 0].copy()
print(f"  Plans with denial data: {len(plans_with_data)}")

total_claims = plans_with_data['Plan_Claims_Received'].sum()
total_denials = plans_with_data['Plan_Claims_Denied'].sum()
overall_denial_rate = total_denials / total_claims * 100 if total_claims > 0 else 0

print(f"  Total claims: {total_claims:,.0f}")
print(f"  Total denials: {total_denials:,.0f}")
print(f"  Overall denial rate: {overall_denial_rate:.1f}%")

# Denial reason columns (non-overlapping set — exclude BH/non-BH subcategories
# since "Not Medically Necessary" is the parent that includes both)
DENIAL_REASON_COLS = {
    'Referral Required': 'Plan_Claims_Denied_Due_To_Referral_Required',
    'Out Of Network': 'Plan_Claims_Denied_Due_To_Out_Of_Network',
    'Services Excluded': 'Plan_Claims_Denied_Due_To_Services_Excluded',
    'Medical Necessity': 'Plan_Claims_Denied_Due_To_Not_Medically_Necessary',
    'Benefit Limit Reached': 'Plan_Claims_Denied_Due_To_Enrollee_Benefit_Limit_Reached',
    'Member Not Covered': 'Plan_Claims_Denied_Due_To_Member_Not_Covered',
    'Investigational/Cosmetic': 'Plan_Claims_Denied_Due_To_Investigational_Experimental_Cosmetic_Procedure',
    'Administrative Reason': 'Plan_Claims_Denied_Due_To_Administrative_Reason',
    'Other': 'Plan_Claims_Denied_Due_To_Other',
}

# BH subcategories (for parity analysis, not added to totals)
BH_COLS = {
    'Medical Necessity (excl BH)': 'Plan_Claims_Denied_Due_To_Not_Medically_Necessary_Excluding_Behavioral_Health',
    'Medical Necessity (BH only)': 'Plan_Claims_Denied_Due_To_Not_Medically_Necessary_Only_Behavioral_Health',
}

reason_results = []
for reason_name, col_name in DENIAL_REASON_COLS.items():
    count = plans_with_data[col_name].fillna(0).sum()
    pct = count / total_denials * 100 if total_denials > 0 else 0
    reason_results.append({
        'reason': reason_name,
        'denial_count': int(count),
        'pct_of_all_denials': round(pct, 2),
    })

reason_df = pd.DataFrame(reason_results).sort_values('denial_count', ascending=False)

# Categorize as Administrative vs Clinical
# ADMINISTRATIVE: barriers that aren't clinical judgments
#   - Referral Required (procedural hoop)
#   - Administrative Reason (paperwork/coding)
#   - Other (unspecified — typically administrative)
#   - Member Not Covered (eligibility error)
# CLINICAL: actual medical judgment
#   - Medical Necessity
#   - Services Excluded (coverage design)
#   - Investigational/Cosmetic
#   - Benefit Limit Reached
# OUT OF NETWORK: separate category (network design)

ADMIN_REASONS = ['Referral Required', 'Administrative Reason', 'Other', 'Member Not Covered']
CLINICAL_REASONS = ['Medical Necessity', 'Services Excluded', 'Investigational/Cosmetic', 'Benefit Limit Reached']
NETWORK_REASONS = ['Out Of Network']

admin_count = reason_df[reason_df['reason'].isin(ADMIN_REASONS)]['denial_count'].sum()
clinical_count = reason_df[reason_df['reason'].isin(CLINICAL_REASONS)]['denial_count'].sum()
network_count = reason_df[reason_df['reason'].isin(NETWORK_REASONS)]['denial_count'].sum()

coded_total = admin_count + clinical_count + network_count
admin_pct = admin_count / coded_total * 100 if coded_total > 0 else 0
clinical_pct = clinical_count / coded_total * 100 if coded_total > 0 else 0
network_pct = network_count / coded_total * 100 if coded_total > 0 else 0

print(f"\n  Denial Reason Breakdown:")
for _, row in reason_df.iterrows():
    print(f"    {row['reason']}: {row['denial_count']:,.0f} ({row['pct_of_all_denials']:.1f}%)")

print(f"\n  Category Summary:")
print(f"    Administrative/Procedural: {admin_count:,.0f} ({admin_pct:.1f}% of coded)")
print(f"    Clinical/Coverage: {clinical_count:,.0f} ({clinical_pct:.1f}% of coded)")
print(f"    Network Design: {network_count:,.0f} ({network_pct:.1f}% of coded)")

# Behavioral health parity analysis
bh_med_nec = plans_with_data['Plan_Claims_Denied_Due_To_Not_Medically_Necessary_Only_Behavioral_Health'].fillna(0).sum()
non_bh_med_nec = plans_with_data['Plan_Claims_Denied_Due_To_Not_Medically_Necessary_Excluding_Behavioral_Health'].fillna(0).sum()
total_med_nec = bh_med_nec + non_bh_med_nec
bh_share = bh_med_nec / total_med_nec * 100 if total_med_nec > 0 else 0
print(f"\n  Behavioral Health Parity:")
print(f"    BH medical necessity denials: {bh_med_nec:,.0f} ({bh_share:.1f}% of med nec)")
print(f"    Non-BH medical necessity denials: {non_bh_med_nec:,.0f} ({100-bh_share:.1f}%)")

# Save denial reason analysis
a2_path = RESULTS_DIR / "analysis2_denial_reasons.csv"
reason_df.to_csv(a2_path, index=False)

# Save category summary
cat_df = pd.DataFrame([
    {'category': 'Administrative/Procedural', 'denial_count': int(admin_count),
     'pct_of_coded': round(admin_pct, 1),
     'includes': 'Referral Required, Administrative Reason, Other, Member Not Covered'},
    {'category': 'Clinical/Coverage', 'denial_count': int(clinical_count),
     'pct_of_coded': round(clinical_pct, 1),
     'includes': 'Medical Necessity, Services Excluded, Investigational/Cosmetic, Benefit Limit'},
    {'category': 'Network Design', 'denial_count': int(network_count),
     'pct_of_coded': round(network_pct, 1),
     'includes': 'Out Of Network'},
])
cat_path = RESULTS_DIR / "analysis2_denial_categories.csv"
cat_df.to_csv(cat_path, index=False)

# ============================================================================
# ANALYSIS 2B: ACA Issuer-Level Denial Rate Variation (ORIGINAL)
# ============================================================================

print("\n[ANALYSIS 2B] ACA Issuer-Level Denial Rate Variation")
print("-" * 60)

issuers_df = pd.read_excel(ACA_EXCEL_PATH, sheet_name='Medical Issuers')
for col in ['Claims_Received', 'Claims_Denied', 'Denial_Rate',
            'Internal_Appeals_Filed', 'Internal_Appeals_Rate',
            'Number_Internal_Appeals_Overturned', 'Internal_Appeals_Overturn_Rate']:
    if col in issuers_df.columns:
        issuers_df[col] = pd.to_numeric(issuers_df[col], errors='coerce')

# Filter to issuers with meaningful volume (>5,000 claims)
issuers_active = issuers_df[issuers_df['Claims_Received'] > 5000].copy()
issuers_active = issuers_active.sort_values('Denial_Rate', ascending=False)

print(f"  Active issuers (>5K claims): {len(issuers_active)}")
# Note: KFF stores Denial_Rate as a proportion (0.19 = 19%), not a percentage
# Multiply by 100 for display
print(f"  Denial rate range: {issuers_active['Denial_Rate'].min()*100:.1f}% - {issuers_active['Denial_Rate'].max()*100:.1f}%")
print(f"  Median denial rate: {issuers_active['Denial_Rate'].median()*100:.1f}%")

# Show top and bottom 5
print(f"\n  TOP 5 highest denial rates:")
for _, r in issuers_active.head(5).iterrows():
    print(f"    {r['Issuer_Name']} ({r['State']}): {r['Denial_Rate']*100:.1f}% "
          f"({r['Claims_Denied']:,.0f}/{r['Claims_Received']:,.0f})")
print(f"\n  BOTTOM 5 lowest denial rates:")
for _, r in issuers_active.tail(5).iterrows():
    print(f"    {r['Issuer_Name']} ({r['State']}): {r['Denial_Rate']*100:.1f}% "
          f"({r['Claims_Denied']:,.0f}/{r['Claims_Received']:,.0f})")

# If every insurer matched the lowest-quartile denial rate, how many fewer denials?
q25_rate = issuers_active['Denial_Rate'].quantile(0.25)
# Denial_Rate is already a proportion (0.19 = 19%), so no need to divide by 100
issuers_active['excess_denials_vs_q25'] = (
    (issuers_active['Denial_Rate'] - q25_rate).clip(lower=0) * issuers_active['Claims_Received']
)
total_excess_vs_q25 = issuers_active['excess_denials_vs_q25'].sum()
print(f"\n  If all issuers matched Q25 denial rate ({q25_rate*100:.1f}%):")
print(f"    Excess denials above Q25: {total_excess_vs_q25:,.0f}")

a2b_path = RESULTS_DIR / "analysis2_insurer_variation.csv"
issuers_active[['State', 'Issuer_Name', 'Parent_Company', 'Claims_Received',
                'Claims_Denied', 'Denial_Rate', 'Internal_Appeals_Rate',
                'Internal_Appeals_Overturn_Rate']].head(30).to_csv(a2b_path, index=False)

# ============================================================================
# ANALYSIS 3: Prior Auth Trend & Excess Denials (ORIGINAL)
# ============================================================================

print("\n[ANALYSIS 3] Prior Auth Trend & Excess Denials 2019-2024 (ORIGINAL)")
print("=" * 80)

hist_df = pd.read_csv(KFF_MA_HISTORICAL_PATH)
print(f"  Loaded {len(hist_df)} years of historical data")

# Use 2019 as baseline (pre-pandemic, pre-AI)
baseline_rate = hist_df[hist_df['year'] == 2019]['denial_rate'].values[0] / 100.0

hist_df['actual_denials'] = hist_df['requests'] * (hist_df['denial_rate'] / 100.0)
hist_df['baseline_denials'] = hist_df['requests'] * baseline_rate
hist_df['excess_denials'] = hist_df['actual_denials'] - hist_df['baseline_denials']
hist_df['excess_cost_mid'] = hist_df['excess_denials'] * PA_CLAIM_COST_MID

print(f"\n  Year-by-Year Trend:")
for _, r in hist_df.iterrows():
    excess_label = f"+{r['excess_denials']:,.0f}" if r['excess_denials'] > 0 else f"{r['excess_denials']:,.0f}"
    print(f"    {int(r['year'])}: {r['requests']:,.0f} requests, "
          f"{r['denial_rate']:.1f}% denial rate, "
          f"{r['actual_denials']:,.0f} denials ({excess_label} excess)")

cumulative_excess = hist_df[hist_df['excess_denials'] > 0]['excess_denials'].sum()
latest = hist_df[hist_df['year'] == 2024].iloc[0]
print(f"\n  2024 excess denials (vs 2019 baseline): {latest['excess_denials']:,.0f}")
print(f"  Cumulative excess denials (2020-2024): {cumulative_excess:,.0f}")
print(f"  Denial rate increase: {baseline_rate*100:.1f}% → {latest['denial_rate']:.1f}% (+{latest['denial_rate']-baseline_rate*100:.1f} pp)")

a3_path = RESULTS_DIR / "analysis3_trend_excess_denials.csv"
hist_df[['year', 'requests', 'denial_rate', 'requests_per_enrollee',
         'actual_denials', 'baseline_denials', 'excess_denials', 'excess_cost_mid']].to_csv(a3_path, index=False)

# ============================================================================
# CURATED COMPONENTS (published sources, pending upgrade)
# ============================================================================

print("\n[CURATED] Components B, D, E (published sources)")
print("=" * 80)

# Component B: Vertical Integration Arbitrage
# Source: Health Affairs Nov 2025 — Optum-owned practices receive 17% higher
#   payments (61% in concentrated markets)
# CMS MA spending: $462B. Estimated 25-35% routed through insurer-owned providers.
# $462B × 0.30 × 0.17 = $23.6B in excess payments
# Conservative: 20% owned × 10% premium = $9.2B
# Aggressive: 35% owned × 17% premium = $27.5B
VI_CONSERVATIVE_B = 9.2
VI_MID_B = 15.7  # 25% owned × 13.5% avg premium
VI_AGGRESSIVE_B = 23.6

# Component D: MLR Gaming
# Mechanism: QI expense reclassification to inflate numerator
# Pending CMS MLR PUF analysis — placeholder from published estimates
# FTC: $7.3B in specialty drug markups (PBM overlap, partial)
# State AG findings: 2-5% of premium revenue reclassified
# Total US health insurance premiums: ~$1.3T
# If 1-3% is reclassified: $13-39B in inflated QI claims
# Conservative estimate of extractable gaming: $5-15B
MLR_CONSERVATIVE_B = 5.0
MLR_MID_B = 10.0
MLR_AGGRESSIVE_B = 15.0

# Component E: MA Risk Adjustment Overpayment
# MEDPAC 2024: MA plans paid 106% of expected costs (6% overpayment)
# CMS MA spending: $462B × 0.06 = $27.7B in excess payments
# But most of this is structural (coding intensity), not gaming
# Recoverable portion (documented upcoding): 1-3% = $4.6-13.9B
# Conservative: $4.6B
MA_RISK_CONSERVATIVE_B = 4.6
MA_RISK_MID_B = 9.2
MA_RISK_AGGRESSIVE_B = 13.9

curated_df = pd.DataFrame([
    {'component': 'B_vertical_integration', 'type': 'CURATED',
     'source': 'Health Affairs Nov 2025, CMS NHE',
     'conservative_B': VI_CONSERVATIVE_B, 'mid_B': VI_MID_B, 'aggressive_B': VI_AGGRESSIVE_B,
     'mechanism': 'Insurer-owned provider 17% payment premium'},
    {'component': 'D_mlr_gaming', 'type': 'CURATED (pending MLR PUF)',
     'source': 'FTC reports, state AG audits',
     'conservative_B': MLR_CONSERVATIVE_B, 'mid_B': MLR_MID_B, 'aggressive_B': MLR_AGGRESSIVE_B,
     'mechanism': 'QI expense reclassification to meet MLR floor'},
    {'component': 'E_ma_risk_adjustment', 'type': 'CURATED',
     'source': 'MEDPAC 2024, OIG audits',
     'conservative_B': MA_RISK_CONSERVATIVE_B, 'mid_B': MA_RISK_MID_B, 'aggressive_B': MA_RISK_AGGRESSIVE_B,
     'mechanism': 'Coding intensity / risk score inflation'},
])

a5_path = RESULTS_DIR / "curated_components.csv"
curated_df.to_csv(a5_path, index=False)

print(f"  Component B (VI Arbitrage): ${VI_CONSERVATIVE_B}B - ${VI_AGGRESSIVE_B}B")
print(f"  Component D (MLR Gaming): ${MLR_CONSERVATIVE_B}B - ${MLR_AGGRESSIVE_B}B")
print(f"  Component E (MA Risk Adj): ${MA_RISK_CONSERVATIVE_B}B - ${MA_RISK_AGGRESSIVE_B}B")

# ============================================================================
# CONSOLIDATED SUMMARY
# ============================================================================

print("\n[CONSOLIDATED SUMMARY]")
print("=" * 80)

# Component A: Wrongful silent denial cost (from Analysis 1)
a_conservative = totals['cost_conservative'] / 1e9
a_mid = totals['cost_mid'] / 1e9
a_aggressive = totals['cost_aggressive'] / 1e9

# Total across all components
total_conservative = a_conservative + VI_CONSERVATIVE_B + MLR_CONSERVATIVE_B + MA_RISK_CONSERVATIVE_B
total_mid = a_mid + VI_MID_B + MLR_MID_B + MA_RISK_MID_B
total_aggressive = a_aggressive + VI_AGGRESSIVE_B + MLR_AGGRESSIVE_B + MA_RISK_AGGRESSIVE_B

print(f"\n  Component A (Care Suppression - ORIGINAL): ${a_conservative:.1f}B - ${a_aggressive:.1f}B")
print(f"  Component B (VI Arbitrage - CURATED):       ${VI_CONSERVATIVE_B:.1f}B - ${VI_AGGRESSIVE_B:.1f}B")
print(f"  Component D (MLR Gaming - CURATED):         ${MLR_CONSERVATIVE_B:.1f}B - ${MLR_AGGRESSIVE_B:.1f}B")
print(f"  Component E (MA Risk Adj - CURATED):        ${MA_RISK_CONSERVATIVE_B:.1f}B - ${MA_RISK_AGGRESSIVE_B:.1f}B")
print(f"\n  TOTAL CONSERVATIVE: ${total_conservative:.1f}B")
print(f"  TOTAL MID:          ${total_mid:.1f}B")
print(f"  TOTAL AGGRESSIVE:   ${total_aggressive:.1f}B")

# Build summary JSON
summary = {
    'metadata': {
        'issue': 8,
        'title': 'The Denial Machine: Insurer Profit Extraction',
        'publication': 'The American Healthcare Conundrum',
        'analysis_date': datetime.now().isoformat(),
        'cms_enrollment_vintage': 'March 2026',
        'kff_data_vintage': 'Calendar Year 2024',
    },
    'data_sources': {
        'cms_ma_enrollment': str(CMS_ENROLLMENT_PATH),
        'kff_ma_prior_auth': str(KFF_MA_INSURER_PATH),
        'kff_ma_historical': str(KFF_MA_HISTORICAL_PATH),
        'kff_aca_marketplace': str(ACA_EXCEL_PATH),
    },
    'component_A_care_suppression': {
        'type': 'ORIGINAL',
        'method': 'CMS MA enrollment × KFF PA requests/enrollee × denial rate × (1-appeal rate) × overturn rate × PA service cost',
        'cms_ma_enrollment': int(totals['cms_ma_enrollment']),
        'total_pa_requests': int(totals['total_pa_requests']),
        'total_denials': int(totals['total_denials']),
        'silent_denials': int(totals['silent_denials']),
        'wrongful_silent_denials': int(totals['wrongful_silent_denials']),
        'conservative_B': round(a_conservative, 2),
        'mid_B': round(a_mid, 2),
        'aggressive_B': round(a_aggressive, 2),
        'pa_claim_cost_range': [PA_CLAIM_COST_CONSERVATIVE, PA_CLAIM_COST_MID, PA_CLAIM_COST_AGGRESSIVE],
    },
    'analysis_2_denial_reasons': {
        'type': 'ORIGINAL',
        'total_aca_claims': int(total_claims),
        'total_aca_denials': int(total_denials),
        'overall_denial_rate_pct': round(overall_denial_rate, 1),
        'administrative_pct_of_coded': round(admin_pct, 1),
        'clinical_pct_of_coded': round(clinical_pct, 1),
        'network_pct_of_coded': round(network_pct, 1),
        'bh_medical_necessity_denials': int(bh_med_nec),
        'non_bh_medical_necessity_denials': int(non_bh_med_nec),
        'bh_share_of_med_nec_pct': round(bh_share, 1),
        'aca_issuer_denial_rate_range': f"{issuers_active['Denial_Rate'].min()*100:.1f}% - {issuers_active['Denial_Rate'].max()*100:.1f}%",
        'aca_issuer_denial_rate_median': round(issuers_active['Denial_Rate'].median()*100, 1),
    },
    'analysis_3_trend': {
        'type': 'ORIGINAL',
        'baseline_year': 2019,
        'baseline_denial_rate_pct': round(baseline_rate * 100, 1),
        'latest_denial_rate_pct': round(latest['denial_rate'], 1),
        'rate_increase_pp': round(latest['denial_rate'] - baseline_rate * 100, 1),
        'excess_denials_2024': int(latest['excess_denials']),
        'cumulative_excess_2020_2024': int(cumulative_excess),
    },
    'component_B_vertical_integration': {
        'type': 'CURATED', 'source': 'Health Affairs Nov 2025',
        'conservative_B': VI_CONSERVATIVE_B, 'mid_B': VI_MID_B, 'aggressive_B': VI_AGGRESSIVE_B,
    },
    'component_D_mlr_gaming': {
        'type': 'CURATED (pending MLR PUF)',
        'conservative_B': MLR_CONSERVATIVE_B, 'mid_B': MLR_MID_B, 'aggressive_B': MLR_AGGRESSIVE_B,
    },
    'component_E_ma_risk_adjustment': {
        'type': 'CURATED', 'source': 'MEDPAC 2024, OIG',
        'conservative_B': MA_RISK_CONSERVATIVE_B, 'mid_B': MA_RISK_MID_B, 'aggressive_B': MA_RISK_AGGRESSIVE_B,
    },
    'consolidated': {
        'conservative_B': round(total_conservative, 1),
        'mid_B': round(total_mid, 1),
        'aggressive_B': round(total_aggressive, 1),
        'note': 'Component A is ORIGINAL (CMS + KFF data). Components B/D/E are CURATED (pending MLR PUF and APCD upgrades).',
    },
    'cross_validation': {
        'our_total_pa_requests': int(totals['total_pa_requests']),
        'kff_reported_total': KFF_TOTAL_PA_REQUESTS_2024,
        'request_ratio': round(float(totals['total_pa_requests'] / KFF_TOTAL_PA_REQUESTS_2024), 3),
        'our_ma_enrollment': int(totals['cms_ma_enrollment']),
        'kff_ma_enrollment': KFF_MA_ENROLLMENT_2024,
        'enrollment_ratio': round(float(totals['cms_ma_enrollment'] / KFF_MA_ENROLLMENT_2024), 3),
        'note': 'Enrollment ratio >1.0 expected: CMS March 2026 vs KFF 2024 base. MA growing ~5%/year.',
    },
}

summary_path = RESULTS_DIR / "issue_08_summary_v3.json"
with open(summary_path, 'w') as f:
    json.dump(summary, f, indent=2)

print(f"\n  Saved summary to {summary_path}")

# ============================================================================
# OUTPUT MANIFEST
# ============================================================================

print("\n" + "=" * 80)
print("OUTPUT FILES:")
print("=" * 80)
outputs = [
    (a1_path, "Analysis 1: Insurer-by-insurer wrongful silent denial costs"),
    (a2_path, "Analysis 2: Denial reason decomposition (9 categories)"),
    (cat_path, "Analysis 2: Administrative vs Clinical category summary"),
    (a2b_path, "Analysis 2B: ACA issuer denial rate ranking (top 30)"),
    (a3_path, "Analysis 3: Prior auth trend & excess denials 2019-2024"),
    (a5_path, "Curated: Components B, D, E (pending upgrade)"),
    (summary_path, "Consolidated summary (JSON)"),
]
for path, desc in outputs:
    size = path.stat().st_size if path.exists() else 0
    print(f"  {path.name} ({size:,} bytes) — {desc}")

print(f"\nAll analyses complete. Run time: {datetime.now().isoformat()}")
