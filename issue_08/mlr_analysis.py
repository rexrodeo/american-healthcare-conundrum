#!/usr/bin/env python3
"""
MLR Public Use File Analysis for Issue #8: The Denial Machine
Analyzes CMS Medical Loss Ratio data 2019-2024

Author: AHC Data Synthesis
Date: 2026-04-13
"""

import pandas as pd
import numpy as np
import json
import os
from pathlib import Path
from collections import defaultdict
import warnings

warnings.filterwarnings('ignore')

# Configuration
DATA_BASE_PATH = Path('/sessions/loving-compassionate-clarke/mnt/healthcare/issue_08/raw_data/mlr/extracted')
OUTPUT_PATH = Path('/sessions/loving-compassionate-clarke/mnt/healthcare/issue_08/results')
YEARS = [2024, 2023, 2022, 2021, 2020, 2019]
BIG_5 = ['UnitedHealth', 'Elevance', 'Anthem', 'CVS', 'Aetna', 'Cigna', 'Humana']

OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

def normalize_column_name(col):
    """Normalize column names to lowercase."""
    return col.lower()

def load_part1_2(year):
    """Load Part1_2_Summary_Data file."""
    path = DATA_BASE_PATH / str(year) / 'Part1_2_Summary_Data_Premium_Claims.csv'

    try:
        df = pd.read_csv(path, dtype={'mr_submission_template_id': 'int64'}, low_memory=False)
        # Normalize column names to lowercase
        df.columns = [col.lower() for col in df.columns]
        return df
    except Exception as e:
        print(f"Error loading Part1_2 for {year}: {e}")
        return None

def load_part3(year):
    """Load Part3_MLR_Rebate_Calculation file."""
    path = DATA_BASE_PATH / str(year) / 'Part3_MLR_Rebate_Calculation.csv'

    try:
        df = pd.read_csv(path, dtype={'mr_submission_template_id': 'int64'}, low_memory=False)
        df.columns = [col.lower() for col in df.columns]
        return df
    except Exception as e:
        print(f"Error loading Part3 for {year}: {e}")
        return None

def load_header_file(year):
    """Load company header file."""
    path = DATA_BASE_PATH / str(year) / 'MR_Submission_Template_Header.csv'

    try:
        df = pd.read_csv(path, low_memory=False)
        df.columns = [col.lower() for col in df.columns]
        return df
    except Exception as e:
        print(f"Error loading header for {year}: {e}")
        return None

def get_market_segment_cols(df):
    """Find market segment columns dynamically."""
    cols = [c for c in df.columns if 'yearly' in c.lower()]
    # Filter to main segments (exclude q1, py, cy variants for aggregation)
    main_cols = [c for c in cols if '_py' not in c.lower() and '_q1' not in c.lower()
                 and '_cy' not in c.lower() and 'deferred' not in c.lower()]
    return main_cols

def safe_sum_cols(df, cols, row_code_col='row_lookup_code'):
    """Safely sum values across columns for a given row code."""
    result = defaultdict(float)

    for _, row in df.iterrows():
        row_code = row.get(row_code_col, '')
        if pd.isna(row_code):
            continue

        # Convert row_code to uppercase for matching
        row_code_upper = str(row_code).upper()

        for col in cols:
            val = row.get(col, 0)
            if pd.notna(val) and val != '':
                try:
                    result[row_code_upper] += float(val)
                except (ValueError, TypeError):
                    pass

    return result

