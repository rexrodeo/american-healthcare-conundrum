"""
Chart 4 v4: Biosimilar Adoption in Medicare Part D (2023)
Complete rewrite focusing on zero overlaps.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

NAVY = '#1A1F2E'
TEAL = '#0E8A72'
RED = '#B7182A'
WHITE = '#F8F8F6'

# ===== LEFT PANEL DATA =====
left_labels = ['Enbrel', 'Humira', 'Lantus', 'Neupogen']
brand_pct = [100, 99, 98, 24]
biosim_pct = [0, 1, 2, 76]

# ===== RIGHT PANEL DATA =====
brand_costs = [9148, 643]
biosim_costs = [2703, 268]

# ===== FIGURE =====
fig = plt.figure(figsize=(10, 5.5), dpi=100, facecolor=WHITE)

# Use gridspec for precise control
gs = fig.add_gridspec(1, 2, width_ratios=[1.1, 1], wspace=0.45,
                       left=0.16, right=0.95, top=0.85, bottom=0.12)
ax1 = fig.add_subplot(gs[0])
ax2 = fig.add_subplot(gs[1])

# ============ LEFT PANEL: Horizontal bars ============
ax1.set_facecolor(WHITE)
y = np.arange(4)
bh = 0.5

for i in range(4):
    # Dark bar (brand)
    ax1.barh(i, brand_pct[i], height=bh, color=NAVY, zorder=2)
    # Teal bar (biosimilar) starts where brand ends
    if biosim_pct[i] > 0:
        ax1.barh(i, biosim_pct[i], height=bh,
                 left=brand_pct[i], color=TEAL, zorder=2)

# Inside labels
for i in range(4):
    if brand_pct[i] >= 90:
        ax1.text(50, i, f'{brand_pct[i]}%', ha='center', va='center',
                 color='white', fontsize=12, fontweight='bold', zorder=3)
    else:
        # Neupogen: brand 24% label centered in dark portion
        ax1.text(12, i, f'{brand_pct[i]}%', ha='center', va='center',
                 color='white', fontsize=10, fontweight='bold', zorder=3)
        # biosimilar label centered in teal portion (starts at brand_pct, width = biosim_pct)
        teal_center = brand_pct[i] + biosim_pct[i] / 2  # e.g. 24 + 38 = 62
        ax1.text(teal_center, i, f'{biosim_pct[i]}%', ha='center', va='center',
                 color='white', fontsize=10, fontweight='bold', zorder=3)

# Right-side annotations
anns = [
    ('0%  patent wall', RED, 'normal'),
    ('1.1%  9 biosimilars,\n         formulary excluded', RED, 'normal'),
    ('1.6%  Semglee launched 2021', RED, 'normal'),
    ('76%  functioning biosimilar market', TEAL, 'bold'),
]
for i, (txt, col, wt) in enumerate(anns):
    ax1.text(105, i, txt, ha='left', va='center', fontsize=7, color=col, fontweight=wt)

ax1.set_xlim(0, 175)
ax1.set_yticks(y)
ax1.set_yticklabels(left_labels, fontsize=10, fontweight='bold')
ax1.invert_yaxis()
ax1.tick_params(axis='x', bottom=False, labelbottom=False)
for s in ax1.spines.values():
    s.set_visible(False)

ax1.set_title('Biosimilar Adoption in Medicare Part D (2023)\nClaims share by molecule',
              fontsize=10, fontweight='bold', color=NAVY, loc='left', pad=12)

leg1 = [mpatches.Patch(color=NAVY, label='Brand originator'),
        mpatches.Patch(color=TEAL, label='Biosimilar / lowest-cost')]
ax1.legend(handles=leg1, loc='lower center', fontsize=7,
           framealpha=0.9, edgecolor='#ccc', bbox_to_anchor=(0.45, -0.1))

# ============ RIGHT PANEL: Grouped bars ============
ax2.set_facecolor(WHITE)
x = np.array([0, 1])
w = 0.28

ax2.bar(x - w/2, brand_costs, w, color=NAVY, zorder=2)
ax2.bar(x + w/2, biosim_costs, w, color=TEAL, zorder=2)

ax2.set_ylim(0, 12000)
ax2.set_xlim(-0.5, 1.7)

# === LABEL STRATEGY: all labels OUTSIDE bars, using annotations with offsets ===

# Humira brand $9,148 — directly above bar, plenty of room
ax2.text(0 - w/2, 9500, '$9,148', ha='center', va='bottom',
         fontsize=10, fontweight='bold', color=NAVY)

# Humira biosimilar $2,703 — above the teal bar with clearance
ax2.text(0 + w/2, 3400, '$2,703', ha='center', va='bottom',
         fontsize=9, fontweight='bold', color=TEAL)

# Lantus brand $643 — above its bar with clear space
ax2.text(1 - w/2, 950, '$643', ha='center', va='bottom',
         fontsize=9, fontweight='bold', color=NAVY)

# Lantus biosimilar $268 — above its bar
ax2.text(1 + w/2, 550, '$268', ha='center', va='bottom',
         fontsize=9, fontweight='bold', color=TEAL)

# "70% cheaper" — in clear right-side space
ax2.text(0.75, 6000, '70%\ncheaper', fontsize=9, color=RED, fontweight='bold',
         ha='center', va='center')

# "58% cheaper" — below the 70% text, also in right-side space
ax2.text(1.45, 3200, '58%\ncheaper', fontsize=9, color=RED, fontweight='bold',
         ha='center', va='center')

# Callout box — upper area
callout = 'Excess spend (two molecules,\nPart D only): ~$7.8B gross,\n~$5.5B net of rebates'
box = dict(boxstyle='round,pad=0.4', facecolor='#fff0f0', edgecolor=RED, alpha=0.95)
ax2.text(1.1, 10800, callout, fontsize=6.5, color=RED, fontweight='bold',
         ha='center', va='top', bbox=box)

ax2.set_xticks(x)
ax2.set_xticklabels(['Humira\n(adalimumab)', 'Lantus\n(ins. glargine)'],
                     fontsize=8.5, fontweight='bold')
ax2.set_ylabel('Avg cost per claim (USD)', fontsize=8, color=NAVY)
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: f'${v:,.0f}'))
ax2.tick_params(axis='y', labelsize=7.5)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

ax2.set_title('Brand vs. Biosimilar:\nCost Per Claim (2023)',
              fontsize=10, fontweight='bold', color=NAVY, loc='left', pad=12)

leg2 = [mpatches.Patch(color=NAVY, label='Brand originator'),
        mpatches.Patch(color=TEAL, label='Biosimilar (avg)')]
ax2.legend(handles=leg2, fontsize=7, loc='upper left',
           framealpha=0.9, edgecolor='#ccc', bbox_to_anchor=(0.0, 0.97))

# Footnote
fig.text(0.04, 0.01,
         'Source: CMS Medicare Part D Spending by Drug, DY2023 (data.cms.gov). Author analysis. '
         'Claims share = molecule-level (brand + all biosimilar NDCs).\n'
         'Adalimumab: $9,148/claim (brand), $2,703 (biosimilar). '
         'Insulin glargine: $643 (Lantus), $268 (Semglee/generics). '
         'Excess net of rebates: $5.5B.',
         fontsize=5.5, color='#777', ha='left', va='bottom', style='italic')

outpath = '/sessions/pensive-clever-hypatia/mnt/healthcare/issue_04/figures/chart4_biosimilar_adoption.png'
fig.savefig(outpath, dpi=150, facecolor=WHITE)
plt.close(fig)

from PIL import Image
im = Image.open(outpath)
print(f'Saved: {im.size[0]}x{im.size[1]}px')
