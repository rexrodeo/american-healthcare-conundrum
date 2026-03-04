"""
The American Healthcare Conundrum — Savings Tracker Generator
Run this after each issue to regenerate the tracker image.
Just add a new entry to ISSUES below.

Design: two-panel
  Top    — full $3T context bar. The tiny sliver IS the point.
  Bottom — zoomed view of $0-ZOOM_B, showing per-issue detail.
  Bracket lines connect the zoom window to the zoomed bar.
"""
import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['text.usetex'] = False
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe
import numpy as np

OUT = '/sessions/confident-nice-fermat/mnt/healthcare/figures/savings_tracker.png'

# ── CONFIG — add one line per published issue ─────────────────────────────────
TARGET_TRILLIONS = 3.0   # Japan benchmark gap, in trillions

ISSUES = [
    {"num": 1, "title": "OTC Drug\nOverspending",  "savings_billions": 0.6},
    {"num": 2, "title": "Brand Drug\nPricing Gap", "savings_billions": 25.0},
    # Add future issues here
]
# ─────────────────────────────────────────────────────────────────────────────

TARGET_B = TARGET_TRILLIONS * 1000   # in billions
ZOOM_B   = 100.0                     # zoomed window upper bound (billions)
# Grow ZOOM_B automatically if cumulative savings exceeds 80% of current ZOOM_B
cumulative = sum(i["savings_billions"] for i in ISSUES)
if cumulative > ZOOM_B * 0.80:
    ZOOM_B = cumulative * 1.5

# Build milestone list
cum = 0
milestones = []
for issue in ISSUES:
    cum += issue["savings_billions"]
    milestones.append({
        **issue,
        "cumulative": cum,
        "pct_of_target": cum / TARGET_B * 100,
        "pct_of_zoom":   cum / ZOOM_B  * 100,
    })
total_b   = milestones[-1]["cumulative"]
total_pct = total_b / TARGET_B * 100

# ── Palette ───────────────────────────────────────────────────────────────────
BLUE      = '#1B6CA8'
BLUE_DARK = '#154E80'
BLUE_LITE = '#D6E8F7'
GOLD      = '#E8A020'
GOLD_LITE = '#FFF3CC'
DARK      = '#1A202C'
MID       = '#4A5568'
WHITE     = '#FFFFFF'
RED       = '#C0392B'

# ── Figure layout — two rows via subplot_mosaic ───────────────────────────────
fig = plt.figure(figsize=(14, 5.8))
fig.patch.set_facecolor(WHITE)

# Manual axes: [left, bottom, width, height] in figure fraction
ax_ctx  = fig.add_axes([0.04, 0.72, 0.88, 0.13])   # context bar (full $3T)
ax_zoom = fig.add_axes([0.04, 0.14, 0.88, 0.34])   # zoomed bar

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

# Filled progress
display_fill = max(total_b, TARGET_B * 0.003)   # at least a thin visible sliver
ax_ctx.add_patch(mpatches.FancyBboxPatch(
    (0, CTX_Y), display_fill, CTX_H,
    boxstyle="round,pad=0", linewidth=0,
    facecolor=BLUE, zorder=2))

# Zoom window highlight (gold rectangle showing which portion is zoomed)
zoom_w = ZOOM_B
ax_ctx.add_patch(mpatches.FancyBboxPatch(
    (0, CTX_Y - 0.04), zoom_w, CTX_H + 0.08,
    boxstyle="round,pad=0", linewidth=1.5,
    facecolor=GOLD_LITE, edgecolor=GOLD, alpha=0.70, zorder=3))

# Re-draw progress fill on top of gold highlight
ax_ctx.add_patch(mpatches.FancyBboxPatch(
    (0, CTX_Y), display_fill, CTX_H,
    boxstyle="round,pad=0", linewidth=0,
    facecolor=BLUE, zorder=4))

# "ZOOMED BELOW" label inside gold window
ax_ctx.text(zoom_w / 2, CTX_Y + CTX_H + 0.08,
            f'\u2193 zoomed below',
            ha='center', va='bottom', fontsize=7.5,
            color=GOLD, fontweight='bold', zorder=6)

