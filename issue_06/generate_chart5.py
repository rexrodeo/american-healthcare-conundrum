#!/usr/bin/env python3
"""
Chart 5: Implant Price Variance — Total Knee Replacement
Horizontal range chart showing the $1,797–$12,093 spread for the same device,
with a reference pricing cap marker.
"""
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['text.usetex'] = False
matplotlib.rcParams['text.parse_math'] = False
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

NAVY = '#1A1F2E'
TEAL = '#0E8A72'
RED = '#B7182A'
GOLD = '#D4AF37'
WHITE = '#F8F8F6'

fig, ax = plt.subplots(figsize=(10, 4.5), dpi=100)
fig.patch.set_facecolor(WHITE)
ax.set_facecolor(WHITE)

# Data
low = 1797
high = 12093
ref_price = high * 0.833  # 16.7% reduction = $10,073

y_center = 0.5

# --- The range bar: gradient from teal (low) to red (high) ---
# Draw as a filled rectangle
ax.barh(y_center, high - low, left=low, height=0.25, color=RED, alpha=0.15,
        edgecolor='none')
# Thick line for the range
ax.plot([low, high], [y_center, y_center], color=RED, linewidth=3, solid_capstyle='round', alpha=0.4)

# Low end marker + label
ax.scatter([low], [y_center], s=200, color=TEAL, zorder=5, edgecolors=NAVY, linewidth=1.5)
ax.text(low, y_center + 0.22, '$1,797', ha='center', va='bottom',
        fontsize=14, fontweight='bold', color=TEAL, family='DejaVu Sans')
ax.text(low, y_center - 0.22, 'Lowest-cost\nhospital', ha='center', va='top',
        fontsize=9, color=TEAL, family='DejaVu Sans')

# High end marker + label
ax.scatter([high], [y_center], s=200, color=RED, zorder=5, edgecolors=NAVY, linewidth=1.5)
ax.text(high, y_center + 0.22, '$12,093', ha='center', va='bottom',
        fontsize=14, fontweight='bold', color=RED, family='DejaVu Sans')
ax.text(high, y_center - 0.22, 'Highest-cost\nhospital', ha='center', va='top',
        fontsize=9, color=RED, family='DejaVu Sans')

# 6.7x label centered on the range line
mid = (low + high) / 2
ax.text(mid, y_center + 0.08, '6.7x price range for the same implant',
        ha='center', va='bottom', fontsize=10, fontweight='bold', color=NAVY, family='DejaVu Sans')

# --- Reference pricing cap ---
ax.plot([ref_price, ref_price], [y_center - 0.18, y_center + 0.18],
        color=GOLD, linewidth=3, zorder=6, solid_capstyle='round')
# Small triangle marker
ax.scatter([ref_price], [y_center - 0.18], marker='v', s=100, color=GOLD, zorder=7)

ax.text(ref_price, y_center - 0.35,
        'Reference pricing cap\n$10,073  (16.7% reduction)',
        ha='center', va='top', fontsize=9, fontweight='bold',
        color='#8B6914', family='DejaVu Sans',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#FFF8E7', edgecolor=GOLD, linewidth=1.2))

# --- Shading the "saved" zone ---
ax.axvspan(ref_price, high, ymin=0.35, ymax=0.65, alpha=0.08, color=GOLD)

# Clean up axes
ax.set_xlim(0, 14000)
ax.set_ylim(-0.15, 1.1)
ax.set_yticks([])
ax.set_xticks([0, 2000, 4000, 6000, 8000, 10000, 12000, 14000])
ax.set_xticklabels(['$0', '$2K', '$4K', '$6K', '$8K', '$10K', '$12K', '$14K'],
                    fontsize=9, color=NAVY, family='DejaVu Sans')
ax.set_xlabel('Total Knee Replacement Implant Cost', fontsize=10, fontweight='bold',
              color=NAVY, family='DejaVu Sans')

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_color(NAVY)
ax.grid(axis='x', alpha=0.15, linestyle='--', color=NAVY)
ax.set_axisbelow(True)

# Title
fig.suptitle('Same Device. Same Manufacturer. 6.7x Price Range.',
             fontsize=14, fontweight='bold', color=NAVY, family='DejaVu Sans', y=0.97)
fig.text(0.5, 0.91, 'Total knee replacement implant costs across US hospitals',
         fontsize=9, color=NAVY, family='DejaVu Sans', ha='center', style='italic')

# Footnote
fig.text(0.12, 0.02,
         'Robinson et al. 2012 (Health Affairs): TKA implant costs across 110 US hospitals. '
         'Fang et al. 2020 (JBJS): reference pricing achieved 16.7% cost reduction.',
         fontsize=6, color=NAVY, family='DejaVu Sans', ha='left', style='italic')

plt.subplots_adjust(top=0.85, bottom=0.18, left=0.06, right=0.96)
plt.savefig('/sessions/blissful-optimistic-allen/mnt/healthcare/issue_06/figures/chart5_implant_variance.png',
            dpi=150, facecolor=WHITE, edgecolor='none')
print('Chart 5 saved.')
plt.close(fig)
