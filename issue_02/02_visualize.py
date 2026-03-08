"""
Issue #2 Charts: Brand Drug Price Differentials
The American Healthcare Conundrum

Charts:
  01: Three-price comparison (Medicare gross, Medicare negotiated, Intl avg)
  02: NHS vs Medicare — ratio chart
  03: RAND country ratios
  04: Dollar savings waterfall
"""
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['text.usetex'] = False
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

import os
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.join(_SCRIPT_DIR, 'figures', '')

# ── Palette (matches Issue #1) ────────────────────────────────────────────────
NAVY   = '#0A1628'
RED    = '#C0392B'
RED2   = '#E74C3C'
TEAL   = '#1ABC9C'
GOLD   = '#F39C12'
WHITE  = '#FFFFFF'
DARK   = '#1A202C'
MID    = '#4A5568'
LIGHT  = '#EDF2F7'
BLUE   = '#2980B9'

# ── Load data ─────────────────────────────────────────────────────────────────
_RESULTS = os.path.join(_SCRIPT_DIR, 'results')
kff  = pd.read_csv(os.path.join(_RESULTS, 'kff_drug_comparison.csv'))
nhs  = pd.read_csv(os.path.join(_RESULTS, 'nhs_vs_medicare.csv'))
rand = pd.read_csv(os.path.join(_RESULTS, 'rand_country_ratios.csv'))


# ══════════════════════════════════════════════════════════════════════════════
# CHART 01 — Three-Price Comparison (log scale)
# Medicare gross vs. negotiated vs. international avg, per 30-day supply
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(13, 7))
fig.patch.set_facecolor(WHITE)
ax.set_facecolor(WHITE)

# Sort by medicare_list descending for visual impact
kff_s = kff.sort_values('medicare_list', ascending=True).reset_index(drop=True)
n = len(kff_s)
y = np.arange(n)
H = 0.22   # bar height

# Bars: medicare_list, medicare_negotiated, intl_avg
bar_configs = [
    ('medicare_list',        '#B7182A', 'Medicare gross list price'),
    ('medicare_negotiated',  BLUE,      'Medicare 2026 negotiated price'),
    ('intl_avg',             TEAL,      'International average (11 OECD nations)'),
]

offsets = [0.24, 0, -0.24]
for (col, color, label), offset in zip(bar_configs, offsets):
    ax.barh(y + offset, kff_s[col], height=H, color=color,
            alpha=0.90, label=label, zorder=3)

# Drug labels on y-axis
ax.set_yticks(y)
ax.set_yticklabels(kff_s['drug'], fontsize=11, fontweight='bold', color=DARK)

# Value annotations on gross bars
for i, row in kff_s.iterrows():
    v = row['medicare_list']
    prefix = '\$'
    if v >= 1000:
        label_txt = f"{prefix}{v/1000:.1f}K"
    else:
        label_txt = f"{prefix}{v:,.0f}"
    ax.text(v * 1.015, i + 0.24, label_txt, va='center', ha='left',
            fontsize=8.5, color='#B7182A', fontweight='bold', zorder=5)

    # Annotate intl avg
    vi = row['intl_avg']
    if vi >= 1000:
        vi_txt = f"{prefix}{vi/1000:.1f}K"
    else:
        vi_txt = f"{prefix}{vi:,.0f}"
    ax.text(vi * 1.015, i - 0.24, vi_txt, va='center', ha='left',
            fontsize=8.5, color=TEAL, fontweight='bold', zorder=5)

ax.set_xscale('log')
ax.xaxis.set_major_formatter(mticker.FuncFormatter(
    lambda x, _: f'\${x:,.0f}' if x < 1000 else f'\${x/1000:.0f}K'))
ax.tick_params(axis='x', labelsize=9, colors=MID)
ax.set_xlabel('Price per 30-day supply (log scale, USD)', fontsize=10, color=MID, labelpad=8)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='x', alpha=0.15, linestyle='--', zorder=0)

legend = ax.legend(loc='lower right', fontsize=9.5,
                   framealpha=0.9, edgecolor=MID)

ax.set_title(
    'Medicare Pays 7\u201325\u00d7 More for Brand Drugs Than Peer Nations\n'
    'Price per 30-day supply for 9 high-spend Medicare Part D drugs (2023 gross / 2026 negotiated / 2024 OECD avg)',
    fontsize=12, fontweight='bold', color=DARK, pad=14)

