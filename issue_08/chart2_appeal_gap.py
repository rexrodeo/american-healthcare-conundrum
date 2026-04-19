"""
Issue #8 Chart 2: The Appeal Gap — UHC vs Humana denial/appeal/overturn funnel.

Fixes the prior version's clipping problem: raw-count labels for narrow
bars (Appeals Filed, Overturned on Appeal) were placed at bar center
regardless of width, which truncated them to partial characters (",0", "6")
because the bar was narrower than the text. This version:

- Labels go INSIDE when the bar is wide enough to contain them comfortably
  (≥15% of panel xlim), OUTSIDE-RIGHT otherwise.
- Inside labels render in white bold on the colored bar.
- Outside labels render in navy bold on white, with the percentage
  appended in a lighter color right after.
- Writes to figures/ via a relative path (session-agnostic).
"""

from pathlib import Path
import matplotlib.pyplot as plt

# ---- Data -----------------------------------------------------------------
insurers  = ["UnitedHealthcare", "Humana"]
denials   = [1_068_806, 653_593]
appeals   = [93_097, 17_690]
overturn  = [53_934, 11_449]

appeal_rate = [a / d * 100 for a, d in zip(appeals, denials)]
overturn_rate_of_denials = [o / d * 100 for o, d in zip(overturn, denials)]

RED, GOLD, TEAL, NAVY = "#B7182A", "#D4AF37", "#0E8A72", "#1A1F2E"
FUNNEL_COLORS = [RED, GOLD, TEAL]

# ---- Figure ---------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(12, 7.0), dpi=100,
                         gridspec_kw={"wspace": 0.30})
plt.subplots_adjust(left=0.08, right=0.97, top=0.78, bottom=0.16)

panel_xlims = [1_300_000, 800_000]
INSIDE_FRACTION = 0.15  # bar must occupy >=15% of panel to hold an inside label

for idx, ax in enumerate(axes):
    insurer = insurers[idx]
    xlim    = panel_xlims[idx]
    values  = [denials[idx], appeals[idx], overturn[idx]]
    pcts    = [100.0, appeal_rate[idx], overturn_rate_of_denials[idx]]
    levels  = ["Total\nDenials", "Appeals\nFiled", "Overturned\non Appeal"]
    heights = [0.80, 0.60, 0.40]
    ypos    = [2, 1, 0]

    ax.barh(ypos, values, height=heights,
            color=FUNNEL_COLORS, edgecolor="white", linewidth=2)

    for val, pct, y, height in zip(values, pcts, ypos, heights):
        inside_ok = val >= INSIDE_FRACTION * xlim
        if inside_ok:
            # Value inside bar, percentage outside-right
            ax.text(val / 2, y, f"{val:,}",
                    va="center", ha="center",
                    fontsize=11, fontweight="bold", color="white")
            ax.text(val + xlim * 0.015, y, f"{pct:.1f}%",
                    va="center", ha="left",
                    fontsize=10, fontweight="bold", color="#333333")
        else:
            # Everything outside-right: value + percentage together
            ax.text(val + xlim * 0.015, y,
                    f"{val:,}   ({pct:.1f}%)",
                    va="center", ha="left",
                    fontsize=10, fontweight="bold", color=NAVY)

    # Left-side level labels
    for level, y in zip(levels, ypos):
        ax.text(-xlim * 0.04, y, level,
                va="center", ha="right",
                fontsize=10, fontweight="bold", color=NAVY)

    ax.set_xlim(-xlim * 0.10, xlim)
    ax.set_ylim(-0.7, 2.7)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Panel title (sits just above axes; main title + subtitle live above)
    ax.text(0.5, 1.04, insurer, transform=ax.transAxes,
            fontsize=13, fontweight="bold", ha="center", color=NAVY)

# ---- Overall title + subtitle --------------------------------------------
fig.suptitle("The Appeal Gap: Most Denials Are Never Challenged",
             fontsize=15, fontweight="bold", y=0.955, color=NAVY)
fig.text(0.5, 0.895,
         "Medicare Advantage standard PA denial and appeal outcomes, CY2025",
         ha="center", fontsize=10, style="italic", color="#666666")

# ---- Key finding callout (bottom center, above footnote) -----------------
fig.text(0.5, 0.08,
         "~977,000 patients denied entitled care, never appealed "
         "(8.7% + 2.7% appeal rates)",
         ha="center", fontsize=10, fontweight="bold", color=NAVY,
         bbox=dict(boxstyle="round,pad=0.6", facecolor="#B7182A",
                   alpha=0.15, edgecolor="#B7182A", linewidth=1.5))

# ---- Footnote ------------------------------------------------------------
fig.text(0.08, 0.02,
         "Source: CMS-0057-F Prior Authorization Transparency Rule, CY2025 "
         "aggregate data. Overturned denials represent full overturns; "
         "partial overturns excluded.",
         fontsize=6.5, ha="left", style="italic", color="#666666")

# ---- Save (session-agnostic relative path) -------------------------------
out = Path(__file__).resolve().parent / "figures" / "chart2_appeal_gap.png"
out.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(out, dpi=150, facecolor="white")
plt.close(fig)
print(f"saved: {out}")
