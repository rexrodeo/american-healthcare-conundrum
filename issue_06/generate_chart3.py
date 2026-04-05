#!/usr/bin/env python3
"""
Chart 3: Supply Cost Decomposition ($170.9B)
Horizontal stacked bar — three segments with external annotations.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Brand colors
NAVY = '#1A1F2E'
TEAL = '#0E8A72'
RED = '#B7182A'
GOLD = '#D4AF37'
WHITE = '#F8F8F6'

fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
fig.patch.set_facecolor(WHITE)
ax.set_facecolor(WHITE)

# Data
categories = ['Medical Supplies', 'Implantable Devices', 'Drugs Charged\nto Patients']
short_labels = ['Supplies', 'Devices', 'Drugs']
values = [40.4, 48.7, 81.9]
percentages = [23.6, 28.5, 47.9]
colors = [TEAL, GOLD, RED]

# Draw horizontal stacked bar
bar_height = 0.5
y_pos = 0
left_pos = 0

bars = []
for i, (val, color) in enumerate(zip(values, colors)):
    bar = ax.barh(y_pos, val, left=left_pos, height=bar_height, color=color, alpha=0.88,
                  edgecolor=NAVY, linewidth=1.5)
    bars.append((left_pos, val))

    # Inside label: dollar amount only (short, fits in all segments)
    cx = left_pos + val / 2
    ax.text(cx, y_pos, f'${val:.1f}B', va='center', ha='center',
            fontsize=12, fontweight='bold', color=WHITE, family='DejaVu Sans')

    left_pos += val

# External annotations above the bar — category names and percentages
# Positioned with leader lines pointing down to bar center
anno_y = 0.48  # just above bar top edge
for i, (cat, val, pct) in enumerate(zip(categories, values, percentages)):
    cx = bars[i][0] + bars[i][1] / 2
    # Stagger heights to avoid overlap: left, center, right are naturally spaced
    label = f'{cat}\n({pct:.1f}%)'
    ax.annotate(label, xy=(cx, 0.25), xytext=(cx, 0.58 + i * 0.12),
                fontsize=9, fontweight='bold', color=NAVY, family='DejaVu Sans',
                ha='center', va='bottom',
                arrowprops=dict(arrowstyle='-', color=NAVY, lw=0.8))

# Y-axis
ax.set_ylim(-0.5, 1.2)
ax.set_yticks([])

# X-axis
ax.set_xlabel('Annual Cost ($ Billions)', fontsize=11, fontweight='bold', color=NAVY, family='DejaVu Sans')
ax.set_xlim(0, 180)
ax.set_xticks([0, 30, 60, 90, 120, 150, 180])
ax.set_xticklabels(['$0B', '$30B', '$60B', '$90B', '$120B', '$150B', '$180B'],
                    fontsize=9, color=NAVY, family='DejaVu Sans')

# Title — positioned with enough clearance
fig.suptitle('Hospital Supply Costs: Where the $170.9B Goes',
             fontsize=14, fontweight='bold', color=NAVY, family='DejaVu Sans', y=0.97)
fig.text(0.5, 0.91, '5,480 hospitals  ·  142.3M discharges  ·  CMS HCRIS FY2023',
         fontsize=9, color=NAVY, family='DejaVu Sans', ha='center', style='italic')

# Grid
ax.grid(axis='x', alpha=0.2, linestyle='--', color=NAVY)
ax.set_axisbelow(True)

# Spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_color(NAVY)

# Footnote
fig.text(0.12, 0.02,
         'Drugs charged to patients (pharmacy, chemotherapy, IV solutions) represent nearly half of hospital supply spending.',
         fontsize=6, color=NAVY, family='DejaVu Sans', ha='left', style='italic')

plt.subplots_adjust(top=0.86, bottom=0.14, left=0.06, right=0.96)
plt.savefig('/sessions/blissful-optimistic-allen/mnt/healthcare/issue_06/figures/chart3_cost_decomposition.png',
            dpi=150, facecolor=WHITE, edgecolor='none')
print('Chart 3 saved.')
plt.close(fig)
