"""
Generate two cover image options for The American Healthcare Conundrum — Issue #1
Substack recommended size: 1600 x 900 (16:9)
"""
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['text.usetex'] = False
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

W, H = 16, 9   # figure units (will render at 100dpi = 1600x900)
OUT_A = '/sessions/confident-nice-fermat/mnt/healthcare/figures/cover_option_a.png'
OUT_B = '/sessions/confident-nice-fermat/mnt/healthcare/figures/cover_option_b.png'

# ── Shared palette ─────────────────────────────────────────────────────────
NAVY    = '#0A1628'
NAVY2   = '#0F2040'
RED     = '#C0392B'
RED2    = '#E74C3C'
WHITE   = '#FFFFFF'
OFFWHITE= '#E8EDF2'
GOLD    = '#F39C12'
TEAL    = '#1ABC9C'
MID     = '#8899AA'

# ══════════════════════════════════════════════════════════════════════════════
# OPTION A — "The Stat"
# Hero: $2 BILLION  /  subline about CVS  /  Issue branding at bottom
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(W, H))
fig.patch.set_facecolor(NAVY)
ax.set_facecolor(NAVY)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

# Subtle grid texture — horizontal rule lines
for y in np.linspace(0.05, 0.95, 18):
    ax.axhline(y, color='white', alpha=0.03, linewidth=0.5)

# Red accent bar on left edge
ax.add_patch(mpatches.Rectangle((0, 0), 0.008, 1,
    facecolor=RED, edgecolor='none', transform=ax.transAxes, zorder=5))

# Top label
ax.text(0.055, 0.88, 'T H E   A M E R I C A N   H E A L T H C A R E   C O N U N D R U M',
        ha='left', va='top', fontsize=12, fontweight='bold',
        color=RED2, transform=ax.transAxes,
        fontfamily='monospace')

ax.text(0.055, 0.80, 'ISSUE  #1   ·   MEDICARE PART D',
        ha='left', va='top', fontsize=10,
        color=MID, transform=ax.transAxes, fontfamily='monospace')

# Thin divider
ax.axhline(0.74, xmin=0.055, xmax=0.95, color=RED, linewidth=0.8, alpha=0.6)

# Hero number
ax.text(0.055, 0.68, '\$2',
        ha='left', va='top', fontsize=108, fontweight='bold',
        color=WHITE, transform=ax.transAxes)
ax.text(0.53, 0.68, 'BILLION',
        ha='left', va='top', fontsize=52, fontweight='bold',
        color=WHITE, transform=ax.transAxes)
ax.text(0.53, 0.535, 'PER YEAR',
        ha='left', va='top', fontsize=28,
        color=GOLD, transform=ax.transAxes, fontweight='bold')

# Sub-stat
ax.text(0.055, 0.32,
        'What Medicare Part D spends annually on drugs',
        ha='left', va='top', fontsize=20, color=OFFWHITE,
        transform=ax.transAxes)
ax.text(0.055, 0.235,
        'you can buy off the shelf at any drugstore.',
        ha='left', va='top', fontsize=20, color=OFFWHITE,
        transform=ax.transAxes)

# Supporting stat
ax.text(0.055, 0.145,
        '83 million claims  ·  18 drugs with OTC equivalents  ·  \$600M in avoidable spending',
        ha='left', va='top', fontsize=11, color=MID,
        transform=ax.transAxes)

# Bottom right branding
ax.text(0.945, 0.06, 'andrewrexroad.substack.com',
        ha='right', va='bottom', fontsize=9, color=MID,
        transform=ax.transAxes, fontfamily='monospace')

plt.tight_layout(pad=0)
plt.savefig(OUT_A, dpi=100, bbox_inches='tight', facecolor=NAVY)
plt.close()
print(f'Saved Option A -> {OUT_A}')


# ══════════════════════════════════════════════════════════════════════════════
# OPTION B — "The Comparison"
# Left: US $14,570  /  Right: Japan $5,790  /  Gap in centre
# ══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(W, H))
fig.patch.set_facecolor(NAVY)
ax.set_facecolor(NAVY)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.axis('off')

