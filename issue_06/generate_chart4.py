#!/usr/bin/env python3
"""
Chart 4: Ownership Breakdown — Total Spend + Median Per Discharge
Two-panel vertical bar chart. Clean layout with no overlapping text.
"""

import matplotlib.pyplot as plt
import numpy as np

NAVY = '#1A1F2E'
TEAL = '#0E8A72'
RED = '#B7182A'
GOLD = '#D4AF37'
WHITE = '#F8F8F6'

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5.5), dpi=100,
                                gridspec_kw={'wspace': 0.45})
fig.patch.set_facecolor(WHITE)

# Data
ownership = ['For-Profit', 'Nonprofit', 'Government']
total_spend = [18.8, 128.9, 23.0]
median_per_dc = [236, 1270, 1332]
n_hospitals = [1576, 2993, 911]
colors_chart = [GOLD, TEAL, RED]

# --- Panel 1: Total Spend ---
bars1 = ax1.bar(ownership, total_spend, color=colors_chart, alpha=0.78,
                edgecolor=NAVY, linewidth=1.5, width=0.6)
for bar, val in zip(bars1, total_spend):
    h = bar.get_height()
    # Place label above bar if bar is short, inside if tall enough
    if h > 30:
        ax1.text(bar.get_x() + bar.get_width()/2, h/2, f'${val:.1f}B',
                 ha='center', va='center', fontsize=12, fontweight='bold',
                 color=WHITE, family='DejaVu Sans')
    else:
        ax1.text(bar.get_x() + bar.get_width()/2, h + 2, f'${val:.1f}B',
                 ha='center', va='bottom', fontsize=11, fontweight='bold',
                 color=NAVY, family='DejaVu Sans')

ax1.set_ylabel('Total Annual Supply Spend ($ Billions)', fontsize=10,
               fontweight='bold', color=NAVY, family='DejaVu Sans')
ax1.set_ylim(0, 155)
ax1.set_title('Total Spend by Ownership', fontsize=11, fontweight='bold',
              color=NAVY, family='DejaVu Sans', pad=8)
ax1.grid(axis='y', alpha=0.2, linestyle='--', color=NAVY)
ax1.set_axisbelow(True)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.spines['left'].set_color(NAVY)
ax1.spines['bottom'].set_visible(False)
ax1.tick_params(axis='x', length=0)
for label in ax1.get_xticklabels():
    label.set_fontsize(9.5)
    label.set_fontweight('bold')
    label.set_color(NAVY)
    label.set_family('DejaVu Sans')

# Hospital counts below x-axis labels
for i, n in enumerate(n_hospitals):
    ax1.text(i, -8, f'N={n:,}', ha='center', va='top', fontsize=7.5,
             color=NAVY, family='DejaVu Sans')

# --- Panel 2: Median Per Discharge ---
bars2 = ax2.bar(ownership, median_per_dc, color=colors_chart, alpha=0.78,
                edgecolor=NAVY, linewidth=1.5, width=0.6)
for bar, val in zip(bars2, median_per_dc):
    h = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2, h + 20, f'${val:,}',
             ha='center', va='bottom', fontsize=11, fontweight='bold',
             color=NAVY, family='DejaVu Sans')

ax2.set_ylabel('Median Cost Per Discharge ($)', fontsize=10,
               fontweight='bold', color=NAVY, family='DejaVu Sans')
ax2.set_ylim(0, 1600)
ax2.set_title('Median Cost Per Discharge', fontsize=11, fontweight='bold',
              color=NAVY, family='DejaVu Sans', pad=8)
ax2.grid(axis='y', alpha=0.2, linestyle='--', color=NAVY)
ax2.set_axisbelow(True)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['left'].set_color(NAVY)
ax2.spines['bottom'].set_visible(False)
ax2.tick_params(axis='x', length=0)
for label in ax2.get_xticklabels():
    label.set_fontsize(9.5)
    label.set_fontweight('bold')
    label.set_color(NAVY)
    label.set_family('DejaVu Sans')

# Suptitle with proper spacing
fig.suptitle('Hospital Supply Spending: Ownership Comparison',
             fontsize=14, fontweight='bold', color=NAVY, family='DejaVu Sans', y=0.97)
fig.text(0.5, 0.91, 'FY2023  ·  5,480 hospitals  ·  $170.9B total supply spend',
         fontsize=9, color=NAVY, family='DejaVu Sans', ha='center', style='italic')

# Footnote
fig.text(0.12, 0.02,
         'For-profit median (\$236/DC) reflects hospital mix (specialty/surgical centers, lower acuity). '
         'Nonprofits carry 75.5% of national supply spend (\$128.9B of \$170.9B).',
         fontsize=6.5, color=NAVY, family='DejaVu Sans', ha='left', style='italic')

plt.subplots_adjust(top=0.86, bottom=0.12, left=0.08, right=0.96)
plt.savefig('/sessions/blissful-optimistic-allen/mnt/healthcare/issue_06/figures/chart4_ownership_breakdown.png',
            dpi=150, facecolor=WHITE, edgecolor='none')
print('Chart 4 saved.')
plt.close(fig)
