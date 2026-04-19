"""
Issue #8 Chart 3 — Savings Components (v3, Path C, 2026-04-17)
4-segment horizontal stacked bar: A+B+C+E = $30B midpoint, booked $32B.
Component D (Deductible-Delay Extraction) dropped pending claims-level data.
"""
import matplotlib
matplotlib.rcParams['text.usetex'] = False
matplotlib.rcParams['text.parse_math'] = False
import matplotlib.pyplot as plt
import pathlib

_PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = str(_PROJECT_ROOT / 'issue_08' / 'figures' / 'chart3_savings_components.png')

# Brand palette
NAVY  = '#1A1F2E'
TEAL  = '#0E8A72'
RED   = '#B7182A'
GOLD  = '#D4AF37'
GREY  = '#666666'
MID   = '#888888'
WHITE = '#FFFFFF'

# Component midpoints (from newsletter Consolidated Estimate, Path C)
components = [
    ('A', 'Care Suppression',          13.7, RED),
    ('B', 'Vertical Integration',      10.3, GOLD),
    ('C', 'AI Denial Escalation',       5.7, TEAL),
    ('E', 'Risk Adjustment',            0.3, GREY),
]
total_mid = sum(c[2] for c in components)   # 30.0
booked    = 32.0
range_lo, range_hi = 22.3, 37.5

# ── Figure ────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
fig.patch.set_facecolor(WHITE)
ax.set_facecolor(WHITE)

BAR_Y = 0
BAR_H = 0.45
cumulative = 0
segments = []

for letter, label, value, color in components:
    ax.barh(BAR_Y, value, left=cumulative, height=BAR_H, color=color,
            edgecolor=WHITE, linewidth=2)
    segments.append({'letter': letter, 'label': label, 'value': value,
                     'color': color, 'start': cumulative,
                     'mid': cumulative + value / 2})
    cumulative += value

# ── Inside labels for WIDE segments (≥$5B ≈ large enough for 1 line) ─────────
WIDE_THRESHOLD = 5.0
for seg in segments:
    if seg['value'] >= WIDE_THRESHOLD:
        ax.text(seg['mid'], BAR_Y, f"{seg['letter']}: ${seg['value']:.1f}B",
                ha='center', va='center',
                fontsize=11, fontweight='bold', color=WHITE, zorder=5)

# ── External labels (names) on alternating rows above the bar ────────────────
ABOVE_ROW_1 = BAR_H / 2 + 0.35
ABOVE_ROW_2 = BAR_H / 2 + 0.75

for i, seg in enumerate(segments):
    # Alternate rows
    y_label = ABOVE_ROW_1 if i % 2 == 0 else ABOVE_ROW_2

    # Connector line
    ax.plot([seg['mid'], seg['mid']],
            [BAR_Y + BAR_H / 2 + 0.02, y_label - 0.04],
            color=seg['color'], linewidth=1.0, linestyle='dotted', zorder=3)

    # Narrow segments (E) get compact label outside
    if seg['value'] < WIDE_THRESHOLD:
        label_txt = f"{seg['letter']}: {seg['label']}\n${seg['value']:.1f}B"
    else:
        label_txt = f"{seg['letter']}: {seg['label']}"

    ax.text(seg['mid'], y_label, label_txt,
            ha='center', va='bottom', fontsize=8.5, fontweight='bold',
            color=seg['color'],
            bbox=dict(boxstyle='round,pad=0.3', facecolor=WHITE,
                      edgecolor=seg['color'], linewidth=1.0),
            zorder=6)

# ── Total callout below the bar ──────────────────────────────────────────────
ax.text(cumulative / 2, BAR_Y - 0.85,
        f'Midpoint: ${total_mid:.1f}B/year   |   Booked: ${booked:.1f}B/year',
        ha='center', va='center', fontsize=12, fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.5', facecolor=NAVY,
                  edgecolor=GOLD, linewidth=2),
        color=GOLD, zorder=6)

ax.text(cumulative / 2, BAR_Y - 1.35,
        f'Range: ${range_lo:.1f}B to ${range_hi:.1f}B per year',
        ha='center', va='center', fontsize=9, style='italic', color=MID)

ax.text(cumulative / 2, BAR_Y - 1.85,
        'Component D (deductible-delay extraction) excluded pending claims-level data',
        ha='center', va='center', fontsize=8, style='italic', color=RED)

# ── Styling ──────────────────────────────────────────────────────────────────
ax.set_xlim(-2, cumulative + 3)
ax.set_ylim(-2.4, 1.25)
ax.set_xticks([])
ax.set_yticks([])
for spine in ax.spines.values():
    spine.set_visible(False)

# ── Title ────────────────────────────────────────────────────────────────────
ax.text(0.5, 1.15,
        'Issue #8: $32 Billion in Recoverable Denial Extraction',
        transform=ax.transAxes, fontsize=14, fontweight='bold',
        ha='center', color=NAVY)
ax.text(0.5, 1.07,
        'Three measurable mechanisms plus risk adjustment; deductible-delay (D) described but not booked',
        transform=ax.transAxes, fontsize=9, style='italic', ha='center', color=MID)

# ── Footnote ─────────────────────────────────────────────────────────────────
fig.text(0.08, 0.02,
         'Sources: CMS-0057-F per-contract PA data (2026), AMA PA Survey (2024), Health Affairs Nov 2025 (Optum premium),\n'
         'Stanford npj Digital Medicine Jan 2026 (AI denial escalation), HHS OIG Oct 2024 (risk adjustment overpayments).',
         fontsize=6, ha='left', style='italic', color=MID)

plt.tight_layout(rect=[0, 0.06, 1, 0.93])
plt.savefig(OUT, dpi=150, bbox_inches='tight', facecolor=WHITE)
plt.close(fig)

print(f"Saved -> {OUT}")
print(f"  Total midpoint: ${total_mid:.1f}B | Booked: ${booked:.1f}B | Range: ${range_lo:.1f}B-${range_hi:.1f}B")
