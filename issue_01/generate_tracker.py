"""
The American Healthcare Conundrum — Savings Tracker v4
Matches Issue #2 style exactly; adds Issue #3 as a distinct red segment.

Layout:
  Top    — full $3T context bar. The tiny sliver IS the point.
  Bottom — zoomed view of $0-ZOOM_B, showing per-issue detail.
  Gold bracket lines connect the zoom window to the zoomed bar.
"""
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['text.usetex'] = False
matplotlib.rcParams['text.parse_math'] = False
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import os

import pathlib
_PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT_TRACKER = str(_PROJECT_ROOT / 'figures' / 'savings_tracker.png')
OUT_CHART5  = str(_PROJECT_ROOT / 'issue_03' / 'figures' / 'chart5_savings_tracker.png')

# ── CONFIG ─────────────────────────────────────────────────────────────────
TARGET_TRILLIONS = 3.0

ISSUES = [
    {"num": 1, "title": "OTC Drug\nOverspending",  "savings_billions": 0.6},
    {"num": 2, "title": "Brand Drug\nPricing Gap", "savings_billions": 25.0},
    {"num": 3, "title": "Hospital\nRef. Pricing",  "savings_billions": 75.0},
]

# ── Palette — Issue #2 blues + new red for Issue #3 ───────────────────────
BLUE      = '#1B6CA8'
BLUE_DARK = '#154E80'
BLUE_LITE = '#D6E8F7'
RED       = '#B7182A'   # project brand red — distinct third color
RED_DARK  = '#8A1020'
GOLD      = '#E8A020'
GOLD_LITE = '#FFF3CC'
DARK      = '#1A202C'
MID       = '#4A5568'
WHITE     = '#FFFFFF'

# Fill colors for zoom bar segments — match Issue #2 progression, red for #3
FILLS      = [BLUE_DARK, BLUE, RED]
LABEL_COLS = [BLUE_DARK, BLUE_DARK, RED_DARK]   # label box border/text color

# ── Milestones ─────────────────────────────────────────────────────────────
TARGET_B   = TARGET_TRILLIONS * 1000
cumulative = sum(i["savings_billions"] for i in ISSUES)

ZOOM_B = 100.0
if cumulative > ZOOM_B * 0.80:
    ZOOM_B = round(cumulative * 1.30 / 25) * 25   # round up to nearest $25B

cum = 0
milestones = []
for i, issue in enumerate(ISSUES):
    cum += issue["savings_billions"]
    milestones.append({
        **issue,
        "cumulative":    cum,
        "pct_of_target": cum / TARGET_B * 100,
        "fill":          FILLS[i],
        "label_col":     LABEL_COLS[i],
    })

total_b   = milestones[-1]["cumulative"]
total_pct = total_b / TARGET_B * 100

# ── Figure ─────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(14, 5.8))
fig.patch.set_facecolor(WHITE)

ax_ctx  = fig.add_axes([0.04, 0.72, 0.88, 0.13])
ax_zoom = fig.add_axes([0.04, 0.14, 0.88, 0.34])

for ax in (ax_ctx, ax_zoom):
    ax.set_facecolor(WHITE)
    ax.axis('off')

# ════════════════════════════════════════════════════════════════════
# PANEL A — Full $3T context bar
# ════════════════════════════════════════════════════════════════════
ax_ctx.set_xlim(0, TARGET_B)
ax_ctx.set_ylim(0, 1)

CTX_Y = 0.15
CTX_H = 0.60

# Background
ax_ctx.add_patch(mpatches.FancyBboxPatch(
    (0, CTX_Y), TARGET_B, CTX_H,
    boxstyle="round,pad=0", linewidth=0.8,
    facecolor=BLUE_LITE, edgecolor=BLUE_DARK, zorder=1))

# Stacked per-issue slivers (minimum visible width so they show)
seg_start = 0
for m in milestones:
    seg_w = max(m["savings_billions"], TARGET_B * 0.003)
    ax_ctx.add_patch(mpatches.FancyBboxPatch(
        (seg_start, CTX_Y), seg_w, CTX_H,
        boxstyle="round,pad=0", linewidth=0,
        facecolor=m["fill"], zorder=2))
    seg_start += m["savings_billions"]

