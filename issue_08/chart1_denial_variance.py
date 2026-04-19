"""
Issue #8 Chart 1: UnitedHealthcare MA PA denial rate variance across 23 contracts.
Horizontal bar chart, sorted ascending.

Key design decisions (read Chart Creation Rules in CLAUDE.md before editing):
- figsize (10, 9) for 23 rows: ~0.38 inches per row, readable.
- Inside labels for bars >=6%; outside-right labels for bars <6% (rule 2).
- Volume-weighted avg callout is anchored to the actual 13.5% row (H0169),
  not floating near the top.
- Request-count annotations for high-volume contracts (H2001, H0543) are
  placed OUTSIDE the bar on the right with bbox backgrounds (no collisions).
- "95.4% approved" UHC headline-claim callout lives in the clear zone
  below the y=0 axis, with enough vertical clearance from the footnote.
- Writes to figures/ relative to this script's location so it runs in any session.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd

# ---- Data -----------------------------------------------------------------
contracts = [
    ("H1537", 25.2, None),
    ("H2001", 23.4, "1.85M requests"),
    ("H0710", 22.3, None),
    ("R5342", 22.1, None),
    ("H5435", 22.0, None),
    ("H3307", 21.6, None),
    ("H3379", 21.4, None),
    ("R0759", 21.2, None),
    ("H3418", 21.1, None),
    ("H0755", 20.9, None),
    ("H8211", 20.9, None),
    ("H1659", 20.7, None),
    ("H2802", 20.6, None),
    ("H8768", 20.6, None),
    ("R2604", 20.6, None),
    ("H5253", 18.9, None),
    ("H2406", 17.3, None),
    ("H0169", 13.5, "volume-weighted avg"),
    ("H3113",  9.9, None),
    ("H4527",  3.4, None),
    ("R6801",  4.0, None),
    ("H0543",  1.8, "1.57M requests"),
    ("H7833",  0.7, None),
]
df = (pd.DataFrame(contracts, columns=["contract", "denial_rate", "note"])
        .sort_values("denial_rate", ascending=True)
        .reset_index(drop=True))

# ---- Style ----------------------------------------------------------------
RED, GOLD, ORANGE, TEAL, NAVY = "#B7182A", "#D4AF37", "#F5A623", "#0E8A72", "#1A1F2E"

def color_for(rate):
    if rate > 20:   return RED
    if rate >= 15:  return GOLD
    if rate >= 10:  return ORANGE
    return TEAL

# ---- Figure ---------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 9), dpi=100)
plt.subplots_adjust(left=0.12, right=0.97, top=0.90, bottom=0.10)

colors = [color_for(r) for r in df["denial_rate"]]
y = range(len(df))
ax.barh(y, df["denial_rate"], color=colors, height=0.72)
ax.set_yticks(list(y))
ax.set_yticklabels(df["contract"], fontsize=9)

# ---- Value labels: inside if >=6%, outside-right if <6% -------------------
INSIDE_CUTOFF = 6.0
for i, row in df.iterrows():
    rate = row["denial_rate"]
    if rate >= INSIDE_CUTOFF:
        ax.text(rate - 0.4, i, f"{rate:.1f}%", va="center", ha="right",
                fontsize=9.5, fontweight="bold", color="white")
    else:
        ax.text(rate + 0.4, i, f"{rate:.1f}%", va="center", ha="left",
                fontsize=9.5, fontweight="bold", color=NAVY)

# ---- Request-count annotations (outside right, bbox'd) --------------------
# Place far to the right of all other content; add visible bbox so they pop.
ANNOTATE_X = 27.2
for i, row in df.iterrows():
    if row["note"] and "requests" in row["note"]:
        ax.annotate(f"({row['note']})",
                    xy=(row["denial_rate"] + 0.2, i), xycoords="data",
                    xytext=(ANNOTATE_X, i), textcoords="data",
                    fontsize=8, style="italic", va="center", ha="left",
                    color="#333333",
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                              edgecolor="#cccccc", alpha=0.95),
                    arrowprops=dict(arrowstyle="-", color="#aaaaaa", lw=0.7))

# ---- Volume-weighted avg: dashed vertical + callout anchored to 13.5% row -
AVG = 13.5
avg_row_idx = df.index[df["contract"] == "H0169"][0]
ax.axvline(AVG, color="#333333", linestyle="--", linewidth=1.4, alpha=0.55, zorder=1)
# Callout sits to the RIGHT of the line, in the blank zone above H0169 row.
ax.annotate(f"Volume-weighted avg: {AVG}%",
            xy=(AVG, avg_row_idx), xycoords="data",
            xytext=(AVG + 0.6, avg_row_idx), textcoords="data",
            fontsize=9, style="italic", color=NAVY, ha="left", va="center",
            bbox=dict(boxstyle="round,pad=0.4", facecolor="white",
                      edgecolor="#999999", alpha=0.95),
            arrowprops=dict(arrowstyle="-", color="#666666", lw=0.8))

# ---- UHC "95.4% approved" callout: parked in the clear zone below y=0 -----
ax.axvline(4.6, color="#999999", linestyle=":", linewidth=1.4, alpha=0.55, zorder=1)
ax.annotate('"95.4% approved" (UHC headline claim)',
            xy=(4.6, 0), xycoords="data",
            xytext=(4.6, -2.2), textcoords="data",
            fontsize=8, style="italic", color="#555555", ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.35", facecolor="#F8F8F6",
                      edgecolor="#999999", alpha=0.95),
            arrowprops=dict(arrowstyle="-", color="#999999", lw=0.7))

# ---- Titles, axes, grid ---------------------------------------------------
ax.set_xlabel("Standard PA Denial Rate (%)", fontsize=11, fontweight="bold")
ax.set_ylabel("Medicare Advantage Contract", fontsize=11, fontweight="bold")
# Main title via suptitle, subtitle via ax.set_title for guaranteed separation.
fig.suptitle("Same Insurer. Same Rules. 36x Variance in Denial Rates.",
             fontsize=15, fontweight="bold", color=NAVY, y=0.965)
ax.set_title("UnitedHealthcare standard PA denial rates, 61 Medicare Advantage contracts, CY2025",
             fontsize=10, style="italic", color="#666666", pad=10)

ax.set_xlim(0, 32)  # headroom for outside-right annotations
ax.set_ylim(-3.2, len(df) - 0.3)
ax.set_xticks([0, 5, 10, 15, 20, 25])
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_linewidth(0.5)
ax.spines["bottom"].set_linewidth(0.5)
ax.grid(axis="x", alpha=0.3, linestyle="-", linewidth=0.5)
ax.set_axisbelow(True)

# ---- Legend (bottom-right, clear zone) ------------------------------------
legend_handles = [
    mpatches.Patch(color=RED,    label=">20% denial rate"),
    mpatches.Patch(color=GOLD,   label="15–20% denial rate"),
    mpatches.Patch(color=ORANGE, label="10–15% denial rate"),
    mpatches.Patch(color=TEAL,   label="<10% denial rate"),
]
ax.legend(handles=legend_handles, loc="lower right", fontsize=8.5,
          frameon=True, fancybox=True)

# ---- Footnote (left-aligned, safe bottom margin) --------------------------
fig.text(0.12, 0.025,
         "Source: CMS-0057-F Prior Authorization Transparency Rule disclosures, April 2026. "
         "Excludes post-acute, behavioral health, and delegated providers.",
         fontsize=6.5, ha="left", style="italic", color="#666666")

# ---- Save (relative path, so runs in any session) -------------------------
out = Path(__file__).resolve().parent / "figures" / "chart1_denial_variance.png"
out.parent.mkdir(parents=True, exist_ok=True)
plt.savefig(out, dpi=150, facecolor="white")
plt.close(fig)
print(f"saved: {out}")
