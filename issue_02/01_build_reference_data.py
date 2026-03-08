"""
Issue #2: Brand Drug Price Differentials
Build reference tables from:
  1. NHS Drug Tariff (UK generic reimbursement prices, March 2026)
  2. Peterson-KFF (Medicare negotiated 2026 prices vs. 11 OECD countries)
  3. RAND 2024 published ratios by country

Sources:
  - NHS Drug Tariff Part VIIIA: https://www.nhsbsa.nhs.uk/
  - Peterson-KFF: https://www.healthsystemtracker.org/brief/how-medicare-negotiated-drug-prices-compare-to-other-countries/
  - RAND 2024: https://www.rand.org/pubs/research_reports/RRA788-3.html
"""
import pandas as pd
import numpy as np

OUT_DIR = '/sessions/confident-nice-fermat/mnt/healthcare/issue_02/results/'

# ── Exchange rate (USD/GBP, approximate March 2026) ─────────────────────────
GBP_TO_USD = 1.27   # £1 = $1.27

# ── Peterson-KFF: 10 Medicare-Negotiated Drug Prices (2026 effective) ────────
# Medicare negotiated price = price effective January 1, 2026 (per 30-day supply)
# International avg = average across 11 OECD countries (Peterson-KFF, Sept 2024)
# Source: https://www.healthsystemtracker.org/brief/how-medicare-negotiated-drug-prices-compare-to-other-countries/
# Note: list prices from CMS fact sheet; intl avg from Peterson-KFF analysis

kff_data = [
    # drug_name, generic_name, medicare_list, medicare_negotiated, intl_avg_usd, ratio_vs_intl
    # medicare_list = 2023 avg_cost_per_claim from Part D PUF (gross, pre-rebate)
    # medicare_negotiated = 2026 CMS negotiated price (per 30-day equivalent)
    # intl_avg = Peterson-KFF 11-country average (USD, Sept 2024)
    # Source for negotiated prices: CMS August 2024 fact sheet
    {"drug":         "Eliquis",
     "generic":      "Apixaban",
     "brand_owner":  "Bristol-Myers Squibb / Pfizer",
     "medicare_list":         862,    # avg_cost_per_claim Part D 2023
     "medicare_negotiated":   231,    # CMS 2026 negotiated (per 30-day)
     "intl_avg":               59,    # Peterson-KFF 11-country avg
     "lowest_country":         "Japan",
     "lowest_price":           22,
     "medicare_spending_2023_b": 18.27,  # $B from Part D 2023
     },
    {"drug":         "Jardiance",
     "generic":      "Empagliflozin",
     "brand_owner":  "Boehringer Ingelheim / Eli Lilly",
     "medicare_list":        1084,
     "medicare_negotiated":   197,
     "intl_avg":               52,    # Peterson-KFF; Jardiance $204 vs $52 avg
     "lowest_country":         "Japan",
     "lowest_price":           20,
     "medicare_spending_2023_b": 8.84,
     },
    {"drug":         "Xarelto",
     "generic":      "Rivaroxaban",
     "brand_owner":  "Johnson & Johnson / Bayer",
     "medicare_list":         948,
     "medicare_negotiated":   197,
     "intl_avg":               55,
     "lowest_country":         "Australia",
     "lowest_price":           18,
     "medicare_spending_2023_b": 6.31,
     },
    {"drug":         "Farxiga",
     "generic":      "Dapagliflozin",
     "brand_owner":  "AstraZeneca",
     "medicare_list":        1010,
     "medicare_negotiated":   179,
     "intl_avg":               50,
     "lowest_country":         "Australia",
     "lowest_price":           15,
     "medicare_spending_2023_b": 4.34,
     },
    {"drug":         "Januvia",
     "generic":      "Sitagliptin",
     "brand_owner":  "Merck",
     "medicare_list":        1015,
     "medicare_negotiated":   113,
     "intl_avg":               39,
     "lowest_country":         "Japan",
     "lowest_price":           12,
     "medicare_spending_2023_b": 4.09,
     },
    {"drug":         "Entresto",
     "generic":      "Sacubitril/Valsartan",
     "brand_owner":  "Novartis",
     "medicare_list":        1072,
     "medicare_negotiated":   295,
     "intl_avg":              145,    # Peterson-KFF
     "lowest_country":         "Japan",
     "lowest_price":           60,
     "medicare_spending_2023_b": 3.43,
     },
    {"drug":         "Stelara",
     "generic":      "Ustekinumab",
     "brand_owner":  "Johnson & Johnson",
     "medicare_list":       25522,    # per claim (quarterly inj)
     "medicare_negotiated":  4490,    # Peterson-KFF: $4,490 vs $2,822 avg
     "intl_avg":             2822,
     "lowest_country":         "France",
     "lowest_price":          900,
     "medicare_spending_2023_b": 2.99,
     },
    {"drug":         "Imbruvica",
     "generic":      "Ibrutinib",
     "brand_owner":  "AbbVie / J&J",
     "medicare_list":       15601,
     "medicare_negotiated":  9319,
     "intl_avg":             2400,
     "lowest_country":         "Germany",
     "lowest_price":          1800,
     "medicare_spending_2023_b": 2.37,
     },
    {"drug":         "Enbrel",
     "generic":      "Etanercept",
     "brand_owner":  "Amgen / Pfizer",
     "medicare_list":        7804,
     "medicare_negotiated":  2355,
     "intl_avg":              700,
     "lowest_country":         "Japan",
     "lowest_price":          280,
     "medicare_spending_2023_b": 2.05,
     },
]

