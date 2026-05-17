"""
generate_all_charts.py — Issue #12: The Consolidation Tax
Single entry-point to wipe figures/*.png and regenerate all 6 charts + hero.
Run from any directory: python3 /path/to/generate_all_charts.py
"""

import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
FIGURES.mkdir(exist_ok=True)

# Wipe existing PNGs (skip if permission denied — e.g. read-only mount)
wiped = 0
for f in FIGURES.glob("*.png"):
    try:
        f.unlink()
        wiped += 1
    except PermissionError:
        pass  # will be overwritten by savefig
print(f"Wiped {wiped} existing PNGs (overwrites remaining)")

# ── Brand colors ─────────────────────────────────────────────────────────────
NAVY  = "#1A1F2E"
TEAL  = "#0E8A72"
RED   = "#B7182A"
GOLD  = "#D4AF37"
WHITE = "#F8F8F6"
LTGRAY = "#8090A0"

# ── Load data ─────────────────────────────────────────────────────────────────
cross_val  = pd.read_csv(RESULTS / "cross_validation.csv")
savings_mkt= pd.read_csv(RESULTS / "savings_by_market.csv")
overlap_df = pd.read_csv(RESULTS / "overlap_subtractions.csv")
with open(RESULTS / "savings_estimate.json") as f:
    est = json.load(f)
with open(RESULTS / "hrr_sensitivity_summary.json") as f:
    hrr = json.load(f)

# ─────────────────────────────────────────────────────────────────────────────
# CHART 1 — Four-anchor coefficient band + our cohort
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
fig.patch.set_facecolor(NAVY)
ax.set_facecolor(NAVY)

# Anchors: (label, lo, hi)
anchors = [
    ("Cooper 2019 (QJE)\nMonopoly differential", 15.3, 15.3),
    ("Dafny/Ho/Lee 2019\n(RAND J Econ)", 7.0, 9.0),
    ("FTC Evanston WP 307\nRetrospective", 11.1, 17.9),
    ("Brot-Goldberg 2024\n(NBER WP 32613)", 8.0, 10.0),
]
our_val = 13.26  # blended weighted-average from cross_validation.csv

y_positions = [4, 3, 2, 1]
labels = [a[0] for a in anchors]
los    = [a[1] for a in anchors]
his    = [a[2] for a in anchors]

for i, (y, lo, hi) in enumerate(zip(y_positions, los, his)):
    if lo == hi:
        # single point — diamond
        ax.plot(lo, y, marker="D", color=TEAL, markersize=10, zorder=3)
        ax.text(lo + 0.3, y, f"{lo}%", color=TEAL, va="center", fontsize=10,
                fontweight="bold")
    else:
        # range bar
        ax.barh(y, hi - lo, left=lo, height=0.4, color=TEAL, alpha=0.75,
                zorder=3)
        ax.text(hi + 0.3, y, f"{lo}–{hi}%", color=TEAL, va="center",
                fontsize=10, fontweight="bold")

# Our cohort — vertical dashed line + label
ax.axvline(our_val, color=GOLD, linewidth=2, linestyle="--", zorder=4, alpha=0.9)
ax.text(our_val + 0.3, 4.75,
        f"Our cohort: {our_val}%",
        color=GOLD, fontsize=10.5, fontweight="bold", va="top")
ax.text(our_val + 0.3, 4.35,
        "(blended, post-2019 mergers)",
        color=GOLD, fontsize=8.5, va="top", alpha=0.85)

# Shade the band region
ax.axvspan(7.0, 17.9, alpha=0.07, color=TEAL)

# Y labels
ax.set_yticks(y_positions)
ax.set_yticklabels(labels, color=WHITE, fontsize=9.5)
ax.set_ylim(0.4, 5.5)
ax.set_xlim(0, 24)
ax.set_xlabel("Price uplift from hospital consolidation (%)", color=WHITE,
              fontsize=10)
ax.tick_params(axis="x", colors=WHITE, labelsize=9)
ax.tick_params(axis="y", colors=WHITE, labelsize=9.5)
for spine in ax.spines.values():
    spine.set_edgecolor(LTGRAY)
ax.xaxis.label.set_color(WHITE)
ax.set_facecolor(NAVY)
ax.grid(axis="x", color=LTGRAY, alpha=0.25, linewidth=0.6)