def calculate_mlr_time_series():
    """Analysis A: MLR Time Series (2019-2024)."""

    print("\n" + "="*80)
    print("ANALYSIS A: MLR TIME SERIES (2019-2024)")
    print("="*80)

    time_series = []

    for year in YEARS:
        print(f"\nProcessing year {year}...", end=' ', flush=True)

        part1_2 = load_part1_2(year)
        part3 = load_part3(year)

        if part1_2 is None or part3 is None:
            print("SKIP (missing files)")
            continue

        # Get market segment columns
        market_cols = get_market_segment_cols(part1_2)
        if not market_cols:
            print("SKIP (no market segment columns found)")
            continue

        # Aggregate key metrics
        metrics = safe_sum_cols(part1_2, market_cols)

        total_premium = metrics.get('TOTAL_DIRECT_PREMIUM_EARNED', 0)
        total_claims = metrics.get('TOTAL_INCURRED_CLAIMS_PT1', 0)
        pharma_rebates = metrics.get('PHARMACEUTICAL_REBATES', 0)

        # Admin expense components
        admin_cost_contain = metrics.get('COST_CONTAINMENT_EXP_NOT_INCL', 0)
        admin_claims_adj = metrics.get('ALL_OTHER_CLAIMS_ADJ_EXPENSES', 0)
        admin_sales = metrics.get('DIR_SALES_SALARIES_AND_BENEFITS', 0)
        admin_broker = metrics.get('AGNTS_AND_BROKERS_FEES_COMMS', 0)
        admin_other = metrics.get('OTHER_GENERAL_AND_ADM_EXPENSES', 0)

        total_admin = admin_cost_contain + admin_claims_adj + admin_sales + admin_broker + admin_other

        # Calculate ratios
        if total_premium > 0:
            medical_loss_ratio = (total_claims / total_premium) * 100
            admin_ratio = (total_admin / total_premium) * 100
        else:
            medical_loss_ratio = 0
            admin_ratio = 0

        row = {
            'year': year,
            'total_premium_billions': total_premium / 1e9,
            'total_claims_billions': total_claims / 1e9,
            'pharma_rebates_billions': pharma_rebates / 1e9,
            'admin_cost_contain_billions': admin_cost_contain / 1e9,
            'admin_claims_adj_billions': admin_claims_adj / 1e9,
            'admin_sales_billions': admin_sales / 1e9,
            'admin_broker_billions': admin_broker / 1e9,
            'admin_other_billions': admin_other / 1e9,
            'total_admin_billions': total_admin / 1e9,
            'computed_mlr_percent': medical_loss_ratio,
            'admin_ratio_percent': admin_ratio,
            'claims_to_premium_percent': (total_claims / total_premium * 100) if total_premium > 0 else 0,
        }

        time_series.append(row)
        print(f"Premium: ${row['total_premium_billions']:.2f}B | Claims: ${row['total_claims_billions']:.2f}B | MLR: {row['computed_mlr_percent']:.1f}%")

    df = pd.DataFrame(time_series)
    output_file = OUTPUT_PATH / 'mlr_time_series.csv'
    df.to_csv(output_file, index=False)

    print(f"\nSaved: {output_file}")
    if len(df) > 0:
        print(f"\nKey Findings:")
        print(f"  Latest year ({int(df.iloc[0]['year'])}) Premium: ${df.iloc[0]['total_premium_billions']:.2f}B")
        print(f"  Latest year ({int(df.iloc[0]['year'])}) Claims: ${df.iloc[0]['total_claims_billions']:.2f}B")
        print(f"  Latest year ({int(df.iloc[0]['year'])}) Admin: ${df.iloc[0]['total_admin_billions']:.2f}B ({df.iloc[0]['admin_ratio_percent']:.1f}%)")
        print(f"  Latest year ({int(df.iloc[0]['year'])}) MLR: {df.iloc[0]['computed_mlr_percent']:.1f}%")

    return df