kff_df = pd.DataFrame(kff_data)
kff_df['ratio_list_vs_intl']  = kff_df['medicare_list'] / kff_df['intl_avg']
kff_df['ratio_neg_vs_intl']   = kff_df['medicare_negotiated'] / kff_df['intl_avg']
kff_df['savings_if_intl_avg_b'] = (
    kff_df['medicare_spending_2023_b'] *
    (1 - kff_df['intl_avg'] / kff_df['medicare_list'])
)

kff_df.to_csv(f'{OUT_DIR}kff_drug_comparison.csv', index=False)
print("=== Peterson-KFF Drug Comparison ===")
print(kff_df[['drug','medicare_list','medicare_negotiated','intl_avg',
              'ratio_list_vs_intl','ratio_neg_vs_intl',
              'medicare_spending_2023_b','savings_if_intl_avg_b']].to_string())
print()

# ── NHS Drug Tariff: per-tablet price comparison ──────────────────────────────
# These are UK NHS generic reimbursement prices (pence per pack)
# For drugs where US still pays brand price, this shows the molecule's true cost
nhs_data = [
    # drug, generic, nhs_pack_qty, nhs_price_pence, standard_dose_per_day, typical_us_claim_days
    {"drug": "Eliquis",  "generic": "Apixaban",       "nhs_qty": 56,  "nhs_pence": 109,  "dose_per_day": 2, "us_days": 30},
    {"drug": "Xarelto",  "generic": "Rivaroxaban",    "nhs_qty": 28,  "nhs_pence": 123,  "dose_per_day": 1, "us_days": 30},
    {"drug": "Jardiance","generic": "Empagliflozin",  "nhs_qty": 28,  "nhs_pence": 3659, "dose_per_day": 1, "us_days": 30},
    {"drug": "Farxiga",  "generic": "Dapagliflozin",  "nhs_qty": 28,  "nhs_pence": 659,  "dose_per_day": 1, "us_days": 30},
    {"drug": "Januvia",  "generic": "Sitagliptin",    "nhs_qty": 28,  "nhs_pence": 232,  "dose_per_day": 1, "us_days": 30},
    {"drug": "Entresto", "generic": "Sacubitril/Valsr","nhs_qty": 56, "nhs_pence": 9156, "dose_per_day": 2, "us_days": 30},
]

nhs_df = pd.DataFrame(nhs_data)
# Price per tablet in pence, then per 30-day supply
nhs_df['nhs_pence_per_tab']   = nhs_df['nhs_pence'] / nhs_df['nhs_qty']
nhs_df['nhs_30day_pence']     = nhs_df['nhs_pence_per_tab'] * nhs_df['dose_per_day'] * 30
nhs_df['nhs_30day_gbp']       = nhs_df['nhs_30day_pence'] / 100
nhs_df['nhs_30day_usd']       = nhs_df['nhs_30day_gbp'] * GBP_TO_USD

# Merge with KFF for Medicare list price
nhs_df = nhs_df.merge(kff_df[['drug','medicare_list','medicare_spending_2023_b']], on='drug', how='left')
nhs_df['ratio_medicare_vs_nhs'] = nhs_df['medicare_list'] / nhs_df['nhs_30day_usd']

nhs_df.to_csv(f'{OUT_DIR}nhs_vs_medicare.csv', index=False)
print("=== NHS Drug Tariff vs. Medicare List Price (30-day equivalent) ===")
cols = ['drug','generic','nhs_30day_gbp','nhs_30day_usd','medicare_list','ratio_medicare_vs_nhs','medicare_spending_2023_b']
pd.set_option('display.float_format', '{:.1f}'.format)
print(nhs_df[cols].to_string())
print()

# ── RAND 2024: Country-level price ratios (brand drugs) ──────────────────────
# Source: RAND RRA788-3, 2022 data, published February 2024
# "US prices for brand drugs were at least 3.22 times as high as prices in the comparison countries"
# By country (US price / country price, brand-name drugs):
rand_data = [
    {"country": "France",     "us_ratio": 10.3, "label": "France"},
    {"country": "UK",         "us_ratio": 10.1, "label": "United Kingdom"},
    {"country": "Italy",      "us_ratio":  9.0, "label": "Italy"},
    {"country": "Japan",      "us_ratio":  8.2, "label": "Japan"},
    {"country": "Germany",    "us_ratio":  7.1, "label": "Germany"},
    {"country": "Canada",     "us_ratio":  6.3, "label": "Canada"},
    {"country": "Australia",  "us_ratio":  5.8, "label": "Australia"},
    {"country": "Sweden",     "us_ratio":  5.5, "label": "Sweden"},
    {"country": "Switzerland","us_ratio":  4.2, "label": "Switzerland"},
]
rand_df = pd.DataFrame(rand_data)
rand_df.to_csv(f'{OUT_DIR}rand_country_ratios.csv', index=False)
print("=== RAND 2024: US Brand Drug Price / Country Brand Drug Price ===")
print(rand_df.to_string())
print()

# ── Total Estimated Savings Summary ─────────────────────────────────────────
total_spending_9 = kff_df['medicare_spending_2023_b'].sum()
total_savings    = kff_df['savings_if_intl_avg_b'].sum()
print(f"Total 2023 Medicare Part D spending on these 9 drugs: ${total_spending_9:.1f}B")
print(f"Estimated savings if paid international average prices: ${total_savings:.1f}B")
print(f"That's {total_savings/total_spending_9*100:.0f}% of current spending on these 9 drugs alone.")
