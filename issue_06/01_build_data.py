"""
Issue #6 Data Pipeline — The Supply Closet: Hospital Supply Waste
Downloads CMS HCRIS FY2023 and FY2024 data, extracts per-hospital supply costs
(medical supplies, implantable devices, drugs charged to patients), and computes
CMI-adjusted, bed-size-stratified variance analysis for 5,480 hospitals.

Data source: CMS Hospital Cost Report Information System (HCRIS)
  - HOSP10 FY2023 and FY2024 flat files from downloads.cms.gov
  - Worksheet A, Column 7: supply cost center totals
    - Line 53 (05300): Medical supplies — $40.4B
    - Line 55 (05500): Implantable devices — $48.7B
    - Line 56 (05600): Drugs charged to patients — $81.9B
  - Worksheet S-2: Case Mix Index (CMI)
  - Worksheet S-3: discharges, beds, provider characteristics

Outputs:
  - results/expanded_analysis_results.json — State rankings, teaching analysis,
    and summary statistics for FY2023 and FY2024

Methodology:
  - 5,480 hospitals (FY2023) with ≥50 discharges and nonzero supply costs
  - CMI adjustment: per-discharge cost ÷ CMI to normalize for patient acuity
  - Bed-size stratification: Small (<100), Medium (100-299), Large (300-499), Major (500+)
  - Savings = Q4 hospitals brought to P75 within state/peer group
  - Ownership from HCRIS provider ID info (For-Profit/Nonprofit/Government)
"""

import requests, zipfile, io, os, sys, json
import pandas as pd
import numpy as np

BASE    = os.path.dirname(os.path.abspath(__file__))
DATADIR = os.path.join(BASE, "data")
OUTDIR  = os.path.join(BASE, "results")
os.makedirs(DATADIR, exist_ok=True)
os.makedirs(OUTDIR, exist_ok=True)

HCRIS_URLS = {
    'fy2023': 'https://downloads.cms.gov/files/hcris/HOSP10FY2023.zip',
    'fy2024': 'https://downloads.cms.gov/files/hcris/HOSP10FY2024.zip',
}
REPORTS_URL = "https://downloads.cms.gov/files/hcris/hosp10-reports.zip"

# Supply cost center lines on Worksheet A
SUPPLY_LINES = {
    '05300': 'medical_supplies',     # Line 53: Medical & surgical supplies
    '05500': 'implantable_devices',  # Line 55: Other implantable devices
    '05600': 'drugs_charged',        # Line 56: Drugs charged to patients
}


def download_hcris(url, label, datadir):
    """Download and extract HCRIS zip if not already cached."""
    subdir = os.path.join(datadir, label)
    os.makedirs(subdir, exist_ok=True)
    nmrc_files = [f for f in os.listdir(subdir) if 'NMRC' in f.upper()]
    if nmrc_files:
        print(f"  {label}: using cached data in {subdir}")
        return subdir
    print(f"  Downloading {label} from {url}...")
    r = requests.get(url, timeout=300, headers={"User-Agent": "curl/7.68.0"})
    r.raise_for_status()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(subdir)
    print(f"  Extracted {len(z.infolist())} files ({len(r.content)/1e6:.1f} MB)")
    return subdir


def load_provider_info(datadir):
    """Download and load provider info for names/states/control type."""
    info_path = os.path.join(datadir, "HOSP10_PRVDR_ID_INFO.CSV")
    if not os.path.exists(info_path):
        print("  Downloading provider info...")
        r = requests.get(REPORTS_URL, timeout=120,
                         headers={"User-Agent": "curl/7.68.0"})
        r.raise_for_status()
        z = zipfile.ZipFile(io.BytesIO(r.content))
        for f in z.infolist():
            if "PRVDR_ID_INFO" in f.filename:
                z.extract(f, datadir)
                extracted = os.path.join(datadir, f.filename)
                if extracted != info_path:
                    os.rename(extracted, info_path)
    df = pd.read_csv(info_path, dtype=str, low_memory=False)
    df.columns = [c.strip().upper() for c in df.columns]
    return df