ax.set_title(
    "Hospital Consolidation Price Effect: Four Anchors + Our Cohort",
    color=WHITE, fontsize=13, fontweight="bold", pad=12
)
ax.text(
    0.0, -0.14,
    "Sources: Cooper QJE 2019; Dafny/Ho/Lee RAND J Econ 2019; FTC WP 307; Brot-Goldberg NBER WP 32613.\n"
    "Computed from CMS POS + HCRIS 2018–2025. Dashed line = Issue #12 blended post-2019 cohort (n=315 HSAs).",
    transform=ax.transAxes, color=LTGRAY, fontsize=6.5, va="top", ha="left"
)

plt.subplots_adjust(bottom=0.20, left=0.28, right=0.96, top=0.88)
out1 = FIGURES / "chart1_coefficient_band.png"
fig.savefig(out1, dpi=150, facecolor=NAVY, bbox_inches=None)
plt.close(fig)
print(f"Saved {out1}")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 2 — HHI shift distribution across 315 merger HSAs
# ─────────────────────────────────────────────────────────────────────────────
# Unique HSAs — use the single row per HSA (315 rows)
hhi_vals = savings_mkt["hhi_shift"].values

fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
fig.patch.set_facecolor(NAVY)
ax.set_facecolor(NAVY)

bins = np.arange(0, 5200, 250)
counts, edges, patches = ax.hist(hhi_vals, bins=bins, color=TEAL, alpha=0.85,
                                  edgecolor=NAVY, linewidth=0.5, zorder=3)

# Color bars above 200 threshold differently
for patch, left in zip(patches, edges[:-1]):
    if left < 200:
        patch.set_facecolor(LTGRAY)
        patch.set_alpha(0.5)

# DOJ/FTC 200-pt threshold
ax.axvline(200, color=RED, linewidth=2, linestyle="--", zorder=4)
ax.text(220, counts.max() * 0.92,
        "DOJ/FTC merger-review\nthreshold: 200 pts",
        color=RED, fontsize=8.5, va="top", ha="left")

# Mean line
mean_hhi = hhi_vals.mean()
ax.axvline(mean_hhi, color=GOLD, linewidth=1.8, linestyle="-", zorder=4,
           alpha=0.9)
ax.text(mean_hhi + 80, counts.max() * 0.78,
        f"Mean: {mean_hhi:,.0f} pts",
        color=GOLD, fontsize=9, va="top", ha="left", fontweight="bold")

ax.set_xlabel("HHI Shift (points)", color=WHITE, fontsize=10)
ax.set_ylabel("Number of merger markets", color=WHITE, fontsize=10)
ax.tick_params(axis="both", colors=WHITE, labelsize=9)
for spine in ax.spines.values():
    spine.set_edgecolor(LTGRAY)
ax.grid(axis="y", color=LTGRAY, alpha=0.25, linewidth=0.6)

ax.set_title(
    "HHI Shift Across 315 Merger HSAs",
    color=WHITE, fontsize=13, fontweight="bold", pad=28
)
subtitle = "Mean shift: 2,319 pts. DOJ/FTC merger-review threshold for already-concentrated markets: 200 pts."
ax.text(0.5, 1.055, subtitle, transform=ax.transAxes, color=LTGRAY,
        fontsize=8.5, ha="center", va="bottom")

ax.text(
    0.0, -0.16,
    "Source: CMS POS 2018–2025 + Dartmouth Atlas HSAs. Top-2 firm combination simulation per HSA-year. "
    "Gray bars (< 200 pts) are below DOJ/FTC threshold.",
    transform=ax.transAxes, color=LTGRAY, fontsize=6.5, va="top", ha="left"
)

plt.subplots_adjust(bottom=0.20, left=0.09, right=0.97, top=0.84)
out2 = FIGURES / "chart2_hhi_shift_distribution.png"
fig.savefig(out2, dpi=150, facecolor=NAVY, bbox_inches=None)
plt.close(fig)
print(f"Saved {out2}")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 3 — HRR vs HSA sensitivity
# ─────────────────────────────────────────────────────────────────────────────
hsa_gross    = 17.37
hsa_ov3      = 3.47
hsa_ov15     = 0.87
hsa_booked   = 13.03

hrr_gross    = hrr["hrr_raw_gross_bil"]      # 21.73
hrr_ov3      = hrr["hrr_overlap_3_bil"]      # 4.35
hrr_ov15     = hrr["hrr_overlap_15_bil"]     # 1.09
hrr_booked   = hrr["hrr_booked_bil"]         # 16.3

