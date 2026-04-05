#!/usr/bin/env python3
"""
Chart 1: Hospital Supply Cost Variance by Bed Size (CMI-Adjusted)
Horizontal range chart: P25-P75 teal bars with red diamond P50 markers.
Ratio annotations placed far right with explicit vertical spacing.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

NAVY = '#1A1F2E'
TEAL = '#0E8A72'
RED = '#B7182A'
GOLD = '#D4AF37'
WHITE = '#F8F8F6'

# Data: label, N, P25, P50, P75, ratio (P75/P25)
data = [
    ('Major (500+)',   149,  451,  777, 1329, 2.9),
    ('Large (300-499)', 320, 543,  893, 1265, 2.3),
    ('Medium (100-299)',1511, 382,  700, 1165, 3.0),
    ('Small (1-99)',   3499, 197,  663, 1509, 7.7),
]

fig, ax = plt.subplots(figsize=(10, 5.5), dpi=100)
fig.patch.set_facecolor(WHITE)
ax.set_facecolor(WHITE)

y_positions = list(range(len(data)))

for i, (label, n, p25, p50, p75, ratio) in enumerate(data):
    # P25-P75 range bar
    ax.barh(i, p75 - p25, left=p25, height=0.5, color=TEAL, alpha=0.65,
            edgecolor=TEAL, linewidth=1.5)
    # P50 diamond
    ax.scatter([p50], [i], s=120, marker='D', color=RED, zorder=5,
              edgecolors=WHITE, linewidth=1.2)

# Y-axis labels: bed size + N on same line
y_labels = [f"{d[0]}  (N={d[1]:,})" for d in data]
ax.set_yticks(y_positions)
ax.set_yticklabels(y_labels, fontsize=9.5, fontweight='bold', color=NAVY, family='DejaVu Sans')
ax.set_ylim(-0.6, len(data) - 0.4)

# X-axis
ax.set_xlabel('Supply Cost Per Discharge ($)', fontsize=11, fontweight='bold',
              color=NAVY, family='DejaVu Sans')
ax.set_xlim(0, 2200)
ax.set_xticks([0, 250, 500, 750, 1000, 1250, 1500, 1750, 2000])
ax.set_xticklabels(['$0', '$250', '$500', '$750', '$1,000', '$1,250', '$1,500', '$1,750', '$2,000'],
                    fontsize=8.5, color=NAVY, family='DejaVu Sans')

# Ratio annotations: place to the right of P75, with enough x-headroom
for i, (label, n, p25, p50, p75, ratio) in enumerate(data):
    ax.text(p75 + 80, i, f'{ratio:.1f}×',
            fontsize=10, fontweight='bold', color=RED, family='DejaVu Sans',
            va='center', ha='left',
            bbox=dict(boxstyle='round,pad=0.3', facecolor=WHITE, edgecolor=RED, linewidth=1.2))

# Title
fig.suptitle('Hospital Supply Cost Variance by Bed Size',
             fontsize=14, fontweight='bold', color=NAVY, family='DejaVu Sans', y=0.97)
fig.text(0.5, 0.915, 'CMI-adjusted per discharge  ·  FY2023  ·  5,480 hospitals',
         fontsize=9, color=NAVY, family='DejaVu Sans', ha='center', style='italic')

# Legend
legend_elements = [
    mpatches.Patch(facecolor=TEAL, alpha=0.65, edgecolor=TEAL, label='P25–P75 Range'),
    Line2D([0], [0], marker='D', color='w', markerfacecolor=RED, markersize=8,
           markeredgecolor=WHITE, label='Median (P50)'),
]
ax.legend(handles=legend_elements, loc='lower right', fontsize=9, frameon=True,
          fancybox=False, edgecolor=NAVY, framealpha=0.95,
          prop={'family': 'DejaVu Sans'})

# Grid
ax.grid(axis='x', alpha=0.2, linestyle='--', color=NAVY)
ax.set_axisbelow(True)

# Spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color(NAVY)
ax.spines['bottom'].set_color(NAVY)

# Footnote
fig.text(0.12, 0.02,
         'P75/P25 ratio (red) shows variance within each peer group. Higher ratios = more unexplained spending differences among similar hospitals.',
         fontsize=6, color=NAVY, family='DejaVu Sans', ha='left', style='italic')

plt.subplots_adjust(top=0.87, bottom=0.13, left=0.30, right=0.95)
plt.savefig('/sessions/friendly-lucid-thompson/mnt/healthcare/issue_06/figures/chart1_supply_variance.png',
            dpi=150, facecolor=WHITE, edgecolor='none')
print('Chart 1 saved.')
plt.close(fig)