# Gold zoom window highlight
ax_ctx.add_patch(mpatches.FancyBboxPatch(
    (0, CTX_Y - 0.04), ZOOM_B, CTX_H + 0.08,
    boxstyle="round,pad=0", linewidth=1.5,
    facecolor=GOLD_LITE, edgecolor=GOLD, alpha=0.70, zorder=3))

# Re-draw slivers on top of gold highlight
seg_start = 0
for m in milestones:
    seg_w = max(m["savings_billions"], TARGET_B * 0.003)
    ax_ctx.add_patch(mpatches.FancyBboxPatch(
        (seg_start, CTX_Y), seg_w, CTX_H,
        boxstyle="round,pad=0", linewidth=0,
        facecolor=m["fill"], zorder=4))
    seg_start += m["savings_billions"]

# "↓ zoomed below" label in gold
ax_ctx.text(ZOOM_B / 2, CTX_Y + CTX_H + 0.08,
            '\u2193 zoomed below',
            ha='center', va='bottom', fontsize=7.5,
            color=GOLD, fontweight='bold', zorder=6)

# $0 label below context bar
ax_ctx.text(0, CTX_Y - 0.08, '$0',
            ha='left', va='top', fontsize=8, color=MID, fontweight='bold')

# $3T label at right
ax_ctx.text(TARGET_B, CTX_Y + CTX_H / 2,
            '  $3T\n  goal',
            ha='left', va='center', fontsize=8.5, color=MID, fontweight='bold',
            linespacing=1.3)

# Progress annotation beside the slivers
ax_ctx.text(total_b + TARGET_B * 0.006, CTX_Y + CTX_H / 2,
            f'${total_b:.1f}B\n({total_pct:.2f}%)',
            ha='left', va='center', fontsize=8, color=BLUE_DARK, fontweight='bold')

# ════════════════════════════════════════════════════════════════════
# PANEL B — Zoomed bar
# ════════════════════════════════════════════════════════════════════
ax_zoom.set_xlim(0, ZOOM_B)
ax_zoom.set_ylim(0, 1)

ZM_Y = 0.34
ZM_H = 0.28

# Background
ax_zoom.add_patch(mpatches.FancyBboxPatch(
    (0, ZM_Y), ZOOM_B, ZM_H,
    boxstyle="round,pad=0", linewidth=0.8,
    facecolor=BLUE_LITE, edgecolor=BLUE_DARK, zorder=1))

# Stacked issue segments
seg_start = 0
for m in milestones:
    ax_zoom.add_patch(mpatches.FancyBboxPatch(
        (seg_start, ZM_Y), m["savings_billions"], ZM_H,
        boxstyle="round,pad=0", linewidth=0,
        facecolor=m["fill"], zorder=2))
    seg_start += m["savings_billions"]

# White dividers between segments
seg_start = 0
for m in milestones[:-1]:
    seg_start += m["savings_billions"]
    ax_zoom.plot([seg_start, seg_start],
                 [ZM_Y - 0.04, ZM_Y + ZM_H + 0.04],
                 color=WHITE, linewidth=2, zorder=4)

# Per-issue callout labels — alternate above/below, matching Issue #2 style
seg_start = 0
for i, m in enumerate(milestones):
    seg_end   = seg_start + m["savings_billions"]
    above     = (i % 2 == 0)   # #1 above, #2 below, #3 above

    # Dot at segment midpoint
    x_mid = seg_start + m["savings_billions"] / 2
    ax_zoom.scatter([seg_end], [ZM_Y + ZM_H / 2],
                    s=90, color=WHITE, edgecolors=m["label_col"],
                    linewidths=1.8, zorder=5)

    # Clamp label x so it doesn't clip the axis
    MARGIN = ZOOM_B * 0.08
    x_label = max(x_mid, MARGIN)
    x_label = min(x_label, ZOOM_B - MARGIN)

    if above:
        label_y = ZM_Y + ZM_H + 0.05
        va      = 'bottom'
        line_y0 = ZM_Y + ZM_H + 0.02
        line_y1 = label_y - 0.01
    else:
        label_y = ZM_Y - 0.05
        va      = 'top'
        line_y0 = ZM_Y - 0.02
        line_y1 = label_y + 0.01

    # Dotted leader
    ax_zoom.plot([x_label, x_label], [line_y0, line_y1],
                 color=m["label_col"], linewidth=1.2,
                 linestyle='dotted', zorder=3)

    # Label box — Issue #2 format: two lines
    delta_txt = f'+${m["savings_billions"]:.1f}B' if i > 0 else f'${m["savings_billions"]:.1f}B'
    label_txt = (f'Issue #{m["num"]}  {delta_txt}\n'
                 f'\u2248 ${m["cumulative"]:.1f}B cumulative')
    ax_zoom.text(x_label, label_y, label_txt,
                 ha='center', va=va,
                 fontsize=9, fontweight='bold', color=m["label_col"],
                 linespacing=1.3,
                 bbox=dict(boxstyle='round,pad=0.3', facecolor=WHITE,
                           edgecolor=m["label_col"], linewidth=1.1),
                 zorder=6)

    seg_start = seg_end