fig, ax = plt.subplots(figsize=(9, 5), dpi=100)
fig.patch.set_facecolor(NAVY)
ax.set_facecolor(NAVY)

x     = np.array([0, 1])
width = 0.35

# Booked (bottom)
b_booked = ax.bar(x, [hsa_booked, hrr_booked], width, label="Booked",
                  color=TEAL, zorder=3)
# Overlap #15 (middle)
b_ov15 = ax.bar(x, [hsa_ov15, hrr_ov15], width,
                bottom=[hsa_booked, hrr_booked], label="Overlap #15 (facility fees)",
                color=GOLD, alpha=0.75, zorder=3)
# Overlap #3 (top)
b_ov3 = ax.bar(x, [hsa_ov3, hrr_ov3], width,
               bottom=[hsa_booked + hsa_ov15, hrr_booked + hrr_ov15],
               label="Overlap #3 (hospital pricing)",
               color=RED, alpha=0.70, zorder=3)

# Value labels inside each segment — check heights first
def label_bar(ax, bar_container, bottoms, color=WHITE, fontsize=10):
    for bar, bot in zip(bar_container, bottoms):
        h = bar.get_height()
        if h >= 0.8:
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bot + h / 2,
                    f"${h:.1f}B",
                    ha="center", va="center", color=color,
                    fontsize=fontsize, fontweight="bold")

label_bar(ax, b_booked,  [0, 0],                        color=WHITE, fontsize=11)
label_bar(ax, b_ov15,    [hsa_booked, hrr_booked],       color=NAVY,  fontsize=9)
label_bar(ax, b_ov3,     [hsa_booked+hsa_ov15, hrr_booked+hrr_ov15], color=WHITE, fontsize=9)

# Gross total annotations outside top
for xi, gross in zip(x, [hsa_gross, hrr_gross]):
    ax.text(xi, gross + 0.5, f"Gross: ${gross:.1f}B",
            ha="center", va="bottom", color=LTGRAY, fontsize=9)

ax.set_xticks(x)
ax.set_xticklabels([
    f"HSA-level\n(n=315 merger markets,\n3,436 nationally)",
    f"HRR-level\n(n=178 merger HRRs,\n306 nationally)"
], color=WHITE, fontsize=9.5)
ax.set_ylabel("Savings ($ billions)", color=WHITE, fontsize=10)
ax.set_ylim(0, 26)
ax.tick_params(axis="y", colors=WHITE, labelsize=9)
ax.tick_params(axis="x", colors=WHITE)
for spine in ax.spines.values():
    spine.set_edgecolor(LTGRAY)
ax.grid(axis="y", color=LTGRAY, alpha=0.25, linewidth=0.6)

ax.legend(loc="upper left", fontsize=8.5, framealpha=0.25,
          facecolor=NAVY, edgecolor=LTGRAY,
          labelcolor=WHITE)

ax.set_title(
    "HSA vs HRR Sensitivity: $13–16 Billion Booked Range",
    color=WHITE, fontsize=13, fontweight="bold", pad=28
)
ax.text(
    0.5, 1.055,
    "HRR aggregates regional pricing power more correctly; HSA provides market-level granularity.",
    transform=ax.transAxes, color=LTGRAY, fontsize=8.5, ha="center", va="bottom"
)

ax.text(
    0.0, -0.18,
    "Source: CMS POS + HCRIS 2018–2025. HSA = Health Service Area (n=3,436 nationally); "
    "HRR = Hospital Referral Region (n=306 nationally).\n"
    "Overlap #3 = Issue #3 hospital pricing (20% subtraction); Overlap #15 = facility-fee differential (5% subtraction).",
    transform=ax.transAxes, color=LTGRAY, fontsize=6.5, va="top", ha="left"
)

plt.subplots_adjust(bottom=0.22, left=0.10, right=0.96, top=0.83)
out3 = FIGURES / "chart3_hrr_vs_hsa_sensitivity.png"
fig.savefig(out3, dpi=150, facecolor=NAVY, bbox_inches=None)
plt.close(fig)
print(f"Saved {out3}")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 4 — Per-market booked savings distribution
# ─────────────────────────────────────────────────────────────────────────────
# Aggregate raw savings by unique HSA
mkt_savings = savings_mkt.groupby("hsa")["raw_savings_bil"].sum().reset_index()
mkt_savings = mkt_savings.sort_values("raw_savings_bil", ascending=False).reset_index(drop=True)
n_mkt = len(mkt_savings)
total_raw = mkt_savings["raw_savings_bil"].sum()

fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
fig.patch.set_facecolor(NAVY)
ax.set_facecolor(NAVY)

vals_m = mkt_savings["raw_savings_bil"].values * 1000  # convert to $M
xs = np.arange(n_mkt)

bar_colors = [RED if i < 5 else (GOLD if i < 20 else TEAL) for i in range(n_mkt)]
ax.bar(xs, vals_m, color=bar_colors, width=1.0, zorder=3)

median_m = np.median(vals_m)
mean_m   = np.mean(vals_m)
ax.axhline(median_m, color=WHITE, linewidth=1.2, linestyle=":", alpha=0.7)
ax.axhline(mean_m, color=GOLD, linewidth=1.4, linestyle="--", alpha=0.9)

# Consolidated callout box (top-right area): mean, median, top-5/top-20 share
# Placed in clear airspace above the bar tail, below the legend.
top5_pct  = mkt_savings.iloc[:5]["raw_savings_bil"].sum() / total_raw * 100
top20_pct = mkt_savings.iloc[:20]["raw_savings_bil"].sum() / total_raw * 100
callout = (f"Mean per market: \\${mean_m:.0f}M  (gold dashed)\n"
           f"Median per market: \\${median_m:.0f}M  (white dotted)\n"
           f"Top 5 markets: {top5_pct:.1f}% of raw savings\n"
           f"Top 20 markets: {top20_pct:.1f}% of raw savings")
ax.text(0.50, 0.68, callout,
        transform=ax.transAxes, color=WHITE, fontsize=10,
        va="top", ha="left",
        bbox=dict(boxstyle="round,pad=0.5", facecolor=NAVY, edgecolor=LTGRAY,
                  alpha=0.95, linewidth=1.2))

# Color legend — upper right
p_red  = mpatches.Patch(color=RED,  label="Top 5 markets")
p_gold = mpatches.Patch(color=GOLD, label="Markets 6–20")
p_teal = mpatches.Patch(color=TEAL, label="Markets 21–315")
ax.legend(handles=[p_red, p_gold, p_teal], loc="upper right",
          fontsize=8.5, framealpha=0.3, facecolor=NAVY,
          edgecolor=LTGRAY, labelcolor=WHITE)

ax.set_xlabel("Merger markets ranked by raw savings (1 = largest)", color=WHITE, fontsize=10)
ax.set_ylabel("Raw savings per market ($M)", color=WHITE, fontsize=10)
ax.tick_params(axis="both", colors=WHITE, labelsize=9)
for spine in ax.spines.values():
    spine.set_edgecolor(LTGRAY)
ax.grid(axis="y", color=LTGRAY, alpha=0.2, linewidth=0.6)
ax.set_xlim(-2, n_mkt + 2)

ax.set_title(
    "Per-Market Booked Savings: No Pareto Outlier Dominance",
    color=WHITE, fontsize=13, fontweight="bold", pad=28
)
ax.text(
    0.5, 1.055,
    f"315 merger HSAs. Median \\${median_m:.0f}M, mean \\${mean_m:.0f}M. No single market drives the headline.",
    transform=ax.transAxes, color=LTGRAY, fontsize=8.5, ha="center", va="bottom"
)

ax.text(
    0.0, -0.16,
    "Source: Issue #12 build pipeline. Raw savings before overlap subtraction. "
    "Red = top 5 markets; gold = markets 6–20; teal = markets 21–315.",
    transform=ax.transAxes, color=LTGRAY, fontsize=6.5, va="top", ha="left"
)

plt.subplots_adjust(bottom=0.18, left=0.09, right=0.97, top=0.84)
out4 = FIGURES / "chart4_per_market_savings.png"
fig.savefig(out4, dpi=150, facecolor=NAVY, bbox_inches=None)
plt.close(fig)
print(f"Saved {out4}")