def calculate_insurer_mlr_2024():
    """Analysis B: Insurer-level MLR analysis for 2024."""

    print("\n" + "="*80)
    print("ANALYSIS B: INSURER-LEVEL MLR (2024)")
    print("="*80)

    year = 2024
    header = load_header_file(year)
    part1_2 = load_part1_2(year)

    if header is None or part1_2 is None:
        print("SKIP: Missing 2024 data files")
        return None

    # Create template ID -> company name mapping (using Grand Total rows)
    company_map = {}

    for _, row in header.iterrows():
        template_id = row.get('mr_submission_template_id')
        company_name = row.get('company_name', 'Unknown')
        is_grand_total = (row.get('business_state') == 'Grand Total')

        if is_grand_total and pd.notna(template_id):
            company_map[int(template_id)] = company_name

    # Get market segment columns
    market_cols = get_market_segment_cols(part1_2)

    insurer_data = []

    for template_id, company_name in company_map.items():
        # Extract rows for this insurer
        insurer_part1 = part1_2[part1_2['mr_submission_template_id'] == template_id]

        if len(insurer_part1) == 0:
            continue

        # Calculate aggregates
        metrics = safe_sum_cols(insurer_part1, market_cols)

        total_premium = metrics.get('TOTAL_DIRECT_PREMIUM_EARNED', 0)
        total_claims = metrics.get('TOTAL_INCURRED_CLAIMS_PT1', 0)
        pharma_rebates = metrics.get('PHARMACEUTICAL_REBATES', 0)

        # Admin expense components
        admin_cost_contain = metrics.get('COST_CONTAINMENT_EXP_NOT_INCL', 0)
        admin_claims_adj = metrics.get('ALL_OTHER_CLAIMS_ADJ_EXPENSES', 0)
        admin_sales = metrics.get('DIR_SALES_SALARIES_AND_BENEFITS', 0)
        admin_broker = metrics.get('AGNTS_AND_BROKERS_FEES_COMMS', 0)
        admin_other = metrics.get('OTHER_GENERAL_AND_ADM_EXPENSES', 0)

        total_admin = admin_cost_contain + admin_claims_adj + admin_sales + admin_broker + admin_other

        # Calculate QI as proxy for potential gaming
        qi_expenses = 0
        for _, row in insurer_part1.iterrows():
            row_code = row.get('row_lookup_code', '')
            if pd.notna(row_code) and ('quality' in str(row_code).lower() or 'qual' in str(row_code).lower()):
                for col in market_cols:
                    val = row.get(col, 0)
                    try:
                        qi_expenses += float(val) if pd.notna(val) else 0
                    except (ValueError, TypeError):
                        pass

        # Calculate MLR
        if total_premium > 0:
            mlr = (total_claims / total_premium) * 100
            admin_ratio = (total_admin / total_premium) * 100
            qi_ratio = (qi_expenses / total_premium) * 100
            qi_to_admin_ratio = (qi_expenses / total_admin * 100) if total_admin > 0 else 0
        else:
            mlr = admin_ratio = qi_ratio = qi_to_admin_ratio = 0

        # Identify Big 5
        is_big_5 = any(big5 in company_name for big5 in BIG_5)

        insurer_data.append({
            'mr_submission_template_id': template_id,
            'company_name': company_name,
            'is_big_5': is_big_5,
            'premium_billions': total_premium / 1e9,
            'claims_billions': total_claims / 1e9,
            'pharma_rebates_billions': pharma_rebates / 1e9,
            'admin_billions': total_admin / 1e9,
            'qi_expenses_millions': qi_expenses / 1e6,
            'mlr_percent': mlr,
            'admin_ratio_percent': admin_ratio,
            'qi_ratio_percent': qi_ratio,
            'qi_to_admin_percent': qi_to_admin_ratio,
        })

    if not insurer_data:
        print("No insurer data found")
        return None

    df = pd.DataFrame(insurer_data)
    df = df.sort_values('premium_billions', ascending=False)

    output_file = OUTPUT_PATH / 'mlr_insurer_2024.csv'
    df.to_csv(output_file, index=False)

    print(f"\nSaved: {output_file}")
    print(f"\nTop 10 Insurers by Premium (2024):")
    for idx, row in df.head(10).iterrows():
        print(f"  {row['company_name']:<50} | Premium: ${row['premium_billions']:>8.2f}B | MLR: {row['mlr_percent']:>6.1f}% | Admin: {row['admin_ratio_percent']:>5.1f}%")

    print(f"\nBig 5 Summary:")
    big5_df = df[df['is_big_5']]
    if len(big5_df) > 0:
        print(f"  Total Premium: ${big5_df['premium_billions'].sum():.2f}B")
        print(f"  Average MLR: {big5_df['mlr_percent'].mean():.1f}%")
        print(f"  Average Admin Ratio: {big5_df['admin_ratio_percent'].mean():.1f}%")
        print(f"  Total QI Expenses: ${big5_df['qi_expenses_millions'].sum():,.0f}M")
        print(f"  Market Share: {(big5_df['premium_billions'].sum() / df['premium_billions'].sum() * 100):.1f}%")

    return df

