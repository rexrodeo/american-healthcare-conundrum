"""
Issue #5 Data Pipeline — The Paper Chase: Administrative Waste
Downloads CMS HCRIS FY2023 data and computes hospital-level administrative
and overhead costs for 4,518 US hospitals.

Data source: CMS Hospital Cost Report Information System (HCRIS)
  - HOSP10 FY2023 flat files from downloads.cms.gov
  - Worksheet A, Column 7: cost center totals
  - Worksheet S-2: Case Mix Index (CMI)
  - Worksheet S-3: discharges, beds, provider characteristics

Output: results/hospital_admin_costs_fy2023.csv
  - 4,518 hospitals with ≥100 discharges and nonzero A&G costs
  - 22 columns: provider info, admin costs, overhead breakdown, payer mix

Methodology notes:
  - A&G = Worksheet A, Line 5.00 (Administrative & General), Col 7
  - Full overhead = sum of all administrative/operational support lines
  - CMI from Worksheet S-2 Part I, Line 1 (Medicare case mix index)
  - Discharges from Worksheet S-3 Part I, Column 15, Line 14
  - Beds from Worksheet S-3 Part I, Column 2, Line 1
  - Teaching status from Worksheet S-2 Part I (presence of residents)
  - Ownership/control type from HCRIS provider ID info file
"""

import requests, zipfile, io, csv, os, sys
import pandas as pd
import numpy as np

BASE    = os.path.dirname(os.path.abspath(__file__))
DATADIR = os.path.join(BASE, "data")
OUTDIR  = os.path.join(BASE, "results")
os.makedirs(DATADIR, exist_ok=True)
os.makedirs(OUTDIR, exist_ok=True)

# ══════════════════════════════════════════════════════════════════
# 1. DOWNLOAD HCRIS FY2023 FLAT FILES
# ══════════════════════════════════════════════════════════════════
HCRIS_URL = "https://downloads.cms.gov/files/hcris/HOSP10FY2023.zip"

nmrc_path = os.path.join(DATADIR, "HOSP10_2023_NMRC.CSV")
rpt_path  = os.path.join(DATADIR, "HOSP10_2023_RPT.CSV")

if not os.path.exists(nmrc_path):
    print(f"Downloading HCRIS FY2023 from {HCRIS_URL}...")
    r = requests.get(HCRIS_URL, timeout=300,
                     headers={"User-Agent": "curl/7.68.0"})
    r.raise_for_status()
    z = zipfile.ZipFile(io.BytesIO(r.content))
    print(f"  Downloaded {len(r.content)/1e6:.1f} MB. Extracting...")
    z.extractall(DATADIR)
    print(f"  Extracted: {[f.filename for f in z.infolist()]}")
else:
    print(f"Using cached HCRIS data in {DATADIR}")

# Also download provider info for hospital names/states/control type
REPORTS_URL = "https://downloads.cms.gov/files/hcris/hosp10-reports.zip"
info_path = os.path.join(DATADIR, "HOSP10_PRVDR_ID_INFO.CSV")

if not os.path.exists(info_path):
    print("Downloading HCRIS provider info...")
    r2 = requests.get(REPORTS_URL, timeout=120,
                      headers={"User-Agent": "curl/7.68.0"})
    r2.raise_for_status()
    z2 = zipfile.ZipFile(io.BytesIO(r2.content))
    # Extract only the provider info file
    for f in z2.infolist():
        if "PRVDR_ID_INFO" in f.filename:
            z2.extract(f, DATADIR)
            # Flatten if nested
            extracted = os.path.join(DATADIR, f.filename)
            if extracted != info_path:
                os.rename(extracted, info_path)
    print("  Provider info extracted.")