# ─────────────────────────────────────────────────────────────────────────────
# CHART 5 — Cumulative Savings Tracker
# ─────────────────────────────────────────────────────────────────────────────
issues = [
    ("#1\nOTC Drugs",     0.6),
    ("#2\nDrug Pricing",  25.0),
    ("#3\nHospital Px",   73.0),
    ("#4\nPBMs",          30.0),
    ("#5\nAdmin Waste",   200.0),
    ("#6\nSupply Waste",  28.0),
    ("#7\nGLP-1",         40.0),
    ("#8\nDenial Mach.",  32.0),
    ("#9\nEmployer",       6.6),
    ("#10\nProcedures",    7.6),
    ("#11\nMA Overpay",   28.0),
    ("#12\nConsol. Tax",  13.0),
]
labels_i = [x[0] for x in issues]
values_i = [x[1] for x in issues]
cumsum   = np.cumsum(values_i)
total_b  = cumsum[-1]   # 483.8
gap_b    = 3240.0       # $3.24T

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5.5), dpi=100,
                               gridspec_kw={"width_ratios": [3, 1], "wspace": 0.45})
fig.patch.set_facecolor(NAVY)
ax1.set_facecolor(NAVY)
ax2.set_facecolor(NAVY)

# Suptitle — give it room at y=0.99, subplots top=0.85 so panels don't collide
fig.suptitle(
    f"Cumulative Savings Identified: \\${total_b:.1f}B  (14.9% of US-Japan Gap)",
    color=WHITE, fontsize=11.5, fontweight="bold", y=0.98
)

# Left panel — per-issue bars
bar_colors_i = [RED if lbl.startswith("#12") else TEAL for lbl in labels_i]
bars = ax1.bar(range(len(issues)), values_i, color=bar_colors_i, zorder=3, width=0.7)

# Value labels inside/above bars
for i, (bar, val) in enumerate(zip(bars, values_i)):
    h = bar.get_height()
    if h >= 20:
        ax1.text(bar.get_x() + bar.get_width() / 2, h / 2,
                 f"${val:.0f}B", ha="center", va="center",
                 color=WHITE, fontsize=7.5, fontweight="bold")
    else:
        ax1.text(bar.get_x() + bar.get_width() / 2, h + 3,
                 f"${val:.0f}B", ha="center", va="bottom",
                 color=WHITE, fontsize=7, fontweight="bold")

# X-tick labels: rotated 30° so 12 short labels don't overlap on a narrow panel
short_names = ["OTC", "Drug Px", "Hosp Px", "PBMs", "Admin", "Supply",
               "GLP-1", "Denial", "Employer", "Procedure", "MA Overpay", "Consol."]
xtick_labels = [f"#{i+1} {s}" for i, s in enumerate(short_names)]
ax1.set_xticks(range(len(issues)))
ax1.set_xticklabels(xtick_labels, color=WHITE, fontsize=8, rotation=35, ha="right")
ax1.set_ylabel("Savings ($B)", color=WHITE, fontsize=9)
ax1.tick_params(axis="y", colors=WHITE, labelsize=8.5)
ax1.tick_params(axis="x", colors=WHITE, pad=2)
for spine in ax1.spines.values():
    spine.set_edgecolor(LTGRAY)
ax1.grid(axis="y", color=LTGRAY, alpha=0.2, linewidth=0.6)
ax1.set_ylim(0, 235)
ax1.set_title("Per-Issue Savings", color=WHITE, fontsize=10, pad=6)

# Right panel — cumulative gauge
pct = total_b / gap_b * 100
ax2.bar([0], [total_b], color=TEAL, width=0.5, zorder=3)
ax2.bar([0], [gap_b - total_b], bottom=[total_b], color=LTGRAY, alpha=0.3,
        width=0.5, zorder=3)

ax2.text(0, total_b / 2, f"${total_b:.1f}B\nidentified",
         ha="center", va="center", color=WHITE, fontsize=10, fontweight="bold")
ax2.text(0, total_b + (gap_b - total_b) / 2,
         f"${(gap_b - total_b)/1000:.2f}T\nremaining",
         ha="center", va="center", color=LTGRAY, fontsize=9)

ax2.set_ylim(0, gap_b * 1.05)
ax2.set_xlim(-0.6, 0.6)
ax2.set_xticks([])
ax2.set_ylabel("$ Billions", color=WHITE, fontsize=9)
ax2.tick_params(axis="y", colors=WHITE, labelsize=8)
for spine in ax2.spines.values():
    spine.set_edgecolor(LTGRAY)