def calculate_admin_decomposition():
    """Analysis D: Admin expense decomposition by category."""

    print("\n" + "="*80)
    print("ANALYSIS D: ADMIN EXPENSE DECOMPOSITION (2019-2024)")
    print("="*80)

    decomposition = []

    for year in YEARS:
        print(f"\nProcessing {year}...", end=' ', flush=True)

        part1_2 = load_part1_2(year)
        if part1_2 is None:
            print("SKIP")
            continue

        market_cols = get_market_segment_cols(part1_2)
        if not market_cols:
            print("SKIP (no market segment columns)")
            continue

        metrics = safe_sum_cols(part1_2, market_cols)

        admin_cost_contain = metrics.get('COST_CONTAINMENT_EXP_NOT_INCL', 0)
        admin_claims_adj = metrics.get('ALL_OTHER_CLAIMS_ADJ_EXPENSES', 0)
        admin_sales = metrics.get('DIR_SALES_SALARIES_AND_BENEFITS', 0)
        admin_broker = metrics.get('AGNTS_AND_BROKERS_FEES_COMMS', 0)
        admin_other = metrics.get('OTHER_GENERAL_AND_ADM_EXPENSES', 0)
        total_premium = metrics.get('TOTAL_DIRECT_PREMIUM_EARNED', 0)

        total_admin = admin_cost_contain + admin_claims_adj + admin_sales + admin_broker + admin_other

        decomposition.append({
            'year': year,
            'total_admin_billions': total_admin / 1e9,
            'cost_contain_billions': admin_cost_contain / 1e9,
            'claims_adj_billions': admin_claims_adj / 1e9,
            'sales_benefits_billions': admin_sales / 1e9,
            'broker_fees_billions': admin_broker / 1e9,
            'other_ga_billions': admin_other / 1e9,
            'total_premium_billions': total_premium / 1e9,
            'cost_contain_pct': (admin_cost_contain / total_admin * 100) if total_admin > 0 else 0,
            'claims_adj_pct': (admin_claims_adj / total_admin * 100) if total_admin > 0 else 0,
            'sales_benefits_pct': (admin_sales / total_admin * 100) if total_admin > 0 else 0,
            'broker_fees_pct': (admin_broker / total_admin * 100) if total_admin > 0 else 0,
            'other_ga_pct': (admin_other / total_admin * 100) if total_admin > 0 else 0,
            'admin_to_premium_pct': (total_admin / total_premium * 100) if total_premium > 0 else 0,
        })

        if total_premium > 0:
            print(f"Total Admin: ${total_admin / 1e9:.2f}B ({(total_admin / total_premium * 100):.1f}% of premium)")
        else:
            print(f"Total Admin: ${total_admin / 1e9:.2f}B (N/A % of premium)")

    df = pd.DataFrame(decomposition)
    output_file = OUTPUT_PATH / 'mlr_admin_decomposition.csv'
    df.to_csv(output_file, index=False)

    print(f"\nSaved: {output_file}")
    print(f"\nAdmin Expense Trend (2019-2024):")
    for _, row in df.iterrows():
        print(f"  {int(row['year'])}: ${row['total_admin_billions']:.2f}B | {row['admin_to_premium_pct']:.1f}% of premium")

    return df

def calculate_rebate_analysis():
    """Analysis C: Rebate trends."""

    print("\n" + "="*80)
    print("ANALYSIS C: REBATE ANALYSIS (2019-2024)")
    print("="*80)

    rebate_trends = []

    for year in YEARS:
        print(f"\nProcessing {year}...", end=' ', flush=True)

        part1_2 = load_part1_2(year)
        if part1_2 is None:
            print("SKIP")
            continue

        market_cols = get_market_segment_cols(part1_2)
        if not market_cols:
            print("SKIP")
            continue

        metrics = safe_sum_cols(part1_2, market_cols)
        pharma_rebates = metrics.get('PHARMACEUTICAL_REBATES', 0)

        rebate_trends.append({
            'year': year,
            'pharma_rebates_billions': pharma_rebates / 1e9,
        })

        print(f"Pharmaceutical Rebates: ${pharma_rebates / 1e9:.2f}B")

    df = pd.DataFrame(rebate_trends)
    output_file = OUTPUT_PATH / 'mlr_rebate_analysis.csv'
    df.to_csv(output_file, index=False)

    print(f"\nSaved: {output_file}")

    return df

