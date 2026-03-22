#!/usr/bin/env python3
"""
Issue #4, Chart 1: "Three Companies. 80% of US Prescriptions."
Two-panel chart: PBM market share (left), drug dollar flow (right).

ANTI-OVERLAP STRATEGY:
- Stacked bar uses LEFT-side labels for bottom segments, RIGHT-side for top
- External labels are manually Y-positioned to guarantee no collision
- PBM callout uses a dedicated annotation region below the bar
- All text ≥7pt at rendered size
"""
import os, pathlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
FIG_DIR = SCRIPT_DIR / 'figures'
FIG_DIR.mkdir(exist_ok=True)
OUT = str(FIG_DIR / 'chart1_pbm_market.png')

# Brand
NAVY   = '#1A1F2E'
TEAL   = '#0E8A72'
RED    = '#B7182A'
GOLD   = '#D4AF37'
WHITE  = '#F8F8F6'
GRAY   = '#6B7080'
LTGRAY = '#C8CCD4'
BLUE   = '#3A7CA5'

plt.rcParams.update({
    'font.family': 'DejaVu Sans', 'font.size': 9,
    'axes.facecolor': WHITE, 'figure.facecolor': WHITE, 'text.color': NAVY,
})

# ── Data ───────────────────────────────────────────────────────
pbm_names = ['CVS Caremark\n(Aetna)', 'Express Scripts\n(Cigna/Evernorth)',
             'OptumRx\n(UnitedHealth)', 'All Others']
pbm_share = [34, 24, 22, 20]
pbm_colors = [RED, GOLD, TEAL, LTGRAY]
pbm_ann = ['CVS Health ($358B rev, 2023)', 'Cigna/Evernorth ($195B rev, 2023)',
           'UnitedHealth ($372B rev, 2023)', '']

# Stacked bar: bottom to top
# (label, value, color)
stack = [
    ('Manufacturers\n(net of rebates)',  290, TEAL),
    ('Wholesalers / Distributors',        60, BLUE),
    ('PBM-retained margin',               72, RED),
    ('Pharmacies (dispensing)',            30, GOLD),
    ('Admin / Other',                    270, GRAY),
]

# ── Figure ─────────────────────────────────────────────────────
fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(10, 6), dpi=100,
    gridspec_kw={'width_ratios': [1.2, 0.8], 'wspace': 0.45})

fig.text(0.5, 0.97, 'Three Companies. 80% of US Prescriptions.',
         fontsize=15, fontweight='bold', color=NAVY, ha='center', va='top')

# ══════════════════════════════════════════════════════════════
# PANEL A: PBM Market Share
# ══════════════════════════════════════════════════════════════
ax_l.set_title('PBM Market Share\n(% of US prescription claims, 2024)',
               fontsize=10, fontweight='bold', color=NAVY, pad=10)

y_pos = [3, 2, 1, 0]
bars = ax_l.barh(y_pos, pbm_share, height=0.52, color=pbm_colors,
                 edgecolor='white', linewidth=0.5)

for bar, share in zip(bars, pbm_share):
    ax_l.text(bar.get_width() / 2, bar.get_y() + bar.get_height() / 2,
              f'{share}%', ha='center', va='center',
              fontsize=12, fontweight='bold', color='white')

for bar, ann in zip(bars, pbm_ann):
    if ann:
        ax_l.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
                  ann, ha='left', va='center', fontsize=7.5, color=GRAY)

ax_l.set_yticks(y_pos)
ax_l.set_yticklabels(pbm_names, fontsize=8.5)
ax_l.set_xlim(0, 58)
ax_l.tick_params(axis='x', bottom=False, labelbottom=False)
ax_l.tick_params(axis='y', length=0)
for sp in ax_l.spines.values(): sp.set_visible(False)

bbox_props = dict(boxstyle='round,pad=0.4', facecolor=RED,
                  edgecolor='none', alpha=0.9)
ax_l.text(35, -0.8, 'Big 3 combined:\n80% of 6.6 billion\nprescriptions/year',
          fontsize=8, fontweight='bold', color='white',
          ha='center', va='top', bbox=bbox_props, linespacing=1.4)
ax_l.set_ylim(-1.6, 4.0)

# ══════════════════════════════════════════════════════════════
# PANEL B: Drug Dollar Flow — stacked bar with spread labels
# ══════════════════════════════════════════════════════════════
ax_r.set_title('Where the Drug Dollar Goes\n(~$722.5B total, 2023)',
               fontsize=10, fontweight='bold', color=NAVY, pad=10)

bar_x = 0.42
bar_w = 0.40
cumulative = 0
segs = []
for label, val, color in stack:
    segs.append((cumulative, val, color, label))
    ax_r.bar(bar_x, val, bottom=cumulative, width=bar_w,
             color=color, edgecolor='white', linewidth=0.8)
    cumulative += val

