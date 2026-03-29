#!/usr/bin/env python3
"""
Issue #5 Chart: Hospital Administrative Cost Variance by Size and Ownership Type
HCRIS FY2023 Worksheet A (Admin & General, Line 500)

Two-panel horizontal bar chart:
- LEFT: Admin cost per discharge by hospital bed-size category (P25, P50, P75)
- RIGHT: Admin cost per discharge by ownership type (For-Profit, Nonprofit, Government)
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Project color scheme
navy = '#1A1F2E'
teal = '#0E8A72'
red = '#B7182A'
gold = '#D4AF37'
white = '#F8F8F6'

# Data: Admin Cost Per Discharge by Bed Size
bed_sizes = ['Small\n(1-99)', 'Medium\n(100-299)', 'Large\n(300-499)', 'Very Large\n(500+)']
p25_data = [444, 613, 849, 900]
p50_data = [2094, 1112, 1187, 1226]
p75_data = [4852, 1643, 1679, 1808]

# Data: Admin Cost Per Discharge by Ownership
ownership_types = ['For-Profit', 'Nonprofit', 'Government']
ownership_median = [460, 1986, 2511]

# Create figure with two subplots side-by-side
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 6), dpi=100)
fig.patch.set_facecolor(navy)

# Suptitle
fig.suptitle('4,641 Hospitals. $142.7 Billion in Administrative Overhead.',
             fontsize=15, fontweight='bold', color=white, y=0.98)

# Subtitle
fig.text(0.5, 0.94, 'Worksheet A, Administrative & General (Line 500) | HCRIS FY2023 | Author analysis',
         ha='center', fontsize=8, color='#999999', style='italic')

# ============ LEFT PANEL: Admin Cost by Hospital Size ============
ax1.set_facecolor(navy)
ax1.spines['left'].set_color(white)
ax1.spines['bottom'].set_color(white)
ax1.spines['right'].set_visible(False)
ax1.spines['top'].set_visible(False)

y_pos = np.arange(len(bed_sizes))
bar_height = 0.25

# Plot P25, P50, P75 as horizontal bars
ax1.barh(y_pos - bar_height, p25_data, bar_height, label='P25', color=teal, alpha=0.85)
ax1.barh(y_pos, p50_data, bar_height, label='P50 (Median)', color=gold, alpha=0.85)
ax1.barh(y_pos + bar_height, p75_data, bar_height, label='P75', color=red, alpha=0.85)

# Customize left panel
ax1.set_yticks(y_pos)
ax1.set_yticklabels(bed_sizes, fontsize=10, color=white, fontweight='bold')
ax1.set_xlabel('Admin Cost Per Discharge ($)', fontsize=11, color=white, fontweight='bold')
ax1.set_title('By Hospital Size', fontsize=11, color=white, fontweight='bold', pad=12)
ax1.tick_params(colors=white, labelsize=9)
ax1.grid(axis='x', alpha=0.2, color=white, linestyle='--')
ax1.set_xlim(0, 5500)

# Add value labels inside/outside bars and ratio annotations
# Small hospitals
ax1.text(2100, -0.26, '$444', fontsize=9, color=white, fontweight='bold', ha='left')
ax1.text(2100, -0.01, '$2,094', fontsize=9, color=navy, fontweight='bold', ha='left', bbox=dict(boxstyle='round,pad=0.3', facecolor=gold, alpha=0.7, edgecolor='none'))
ax1.text(4950, 0.26, '$4,852', fontsize=9, color=white, fontweight='bold', ha='left')
ax1.text(5200, -0.04, '10.9x', fontsize=8, color=gold, fontweight='bold', style='italic')

# Medium hospitals
ax1.text(700, 0.74, '$613', fontsize=9, color=white, fontweight='bold', ha='left')
ax1.text(1150, 0.99, '$1,112', fontsize=9, color=navy, fontweight='bold', ha='left', bbox=dict(boxstyle='round,pad=0.3', facecolor=gold, alpha=0.7, edgecolor='none'))
ax1.text(1700, 1.26, '$1,643', fontsize=9, color=white, fontweight='bold', ha='left')
ax1.text(1900, 0.96, '2.7x', fontsize=8, color=gold, fontweight='bold', style='italic')

# Large hospitals
ax1.text(900, 1.74, '$849', fontsize=9, color=white, fontweight='bold', ha='left')
ax1.text(1250, 1.99, '$1,187', fontsize=9, color=navy, fontweight='bold', ha='left', bbox=dict(boxstyle='round,pad=0.3', facecolor=gold, alpha=0.7, edgecolor='none'))
ax1.text(1750, 2.26, '$1,679', fontsize=9, color=white, fontweight='bold', ha='left')
ax1.text(1950, 1.96, '2.0x', fontsize=8, color=gold, fontweight='bold', style='italic')

# Very Large hospitals
ax1.text(950, 2.74, '$900', fontsize=9, color=white, fontweight='bold', ha='left')
ax1.text(1300, 2.99, '$1,226', fontsize=9, color=navy, fontweight='bold', ha='left', bbox=dict(boxstyle='round,pad=0.3', facecolor=gold, alpha=0.7, edgecolor='none'))
ax1.text(1850, 3.26, '$1,808', fontsize=9, color=white, fontweight='bold', ha='left')
ax1.text(2050, 2.96, '2.0x', fontsize=8, color=gold, fontweight='bold', style='italic')

ax1.legend(loc='lower right', fontsize=8, framealpha=0.9, facecolor=navy, edgecolor=white)

# ============ RIGHT PANEL: Admin Cost by Ownership Type ============
ax2.set_facecolor(navy)
ax2.spines['left'].set_color(white)
ax2.spines['bottom'].set_color(white)
ax2.spines['right'].set_visible(False)
ax2.spines['top'].set_visible(False)

# Color mapping for ownership types
colors_ownership = [teal, gold, red]
y_pos_ownership = np.arange(len(ownership_types))

bars = ax2.barh(y_pos_ownership, ownership_median, color=colors_ownership, alpha=0.85, height=0.5)

# Customize right panel
ax2.set_yticks(y_pos_ownership)
ax2.set_yticklabels(ownership_types, fontsize=10, color=white, fontweight='bold')
ax2.set_xlabel('Median Admin Cost Per Discharge ($)', fontsize=11, color=white, fontweight='bold')
ax2.set_title('By Ownership Type', fontsize=11, color=white, fontweight='bold', pad=12)
ax2.tick_params(colors=white, labelsize=9)
ax2.grid(axis='x', alpha=0.2, color=white, linestyle='--')
ax2.set_xlim(0, 3000)

# Add value labels and ratio callout
ax2.text(500, 0, '$460', fontsize=10, color=white, fontweight='bold', ha='left', va='center')
ax2.text(2050, 1, '$1,986', fontsize=10, color=navy, fontweight='bold', ha='left', va='center', bbox=dict(boxstyle='round,pad=0.4', facecolor=gold, alpha=0.7, edgecolor='none'))
ax2.text(2600, 2, '$2,511', fontsize=10, color=white, fontweight='bold', ha='left', va='center')

# Ratio annotation with leader line
ax2.annotate('Nonprofit vs.\nFor-Profit:\n4.3x', xy=(1986, 1), xytext=(1200, 1.4),
            fontsize=8, color=gold, fontweight='bold', style='italic',
            arrowprops=dict(arrowstyle='-', color=gold, lw=1, alpha=0.7),
            bbox=dict(boxstyle='round,pad=0.4', facecolor=navy, edgecolor=gold, alpha=0.8, linewidth=1))

# ============ FOOTNOTE ============
fig.text(0.12, 0.02,
         'Source: CMS HCRIS HOSP10-REPORTS FY2023 (Worksheet A, Col 700). N=4,641 hospitals with ≥100 discharges.\n' +
         "For-profit's lower median may reflect corporate parent cost allocation, not operational efficiency alone.",
         ha='left', fontsize=6, color='#CCCCCC', linespacing=1.6)

# Adjust layout to prevent overlap
plt.subplots_adjust(top=0.88, bottom=0.12, left=0.10, right=0.96, wspace=0.4)

# Save at 150dpi
output_path = '/Users/minirex/healthcare/issue_05/figures/chart6_admin_variance.png'
plt.savefig(output_path, dpi=150, facecolor=navy, edgecolor='none', bbox_inches='tight')
print(f'Chart saved to: {output_path}')

plt.close(fig)
print('Figure closed and memory freed.')