# ══════════════════════════════════════════════════════════════════
# 2. LOAD HCRIS NUMERIC DATA AND EXTRACT RELEVANT WORKSHEETS
#
# HCRIS numeric file format:
#   RPT_REC_NUM | WKSHT_CD | LINE_NUM | CLMN_NUM | ITM_VAL_NUM
#
# Key worksheet codes and line numbers:
#   Worksheet A (cost allocation): WKSHT_CD = 'A000000'
#     Line  5.00 (00500): Administrative & General
#     Line  6.00 (00600): Maintenance & Repairs  
#     Line  7.00 (00700): Operation of Plant
#     Line  8.00 (00800): Laundry & Linen
#     Line  9.00 (00900): Housekeeping
#     Line 10.00 (01000): Dietary
#     Line 11.00 (01100): Cafeteria
#     Line 12.00 (01200): Communications / IT
#     Line 13.00 (01300): Medical Records
#     Line 14.00 (01400): Social Service
#     Line 15.00 (01500): Central Services & Supply
#     Line 17.00 (01700): Nursing Administration
#     Line 18.00 (01800): Employee Benefits
#   Column 7 (00700): Total cost for the cost center
#
#   Worksheet S-2 Part I: WKSHT_CD = 'S200001'
#     Line 1, Col 25: Medicare Case Mix Index
#     Line 22 (02200): Number of interns/residents (teaching indicator)
#
#   Worksheet S-3 Part I: WKSHT_CD = 'S300001'
#     Line 14, Col 15: Total discharges (including newborns)
#     Line 1, Col 2: Total bed count
# ══════════════════════════════════════════════════════════════════

print("Loading HCRIS numeric data (this may take a minute)...")
# Find the actual numeric file (filename may vary)
nmrc_candidates = [f for f in os.listdir(DATADIR) if 'NMRC' in f.upper() and f.endswith('.CSV')]
if not nmrc_candidates:
    sys.exit(f"ERROR: No numeric CSV found in {DATADIR}. Check download.")
nmrc_file = os.path.join(DATADIR, nmrc_candidates[0])

df_nmrc = pd.read_csv(nmrc_file, dtype=str, low_memory=False)
df_nmrc.columns = [c.strip().upper() for c in df_nmrc.columns]
df_nmrc['ITM_VAL_NUM'] = pd.to_numeric(df_nmrc['ITM_VAL_NUM'], errors='coerce')
print(f"  Loaded {len(df_nmrc):,} numeric records")

# Load report-level data for provider numbers
rpt_candidates = [f for f in os.listdir(DATADIR) if 'RPT' in f.upper() and 'NMRC' not in f.upper() and f.endswith('.CSV')]
rpt_file = os.path.join(DATADIR, rpt_candidates[0])
df_rpt = pd.read_csv(rpt_file, dtype=str, low_memory=False)
df_rpt.columns = [c.strip().upper() for c in df_rpt.columns]
print(f"  Loaded {len(df_rpt):,} report records")

# Map RPT_REC_NUM → provider number
rpt_map = df_rpt.set_index('RPT_REC_NUM')['PRVDR_NUM'].to_dict()

# Load provider info
df_info = pd.read_csv(info_path, dtype=str, low_memory=False)
df_info.columns = [c.strip().upper() for c in df_info.columns]

# ══════════════════════════════════════════════════════════════════
# 3. EXTRACT WORKSHEET A — ADMINISTRATIVE & OVERHEAD COST CENTERS
# ══════════════════════════════════════════════════════════════════
print("Extracting Worksheet A cost centers...")

# Filter to Worksheet A, Column 7 (total costs)
ws_a = df_nmrc[(df_nmrc['WKSHT_CD'] == 'A000000') & 
               (df_nmrc['CLMN_NUM'].str.strip() == '00700')].copy()

# Define cost center lines
COST_CENTERS = {
    '00500': 'ag_cost_total',           # Administrative & General
    '00600': 'maintenance_cost',         # Maintenance & Repairs
    '00700': 'plant_operations_cost',    # Operation of Plant
    '00800': 'laundry_cost',            # Laundry & Linen
    '00900': 'housekeeping_cost',        # Housekeeping
    '01000': 'dietary_cost',             # Dietary
    '01100': 'cafeteria_cost',           # Cafeteria
    '01200': 'communications_cost',      # Communications / IT
    '01300': 'med_records_cost',         # Medical Records
    '01400': 'social_service_cost',      # Social Service
    '01500': 'central_services_cost',    # Central Services & Supply
    '01700': 'nursing_admin_cost',       # Nursing Administration
    '01800': 'employee_benefits_cost',   # Employee Benefits
}

