#!/usr/bin/env python3
"""
Chart 3: Savings Tracker — Full Breakdown by Issue
Issue #6 — The Supply Closet
Running total: $356.6B / $3T (11.9%)

Stacked horizontal bar showing cumulative savings from Issues #1-#6
"""

import matplotlib.pyplot as plt
import numpy as np

# Color scheme
NAVY = '#1A1F2E'
TEAL = '#0E8A72'
RED = '#B7182A'
GOLD = '#D4AF37'
WHITE = '#F8F8F6'
LIGHT_GRAY = '#E0E0E0'

# Data from CLAUDE.md and RESEARCH_BRIEF
issues = ['#1\nOTC Drugs', '#2\nDrug Pricing', '#3\nHospital\nPricing',
          '#4\nPBMs', '#5\nAdmin Waste', '#6\nSupply Waste']
savings = [0.6, 25.0, 73.0, 30.0, 200.0, 28.0]
cumulative = np.cumsum(savings)

# Colors for each issue (cycling through palette)
colors_issues = [GOLD, TEAL, RED, GOLD, TEAL, RED]

# Set up figure
fig, ax = plt.subplots(figsize=(10, 6), dpi=100)

# Create stacked bar (horizontal)
y_pos = 0
left_pos = 0
bars = []
bar_width = 0.6

for i, (issue, saving, color) in enumerate(zip(issues, savings, colors_issues)):
    bar = ax.barh(y_pos, saving, left=left_pos, height=bar_width,
                   color=color, alpha=0.85, edgecolor=NAVY, linewidth=1)
    bars.append(bar)

    # Label inside the bar if space allows
    if saving >= 5:
        label_text = f'${saving:.1f}B'
        ax.text(left_pos + saving/2, y_pos, label_text,
                ha='center', va='center', fontsize=10, fontweight='bold', color=WHITE)

    left_pos += saving

# Customization
ax.set_ylim(-0.5, 0.5)
ax.set_xlim(0, 3000)
ax.set_yticks([])
ax.set_xlabel('Cumulative Savings Identified ($ Billions)', fontsize=11, fontweight='bold')
ax.set_title('The American Healthcare Conundrum: Savings Tracker\nCumulative Addressable Savings by Issue',
             fontsize=13, fontweight='bold', pad=15, color=NAVY)

# Add issue labels below the bar
for i, (issue, saving) in enumerate(zip(issues, savings)):
    if i == 0:
        pos = saving / 2
    else:
        pos = cumulative[i-1] + saving / 2
    ax.text(pos, -0.35, issue, ha='center', va='top', fontsize=9, fontweight='bold', color=NAVY)

# Add running total annotations above the bar
for i, cum in enumerate(cumulative):
    if i == 0:
        label = f'${cum:.1f}B'
        ax.text(cum, 0.32, label, ha='right', va='bottom', fontsize=9,
                fontweight='bold', color=NAVY, bbox=dict(boxstyle='round,pad=0.3',
                facecolor=WHITE, edgecolor=NAVY, linewidth=0.5))

# Final total annotation
ax.text(cumulative[-1], 0.45, f'Total: ${cumulative[-1]:.1f}B\n(11.9% of $3T target)',
        ha='right', va='bottom', fontsize=11, fontweight='bold', color=RED,
        bbox=dict(boxstyle='round,pad=0.6', facecolor=GOLD, alpha=0.2, edgecolor=RED, linewidth=1))

# Target line
ax.axvline(x=3000, color=NAVY, linestyle='--', linewidth=2, alpha=0.5, label='$3T Target')
ax.text(3000, 0.48, '$3 Trillion\nTarget', ha='center', va='bottom', fontsize=9,
        fontweight='bold', color=NAVY, style='italic')

# Grid
ax.grid(axis='x', alpha=0.3, linestyle='--')
ax.set_axisbelow(True)

# Footer note
fig.text(0.12, 0.02,
         'Data: CMS HCRIS FY2023, CMS NHE 2023, published academic literature. See newsletter for methodology and citations. '
         'Savings booked at conservative end of estimated range for methodological defensibility.',
         ha='left', fontsize=5.5, color='gray', wrap=True)

plt.tight_layout(rect=[0, 0.06, 1, 1])
plt.savefig('/sessions/blissful-optimistic-allen/mnt/healthcare/issue_06/figures/chart3_savings_tracker.png',
            dpi=150, bbox_inches='tight', facecolor=WHITE)
print("Chart 3 saved: chart3_savings_tracker.png")
plt.close(fig)
