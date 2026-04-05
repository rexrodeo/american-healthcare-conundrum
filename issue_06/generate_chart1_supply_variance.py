#!/usr/bin/env python3
"""
Chart 1: Hospital Supply Cost Variance by Bed Size (CMI-Adjusted)
Issue #6 — The Supply Closet

Data source: RESEARCH_BRIEF.md Section 2a
CMI-adjusted per-discharge cost for combined supply/device/drug costs
"""

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches

# Color scheme
NAVY = '#1A1F2E'
TEAL = '#0E8A72'
RED = '#B7182A'
GOLD = '#D4AF37'
WHITE = '#F8F8F6'

# Data from RESEARCH_BRIEF
bed_sizes = ['Small\n(1-99)', 'Medium\n(100-299)', 'Large\n(300-499)', 'Major\n(500+)']
hospitals_n = [3499, 1511, 320, 149]
p25 = [197, 382, 543, 451]
p50 = [663, 700, 893, 777]
p75 = [1509, 1165, 1265, 1329]
p90 = [3005, 1724, 1784, 1793]
ratios = [7.7, 3.0, 2.3, 2.9]

# Set up figure
fig, ax = plt.subplots(figsize=(10, 6), dpi=100)

# X positions for grouped bars
x_pos = np.arange(len(bed_sizes))
width = 0.18

# Create bars
bars_p25 = ax.bar(x_pos - 1.5*width, p25, width, label='P25', color=TEAL, alpha=0.8)
bars_p50 = ax.bar(x_pos - 0.5*width, p50, width, label='P50', color=GOLD, alpha=0.8)
bars_p75 = ax.bar(x_pos + 0.5*width, p75, width, label='P75', color=RED, alpha=0.8)
bars_p90 = ax.bar(x_pos + 1.5*width, p90, width, label='P90', color=NAVY, alpha=0.8)

# Customization
ax.set_ylabel('Cost per Discharge (USD)', fontsize=11, fontweight='bold')
ax.set_xlabel('Hospital Bed Size (Count)', fontsize=11, fontweight='bold')
ax.set_title('CMI-Adjusted Supply Cost Variance by Hospital Bed Size\n(Medical Supplies + Implantable Devices + Drugs)',
             fontsize=13, fontweight='bold', pad=15, color=NAVY)
ax.set_xticks(x_pos)
ax.set_xticklabels(bed_sizes, fontsize=10)
ax.set_ylim(0, 3500)
ax.legend(loc='upper left', fontsize=10, framealpha=0.95)
ax.grid(axis='y', alpha=0.3, linestyle='--')
ax.set_axisbelow(True)

# Add ratio annotations above P75 bars (P75/P25 ratio)
for i, (p75_val, ratio) in enumerate(zip(p75, ratios)):
    ax.text(i + 0.5*width, p75_val + 150, f'{ratio}×\nvariance',
            ha='center', va='bottom', fontsize=9, fontweight='bold', color=RED)

# Add hospital count labels below X-axis
for i, n in enumerate(hospitals_n):
    ax.text(i, -250, f'n={n:,}', ha='center', va='top', fontsize=8, color=NAVY, style='italic')

# Footer note
fig.text(0.12, 0.02,
         'Data: CMS HCRIS FY2023, 5,480 hospitals. Cost per discharge adjusted for case-mix intensity (CMI). '
         'P25/P50/P75/P90 = percentiles.',
         ha='left', fontsize=5.5, color='gray', wrap=True)

plt.tight_layout(rect=[0, 0.04, 1, 1])
plt.savefig('/sessions/blissful-optimistic-allen/mnt/healthcare/issue_06/figures/chart1_supply_variance.png',
            dpi=150, bbox_inches='tight', facecolor=WHITE)
print("Chart 1 saved: chart1_supply_variance.png")
plt.close(fig)