note = (
    'Medicare gross list price = 2023 Part D gross cost per claim (pre-rebate). '
    'Actual Medicare net cost after rebates \u224825\u201330% lower, but still far above peer countries. '
    'Source: CMS Part D PUF 2023; Peterson-KFF (Dec 2024); RAND RRA788-3 (2024); NHS Drug Tariff.'
)
ax.text(0.5, -0.055, note, transform=ax.transAxes,
        ha='center', va='top', fontsize=7.5, color=MID, style='italic')

plt.tight_layout(rect=[0, 0.04, 1, 1])
plt.savefig(f'{FIG_DIR}01_three_price_comparison.png', dpi=160, bbox_inches='tight', facecolor=WHITE)
plt.close()
print(f'Saved chart 01')


# ══════════════════════════════════════════════════════════════════════════════
# CHART 02 — NHS vs Medicare Ratio (horizontal lollipop chart)
# How many times more expensive is Medicare than the UK NHS generic price
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(11, 5.5))
fig.patch.set_facecolor(WHITE)
ax.set_facecolor(WHITE)

nhs_s = nhs.sort_values('ratio_medicare_vs_nhs', ascending=True).reset_index(drop=True)
n = len(nhs_s)
y = np.arange(n)

# Lollipop
ax.hlines(y, 1, nhs_s['ratio_medicare_vs_nhs'], colors=MID, linewidth=2, alpha=0.4, zorder=2)
ax.scatter(nhs_s['ratio_medicare_vs_nhs'], y, s=200, color=RED2, zorder=5, edgecolors='white', linewidths=1.5)
ax.axvline(1, color=TEAL, linewidth=1.5, linestyle='--', alpha=0.8, zorder=1)

# Drug labels
ax.set_yticks(y)
ax.set_yticklabels(
    [f"{r['drug']}\n({r['generic']})" for _, r in nhs_s.iterrows()],
    fontsize=10, color=DARK
)

# Ratio annotations
for i, row in nhs_s.iterrows():
    r = row['ratio_medicare_vs_nhs']
    ax.text(r + max(r * 0.015, 5), i,
            f'{r:,.0f}\u00d7',
            va='center', ha='left', fontsize=11, fontweight='bold',
            color=RED2, zorder=6)
    # NHS price annotation
    ax.text(1.5, i - 0.28,
            f"NHS: \${row['nhs_30day_usd']:.2f} / 30 days",
            va='center', ha='left', fontsize=8.5, color=TEAL, style='italic')

ax.set_xlim(0, nhs_s['ratio_medicare_vs_nhs'].max() * 1.2)
ax.set_xlabel('Medicare price as multiple of NHS generic price (per 30-day supply)',
              fontsize=10, color=MID, labelpad=8)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.0f}\u00d7'))
ax.tick_params(axis='x', labelsize=9, colors=MID)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='x', alpha=0.12, linestyle='--', zorder=0)

# Label the 1x line
ax.text(1, n - 0.3, 'NHS\nprice', ha='center', va='top', fontsize=8,
        color=TEAL, fontweight='bold')

ax.set_title(
    'Same Molecule, Starkly Different Price\n'
    'Medicare gross cost vs. UK NHS generic reimbursement price (identical active ingredient)',
    fontsize=12, fontweight='bold', color=DARK, pad=14)

note = (
    'NHS prices = UK Drug Tariff Part VIIIA reimbursement price (March 2026) for generic equivalents. '
    'Apixaban and rivaroxaban have been generic in the UK since 2017\u20132021; empagliflozin and dapagliflozin since 2022\u20132024. '
    'In the US, brand manufacturers use patent thickets, pay-for-delay deals, and other tactics to maintain market exclusivity.'
)
ax.text(0.5, -0.09, note, transform=ax.transAxes,
        ha='center', va='top', fontsize=7.5, color=MID, style='italic',
        wrap=True)

plt.tight_layout(rect=[0, 0.07, 1, 1])
plt.savefig(f'{FIG_DIR}02_nhs_vs_medicare_ratio.png', dpi=160, bbox_inches='tight', facecolor=WHITE)
plt.close()
print(f'Saved chart 02')


# ══════════════════════════════════════════════════════════════════════════════
# CHART 03 — RAND Country Ratios (US brand price / country brand price)
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 5.5))
fig.patch.set_facecolor(WHITE)
ax.set_facecolor(WHITE)

rand_s = rand.sort_values('us_ratio', ascending=True).reset_index(drop=True)
n = len(rand_s)
y = np.arange(n)

colors = [RED2 if r >= 8 else BLUE if r >= 6 else MID
          for r in rand_s['us_ratio']]

