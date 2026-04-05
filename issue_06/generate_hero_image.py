#!/usr/bin/env python3
"""
Hero Image for Issue #6: The Supply Closet
1456×1048px (14:10 aspect ratio)
Safe zone: 900×550px centered (62% width, 52% height)

Brand template:
- Series branding top-center: red "THE AMERICAN HEALTHCARE CONUNDRUM" + gold "ISSUE #6"
- Main hook: "$170.9 BILLION" or "$28 BILLION IN WASTE"
- Supporting stat: "5,480 hospitals. Up to 7.7× variance in supply costs."
- Navy background with subtle grid
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Color scheme
NAVY = '#1A1F2E'
TEAL = '#0E8A72'
RED = '#B7182A'
GOLD = '#D4AF37'
WHITE = '#F8F8F6'

# Create figure at render size (1456×1048) for 150dpi output
# 1456px / 150dpi = 9.7 inches
# 1048px / 150dpi = 6.99 inches
fig_width = 1456 / 150  # ~9.7 inches
fig_height = 1048 / 150  # ~7 inches

fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=150)
ax.set_xlim(0, 1456)
ax.set_ylim(0, 1048)
ax.axis('off')

# Navy background with subtle grid
ax.set_facecolor(NAVY)

# Add subtle grid pattern
for i in range(0, 1456, 100):
    ax.plot([i, i], [0, 1048], color=WHITE, alpha=0.03, linewidth=0.5)
for i in range(0, 1048, 100):
    ax.plot([0, 1456], [i, i], color=WHITE, alpha=0.03, linewidth=0.5)

# Top branding bar
top_bar = patches.Rectangle((0, 900), 1456, 148, linewidth=0, facecolor=RED, alpha=0.1)
ax.add_patch(top_bar)

# Title at top
ax.text(728, 980, 'THE AMERICAN HEALTHCARE CONUNDRUM', fontsize=32, fontweight='bold',
        ha='center', va='center', color=RED, family='sans-serif')

# Issue number in gold
ax.text(728, 920, 'ISSUE #6', fontsize=40, fontweight='bold',
        ha='center', va='center', color=GOLD, family='sans-serif')

# Red divider line
ax.plot([200, 1256], [895, 895], color=RED, linewidth=3)

# Main hook number (centered in safe zone, vertically centered)
# Safe zone center: 728, 524
ax.text(728, 620, '$170.9 BILLION', fontsize=72, fontweight='bold',
        ha='center', va='center', color=WHITE, family='sans-serif')

# Subtitle below hook
ax.text(728, 550, 'Annual Hospital Supply Costs', fontsize=28,
        ha='center', va='center', color=GOLD, family='sans-serif', style='italic')

# Supporting stat: variance info
ax.text(728, 460, '5,480 Hospitals', fontsize=20,
        ha='center', va='top', color=TEAL, fontweight='bold', family='sans-serif')

ax.text(728, 420, 'Up to 7.7× Variance in Supply Costs', fontsize=20,
        ha='center', va='top', color=WHITE, family='sans-serif')

# Bottom stats bar
bottom_bar = patches.Rectangle((0, 0), 1456, 140, linewidth=0, facecolor=GOLD, alpha=0.08)
ax.add_patch(bottom_bar)

# Three key stats at bottom
ax.text(364, 70, '$28B in Savings\nIdentified', fontsize=16, fontweight='bold',
        ha='center', va='center', color=TEAL, family='sans-serif')

ax.text(728, 70, 'Procurement Inefficiency\nOperating Room Waste\nExpiration/Disposal', fontsize=12,
        ha='center', va='center', color=WHITE, family='sans-serif')

ax.text(1092, 70, 'Reference Pricing\nGPO Transparency\nSupply Standardization', fontsize=12,
        ha='center', va='center', color=RED, family='sans-serif')

# Save at 150dpi to get 1456×1048px output
plt.savefig('/sessions/blissful-optimistic-allen/mnt/healthcare/issue_06/figures/hero_cover.png',
            dpi=150, bbox_inches='tight', facecolor=NAVY, edgecolor='none')
print("Hero image saved: hero_cover.png (1456×1048px)")
plt.close(fig)