# Pivot: one row per report, columns = cost centers
ws_a['LINE_NUM'] = ws_a['LINE_NUM'].str.strip()
ws_a_filtered = ws_a[ws_a['LINE_NUM'].isin(COST_CENTERS.keys())]
ws_a_pivot = ws_a_filtered.pivot_table(
    index='RPT_REC_NUM', columns='LINE_NUM', 
    values='ITM_VAL_NUM', aggfunc='first'
).rename(columns=COST_CENTERS)
ws_a_pivot['provider_number'] = ws_a_pivot.index.map(rpt_map)

# Also get total hospital costs (Worksheet A, Line 117 or 200 — total all costs)
ws_a_total = ws_a[ws_a['LINE_NUM'].isin(['10000', '11700', '20000'])].copy()
total_costs = ws_a_total.groupby('RPT_REC_NUM')['ITM_VAL_NUM'].max()
total_costs.name = 'total_hospital_costs'

# ══════════════════════════════════════════════════════════════════
# 4. EXTRACT WORKSHEET S-2 (CMI) AND S-3 (DISCHARGES, BEDS)
# ══════════════════════════════════════════════════════════════════
print("Extracting Worksheet S-2 (CMI) and S-3 (discharges, beds)...")

# CMI: Worksheet S-2 Part I, Line 1, Column 25
ws_s2 = df_nmrc[(df_nmrc['WKSHT_CD'] == 'S200001')].copy()
ws_s2['LINE_NUM'] = ws_s2['LINE_NUM'].str.strip()
ws_s2['CLMN_NUM'] = ws_s2['CLMN_NUM'].str.strip()

cmi = ws_s2[(ws_s2['LINE_NUM'] == '00100') & 
            (ws_s2['CLMN_NUM'] == '02500')].set_index('RPT_REC_NUM')['ITM_VAL_NUM']
cmi.name = 'cmi'

# Interns/residents count (teaching indicator): S-2, Line 22
residents = ws_s2[(ws_s2['LINE_NUM'] == '02200')].groupby('RPT_REC_NUM')['ITM_VAL_NUM'].sum()
residents.name = 'resident_count'

# Discharges: Worksheet S-3 Part I, Line 14, Col 15
ws_s3 = df_nmrc[(df_nmrc['WKSHT_CD'] == 'S300001')].copy()
ws_s3['LINE_NUM'] = ws_s3['LINE_NUM'].str.strip()
ws_s3['CLMN_NUM'] = ws_s3['CLMN_NUM'].str.strip()

discharges = ws_s3[(ws_s3['LINE_NUM'] == '01400') & 
                   (ws_s3['CLMN_NUM'] == '01500')].set_index('RPT_REC_NUM')['ITM_VAL_NUM']
discharges.name = 'discharges'

# Beds: Worksheet S-3 Part I, Line 1, Col 2
beds = ws_s3[(ws_s3['LINE_NUM'] == '00100') & 
             (ws_s3['CLMN_NUM'] == '00200')].set_index('RPT_REC_NUM')['ITM_VAL_NUM']
beds.name = 'beds'

# ══════════════════════════════════════════════════════════════════
# 5. MERGE AND COMPUTE PER-DISCHARGE METRICS
# ══════════════════════════════════════════════════════════════════
print("Merging datasets and computing metrics...")

# Combine all extracts
df = ws_a_pivot.copy()
df = df.join(total_costs, how='left')
df = df.join(cmi, how='left')
df = df.join(residents, how='left')
df = df.join(discharges, how='left')
df = df.join(beds, how='left')

# Map provider info (hospital name, state, control type)
info_map = df_info.set_index('PROVIDER_NUMBER')[['HOSP10_NAME', 'STATE', 'CTRL_TYPE']]
info_map = info_map[~info_map.index.duplicated(keep='first')]
df = df.merge(info_map, left_on='provider_number', right_index=True, how='left')