# $0 and $3T labels
ax_ctx.text(0, CTX_Y - 0.08, '\$0',
            ha='left', va='top', fontsize=8, color=MID, fontweight='bold')
ax_ctx.text(TARGET_B, CTX_Y + CTX_H / 2,
            f'  \$3T\n  target',
            ha='left', va='center', fontsize=8.5, color=MID, fontweight='bold',
            linespacing=1.3)

# Progress % annotation inside bar (right-aligned)
ax_ctx.text(display_fill + TARGET_B * 0.006, CTX_Y + CTX_H / 2,
            f'\${total_b:.1f}B\n{total_pct:.2f}%',
            ha='left', va='center', fontsize=8, color=BLUE_DARK, fontweight='bold')

# ════════════════════════════════════════════════════════════════════
# PANEL B — Zoomed bar ($0 → ZOOM_B)
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

# Fill each issue as a stacked segment with a distinct shade
FILLS = [BLUE_DARK, BLUE, '#3A8CC8', '#5BA3D8']   # progressively lighter
seg_start = 0
for i, m in enumerate(milestones):
    seg_w = m["savings_billions"]
    ax_zoom.add_patch(mpatches.FancyBboxPatch(
        (seg_start, ZM_Y), seg_w, ZM_H,
        boxstyle="round,pad=0", linewidth=0,
        facecolor=FILLS[i % len(FILLS)], zorder=2))
    seg_start += seg_w

# Divider ticks + labels for each milestone
seg_start = 0
for i, m in enumerate(milestones):
    seg_end = seg_start + m["savings_billions"]
    above   = (i % 2 == 0)

    # Tick at segment end
    ax_zoom.plot([seg_end, seg_end],
                 [ZM_Y - 0.04, ZM_Y + ZM_H + 0.04],
                 color=WHITE, linewidth=2, zorder=4)
    ax_zoom.scatter([seg_end], [ZM_Y + ZM_H / 2],
                    s=90, color=WHITE, edgecolors=BLUE_DARK,
                    linewidths=1.8, zorder=5)

    # Label position — center of this issue's segment, clamped so label box
    # doesn't clip the left or right axis edge (assume box ~10B wide at this scale)
    LABEL_MARGIN = ZOOM_B * 0.08
    x_mid = seg_start + m["savings_billions"] / 2
    x_mid = max(x_mid, LABEL_MARGIN)
    x_mid = min(x_mid, ZOOM_B - LABEL_MARGIN)

    if above:
        label_y  = ZM_Y + ZM_H + 0.05
        va       = 'bottom'
        line_y0  = ZM_Y + ZM_H + 0.02
        line_y1  = label_y - 0.01
    else:
        label_y  = ZM_Y - 0.05
        va       = 'top'
        line_y0  = ZM_Y - 0.02
        line_y1  = label_y + 0.01

    # Leader
    ax_zoom.plot([x_mid, x_mid], [line_y0, line_y1],
                 color=BLUE_DARK, linewidth=1.2,
                 linestyle='dotted', zorder=3)

    # Label box
    delta_txt = f'+\${m["savings_billions"]:.1f}B' if i > 0 else f'\${m["savings_billions"]:.1f}B'
    label_txt = (f'Issue #{m["num"]}\n'
                 f'{delta_txt}  \u00b7  cumul. \${m["cumulative"]:.1f}B')
    ax_zoom.text(x_mid, label_y,
                 label_txt,
                 ha='center', va=va,
                 fontsize=9, fontweight='bold', color=BLUE_DARK,
                 bbox=dict(boxstyle='round,pad=0.3', facecolor=WHITE,
                           edgecolor=BLUE_DARK, linewidth=1.1),
                 zorder=6)

    seg_start = seg_end

# Remaining space in zoom window label
remaining_in_zoom = ZOOM_B - total_b
ax_zoom.text(total_b + remaining_in_zoom / 2, ZM_Y + ZM_H / 2,
             f'...{remaining_in_zoom:.0f}B remaining\nin zoom window',
             ha='center', va='center', fontsize=8, color=MID,
             style='italic', zorder=3)