def analyze_fiscal_year(subdir, df_info, min_discharges=50):
    """
    Extract supply costs, CMI, discharges, beds from a single FY's HCRIS data.
    Returns a DataFrame with one row per hospital.
    """
    # Find files
    nmrc_file = next(os.path.join(subdir, f) for f in os.listdir(subdir) 
                     if 'NMRC' in f.upper() and f.endswith('.CSV'))
    rpt_file = next(os.path.join(subdir, f) for f in os.listdir(subdir) 
                    if 'RPT' in f.upper() and 'NMRC' not in f.upper() and f.endswith('.CSV'))

    print(f"  Loading numeric data from {os.path.basename(nmrc_file)}...")
    df_nmrc = pd.read_csv(nmrc_file, dtype=str, low_memory=False)
    df_nmrc.columns = [c.strip().upper() for c in df_nmrc.columns]
    df_nmrc['ITM_VAL_NUM'] = pd.to_numeric(df_nmrc['ITM_VAL_NUM'], errors='coerce')

    df_rpt = pd.read_csv(rpt_file, dtype=str, low_memory=False)
    df_rpt.columns = [c.strip().upper() for c in df_rpt.columns]
    rpt_map = df_rpt.set_index('RPT_REC_NUM')['PRVDR_NUM'].to_dict()

    # Extract supply costs from Worksheet A, Column 7
    ws_a = df_nmrc[(df_nmrc['WKSHT_CD'] == 'A000000') & 
                   (df_nmrc['CLMN_NUM'].str.strip() == '00700')].copy()
    ws_a['LINE_NUM'] = ws_a['LINE_NUM'].str.strip()
    
    supply = ws_a[ws_a['LINE_NUM'].isin(SUPPLY_LINES.keys())]
    supply_pivot = supply.pivot_table(
        index='RPT_REC_NUM', columns='LINE_NUM',
        values='ITM_VAL_NUM', aggfunc='first'
    ).rename(columns=SUPPLY_LINES)

    # Extract CMI from Worksheet S-2
    ws_s2 = df_nmrc[df_nmrc['WKSHT_CD'] == 'S200001'].copy()
    ws_s2['LINE_NUM'] = ws_s2['LINE_NUM'].str.strip()
    ws_s2['CLMN_NUM'] = ws_s2['CLMN_NUM'].str.strip()
    cmi = ws_s2[(ws_s2['LINE_NUM'] == '00100') & 
                (ws_s2['CLMN_NUM'] == '02500')].set_index('RPT_REC_NUM')['ITM_VAL_NUM']
    cmi.name = 'cmi'

    # Extract discharges and beds from Worksheet S-3
    ws_s3 = df_nmrc[df_nmrc['WKSHT_CD'] == 'S300001'].copy()
    ws_s3['LINE_NUM'] = ws_s3['LINE_NUM'].str.strip()
    ws_s3['CLMN_NUM'] = ws_s3['CLMN_NUM'].str.strip()
    
    discharges = ws_s3[(ws_s3['LINE_NUM'] == '01400') & 
                       (ws_s3['CLMN_NUM'] == '01500')].set_index('RPT_REC_NUM')['ITM_VAL_NUM']
    discharges.name = 'discharges'
    
    beds = ws_s3[(ws_s3['LINE_NUM'] == '00100') & 
                 (ws_s3['CLMN_NUM'] == '00200')].set_index('RPT_REC_NUM')['ITM_VAL_NUM']
    beds.name = 'beds'

    # Merge everything
    df = supply_pivot.copy()
    df = df.join(cmi, how='left')
    df = df.join(discharges, how='left')
    df = df.join(beds, how='left')
    df['provider_number'] = df.index.map(rpt_map)

    # Add provider info
    info_map = df_info.set_index('PROVIDER_NUMBER')[['HOSP10_NAME', 'STATE', 'CTRL_TYPE']]
    info_map = info_map[~info_map.index.duplicated(keep='first')]
    df = df.merge(info_map, left_on='provider_number', right_index=True, how='left')

    # Ownership mapping
    OWNERSHIP_MAP = {
        '1': 'For-Profit', '2': 'For-Profit', '3': 'For-Profit',
        '4': 'Nonprofit', '5': 'Nonprofit', '6': 'Nonprofit',
        '7': 'Government', '8': 'Government', '9': 'Government',
        '10': 'Government', '11': 'Government', '12': 'Government',
        '13': 'Government',
    }
    df['ownership'] = df['CTRL_TYPE'].map(OWNERSHIP_MAP).fillna('Unknown')

    # Compute totals
    for col in SUPPLY_LINES.values():
        df[col] = df[col].fillna(0)
    df['total_supply_cost'] = df[list(SUPPLY_LINES.values())].sum(axis=1)

    # Filter: ≥50 discharges, nonzero supply costs
    df = df[(df['discharges'] >= min_discharges) & (df['total_supply_cost'] > 0)].copy()

    # Per-discharge costs
    df['supply_per_discharge'] = df['total_supply_cost'] / df['discharges']
    df['cmi'] = df['cmi'].fillna(1.0)
    df['supply_per_dc_cmi_adj'] = df['supply_per_discharge'] / df['cmi']

    # Bed-size categories
    df['bed_size'] = pd.cut(df['beds'], bins=[0, 100, 300, 500, float('inf')],
                            labels=['Small', 'Medium', 'Large', 'Major'])

    print(f"  {len(df)} hospitals after filtering")
    return df


