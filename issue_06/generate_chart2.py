#!/usr/bin/env python3
"""
Chart 2: Medical Surplus Nonprofits — Annual In-Kind Donations
Horizontal bar chart with log scale. Clean label positioning.
"""

import matplotlib.pyplot as plt
import numpy as np

NAVY = '#1A1F2E'
TEAL = '#0E8A72'
RED = '#B7182A'
WHITE = '#F8F8F6'

orgs = ['Direct Relief', 'MAP International', 'Project C.U.R.E.', 'MedShare', 'Afya Foundation', 'Hand in Hand Logistics']
revenues = [2270, 890, 65.3, 18.4, 6.7, 1.1]

fig, ax = plt.subplots(figsize=(10, 5.5), dpi=100)
fig.patch.set_facecolor(WHITE)
ax.set_facecolor(WHITE)

bars = ax.barh(orgs, revenues, color=TEAL,
               alpha=0.75, edgecolor=NAVY, linewidth=1.5, height=0.55)

ax.set_xscale('log')
ax.set_xlabel('Annual Revenue (\$ Millions, Log Scale)', fontsize=11, fontweight='bold',
              color=NAVY, family='DejaVu Sans')
ax.set_xlim(0.5, 6000)
ax.set_xticks([1, 10, 100, 1000])
ax.set_xticklabels(['\$1M', '\$10M', '\$100M', '\$1B'], fontsize=9, color=NAVY, family='DejaVu Sans')

for label in ax.get_yticklabels():
    label.set_fontsize(10)
    label.set_fontweight('bold')
    label.set_color(NAVY)
    label.set_family('DejaVu Sans')

# Value labels: outside to the right of each bar
for bar, rev in zip(bars, revenues):
    w = bar.get_width()
    # Place label to the right with enough space on log scale
    label_x = w * 1.3
    if rev >= 1000:
        label_text = f'\${rev/1000:.1f}B'
    else:
        label_text = f'\${rev:.1f}M'
    ax.text(label_x, bar.get_y() + bar.get_height()/2, label_text,
            va='center', ha='left', fontsize=9, fontweight='bold',
            color=NAVY, family='DejaVu Sans')

# Title with proper spacing
fig.suptitle('Medical Surplus Nonprofits: Annual Revenue',
             fontsize=14, fontweight='bold', color=NAVY, family='DejaVu Sans', y=0.97)
fig.text(0.5, 0.91, 'In-kind medical supply organizations  ·  IRS Form 990 data (FY2023)',
         fontsize=9, color=NAVY, family='DejaVu Sans', ha='center', style='italic')

ax.grid(axis='x', alpha=0.2, linestyle='--', color=NAVY)
ax.set_axisbelow(True)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color(NAVY)
ax.spines['bottom'].set_color(NAVY)

fig.text(0.12, 0.02,
         'Log scale shows both large organizations (Direct Relief: \$2.3B) and smaller regional nonprofits '
         '(Hand in Hand: \$1.1M). Total in-kind medical goods: >\$3.3B annually.',
         fontsize=6, color=NAVY, family='DejaVu Sans', ha='left', style='italic')

plt.subplots_adjust(top=0.86, bottom=0.12, left=0.24, right=0.95)
plt.savefig('/sessions/blissful-optimistic-allen/mnt/healthcare/issue_06/figures/chart2_surplus_nonprofits.png',
            dpi=150, facecolor=WHITE, edgecolor='none')
print('Chart 2 saved.')
plt.close(fig)