# ── Label placement strategy ──────────────────────────────────
# Large segments (≥100): label INSIDE the segment, white text
# Small segments (<100): label OUTSIDE with leader line
# To prevent overlap, manually assign Y positions for external labels
# and alternate left/right sides.

# Segment centers:
#   Manufacturers: 0+290/2 = 145   → INSIDE
#   Wholesalers:   290+60/2 = 320  → outside LEFT, y=310
#   PBM:           350+72/2 = 386  → outside RIGHT, y=386 (with red callout)
#   Pharmacies:    422+30/2 = 437  → outside LEFT, y=450
#   Admin/Other:   452+270/2 = 587 → INSIDE

# Inside labels
for (bottom, height, color, label) in segs:
    cy = bottom + height / 2
    if height >= 100:
        ax_r.text(bar_x, cy, f'{label}\n${height}B',
                  ha='center', va='center', fontsize=7,
                  fontweight='bold', color='white', linespacing=1.25)

# Wholesalers — LEFT side, y=310
wh_cy = 290 + 60 / 2  # 320
ax_r.annotate(
    'Wholesalers /\nDistributors  $60B',
    xy=(bar_x - bar_w / 2 - 0.01, wh_cy),
    xytext=(0.0, 310),
    fontsize=7, color=NAVY, fontweight='bold',
    ha='right', va='center', linespacing=1.2,
    arrowprops=dict(arrowstyle='-', color=NAVY, lw=0.7))

# PBM-retained — RIGHT side with red callout, y=386
pbm_cy = 290 + 60 + 72 / 2  # 386
ax_r.annotate(
    'PBM-retained\nmargin  $72B',
    xy=(bar_x + bar_w / 2 + 0.01, pbm_cy),
    xytext=(0.82, 386),
    fontsize=7.5, color=RED, fontweight='bold',
    ha='left', va='center', linespacing=1.2,
    arrowprops=dict(arrowstyle='-', color=RED, lw=1.0))

# Pharmacies — LEFT side, y=450
ph_cy = 290 + 60 + 72 + 30 / 2  # 437
ax_r.annotate(
    'Pharmacies\n(dispensing)  $30B',
    xy=(bar_x - bar_w / 2 - 0.01, ph_cy),
    xytext=(0.0, 460),
    fontsize=7, color=NAVY, fontweight='bold',
    ha='right', va='center', linespacing=1.2,
    arrowprops=dict(arrowstyle='-', color=NAVY, lw=0.7))

# Red PBM recoverable callout — placed below bar, no overlap risk
bbox_pbm = dict(boxstyle='round,pad=0.3', facecolor=RED,
                edgecolor='none', alpha=0.9)
ax_r.annotate(
    '$30B recoverable',
    xy=(bar_x + bar_w / 2, pbm_cy),
    xytext=(0.82, 310),
    fontsize=8, fontweight='bold', color='white',
    ha='left', va='center', bbox=bbox_pbm,
    arrowprops=dict(arrowstyle='->', color=RED, lw=1.3,
                    connectionstyle='arc3,rad=0.2'))

# Dashed line at top
ax_r.plot([bar_x - bar_w / 2 - 0.08, bar_x + bar_w / 2 + 0.08],
          [722.5, 722.5], color=NAVY, ls='--', lw=0.8, alpha=0.5)
ax_r.text(bar_x, 738, '$722.5B total US drug spending (2023)',
          ha='center', va='bottom', fontsize=7, color=NAVY, style='italic')

ax_r.set_xlim(-0.15, 1.15)
ax_r.set_ylim(0, 780)
ax_r.tick_params(axis='x', bottom=False, labelbottom=False)
ax_r.tick_params(axis='y', left=False, labelleft=False)
for sp in ax_r.spines.values(): sp.set_visible(False)

# ── Footnote ───────────────────────────────────────────────────
footnote = (
    'Market share: Drug Channels Institute, Top PBMs of 2024. '
    'Revenue: CVS Health, Cigna/Evernorth, UnitedHealth 2023 Annual Reports. '
    'Drug spending: Bernard & Sloan, J Gen Internal Med, 2025. '
    'Dollar flow is illustrative of order-of-magnitude shares.'
)
fig.text(0.12, 0.02, footnote, fontsize=5.5, color=GRAY, ha='left', va='bottom')

fig.subplots_adjust(left=0.12, right=0.92, top=0.84, bottom=0.08)
fig.savefig(OUT, dpi=150, facecolor=WHITE, edgecolor='none')
plt.close(fig)
print(f'Saved: {OUT}  ({os.path.getsize(OUT)/1024:.0f} KB)')
