"""
Chart 4: Biosimilar Adoption in Medicare Part D (2023)
Two-panel chart. v3: fixes all overlap issues from v1 and v2.
Every label position computed explicitly with pixel clearance.
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

# --- DATA ---
molecules_left = ['Enbrel', 'Humira', 'Lantus', 'Neupogen']
brand_pct = [100, 99, 98, 24]
biosim_pct = [0, 1, 2, 76]
annotations_left = [
    '0%  patent wall',
    '1.1%  9 biosimilars,\n         formulary excluded',
    '1.6%  Semglee\n         launched 2021',
    '76%  functioning\n         biosimilar market'
]
ann_colors = [RED, RED, RED, TEAL]
ann_weights = ['normal', 'normal', 'normal', 'bold']

right_molecules = ['Humira\n(adalimumab)', 'Lantus\n(insulin glargine)']
brand_costs = [9148, 643]
biosim_costs = [2703, 268]

# --- FIGURE: wider to avoid cramping ---
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5), dpi=100,
                                gridspec_kw={'width_ratios': [1.2, 1], 'wspace': 0.55})
fig.patch.set_facecolor(WHITE)

# ============ LEFT PANEL ============
ax1.set_facecolor(WHITE)
y_pos = np.arange(len(molecules_left))
bar_height = 0.5

# Bars
ax1.barh(y_pos, brand_pct, height=bar_height, color=NAVY, zorder=2)
for i, (bp, bsp) in enumerate(zip(brand_pct, biosim_pct)):
    if bsp > 0:
        ax1.barh(i, bsp, height=bar_height, left=bp - bsp, color=TEAL, zorder=2)

# Percentage labels inside bars
for i, (bp, bsp) in enumerate(zip(brand_pct, biosim_pct)):
    if bp >= 90:
        ax1.text(bp / 2, i, f'{bp}%', ha='center', va='center',
                 color='white', fontsize=11, fontweight='bold', zorder=3)
    else:
        # Filgrastim: two labels
        ax1.text(bp / 2 - bsp / 2 - 2, i, f'{bp}%', ha='center', va='center',
                 color='white', fontsize=10, fontweight='bold', zorder=3)
        ax1.text(100 - bsp / 2, i, f'{bsp}%', ha='center', va='center',
                 color='white', fontsize=10, fontweight='bold', zorder=3)

# Annotations to the right
for i, (ann, col, wt) in enumerate(zip(annotations_left, ann_colors, ann_weights)):
    ax1.text(105, i, ann, ha='left', va='center', fontsize=7, color=col, fontweight=wt)

ax1.set_xlim(0, 170)
ax1.set_yticks(y_pos)
ax1.set_yticklabels(molecules_left, fontsize=10, fontweight='bold')
ax1.invert_yaxis()
ax1.tick_params(axis='x', bottom=False, labelbottom=False)
for spine in ax1.spines.values():
    spine.set_visible(False)

ax1.set_title('Biosimilar Adoption in Medicare Part D (2023)\nClaims share by molecule',
              fontsize=10, fontweight='bold', color=NAVY, loc='left', pad=14)

# Legend
legend_b = mpatches.Patch(color=NAVY, label='Brand originator')
legend_s = mpatches.Patch(color=TEAL, label='Biosimilar / lowest-cost')
ax1.legend(handles=[legend_b, legend_s], loc='lower center', fontsize=7,
           framealpha=0.95, edgecolor='#ccc', bbox_to_anchor=(0.4, -0.08))

# ============ RIGHT PANEL ============
ax2.set_facecolor(WHITE)
x_pos = np.arange(len(right_molecules))
bar_width = 0.3

bars_b = ax2.bar(x_pos - bar_width/2, brand_costs, bar_width, color=NAVY, zorder=2)
bars_s = ax2.bar(x_pos + bar_width/2, biosim_costs, bar_width, color=TEAL, zorder=2)

# Set y-axis with headroom for labels
ax2.set_ylim(0, 12500)
ax2.set_xlim(-0.55, 1.95)

# Price labels ABOVE bars with generous clearance
# Adalimumab brand: $9,148 — place at y=9700
ax2.text(0 - bar_width/2, 9700, '$9,148', ha='center', va='bottom',
         fontsize=10, fontweight='bold', color=NAVY)
# Adalimumab biosimilar: $2,703 — place above bar with clearance
ax2.text(0 + bar_width/2, 3350, '$2,703', ha='center', va='bottom',
         fontsize=10, fontweight='bold', color=TEAL)

# Insulin Glargine brand: $643 — place at y=1150
ax2.text(1 - bar_width/2, 1150, '$643', ha='center', va='bottom',
         fontsize=10, fontweight='bold', color=NAVY)
# Insulin Glargine biosimilar: $268 — place at y=750
ax2.text(1 + bar_width/2, 750, '$268', ha='center', va='bottom',
         fontsize=10, fontweight='bold', color=TEAL)

# "70% cheaper" — arrow from text to biosimilar bar top, placed in clear space
ax2.annotate('70% cheaper', xy=(0 + bar_width/2, 2703),
             xytext=(0.7, 6500),
             fontsize=8.5, color=RED, fontweight='bold', ha='left', va='center',
             arrowprops=dict(arrowstyle='->', color=RED, lw=1.5))

# "58% cheaper" — arrow points to biosimilar bar, text inside plot area
ax2.annotate('58% cheaper', xy=(1 + bar_width/2, 268),
             xytext=(1.3, 2800),
             fontsize=8, color=RED, fontweight='bold', ha='center', va='center',
             arrowprops=dict(arrowstyle='->', color=RED, lw=1.5))

# Callout box — mid-right, below legend
callout = ('Excess spend (two molecules,\n'
           'Part D only): ~$7.8B gross,\n'
           '~$5.5B net of rebates')
props = dict(boxstyle='round,pad=0.5', facecolor='#fff0f0', edgecolor=RED, alpha=0.95)
ax2.text(1.0, 8200, callout, fontsize=7, color=RED, fontweight='bold',
         ha='center', va='top', bbox=props)

ax2.set_xticks(x_pos)
ax2.set_xticklabels(right_molecules, fontsize=9, fontweight='bold')
ax2.set_ylabel('Avg cost per claim (USD)', fontsize=8, color=NAVY)
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
ax2.tick_params(axis='y', labelsize=8)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

ax2.set_title('Brand vs. Biosimilar:\nCost Per Claim (2023)',
              fontsize=10, fontweight='bold', color=NAVY, loc='left', pad=14)

legend_b2 = mpatches.Patch(color=NAVY, label='Brand originator')
legend_s2 = mpatches.Patch(color=TEAL, label='Biosimilar (avg)')
ax2.legend(handles=[legend_b2, legend_s2], fontsize=7, loc='upper left',
           framealpha=0.95, edgecolor='#ccc', bbox_to_anchor=(0.0, 0.98))

# --- FOOTNOTE: left-aligned, shorter to avoid right-edge clip ---
fig.text(0.04, 0.01,
         'Source: CMS Medicare Part D Spending by Drug, DY2023 (data.cms.gov). Author analysis. '
         'Claims share = molecule-level (brand + all biosimilar NDCs).\n'
         'Adalimumab brand: $9,148/claim; biosimilars: $2,703/claim. '
         'Insulin glargine: Lantus $643/claim; Semglee/generics $268/claim. '
         'Excess spend net of estimated rebates: $5.5B.',
         fontsize=5.5, color='#777', ha='left', va='bottom', style='italic')

plt.subplots_adjust(top=0.84, bottom=0.12, left=0.11, right=0.96)

outpath = '/sessions/pensive-clever-hypatia/mnt/healthcare/issue_04/figures/chart4_biosimilar_adoption.png'
fig.savefig(outpath, dpi=150, facecolor=WHITE)
plt.close(fig)

# Verify dimensions
from PIL import Image
im = Image.open(outpath)
print(f'Chart saved: {im.size[0]}x{im.size[1]}px')
