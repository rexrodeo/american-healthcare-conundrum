"""
Chart 4: Biosimilar Adoption in Medicare Part D (2023)
Two-panel chart: left = claims share by molecule, right = cost per claim comparison
Fixes overlap issues from v1.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Brand colors
NAVY = '#1A1F2E'
TEAL = '#0E8A72'
RED = '#B7182A'
GOLD = '#D4AF37'
WHITE = '#F8F8F6'
DARK_BAR = '#1A1F2E'

# --- DATA ---
molecules = ['Etanercept\n(Enbrel)', 'Adalimumab\n(Humira)', 'Insulin Glargine\n(Lantus)', 'Filgrastim\n(Neupogen)']
brand_pct = [100, 99, 98, 24]
biosim_pct = [0, 1, 2, 76]
annotations_left = [
    '0% — patent wall',
    '1.1% — 9 biosimilars,\nformulary excluded',
    '1.6% — Semglee\nlaunched 2021',
    '76% — functioning\nbiosimilar market'
]

# Right panel data
right_molecules = ['Adalimumab\n(Humira)', 'Insulin Glargine\n(Lantus)']
brand_costs = [9148, 643]
biosim_costs = [2703, 268]

# --- FIGURE ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5.5), dpi=100,
                                gridspec_kw={'width_ratios': [1.1, 1], 'wspace': 0.45})
fig.patch.set_facecolor(WHITE)

# ============ LEFT PANEL: Horizontal stacked bars ============
ax1.set_facecolor(WHITE)
y_pos = np.arange(len(molecules))
bar_height = 0.55

# Brand bars (dark)
bars_brand = ax1.barh(y_pos, brand_pct, height=bar_height, color=DARK_BAR, zorder=2)
# Biosimilar bars (teal, stacked)
bars_biosim = ax1.barh(y_pos, biosim_pct, height=bar_height, left=[b - bs for b, bs in zip(brand_pct, biosim_pct)],
                        color=TEAL, zorder=2)

# Labels inside bars
for i, (bp, bsp) in enumerate(zip(brand_pct, biosim_pct)):
    if bp >= 90:
        ax1.text(50, i, f'{bp}%', ha='center', va='center', color='white', fontsize=11, fontweight='bold', zorder=3)
    elif bp >= 20:
        ax1.text(bp/2 - bsp/2, i, f'{bp}%', ha='center', va='center', color='white', fontsize=10, fontweight='bold', zorder=3)
    if bsp >= 10:
        ax1.text(100 - bsp/2, i, f'{bsp}%', ha='center', va='center', color='white', fontsize=10, fontweight='bold', zorder=3)

# Annotations to the right of bars
for i, ann in enumerate(annotations_left):
    color = TEAL if i == 3 else RED
    fontweight = 'bold' if i == 3 else 'normal'
    ax1.text(104, i, ann, ha='left', va='center', fontsize=7.5, color=color, fontweight=fontweight)

ax1.set_xlim(0, 165)
ax1.set_yticks(y_pos)
ax1.set_yticklabels(molecules, fontsize=9, fontweight='bold')
ax1.invert_yaxis()
ax1.set_xlabel('')
ax1.tick_params(axis='x', which='both', bottom=False, labelbottom=False)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.spines['bottom'].set_visible(False)

ax1.set_title('Biosimilar Adoption in Medicare Part D (2023)\nClaims share by molecule',
              fontsize=10, fontweight='bold', color=NAVY, loc='left', pad=12)

# Legend for left panel
legend_brand = mpatches.Patch(color=DARK_BAR, label='Brand originator')
legend_biosim = mpatches.Patch(color=TEAL, label='Biosimilar / lowest-cost')
ax1.legend(handles=[legend_brand, legend_biosim], loc='lower right', fontsize=7.5,
           framealpha=0.9, edgecolor='#ddd')

# ============ RIGHT PANEL: Grouped bar chart ============
ax2.set_facecolor(WHITE)
x_pos = np.arange(len(right_molecules))
bar_width = 0.32

bars_b = ax2.bar(x_pos - bar_width/2, brand_costs, bar_width, color=DARK_BAR, zorder=2, label='Brand originator')
bars_s = ax2.bar(x_pos + bar_width/2, biosim_costs, bar_width, color=TEAL, zorder=2, label='Biosimilar (avg)')

# Price labels above bars — with enough clearance
for bar, cost in zip(bars_b, brand_costs):
    ax2.text(bar.get_x() + bar.get_width()/2, cost + 250, f'${cost:,}',
             ha='center', va='bottom', fontsize=10, fontweight='bold', color=NAVY)

for bar, cost in zip(bars_s, biosim_costs):
    ax2.text(bar.get_x() + bar.get_width()/2, cost + 250, f'${cost:,}',
             ha='center', va='bottom', fontsize=10, fontweight='bold', color=TEAL)

# Percentage cheaper annotations — placed well below the brand label, connected by arrow
# Adalimumab: 70% cheaper
ax2.annotate('70% cheaper', xy=(0 + bar_width/2, 2703 + 250),
             xytext=(0.55, 6200),
             fontsize=8, color=RED, fontweight='bold',
             arrowprops=dict(arrowstyle='->', color=RED, lw=1.2),
             ha='left', va='center')

# Insulin Glargine: 58% cheaper
ax2.annotate('58% cheaper', xy=(1 + bar_width/2, 268 + 150),
             xytext=(1.4, 1800),
             fontsize=8, color=RED, fontweight='bold',
             arrowprops=dict(arrowstyle='->', color=RED, lw=1.2),
             ha='left', va='center')

# Callout box for excess spend — positioned in upper right clear space
callout_text = ('Excess spend\n'
                '(adalimumab +\n'
                'insulin glargine,\n'
                'Part D only):\n'
                '~$7.8B gross\n'
                '~$5.5B net')
props = dict(boxstyle='round,pad=0.5', facecolor='#fff0f0', edgecolor=RED, alpha=0.95)
ax2.text(1.65, 8500, callout_text, fontsize=7.5, color=RED, fontweight='bold',
         ha='center', va='top', bbox=props)

ax2.set_ylim(0, 11000)
ax2.set_xlim(-0.6, 2.1)
ax2.set_xticks(x_pos)
ax2.set_xticklabels(right_molecules, fontsize=9, fontweight='bold')
ax2.set_ylabel('Average cost per claim (USD)', fontsize=8, color=NAVY)
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
ax2.tick_params(axis='y', labelsize=8)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

ax2.set_title('Brand vs. Biosimilar: Cost Per Claim (2023)\nMedicare pays brand prices despite alternatives',
              fontsize=10, fontweight='bold', color=NAVY, loc='left', pad=12)

ax2.legend(fontsize=7.5, loc='upper right', framealpha=0.9, edgecolor='#ddd')

# --- FOOTNOTE ---
fig.text(0.03, 0.01,
         'Source: CMS Medicare Part D Spending by Drug, DY2023 (data.cms.gov, released May 2025). Author analysis. '
         'Claims share = molecule-level (brand + all biosimilar NDCs).\n'
         'Adalimumab brand: $9,148 avg/claim; biosimilars: $2,703 avg/claim. '
         'Insulin glargine: Lantus $643 avg/claim; Semglee/generics $268 avg/claim. '
         'Excess spend net of estimated rebates: $5.5B (two molecules, Medicare Part D only).',
         fontsize=5.5, color='#666', ha='left', va='bottom', style='italic')

plt.subplots_adjust(top=0.85, bottom=0.09, left=0.13, right=0.97)

fig.savefig('/sessions/pensive-clever-hypatia/mnt/healthcare/issue_04/figures/chart4_biosimilar_adoption.png',
            dpi=150, facecolor=WHITE, bbox_inches=None)
plt.close(fig)
print('Chart saved successfully.')