# Axis labels below zoomed bar
ax_zoom.text(0, ZM_Y - 0.17, '\$0',
             ha='left', va='top', fontsize=8.5, color=MID, fontweight='bold')
ax_zoom.text(ZOOM_B, ZM_Y - 0.17, f'\${ZOOM_B:.0f}B',
             ha='right', va='top', fontsize=8.5, color=MID, fontweight='bold')
zoom_ratio = int(round(TARGET_B / ZOOM_B))
ax_zoom.text(ZOOM_B / 2, ZM_Y - 0.17,
             f'Zoom window  (1/{zoom_ratio} of \${TARGET_TRILLIONS:.0f}T scale \u2014 {ZOOM_B/TARGET_B*100:.1f}% of target)',
             ha='center', va='top', fontsize=8, color=GOLD, fontweight='bold')

# ── Bracket lines connecting context zoom window to zoomed bar ────────────────
# We draw these using figure-level coordinates via fig.add_artist / line2D
# Left edge bracket: context left → zoom bar left
# Right edge bracket: context right (ZOOM_B) → zoom bar right

# Transform: context bar ax_ctx — ZOOM_B/TARGET_B is the right edge of window
# We'll use ax.transData -> fig.transFigure
from matplotlib.lines import Line2D

def data_to_fig(ax, x, y):
    """Convert data coords to figure fraction."""
    return ax.transData.transform((x, y))

# Get pixel positions of bracket corners, convert to figure fraction
fig.canvas.draw()   # force layout so transforms work
fig_w, fig_h = fig.get_size_inches() * fig.dpi

# Context bar: left and right edges of zoom window, at bottom of bar
ctx_left_px  = ax_ctx.transData.transform((0,       CTX_Y))
ctx_right_px = ax_ctx.transData.transform((ZOOM_B,  CTX_Y))

# Zoom bar: left and right edges, at top of bar
zm_left_px   = ax_zoom.transData.transform((0,      ZM_Y + ZM_H))
zm_right_px  = ax_zoom.transData.transform((ZOOM_B, ZM_Y + ZM_H))

def to_frac(px):
    return (px[0] / fig_w, px[1] / fig_h)

for ctx_px, zm_px in [(ctx_left_px, zm_left_px), (ctx_right_px, zm_right_px)]:
    cx, cy = to_frac(ctx_px)
    zx, zy = to_frac(zm_px)
    line = Line2D([cx, zx], [cy, zy],
                  transform=fig.transFigure,
                  color=GOLD, linewidth=1.2,
                  linestyle='--', alpha=0.75)
    fig.add_artist(line)

# ── Title and subtitle ────────────────────────────────────────────────────────
fig.text(0.50, 0.985,
         'The American Healthcare Conundrum \u2014 Savings Tracker',
         ha='center', va='top', fontsize=13, fontweight='bold', color=DARK)

fig.text(0.50, 0.955,
         'Benchmarked against Japan \u2014 highest life expectancy, lowest infant mortality '
         'in the OECD, at \$5,790/capita vs. \$14,570 in the US',
         ha='center', va='top', fontsize=8.5, color=MID)

# ── Bottom note ───────────────────────────────────────────────────────────────
fig.text(0.50, 0.01,
         f'Cumulative savings identified: \${total_b:.1f}B  \u00b7  '
         f'{total_pct:.3f}% of the \u223c\$3T annual gap with Japan  '
         f'\u00b7  Issues published: {len(milestones)}',
         ha='center', va='bottom', fontsize=8, color=MID)

plt.savefig(OUT, dpi=160, bbox_inches='tight', facecolor=WHITE)
plt.close()
print(f'Tracker saved -> {OUT}')
print(f'  Cumulative: \${total_b:.1f}B  ({total_pct:.3f}% of \$3T target)')
print(f'  Zoom window: \$0-\${ZOOM_B:.0f}B')
print(f'  Issues: {len(milestones)}')
