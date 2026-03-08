"""
Chart: Which drug gaps are growing vs. shrinking? (2019–2023)
For The American Healthcare Conundrum — Issue #1
"""
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['text.usetex'] = False
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import os, pathlib
_PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = str(_PROJECT_ROOT / 'figures' / '05_gap_trends.png')

# ── Palette ──────────────────────────────────────────────────────────────────
TEAL  = '#16A085'
RED   = '#C0392B'
DARK  = '#2C3E50'
MID   = '#4A5568'
WHITE = '#FFFFFF'

# ── Load data ─────────────────────────────────────────────────────────────────
df = pd.read_parquet(str(_PROJECT_ROOT / 'data' / 'raw' / 'part_d_long.parquet'))
drugs_2023 = pd.read_csv(str(_PROJECT_ROOT / 'results' / 'by_drug_2023.csv'))

EXCLUDE = ['Dexlansoprazole', 'Naproxen/Esomeprazole Mag', 'Desloratadine',
           'Ibuprofen/FAmotidine', 'Hydrocodone/Ibuprofen',
           'Omeprazole/Amoxicill/Rifabutin', 'Lansoprazole/Amoxiciln/Clarith',
           'Desloratadine/Pseudoephedrine', 'Famotidine/PF',
           'Famotidine In NaCl,Iso-Osm/PF', 'Esomeprazole Sodium']

raw = drugs_2023[~drugs_2023['generic_name'].isin(EXCLUDE)].copy()

# For Esomeprazole, force Nexium 24HR as the correct OTC comparator
esomep_row = (raw[raw['generic_name'] == 'Esomeprazole Magnesium']
              [raw['otc_brand'] == 'Nexium 24HR']
              .nlargest(1, 'savings'))

crosswalk = (raw[raw['generic_name'] != 'Esomeprazole Magnesium']
             .sort_values('savings', ascending=False)
             .drop_duplicates('generic_name'))
crosswalk = pd.concat([crosswalk, esomep_row], ignore_index=True)
crosswalk = crosswalk[['generic_name','otc_brand','category','otc_unit_cost']]

# Multi-year join
matched = df[
    (df['manufacturer'] == 'Overall') &
    (df['generic_name'].isin(crosswalk['generic_name']))
].merge(crosswalk, on='generic_name', how='left')

matched['savings'] = matched['tot_spending'] - matched['tot_claims'] * 30 * matched['otc_unit_cost']

yearly_drug = (matched
    .groupby(['generic_name', 'otc_brand', 'year'])
    .agg(savings=('savings', 'sum'))
    .reset_index())

s19 = yearly_drug[yearly_drug['year'] == 2019].set_index('generic_name')['savings']
s23 = yearly_drug[yearly_drug['year'] == 2023].set_index('generic_name')['savings']
brand = yearly_drug[yearly_drug['year'] == 2023].set_index('generic_name')['otc_brand']

summary = pd.DataFrame({'s19': s19, 's23': s23, 'brand': brand}).dropna()
summary['change'] = summary['s23'] - summary['s19']

# Keep only drugs with ≥$10M savings in at least one year (filter noise)
summary = summary[(summary['s19'].abs() > 10e6) | (summary['s23'].abs() > 10e6)]

# Sort: most-shrinking at bottom, most-growing at top
summary = summary.sort_values('change', ascending=True)

print("Final chart data:")
for idx, row in summary.iterrows():
    sign = '+' if row['change'] >= 0 else ''
    print(f"  {idx:35s}  {sign}${row['change']/1e6:+6.0f}M   "
          f"(${row['s19']/1e6:.0f}M → ${row['s23']/1e6:.0f}M)")

# ── Display labels ─────────────────────────────────────────────────────────────
LABEL_MAP = {
    'Esomeprazole Magnesium': 'Nexium 24HR (Esomeprazole)',
    'Fluticasone Propionate': 'Flonase (Fluticasone)',
    'Famotidine':             'Pepcid AC (Famotidine)',
    'Omeprazole':             'Prilosec OTC (Omeprazole)',
    'Omeprazole/Sodium Bicarbonate': 'Zegerid OTC (Omeprazole/Sod. Bicarb.)',
    'Azelastine HCl':         'Astepro (Azelastine)',
    'Mometasone Furoate':     'Nasonex 24HR (Mometasone)',
    'Levocetirizine Dihydrochloride': 'Xyzal (Levocetirizine)',
    'Cetirizine HCl':         'Zyrtec (Cetirizine)',
    'Ibuprofen':              'Advil / Motrin (Ibuprofen)',
    'Lansoprazole':           'Prevacid 24HR (Lansoprazole)',
    'Naproxen Sodium':        'Aleve (Naproxen)',
    'Azelastine/Fluticasone': 'Dymista (Azelastine/Fluticasone)',
    'Loperamide HCl':         'Imodium (Loperamide)',
    'Triamcinolone Acetonide':'Kenalog (Triamcinolone)',
    'Minoxidil':              'Rogaine (Minoxidil)',
    'Omeprazole Magnesium':   'Prilosec OTC (Omeprazole Mg)',
    'Diphenhydramine HCl':    'Benadryl (Diphenhydramine)',
}