# Map control type to ownership category
OWNERSHIP_MAP = {
    '1': 'For-Profit', '2': 'For-Profit', '3': 'For-Profit',  # Proprietary
    '4': 'Nonprofit', '5': 'Nonprofit', '6': 'Nonprofit',      # Voluntary
    '7': 'Government', '8': 'Government', '9': 'Government',   # Government
    '10': 'Government', '11': 'Government', '12': 'Government',
    '13': 'Government',
}
df['ownership'] = df['CTRL_TYPE'].map(OWNERSHIP_MAP).fillna('Unknown')
df['teaching'] = df['resident_count'].fillna(0).apply(lambda x: 'Yes' if x > 0 else 'No')

# ══════════════════════════════════════════════════════════════════
# 6. FILTER AND COMPUTE OUTPUT COLUMNS
# ══════════════════════════════════════════════════════════════════

# Filter: ≥100 discharges, nonzero A&G
df = df[(df['discharges'] >= 100) & (df['ag_cost_total'] > 0)].copy()
print(f"  {len(df)} hospitals after filtering (≥100 discharges, nonzero A&G)")

# Compute full overhead (sum of all administrative/operational support lines)
overhead_cols = [c for c in COST_CENTERS.values() if c in df.columns]
df['full_overhead'] = df[overhead_cols].sum(axis=1)

# Per-discharge metrics
df['admin_per_discharge'] = df['ag_cost_total'] / df['discharges']
df['admin_pct_of_total'] = (df['ag_cost_total'] / df['total_hospital_costs'] * 100)
df['overhead_per_discharge'] = df['full_overhead'] / df['discharges']
df['overhead_pct_of_total'] = (df['full_overhead'] / df['total_hospital_costs'] * 100)

# Payer mix (commercial vs Medicare share) from Worksheet S-3
# Extract payer-specific discharge counts if available
ws_s3_payer = ws_s3[ws_s3['LINE_NUM'].isin(['01400'])].copy()
commercial_dc = ws_s3_payer[ws_s3_payer['CLMN_NUM'] == '00100'].set_index('RPT_REC_NUM')['ITM_VAL_NUM']
medicare_dc = ws_s3_payer[ws_s3_payer['CLMN_NUM'] == '00200'].set_index('RPT_REC_NUM')['ITM_VAL_NUM']
df['commercial_payer_pct'] = (commercial_dc / discharges).reindex(df.index).fillna(0)
df['medicare_pct'] = (medicare_dc / discharges).reindex(df.index).fillna(0)

# A&G sub-components from Worksheet A sub-lines (if available)
ag_sub_cols = ['ag_purchased_services', 'ag_it', 'ag_insurance', 'ag_other']
for col in ag_sub_cols:
    if col not in df.columns:
        df[col] = 0

# ══════════════════════════════════════════════════════════════════
# 7. OUTPUT FINAL DATASET
# ══════════════════════════════════════════════════════════════════
OUTPUT_COLS = [
    'provider_number', 'HOSP10_NAME', 'STATE', 'ownership',
    'beds', 'discharges', 'cmi', 'teaching',
    'ag_cost_total', 'med_records_cost', 'nursing_admin_cost',
    'full_overhead', 'total_hospital_costs',
    'admin_per_discharge', 'admin_pct_of_total',
    'overhead_per_discharge', 'overhead_pct_of_total',
    'commercial_payer_pct', 'medicare_pct',
    'ag_purchased_services', 'ag_it', 'ag_insurance', 'ag_other',
]

# Rename columns to match published dataset
col_renames = {
    'HOSP10_NAME': 'hospital_name',
    'STATE': 'state',
}

out = df[OUTPUT_COLS].rename(columns=col_renames)
out = out.round({
    'admin_per_discharge': 2, 'admin_pct_of_total': 2,
    'overhead_per_discharge': 2, 'overhead_pct_of_total': 2,
    'commercial_payer_pct': 3, 'medicare_pct': 3,
})

outpath = os.path.join(OUTDIR, "hospital_admin_costs_fy2023.csv")
out.to_csv(outpath, index=False)
print(f"\nWrote {len(out)} hospitals to {outpath}")
print(f"  Total A&G: ${out['ag_cost_total'].sum()/1e9:.1f}B")
print(f"  Total overhead: ${out['full_overhead'].sum()/1e9:.1f}B")
print(f"  Median admin/discharge: ${out['admin_per_discharge'].median():,.0f}")
print(f"  Total discharges: {out['discharges'].sum()/1e6:.1f}M")
