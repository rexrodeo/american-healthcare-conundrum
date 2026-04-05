#!/usr/bin/env python3
"""
Chart 2: Medical Surplus Nonprofits — Annual In-Kind Donations
Issue #6 — The Supply Closet

Data source: RESEARCH_BRIEF.md Section 4a, ProPublica Form 990 data
Horizontal bar chart of major medical surplus nonprofits
"""

import matplotlib.pyplot as plt
import numpy as np

# Color scheme
NAVY = '#1A1F2E'
TEAL = '#0E8A72'
RED = '#B7182A'
GOLD = '#D4AF37'
WHITE = '#F8F8F6'

# Data from RESEARCH_BRIEF
organizations = [
    'Direct Relief',
    'MAP International',
    'Project C.U.R.E.',
    'MATTER',
    'MedShare',
    'Afya Foundation'
]

revenues = [2270, 890, 65.3, 35.0, 18.4, 11.6]  # Millions
colors_bars = [RED, RED, TEAL, TEAL, GOLD, GOLD]

# Set up figure
fig, ax = plt.subplots(figsize=(10, 6), dpi=100)

# Create horizontal bars
y_pos = np.arange(len(organizations))
bars = ax.barh(y_pos, revenues, color=colors_bars, alpha=0.85, edgecolor=NAVY, linewidth=0.5)

# Customization
ax.set_yticks(y_pos)
ax.set_yticklabels(organizations, fontsize=10)
ax.set_xlabel('Annual Revenue ($ Millions)', fontsize=11, fontweight='bold')
ax.set_title('Medical Surplus Nonprofits: Annual In-Kind Donations\nMonitoring the Pipeline of Excess Hospital Supplies',
             fontsize=13, fontweight='bold', pad=15, color=NAVY)
ax.set_xlim(0, 2500)
ax.grid(axis='x', alpha=0.3, linestyle='--')
ax.set_axisbelow(True)

# Add value labels on bars
for i, (bar, rev) in enumerate(zip(bars, revenues)):
    if rev >= 100:
        label_text = f'${rev:,.0f}M'
    else:
        label_text = f'${rev:,.1f}M'

    ax.text(rev + 50, bar.get_y() + bar.get_height()/2,
            label_text, va='center', ha='left', fontsize=10, fontweight='bold', color=NAVY)

# Add context annotation
ax.text(0.02, 0.98, 'Direct Relief and MAP International dominate the medical surplus ecosystem,\nprocessing >$3.3B annually in donated hospital supplies.',
        transform=ax.transAxes, fontsize=9, va='top', ha='left',
        bbox=dict(boxstyle='round,pad=0.8', facecolor=GOLD, alpha=0.15, edgecolor=NAVY, linewidth=0.5))

# Footer note
fig.text(0.12, 0.02,
         'Data: ProPublica Nonprofit Explorer (Form 990 FY2023). Includes IRS Schedule M drug & medical supplies contributions. '
         'Direct Relief figure includes pharmaceutical donations channel (~$2.1B).',
         ha='left', fontsize=5.5, color='gray', wrap=True)

plt.tight_layout(rect=[0, 0.06, 1, 1])
plt.savefig('/sessions/blissful-optimistic-allen/mnt/healthcare/issue_06/figures/chart2_surplus_nonprofits.png',
            dpi=150, bbox_inches='tight', facecolor=WHITE)
print("Chart 2 saved: chart2_surplus_nonprofits.png")
plt.close(fig)