# Remaining space label in zoom bar
remaining = ZOOM_B - total_b
if remaining > ZOOM_B * 0.10:
    ax_zoom.text(total_b + remaining / 2, ZM_Y + ZM_H / 2,
                 f'...{remaining:.0f}B more\nto fill this window',
                 ha='center', va='center', fontsize=8, color=MID,
                 style='italic', zorder=3)

# Axis labels below zoom bar
ax_zoom.text(0,      ZM_Y - 0.17, '$0',
             ha='left',  va='top', fontsize=8.5, color=MID, fontweight='bold')
ax_zoom.text(ZOOM_B, ZM_Y - 0.17, f'${ZOOM_B:.0f}B',
             ha='right', va='top', fontsize=8.5, color=MID, fontweight='bold')
zoom_ratio = int(round(TARGET_B / ZOOM_B))
ax_zoom.text(ZOOM_B / 2, ZM_Y - 0.17,
             f'Zoomed view  (${ZOOM_B:.0f}B window — {ZOOM_B/TARGET_B*100:.1f}% of $3T target)',
             ha='center', va='top', fontsize=8, color=GOLD, fontweight='bold')

# ── Bracket lines: context zoom box → zoomed bar ──────────────────────────
fig.canvas.draw()
fig_w, fig_h = fig.get_size_inches() * fig.dpi

ctx_left_px  = ax_ctx.transData.transform((0,      CTX_Y))
ctx_right_px = ax_ctx.transData.transform((ZOOM_B, CTX_Y))
zm_left_px   = ax_zoom.transData.transform((0,      ZM_Y + ZM_H))
zm_right_px  = ax_zoom.transData.transform((ZOOM_B, ZM_Y + ZM_H))

def to_frac(px):
    return (px[0] / fig_w, px[1] / fig_h)

for ctx_px, zm_px in [(ctx_left_px, zm_left_px), (ctx_right_px, zm_right_px)]:
    cx, cy = to_frac(ctx_px)
    zx, zy = to_frac(zm_px)
    fig.add_artist(Line2D([cx, zx], [cy, zy],
                          transform=fig.transFigure,
                          color=GOLD, linewidth=1.2, linestyle='--', alpha=0.75))

# ── Title ──────────────────────────────────────────────────────────────────
fig.text(0.50, 0.985,
         'The American Healthcare Conundrum — Savings Tracker',
         ha='center', va='top', fontsize=13, fontweight='bold', color=DARK)

fig.text(0.50, 0.952,
         f'${total_b:.1f}B identified so far  \u00b7  '
         f'{total_pct:.2f}% of the ~$3T annual gap with Japan  '
         f'\u00b7  {len(milestones)} issues published',
         ha='center', va='top', fontsize=8.5, color=MID)

# ── Footer ─────────────────────────────────────────────────────────────────
fig.text(0.50, 0.01,
         'Benchmarked against Japan — highest life expectancy, lowest infant mortality '
         'in the OECD ($5,790/capita vs. $14,570 in the US)',
         ha='center', va='bottom', fontsize=8, color=MID, style='italic')

# ── Save ───────────────────────────────────────────────────────────────────
for out_path in [OUT_TRACKER, OUT_CHART5]:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, dpi=160, bbox_inches='tight', facecolor=WHITE)
    print(f'Saved -> {out_path}')

plt.close()
print(f'  Cumulative: ${total_b:.1f}B  ({total_pct:.2f}% of $3T)')
print(f'  Zoom window: $0-${ZOOM_B:.0f}B')