bars = ax.barh(y, rand_s['us_ratio'] - 1, left=1,
               color=colors, edgecolor='white', linewidth=0.5,
               height=0.6, zorder=3)

# 1x reference line
ax.axvline(1, color=DARK, linewidth=1.5, zorder=4)

ax.set_yticks(y)
ax.set_yticklabels(rand_s['label'], fontsize=11, color=DARK)
ax.set_xlim(0, rand_s['us_ratio'].max() * 1.2)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.0f}\u00d7'))
ax.tick_params(axis='x', labelsize=9, colors=MID)
ax.set_xlabel('US brand drug prices as a multiple of each country\'s prices',
              fontsize=10, color=MID, labelpad=8)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='x', alpha=0.12, linestyle='--', zorder=0)

# Value labels
for i, row in rand_s.iterrows():
    ax.text(row['us_ratio'] + 0.1, i,
            f"{row['us_ratio']:.1f}\u00d7",
            va='center', ha='left', fontsize=11, fontweight='bold',
            color=colors[i], zorder=5)

ax.set_title(
    'US Brand Drug Prices Vs. Peer Countries\n'
    'How many times more the US pays for the same brand-name drugs (2022 data, RAND)',
    fontsize=12, fontweight='bold', color=DARK, pad=14)

note = (
    'Source: RAND Corporation, "International Prescription Drug Price Comparisons: Estimates Using 2022 Data," '
    'RRA788-3, February 2024. Ratios represent US manufacturer list prices / comparator country prices '
    'for brand-name originator drugs. US prices include estimated rebates per RAND methodology.'
)
ax.text(0.5, -0.09, note, transform=ax.transAxes,
        ha='center', va='top', fontsize=7.5, color=MID, style='italic')

plt.tight_layout(rect=[0, 0.07, 1, 1])
plt.savefig(f'{FIG_DIR}03_rand_country_ratios.png', dpi=160, bbox_inches='tight', facecolor=WHITE)
plt.close()
print(f'Saved chart 03')


# ══════════════════════════════════════════════════════════════════════════════
# CHART 04 — Spending & Savings Waterfall
# How much Medicare spends on each drug + potential savings at intl avg price
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(13, 6.5))
fig.patch.set_facecolor(WHITE)
ax.set_facecolor(WHITE)

kff_s4 = kff.sort_values('medicare_spending_2023_b', ascending=False).reset_index(drop=True)
n = len(kff_s4)
x = np.arange(n)
W = 0.35

savings  = kff_s4['savings_if_intl_avg_b'].values
spending = kff_s4['medicare_spending_2023_b'].values
intl_cost = spending - savings   # what Medicare would pay at intl avg prices

ax.bar(x - W/2, spending,  width=W, color='#B7182A', alpha=0.85,
       label='Medicare actual gross spending (2023)', zorder=3)
ax.bar(x + W/2, intl_cost, width=W, color=TEAL, alpha=0.85,
       label='Estimated cost if paid international average prices', zorder=3)

# Savings arrow + label
for i, (sp, sav, ic) in enumerate(zip(spending, savings, intl_cost)):
    # Arrow from international bar top to actual bar top
    if sav > 0.1:
        ax.annotate('', xy=(i - W/2, sp), xytext=(i + W/2, ic),
                    arrowprops=dict(arrowstyle='<->', color=GOLD,
                                   lw=1.5, mutation_scale=12), zorder=6)
        ax.text(i, sp + sp * 0.03,
                f'save\n\${sav:.1f}B',
                ha='center', va='bottom', fontsize=8, fontweight='bold',
                color=GOLD, zorder=7)

ax.set_xticks(x)
ax.set_xticklabels(kff_s4['drug'], fontsize=11, fontweight='bold', color=DARK,
                   rotation=0)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'\${v:.0f}B'))
ax.tick_params(axis='y', labelsize=9, colors=MID)
ax.set_ylabel('Annual Medicare Part D spending (billions USD)', fontsize=10, color=MID)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', alpha=0.15, linestyle='--', zorder=0)
ax.legend(loc='upper right', fontsize=9.5, framealpha=0.9, edgecolor=MID)

# Total summary annotation
total_sp  = spending.sum()
total_sav = savings.sum()
ax.text(0.98, 0.92,
        f'9-drug total:  \${total_sp:.0f}B spent\n'
        f'Estimated savings: \${total_sav:.0f}B ({total_sav/total_sp*100:.0f}%)',
        transform=ax.transAxes, ha='right', va='top',
        fontsize=10, fontweight='bold', color=DARK,
        bbox=dict(boxstyle='round,pad=0.4', facecolor=LIGHT,
                  edgecolor=MID, linewidth=1))

