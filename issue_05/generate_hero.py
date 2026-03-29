"""
Hero Image for Issue #5: The Paper Chase — Administrative Waste
$200B/year savings. 5.6× US vs peer admin cost per capita.
4,518 hospitals analyzed. Safe zone: centered 900×550 in 1456×1048.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
import os

# Brand colors
NAVY = '#1A1F2E'
TEAL = '#0E8A72'
RED = '#B7182A'
GOLD = '#D4AF37'
WHITE = '#F8F8F6'
DARK_NAVY = '#111520'
MID_NAVY = '#252B3D'

# Canvas
W_IN = 14.56
H_IN = 10.48
DPI_WORK = 72
DPI_SAVE = 150

BASE = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.join(BASE, 'figures')
ROOT_FIG = os.path.join(os.path.dirname(BASE), 'figures')

fig = plt.figure(figsize=(W_IN, H_IN), dpi=DPI_WORK, facecolor=NAVY)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.set_facecolor(NAVY)
ax.axis('off')

# Subtle grid pattern
for i in range(0, 101, 5):
    ax.axhline(i, color=MID_NAVY, linewidth=0.3, alpha=0.5)
    ax.axvline(i, color=MID_NAVY, linewidth=0.3, alpha=0.5)

# Series branding — top center
ax.text(50, 74, 'THE AMERICAN HEALTHCARE CONUNDRUM',
        fontsize=11, color=RED, fontweight='bold', ha='center', va='center',
        fontfamily='sans-serif')
ax.text(50, 70.5, 'ISSUE #5', fontsize=9, color=GOLD,
        ha='center', va='center', fontfamily='sans-serif')

# Divider line
ax.plot([30, 70], [67.5, 67.5], color=RED, linewidth=1.5, alpha=0.7)

# Main headline
ax.text(50, 60, 'The Paper Chase.',
        fontsize=44, color=WHITE, fontweight='bold', ha='center', va='center',
        fontfamily='sans-serif')

# Subtitle — the savings number
ax.text(50, 52, '$200 Billion Per Year in Administrative Waste.',
        fontsize=18, color=TEAL, ha='center', va='center',
        fontfamily='sans-serif', fontweight='bold')

# Comparison boxes — US vs peers (per capita admin cost)
box_y = 33
box_h = 14
box_w = 18

# US box (left) — red accent
us_box = FancyBboxPatch((22, box_y - box_h/2), box_w, box_h,
                         boxstyle="round,pad=0.8", facecolor=DARK_NAVY,
                         edgecolor=RED, linewidth=2)
ax.add_patch(us_box)

ax.text(31, box_y + 3.5, 'UNITED STATES', fontsize=8, color=RED,
        fontweight='bold', ha='center', va='center', fontfamily='sans-serif',
        bbox=dict(boxstyle='round,pad=0.3', facecolor=RED, edgecolor=RED, alpha=0.9))
ax.texts[-1].set_color(WHITE)

ax.text(31, box_y - 0.5, '$4,983', fontsize=32, color=RED,
        fontweight='bold', ha='center', va='center', fontfamily='sans-serif')
ax.text(31, box_y - 4.5, 'admin per capita', fontsize=8, color=WHITE,
        ha='center', va='center', fontfamily='sans-serif', alpha=0.7)

# VS circle
circle = mpatches.Circle((50, box_y), 3.5, facecolor=GOLD, edgecolor=GOLD,
                          linewidth=0, zorder=5)
ax.add_patch(circle)
ax.text(50, box_y, 'VS', fontsize=11, color=NAVY, fontweight='bold',
        ha='center', va='center', fontfamily='sans-serif', zorder=6)

# Peer box (right) — teal accent
peer_box = FancyBboxPatch((60, box_y - box_h/2), box_w, box_h,
                           boxstyle="round,pad=0.8", facecolor=DARK_NAVY,
                           edgecolor=TEAL, linewidth=2)
ax.add_patch(peer_box)

ax.text(69, box_y + 3.5, '10-PEER AVG', fontsize=8, color=TEAL,
        fontweight='bold', ha='center', va='center', fontfamily='sans-serif',
        bbox=dict(boxstyle='round,pad=0.3', facecolor=TEAL, edgecolor=TEAL, alpha=0.9))
ax.texts[-1].set_color(WHITE)

ax.text(69, box_y - 0.5, '$884', fontsize=32, color=TEAL,
        fontweight='bold', ha='center', va='center', fontfamily='sans-serif')
ax.text(69, box_y - 4.5, 'admin per capita', fontsize=8, color=WHITE,
        ha='center', va='center', fontfamily='sans-serif', alpha=0.7)

# 5.6× callout between the boxes, above the VS
ax.text(50, box_y + 7.5, '5.6\u00d7', fontsize=20, color=GOLD,
        fontweight='bold', ha='center', va='center', fontfamily='sans-serif')

# Bottom context bar
ax.text(50, 21,
        '4,518 hospitals analyzed  \u00b7  Original HCRIS FY2023 data  \u00b7  $328.6B identified toward $3T gap',
        fontsize=9, color=WHITE, ha='center', va='center',
        fontfamily='sans-serif', alpha=0.45)

# Save
os.makedirs(FIG_DIR, exist_ok=True)
out_issue = os.path.join(FIG_DIR, 'hero_cover.png')
out_root  = os.path.join(ROOT_FIG, 'hero_issue_05.png')

for out in [out_issue, out_root]:
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.savefig(out, dpi=DPI_SAVE, facecolor=NAVY, bbox_inches='tight', pad_inches=0)
    print(f'Saved -> {out}')

plt.close(fig)