labels   = [LABEL_MAP.get(idx, idx) for idx in summary.index]
changes  = summary['change'].values / 1e6
s19_vals = summary['s19'].values / 1e6
s23_vals = summary['s23'].values / 1e6
colors   = [RED if c < 0 else TEAL for c in changes]
n = len(summary)

# ── Figure ────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(13, max(7, n * 0.72 + 2.5)))
fig.patch.set_facecolor(WHITE)
ax.set_facecolor(WHITE)

y = np.arange(n)
ax.barh(y, changes, color=colors, edgecolor='white', linewidth=0.5,
        height=0.58, zorder=3)

# Zero line
ax.axvline(0, color=DARK, linewidth=1.4, zorder=4)

# Shading
xlim_max = max(abs(changes)) * 1.5
ax.set_xlim(-xlim_max, xlim_max)
ax.axvspan(0, xlim_max, alpha=0.035, color=TEAL, zorder=1)
ax.axvspan(-xlim_max, 0, alpha=0.035, color=RED, zorder=1)

# Value labels
for i, (chg, s19v, s23v) in enumerate(zip(changes, s19_vals, s23_vals)):
    ha = 'left' if chg >= 0 else 'right'
    offset = xlim_max * 0.015 * (1 if chg >= 0 else -1)
    sign = '+' if chg >= 0 else ''
    ax.text(chg + offset, i + 0.08,
            f'{sign}\${chg:,.0f}M',
            va='center', ha=ha, fontsize=8.5, fontweight='bold',
            color=TEAL if chg >= 0 else RED, zorder=5)
    ax.text(chg + offset, i - 0.20,
            f'\${s19v:,.0f}M \u2192 \${s23v:,.0f}M',
            va='center', ha=ha, fontsize=7, color=MID, zorder=5)

ax.set_yticks(y)
ax.set_yticklabels(labels, fontsize=9.5, color=DARK)
ax.tick_params(axis='x', labelsize=9, colors=MID)
ax.set_xlabel('Change in estimated potential savings, 2019 \u2192 2023 ($ millions)',
              fontsize=10, color=MID, labelpad=8)

# Section headers — pinned to axes corners using transAxes so they
# never collide with bar value labels regardless of data range
ax.text(0.985, 0.995, 'GAP GROWING \u2191\n(problem worsening)',
        ha='right', va='top', fontsize=8.5, fontweight='bold',
        color=TEAL, alpha=0.85, transform=ax.transAxes,
        bbox=dict(boxstyle='round,pad=0.25', facecolor='white',
                  edgecolor=TEAL, linewidth=0.8, alpha=0.9))
ax.text(0.015, 0.995, '\u2193 GAP SHRINKING\n(giving credit here)',
        ha='left', va='top', fontsize=8.5, fontweight='bold',
        color=RED, alpha=0.85, transform=ax.transAxes,
        bbox=dict(boxstyle='round,pad=0.25', facecolor='white',
                  edgecolor=RED, linewidth=0.8, alpha=0.9))

ax.set_title(
    'Which Drug Price Gaps Are Growing vs. Shrinking? (2019\u20132023)\n'
    'Estimated annual savings if Medicare Part D paid OTC retail prices',
    fontsize=12, fontweight='bold', color=DARK, pad=14)

note = (
    'Shrinking gaps may reflect: (1) generic Rx prices falling toward OTC levels independently of policy \u2014 credit where due; '
    '(2) declining claims volume;\n'
    '(3) beneficiaries switching to OTC alternatives. '
    'Growing gaps show where the problem is getting worse, not better.'
)
ax.text(0.5, -0.05, note, transform=ax.transAxes,
        ha='center', va='top', fontsize=7.5, color=MID, style='italic')

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='x', alpha=0.2, linestyle='--', zorder=0)

plt.tight_layout(rect=[0, 0.06, 1, 1])
plt.savefig(OUT, dpi=160, bbox_inches='tight', facecolor=WHITE)
plt.close()
print(f'\nSaved -> {OUT}')