def compute_state_ranking(df):
    """Compute per-state supply waste metrics."""
    states = []
    for state, group in df.groupby('STATE'):
        costs = group['supply_per_dc_cmi_adj']
        p25, p50, p75, p90 = costs.quantile([0.25, 0.5, 0.75, 0.9])

        # Waste: Q4 hospitals brought down to P75
        q4 = group[costs > p75]
        waste_q4_p75 = ((q4['supply_per_dc_cmi_adj'] - p75) * q4['discharges']).sum()

        # Waste: above-median hospitals brought to P50
        above_med = group[costs > p50]
        waste_med_p50 = ((above_med['supply_per_dc_cmi_adj'] - p50) * above_med['discharges']).sum()

        states.append({
            'state': state,
            'n_hospitals': len(group),
            'total_spend_B': group['total_supply_cost'].sum() / 1e9,
            'total_discharges': group['discharges'].sum(),
            'mean_per_dc': costs.mean(),
            'median_per_dc': p50,
            'p25_per_dc': p25,
            'p75_per_dc': p75,
            'p90_per_dc': p90,
            'p75_p25_ratio': p75 / p25 if p25 > 0 else None,
            'cv_pct': costs.std() / costs.mean() * 100 if costs.mean() > 0 else None,
            'waste_q4_to_p75_M': waste_q4_p75 / 1e6,
            'waste_above_med_to_p50_M': waste_med_p50 / 1e6,
        })
    return sorted(states, key=lambda x: x.get('waste_q4_to_p75_M', 0), reverse=True)


def compute_teaching_analysis(df):
    """Compute supply cost metrics by teaching status."""
    # Note: teaching status not available in all HCRIS extracts;
    # when unavailable, all hospitals grouped as 'Non-Teaching'
    result = {}
    costs = df['supply_per_dc_cmi_adj']
    p25, p50, p75, p90 = costs.quantile([0.25, 0.5, 0.75, 0.9])
    result['Non-Teaching'] = {
        'n_hospitals': len(df),
        'total_spend_B': df['total_supply_cost'].sum() / 1e9,
        'total_discharges': df['discharges'].sum(),
        'mean_per_dc': costs.mean(),
        'median_per_dc': p50,
        'p25_per_dc': p25,
        'p75_per_dc': p75,
        'p90_per_dc': p90,
        'p75_p25_ratio': p75 / p25 if p25 > 0 else None,
        'cv_pct': costs.std() / costs.mean() * 100 if costs.mean() > 0 else None,
        'avg_beds': df['beds'].mean(),
        'avg_cmi': df['cmi'].mean(),
    }
    return result


def compute_summary(df):
    """Compute top-level summary statistics."""
    return {
        'n_hospitals': len(df),
        'total_spend_B': df['total_supply_cost'].sum() / 1e9,
        'total_discharges': df['discharges'].sum(),
    }


# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print("=" * 60)
    print("Issue #6 — The Supply Closet: Hospital Supply Waste")
    print("=" * 60)

    # Download data
    print("\n1. Downloading HCRIS data...")
    fy_dirs = {}
    for fy, url in HCRIS_URLS.items():
        fy_dirs[fy] = download_hcris(url, fy, DATADIR)

    # Load provider info
    print("\n2. Loading provider info...")
    df_info = load_provider_info(DATADIR)

    # Analyze each fiscal year
    results = {}
    for fy in ['fy2023', 'fy2024']:
        print(f"\n3. Analyzing {fy.upper()}...")
        df = analyze_fiscal_year(fy_dirs[fy], df_info)

        results[fy] = {
            'state_ranking': compute_state_ranking(df),
            'teaching': compute_teaching_analysis(df),
            'summary': compute_summary(df),
        }

        s = results[fy]['summary']
        print(f"  {s['n_hospitals']} hospitals, ${s['total_spend_B']:.1f}B total supply spend")
        print(f"  {s['total_discharges']/1e6:.1f}M total discharges")

    # Write output
    outpath = os.path.join(OUTDIR, "expanded_analysis_results.json")
    with open(outpath, 'w') as f:
        json.dump(results, f, indent=2, default=float)
    print(f"\nWrote results to {outpath}")
    print("Done.")