# Dividing line in centre
ax.axvline(0.5, color=WHITE, linewidth=0.6, alpha=0.15)

# Left panel — US
ax.add_patch(mpatches.Rectangle((0, 0), 0.5, 1,
    facecolor='#0D0D1A', edgecolor='none'))
ax.text(0.25, 0.82, 'UNITED STATES', ha='center', va='center',
        fontsize=13, fontweight='bold', color=RED2,
        transform=ax.transAxes, fontfamily='monospace')
ax.text(0.25, 0.60, '\$14,570',
        ha='center', va='center', fontsize=62, fontweight='bold',
        color=RED2, transform=ax.transAxes)
ax.text(0.25, 0.445, 'per capita / year',
        ha='center', va='center', fontsize=14, color=MID,
        transform=ax.transAxes)

# US stats
for i, stat in enumerate([
    '78.4 yr  life expectancy',
    '5.6      infant deaths / 1,000',
    '#1       healthcare spending',
]):
    ax.text(0.25, 0.34 - i * 0.08, stat,
            ha='center', va='center', fontsize=11, color=OFFWHITE,
            transform=ax.transAxes, fontfamily='monospace')

# Right panel — Japan
ax.add_patch(mpatches.Rectangle((0.5, 0), 0.5, 1,
    facecolor=NAVY, edgecolor='none'))
ax.text(0.75, 0.82, 'JAPAN', ha='center', va='center',
        fontsize=13, fontweight='bold', color=TEAL,
        transform=ax.transAxes, fontfamily='monospace')
ax.text(0.75, 0.60, '\$5,790',
        ha='center', va='center', fontsize=62, fontweight='bold',
        color=TEAL, transform=ax.transAxes)
ax.text(0.75, 0.445, 'per capita / year',
        ha='center', va='center', fontsize=14, color=MID,
        transform=ax.transAxes)

for i, stat in enumerate([
    '84.3 yr  life expectancy',
    '1.7      infant deaths / 1,000',
    '#1       outcomes in OECD',
]):
    ax.text(0.75, 0.34 - i * 0.08, stat,
            ha='center', va='center', fontsize=11, color=OFFWHITE,
            transform=ax.transAxes, fontfamily='monospace')

# Centre badge showing gap
gap_circle = mpatches.Circle((0.5, 0.60), 0.09,
    facecolor=NAVY2, edgecolor=GOLD, linewidth=2,
    transform=ax.transAxes, zorder=10)
ax.add_patch(gap_circle)
ax.text(0.5, 0.615, '2.5\u00d7',
        ha='center', va='center', fontsize=22, fontweight='bold',
        color=GOLD, transform=ax.transAxes, zorder=11)
ax.text(0.5, 0.555, 'more',
        ha='center', va='center', fontsize=10, color=GOLD,
        transform=ax.transAxes, zorder=11)

# Title at top
ax.text(0.5, 0.955,
        'THE AMERICAN HEALTHCARE CONUNDRUM  ·  ISSUE #1',
        ha='center', va='top', fontsize=12, fontweight='bold',
        color=WHITE, transform=ax.transAxes, fontfamily='monospace',
        alpha=0.7)

# Bottom tagline
ax.axhline(0.12, xmin=0.1, xmax=0.9, color=WHITE, linewidth=0.5, alpha=0.2)
ax.text(0.5, 0.085,
        'Better outcomes. Half the cost. What is the United States doing differently — and why?',
        ha='center', va='center', fontsize=13, color=OFFWHITE,
        transform=ax.transAxes, style='italic')
ax.text(0.5, 0.035, 'andrewrexroad.substack.com',
        ha='center', va='center', fontsize=9, color=MID,
        transform=ax.transAxes, fontfamily='monospace')

plt.tight_layout(pad=0)
plt.savefig(OUT_B, dpi=100, bbox_inches='tight', facecolor=NAVY)
plt.close()
print(f'Saved Option B -> {OUT_B}')