ax2.set_title(f"{pct:.1f}% of\n\\$3.24T gap", color=GOLD, fontsize=10,
              fontweight="bold", pad=6)

fig.text(
    0.02, 0.02,
    "Sources: Published Issues #1–#12. Full-scale gap: CMS NHE 2024 + OECD Health at a Glance 2025 ($3.24T).",
    color=LTGRAY, fontsize=6.5, va="bottom", ha="left"
)

# Bottom margin increased to accommodate rotated x-tick labels
plt.subplots_adjust(bottom=0.24, left=0.08, right=0.97, top=0.83)
out5 = FIGURES / "chart5_savings_tracker.png"
fig.savefig(out5, dpi=150, facecolor=NAVY, bbox_inches=None)
plt.close(fig)
print(f"Saved {out5}")

# ─────────────────────────────────────────────────────────────────────────────
# HERO IMAGE — hero_cover.png  (2184×1572 @ 150dpi = figsize 14.56×10.48 @ 100dpi)
# Safe zone: center 62% wide × 52% tall
# ─────────────────────────────────────────────────────────────────────────────
FW, FH = 14.56, 10.48
fig = plt.figure(figsize=(FW, FH), dpi=100)
fig.patch.set_facecolor(NAVY)
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, FW)
ax.set_ylim(0, FH)
ax.axis("off")
ax.set_facecolor(NAVY)

# Subtle background grid
for gx in np.arange(0, FW, 1.0):
    ax.axvline(gx, color=WHITE, alpha=0.03, linewidth=0.5)
for gy in np.arange(0, FH, 1.0):
    ax.axhline(gy, color=WHITE, alpha=0.03, linewidth=0.5)

CX = FW / 2  # 7.28 — center x
SZ_X_LO = CX - FW * 0.31   # safe zone left  (19% margin)
SZ_X_HI = CX + FW * 0.31   # safe zone right
SZ_Y_LO = FH * 0.24         # safe zone bottom (24% margin)
SZ_Y_HI = FH * 0.76         # safe zone top

# ── Top-center series banner ──────────────────────────────────────────────────
banner_y = SZ_Y_HI + 0.20
ax.text(CX, banner_y,
        "THE AMERICAN HEALTHCARE CONUNDRUM",
        color=RED, fontsize=22, fontweight="bold",
        ha="center", va="center",
        fontfamily="DejaVu Sans")

# Issue number in gold
ax.text(CX, banner_y - 0.65,
        "ISSUE #12",
        color=GOLD, fontsize=18, fontweight="bold",
        ha="center", va="center")

# Red horizontal rule
rule_y = banner_y - 1.10
ax.plot([SZ_X_LO, SZ_X_HI], [rule_y, rule_y], color=RED, linewidth=2.5)

# ── Main hook number ──────────────────────────────────────────────────────────
hook_y = rule_y - 1.3
ax.text(CX, hook_y,
        "$13 BILLION",
        color=GOLD, fontsize=72, fontweight="bold",
        ha="center", va="center",
        fontfamily="DejaVu Sans")

# ── Subheadline ───────────────────────────────────────────────────────────────
sub_y = hook_y - 1.45
ax.text(CX, sub_y,
        "What Hospital Consolidation Costs\nCommercial Payers Each Year",
        color=WHITE, fontsize=28, fontweight="bold",
        ha="center", va="center",
        linespacing=1.35,
        fontfamily="DejaVu Sans")

# ── Stats bar ─────────────────────────────────────────────────────────────────
stats_y = SZ_Y_LO + 0.10
stats_text = "1,155 OWNERSHIP CHANGES  ·  315 MERGER MARKETS  ·  POST-2019 COHORT  ·  13.3% BLENDED UPLIFT"
ax.text(CX, stats_y,
        stats_text,
        color=LTGRAY, fontsize=11.5,
        ha="center", va="center",
        fontfamily="DejaVu Sans")

out_hero = FIGURES / "hero_cover.png"
fig.savefig(out_hero, dpi=150, facecolor=NAVY, bbox_inches=None)
plt.close(fig)
print(f"Saved {out_hero}")

print("\nAll 6 PNGs generated successfully.")
print(f"Figures directory: {FIGURES}")
for f in sorted(FIGURES.glob("*.png")):
    print(f"  {f.name}: {f.stat().st_size:,} bytes")
