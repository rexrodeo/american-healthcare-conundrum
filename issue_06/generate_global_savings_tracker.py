#!/usr/bin/env python3
"""
Global Savings Tracker for the Series
Updated with Issue #6 data
File: /mnt/healthcare/figures/savings_tracker.png

Stacked horizontal bar showing all issues to date with progress toward $3T target
"""

import matplotlib.pyplot as plt
import numpy as np

# Color scheme
NAVY = '#1A1F2E'
TEAL = '#0E8A72'
RED = '#B7182A'
GOLD = '#D4AF37'
WHITE = '#F8F8F6'

# Data from CLAUDE.md and RESEARCH_BRIEF
issues = ['Issue #1:\nOTC Drugs', 'Issue #2:\nDrug Pricing', 'Issue #3:\nHospital\nPricing',
          'Issue #4:\nPBMs', 'Issue #5:\nAdmin Waste', 'Issue #6:\nSupply Waste']
savings = [0.6, 25.0, 73.0, 30.0, 200.0, 28.0]
cumulative = np.cumsum(savings)
total = cumulative[-1]

# Colors for each issue
colors_issues = [GOLD, TEAL, RED, GOLD, TEAL, RED]

# Set up figure (horizontal orientation for Substack)
fig, ax = plt.subplots(figsize=(12, 4), dpi=100)

# Create stacked bar
y_pos = 0
left_pos = 0
bar_width = 0.5

for i, (issue, saving, color) in enumerate(zip(issues, savings, colors_issues)):
    bar = ax.barh(y_pos, saving, left=left_pos, height=bar_width,
                   color=color, alpha=0.85, edgecolor=NAVY, linewidth=1.5)

    # Label inside bar if space allows
    if saving >= 8:
        label_text = f'${saving:.1f}B' if saving >= 1 else f'${saving:.2f}B'
        ax.text(left_pos + saving/2, y_pos, label_text,
                ha='center', va='center', fontsize=10, fontweight='bold', color=WHITE)

    left_pos += saving

# Customization
ax.set_ylim(-0.6, 0.6)
ax.set_xlim(0, 3200)
ax.set_yticks([])
ax.set_xlabel('Cumulative Savings Identified ($ Billions)', fontsize=11, fontweight='bold', labelpad=10)
ax.set_title('The American Healthcare Conundrum: Running Savings Tracker\n356.6 Billion Identified (11.9% of 3 Trillion Target)',
             fontsize=13, fontweight='bold', pad=15, color=NAVY)

# Add issue labels below bar
for i, (issue, saving) in enumerate(zip(issues, savings)):
    if i == 0:
        pos = saving / 2
    else:
        pos = cumulative[i-1] + saving / 2
    ax.text(pos, -0.42, issue, ha='center', va='top', fontsize=8, fontweight='bold', color=NAVY)

# Progress annotation
progress_pct = (total / 3000) * 100
ax.text(total, 0.32, f'${total:.1f}B\n({progress_pct:.1f}%)',
        ha='center', va='bottom', fontsize=11, fontweight='bold', color=RED,
        bbox=dict(boxstyle='round,pad=0.5', facecolor=GOLD, alpha=0.25, edgecolor=RED, linewidth=1.5))

# Target indicator
ax.axvline(x=3000, color=NAVY, linestyle='--', linewidth=2.5, alpha=0.6)
ax.text(3000, 0.48, '$3 Trillion Target', ha='center', va='bottom', fontsize=10,
        fontweight='bold', color=NAVY, style='italic')

# Grid
ax.grid(axis='x', alpha=0.3, linestyle='--')
ax.set_axisbelow(True)

# Footer note
fig.text(0.12, 0.02,
         'Savings booked at conservative end of estimated range. Methodology: Issue #1 (rebate-adjusted CMS Part D), '
         '#2 (49% rebate adjustment), #3 (RAND markup + reference pricing), #4 (rebate pass-through), #5 (Woolhandler update), '
         '#6 (within-peer CMI-adjusted variance).',
         ha='left', fontsize=5.5, color='gray', wrap=True)

plt.tight_layout(rect=[0, 0.08, 1, 1])
plt.savefig('/sessions/blissful-optimistic-allen/mnt/healthcare/figures/savings_tracker.png',
            dpi=150, bbox_inches='tight', facecolor=WHITE)
print("Global savings tracker updated: /figures/savings_tracker.png")
print(f"Total savings identified: ${total:.1f}B / $3,000B (11.9%)")
plt.close(fig)