ax.set_title(
    'Medicare Overpays \$49 Billion on Just 9 Brand Drugs\n'
    '2023 gross spending vs. estimated cost at 11-country OECD average price',
    fontsize=12, fontweight='bold', color=DARK, pad=14)

note = (
    'Savings estimate = (Medicare gross cost per claim \u2212 international average cost) \u00d7 total Medicare claims 2023. '
    'Medicare gross costs are pre-rebate; actual net overpayment may be lower but remains substantial. '
    'International average from Peterson-KFF analysis of 11 OECD countries (2024).'
)
ax.text(0.5, -0.055, note, transform=ax.transAxes,
        ha='center', va='top', fontsize=7.5, color=MID, style='italic')

plt.tight_layout(rect=[0, 0.04, 1, 1])
plt.savefig(f'{FIG_DIR}04_spending_and_savings.png', dpi=160, bbox_inches='tight', facecolor=WHITE)
plt.close()
print(f'Saved chart 04')


# ══════════════════════════════════════════════════════════════════════════════
# CHART 05 — Hero Stat: Eliquis Deep Dive
# One drug, four price points — a clear narrative in a single chart
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(11, 5.5))
fig.patch.set_facecolor(WHITE)
ax.set_facecolor(WHITE)

prices = [862, 231, 59, 1.50]
labels = [
    'Medicare\ngross list\n(2023)',
    'Medicare\nnegotiated\n(2026 IRA)',
    'International\naverage\n(11 OECD)',
    'UK NHS\ngeneric\n(2026)'
]
colors = ['#B7182A', BLUE, TEAL, '#16A085']

bars = ax.bar(range(4), prices, color=colors, width=0.55,
              edgecolor='white', linewidth=1.5, zorder=3)

# Value labels on bars
for i, (p, bar) in enumerate(zip(prices, bars)):
    if p >= 1:
        txt = f'\${p:,.0f}' if p >= 10 else f'\${p:.2f}'
    else:
        txt = f'\${p:.2f}'
    ax.text(i, p + prices[0] * 0.012, txt,
            ha='center', va='bottom', fontsize=12, fontweight='bold',
            color=colors[i], zorder=5)

# Ratio labels below x-axis
ratios = [1, prices[0]/prices[1], prices[0]/prices[2], prices[0]/prices[3]]
ratio_labels = ['baseline', f'{ratios[1]:.0f}\u00d7 cheaper', f'{ratios[2]:.0f}\u00d7 cheaper', f'{ratios[3]:,.0f}\u00d7 cheaper']
for i, (r, rl) in enumerate(zip(ratios, ratio_labels)):
    ax.text(i, -prices[0]*0.045, rl, ha='center', va='top', fontsize=9.5,
            color=colors[i], fontweight='bold' if i > 0 else 'normal')

ax.set_xticks(range(4))
ax.set_xticklabels(labels, fontsize=10.5, color=DARK)
ax.set_ylim(-prices[0]*0.08, prices[0]*1.18)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'\${v:,.0f}' if v >= 0 else ''))
ax.tick_params(axis='y', labelsize=9, colors=MID)
ax.set_ylabel('Price per 30-day supply (USD)', fontsize=10, color=MID)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', alpha=0.12, linestyle='--', zorder=0)

ax.set_title(
    'Eliquis (Apixaban): Four Prices, One Molecule\n'
    '\$18.3 billion in annual Medicare spending on a drug that costs \$1.50 in the UK',
    fontsize=12, fontweight='bold', color=DARK, pad=14)

note = (
    'Apixaban is the active ingredient in Eliquis. It has been available as a generic in the UK since 2017. '
    'In the US, Bristol-Myers Squibb and Pfizer have used patent extensions and pay-for-delay settlements to maintain exclusivity. '
    'Eliquis remained the #1 Medicare Part D drug by spending in 2023 (\$18.3B).'
)
ax.text(0.5, -0.13, note, transform=ax.transAxes,
        ha='center', va='top', fontsize=7.5, color=MID, style='italic')

plt.tight_layout(rect=[0, 0.10, 1, 1])
plt.savefig(f'{FIG_DIR}05_eliquis_deep_dive.png', dpi=160, bbox_inches='tight', facecolor=WHITE)
plt.close()
print(f'Saved chart 05')

print('\nAll charts saved.')