def create_summary():
    """Create consolidated findings JSON."""

    print("\n" + "="*80)
    print("SUMMARY: KEY FINDINGS")
    print("="*80)

    # Load results
    time_series = pd.read_csv(OUTPUT_PATH / 'mlr_time_series.csv')
    insurer_2024 = pd.read_csv(OUTPUT_PATH / 'mlr_insurer_2024.csv')
    admin_decomp = pd.read_csv(OUTPUT_PATH / 'mlr_admin_decomposition.csv')
    rebate_trends = pd.read_csv(OUTPUT_PATH / 'mlr_rebate_analysis.csv')

    summary = {
        'analysis_date': '2026-04-13',
        'data_source': 'CMS Medical Loss Ratio Public Use Files (2019-2024)',
        'key_findings': {
            'latest_year_2024': {
                'total_market_premium_billions': round(time_series.iloc[0]['total_premium_billions'], 2),
                'total_market_claims_billions': round(time_series.iloc[0]['total_claims_billions'], 2),
                'total_admin_expenses_billions': round(time_series.iloc[0]['total_admin_billions'], 2),
                'admin_as_pct_of_premium': round(time_series.iloc[0]['admin_ratio_percent'], 1),
                'computed_mlr_percent': round(time_series.iloc[0]['computed_mlr_percent'], 1),
            },
            'big_5_concentration_2024': {
                'companies_with_data': len(insurer_2024[insurer_2024['is_big_5']]),
                'total_premium_billions': round(insurer_2024[insurer_2024['is_big_5']]['premium_billions'].sum(), 2),
                'market_share_pct': round(insurer_2024[insurer_2024['is_big_5']]['premium_billions'].sum() /
                                         insurer_2024['premium_billions'].sum() * 100, 1),
                'average_mlr_percent': round(insurer_2024[insurer_2024['is_big_5']]['mlr_percent'].mean(), 1),
                'average_admin_ratio_percent': round(insurer_2024[insurer_2024['is_big_5']]['admin_ratio_percent'].mean(), 1),
            },
            'admin_decomposition_2024': {
                'cost_containment_pct': round(admin_decomp.iloc[0]['cost_contain_pct'], 1),
                'claims_adjustment_pct': round(admin_decomp.iloc[0]['claims_adj_pct'], 1),
                'sales_and_benefits_pct': round(admin_decomp.iloc[0]['sales_benefits_pct'], 1),
                'broker_fees_pct': round(admin_decomp.iloc[0]['broker_fees_pct'], 1),
                'other_ga_pct': round(admin_decomp.iloc[0]['other_ga_pct'], 1),
            },
        },
        'methodology_notes': [
            'Market segments aggregated: Individual, Small Group, Large Group, Mini-Med (all yearly variants)',
            'MLR calculated as: (Claims) / Premium',
            'Admin expenses include: cost containment, claims adjustment, sales, broker fees, other G&A',
            'Big 5 identified by company name matching: UnitedHealth, Elevance, Anthem, CVS, Aetna, Cigna, Humana',
            'Grand Total rows used for insurer-level analysis',
            'All figures in billions unless otherwise noted',
        ],
    }

    output_file = OUTPUT_PATH / 'mlr_analysis_summary.json'
    with open(output_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"\nSaved: {output_file}")
    print(f"\nKEY FINDINGS SUMMARY:")
    print(f"  2024 Total Market Premium: ${summary['key_findings']['latest_year_2024']['total_market_premium_billions']:.2f}B")
    print(f"  2024 Total Market Claims: ${summary['key_findings']['latest_year_2024']['total_market_claims_billions']:.2f}B")
    print(f"  2024 Total Admin Expenses: ${summary['key_findings']['latest_year_2024']['total_admin_expenses_billions']:.2f}B")
    print(f"  2024 Admin as % of Premium: {summary['key_findings']['latest_year_2024']['admin_as_pct_of_premium']:.1f}%")
    print(f"  Big 5 Market Share: {summary['key_findings']['big_5_concentration_2024']['market_share_pct']:.1f}%")
    print(f"  Big 5 Average MLR: {summary['key_findings']['big_5_concentration_2024']['average_mlr_percent']:.1f}%")

    return summary

def main():
    """Run all analyses."""

    print("\n")
    print("*" * 80)
    print("CMS MLR PUBLIC USE FILE ANALYSIS FOR ISSUE #8")
    print("The Denial Machine: Insurer Gaming and Prior Authorization")
    print("*" * 80)

    # Run analyses
    time_series_df = calculate_mlr_time_series()
    insurer_df = calculate_insurer_mlr_2024()
    admin_df = calculate_admin_decomposition()
    rebate_df = calculate_rebate_analysis()
    summary = create_summary()

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print(f"\nAll outputs saved to: {OUTPUT_PATH}")
    print("\nGenerated files:")
    print("  1. mlr_time_series.csv - Year-by-year aggregate MLR data (2019-2024)")
    print("  2. mlr_insurer_2024.csv - Insurer-level MLR analysis (2024)")
    print("  3. mlr_admin_decomposition.csv - Admin expense breakdown by category")
    print("  4. mlr_rebate_analysis.csv - Rebate trends over time")
    print("  5. mlr_analysis_summary.json - Consolidated key findings")

if __name__ == '__main__':
    main()
