"""
Issue #3 Visualization Script — The 254% Problem
Generates 5 publication-quality charts for the newsletter.

Brand palette:
  Navy  #1A1F2E  |  Teal  #0E8A72  |  Red  #B7182A
  Gold  #D4AF37  |  Off-white  #F8F8F6  |  Mid-grey  #8A8F9E

All charts: DejaVu Sans, 150 dpi, tight layout, 7-9% bottom margin for footnote.
"""

import json, os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
from matplotlib.patches import FancyArrowPatch

# ── Paths ──────────────────────────────────────────────────────────
RESDIR  = "/sessions/magical-youthful-ride/mnt/healthcare/issue_03/results"
FIGDIR  = "/sessions/magical-youthful-ride/mnt/healthcare/issue_03/figures"
os.makedirs(FIGDIR, exist_ok=True)

# ── Brand palette ─────────────────────────────────────────────────
NAVY   = "#1A1F2E"
TEAL   = "#0E8A72"
RED    = "#B7182A"
GOLD   = "#D4AF37"
WHITE  = "#F8F8F6"
GREY   = "#8A8F9E"
LGREY  = "#D0D3DC"

DPI = 150

def fmt_k(x, pos=None):
    """Format dollar amounts as $Xk or $XM."""
    if abs(x) >= 1e6:
        return f"${x/1e6:.0f}M"
    return f"${x/1000:.0f}k"

def save(fig, name, extra_bottom=0.09):
    fig.subplots_adjust(bottom=extra_bottom)
    path = os.path.join(FIGDIR, name)
    fig.savefig(path, dpi=DPI, bbox_inches="tight",
                facecolor=WHITE, edgecolor="none")
    plt.close(fig)
    print(f"  Saved: {name}")
    return path

# ══════════════════════════════════════════════════════════════════
# CHART 1 — International Procedure Price Comparison
# Horizontal grouped bar chart: 5 procedures × 6 countries
# ══════════════════════════════════════════════════════════════════
print("\n=== Chart 1: International Procedure Price Comparison ===")

with open(os.path.join(RESDIR, "procedure_prices.json")) as f:
    procs = json.load(f)

# Select 4 procedures + 6 countries for clean layout
# Countries from iFHP 2024-2025 primary source (2022 data); Japan not included in iFHP
selected_procs = ["Hip Replacement", "Knee Replacement",
                   "Coronary Bypass", "Appendectomy"]
countries_order = ["Spain", "New Zealand", "UK", "Germany", "Australia", "USA"]
country_colors  = {
    "USA":         RED,
    "Germany":     TEAL,
    "UK":          "#4A7C9E",
    "Australia":   "#2E9E6B",
    "Spain":       GOLD,
    "New Zealand": "#7B6FAD",
}

fig, axes = plt.subplots(1, 4, figsize=(14, 5.5), facecolor=WHITE)
fig.patch.set_facecolor(WHITE)

for ax, proc in zip(axes, selected_procs):
    prices = procs[proc]
    vals   = [prices.get(c, np.nan) for c in countries_order]

    # Compute US ratio for each country
    us_val = prices["USA"]

    bars = ax.barh(countries_order, vals,
                   color=[country_colors[c] for c in countries_order],
                   edgecolor="none", height=0.65)

    # Value labels on bars
    for bar, val, country in zip(bars, vals, countries_order):
        if not np.isnan(val):
            label = f"${val/1000:.0f}k"
            ax.text(val + us_val * 0.01, bar.get_y() + bar.get_height()/2,
                    label, va="center", ha="left",
                    fontsize=7.5, color=NAVY,
                    fontfamily="DejaVu Sans", fontweight="bold" if country == "USA" else "normal")

    ax.set_xlim(0, us_val * 1.35)
    ax.set_facecolor(WHITE)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color(LGREY)
    ax.tick_params(left=False, bottom=False, labelsize=8)
    ax.xaxis.set_visible(False)

    # Ratio badge for US bar — value already shown by black bar label, so just flag it
    ax.text(0.97, 0.97, "← US price",
            transform=ax.transAxes, ha="right", va="top",
            fontsize=8.5, color=RED, fontweight="bold",
            fontfamily="DejaVu Sans")

    ax.set_title(proc, fontsize=9.5, fontweight="bold", color=NAVY,
                 fontfamily="DejaVu Sans", pad=8)

fig.suptitle("The Same Operation. A Very Different Price.",
             fontsize=14, fontweight="bold", color=NAVY,
             fontfamily="DejaVu Sans", y=1.01)

fig.text(0.5, -0.03,
         "Source: iFHP International Health Cost Comparison Report 2024-2025 (2022 data), produced with HCCI. "
         "Prices are median insurer-paid (allowed) amounts. Countries shown: USA, Australia, Germany, New Zealand, Spain, UK.",
         ha="center", fontsize=7, color=GREY, fontfamily="DejaVu Sans", style="italic")

save(fig, "chart1_international_comparison.png", extra_bottom=0.10)

# ══════════════════════════════════════════════════════════════════
# CHART 2 — The Price Stack (Hip Replacement Waterfall)
# Shows 5 tiers: cost → intl → Medicare → commercial → chargemaster
# ══════════════════════════════════════════════════════════════════
print("\n=== Chart 2: Price Stack — Hip Replacement ===")

with open(os.path.join(RESDIR, "price_stack_hip.json")) as f:
    stack = json.load(f)

layers = stack["layers"]
labels = [l["label"] for l in layers]
values = [l["value"] for l in layers]
colors = [l["color"] for l in layers]
# Update chargemaster to slightly lighter dark red
colors[-1] = "#8B1010"

fig, ax = plt.subplots(figsize=(9, 5.2), facecolor=WHITE)
ax.set_facecolor(WHITE)

# Horizontal bars
bars = ax.barh(range(len(labels)), values,
               color=colors, edgecolor=WHITE, linewidth=0.5, height=0.65)

# Value labels — inside each bar, white bold text
for i, (bar, val) in enumerate(zip(bars, values)):
    label = f"${val:,.0f}"
    # Centre label at 50% of bar width; keep it inside even for short bars
    x_pos = val * 0.5
    ax.text(x_pos, bar.get_y() + bar.get_height()/2,
            label, va="center", ha="center",
            fontsize=10, color=WHITE, fontweight="bold",
            fontfamily="DejaVu Sans")

# Annotations — fixed right column, well past the chargemaster bar ($73k)
ANNOT_X = 78000
peer_median = stack["peer_median"]
gap_dollars = values[3] - values[2]
ratios = {
    4: f"Uninsured list price\n{values[4]/values[0]:.0f}× actual cost",
    3: (f"US commercial (iFHP)\n"
        f"+{stack['gap_medicare_to_commercial_pct']:.0%} over Medicare  "
        f"(${gap_dollars:,.0f} gap)\n"
        f"{values[3]/values[0]:.1f}× actual cost"),
    2: f"Medicare rate (DRG 470)\n{values[2]/values[0]:.2f}× actual cost",
    1: f"Peer median\n(Germany / Spain / UK / NZ)\n{peer_median/values[0]:.2f}× actual cost",
    0: f"Actual hospital cost\n(HCRIS FY2023 est.)",
}
for idx, text in ratios.items():
    ax.text(ANNOT_X, idx,
            text, va="center", ha="left",
            fontsize=7, color=GREY, fontfamily="DejaVu Sans",
            linespacing=1.5)

ax.set_yticks(range(len(labels)))
ax.set_yticklabels(labels, fontsize=9.5, color=NAVY, fontfamily="DejaVu Sans")
ax.invert_yaxis()

ax.set_xlim(0, 130000)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_k))
ax.tick_params(bottom=True, left=False, labelsize=9)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)
ax.spines["bottom"].set_color(LGREY)
ax.xaxis.label.set_color(GREY)

# Arrow highlighting the Medicare → Commercial gap — sits cleanly between the two bars
y_arrow = 2.5
ax.annotate("", xy=(values[3], y_arrow), xytext=(values[2], y_arrow),
            arrowprops=dict(arrowstyle="<->", color=RED, lw=1.8))

ax.set_title("Hip Replacement: Five Ways to Price the Same Operation",
             fontsize=12, fontweight="bold", color=NAVY,
             fontfamily="DejaVu Sans", pad=10)

fig.text(0.5, -0.04,
         "Sources: US commercial and peer median from iFHP International Health Cost Comparison Report 2024-2025 "
         "(2022 data, median insurer-paid amounts). Medicare rate: CMS IPPS FY2024 DRG 470 (~$15,000 wage-adjusted). "
         "Actual hospital cost: estimated from CMS HCRIS FY2023 (Medicare = ~125% of operating cost). "
         "Chargemaster: typical published list price for this procedure (hospital price transparency data). "
         "RAND Round 5.1: commercial = 254% of Medicare across all inpatient procedures nationally.",
         ha="center", fontsize=6.5, color=GREY, fontfamily="DejaVu Sans", style="italic",
         wrap=True)

save(fig, "chart2_price_stack.png", extra_bottom=0.10)

# ══════════════════════════════════════════════════════════════════
# CHART 3 — Hospital Markup Distribution (from HCRIS FY2022)
# Histogram of 1/CCR across 3,187 US hospitals
# ══════════════════════════════════════════════════════════════════
print("\n=== Chart 3: Hospital Markup Distribution (HCRIS) ===")

ccr_df = pd.read_csv(os.path.join(RESDIR, "hospital_ccr_2023.csv"))

fig, ax = plt.subplots(figsize=(9, 5.2), facecolor=WHITE)
ax.set_facecolor(WHITE)

# Filter to plausible markup range
df_plot = ccr_df[(ccr_df.markup >= 1.0) & (ccr_df.markup <= 10.0)].copy()

# Color bars by markup bucket
bins = np.arange(1.0, 10.25, 0.25)
n_hospitals = len(ccr_df)  # Use full dataset count (3,187) for title; histogram shows 1x-10x range

# Compute histogram
counts, edges = np.histogram(df_plot.markup, bins=bins)

# Color: green below 2x, gold 2-3x, red above 3x (HCCI median = 3.5x)
bar_colors = []
for left in edges[:-1]:
    if left < 2.0:
        bar_colors.append(TEAL)
    elif left < 3.0:
        bar_colors.append(GOLD)
    else:
        bar_colors.append(RED)

ax.bar(edges[:-1], counts, width=0.23, color=bar_colors,
       edgecolor=WHITE, linewidth=0.3, align="edge")

# Vertical reference lines
# Note: "Medicare (approx 1.6×)" line removed — derivation unclear and
# label overlaps "International peer avg" at adjacent x position.
ylim_top = ax.get_ylim()[1]
refs = {
    "International\npeer avg (1.3×)": (1.3, 0.92),
    "HCCI study\nmedian (3.5×)":      (3.5, 0.92),
}
for label, (x, y_frac) in refs.items():
    ax.axvline(x, color=NAVY, lw=1.4, linestyle="--", alpha=0.7)
    ax.text(x + 0.07, ylim_top * y_frac, label,
            va="top", ha="left", fontsize=7.5, color=NAVY,
            fontfamily="DejaVu Sans", linespacing=1.4)

# Labels
ax.set_xlabel("Hospital markup (gross charges ÷ operating costs)",
              fontsize=10, color=NAVY, fontfamily="DejaVu Sans")
ax.set_ylabel("Number of hospitals", fontsize=10, color=NAVY,
              fontfamily="DejaVu Sans")
ax.set_title(f"How Much Do US Hospitals Charge vs. What They Spend?\n"
             f"Cost-to-Charge Ratios Across {n_hospitals:,} US Hospitals, 2023",
             fontsize=11, fontweight="bold", color=NAVY,
             fontfamily="DejaVu Sans", pad=10, linespacing=1.4)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)
ax.spines["bottom"].set_color(LGREY)
ax.tick_params(left=False, labelsize=9)
ax.yaxis.grid(True, color=LGREY, linewidth=0.6)
ax.set_axisbelow(True)

# Legend patches
patches = [
    mpatches.Patch(color=TEAL, label="Below 2× (low markup)"),
    mpatches.Patch(color=GOLD, label="2–3× markup"),
    mpatches.Patch(color=RED,  label="Above 3× markup"),
]
ax.legend(handles=patches, fontsize=8.5, frameon=False, loc="upper right")

# Annotation: pct above 3x
pct_above_3x = (df_plot.markup > 3.0).mean()
pct_above_2x = (df_plot.markup > 2.0).mean()
ax.text(0.98, 0.72,
        f"{pct_above_3x:.0%} of hospitals\ncharge 3× or more\nthan their costs",
        transform=ax.transAxes, ha="right", va="top",
        fontsize=9, color=RED, fontweight="bold",
        fontfamily="DejaVu Sans", linespacing=1.4,
        bbox=dict(boxstyle="round,pad=0.3", facecolor=WHITE, edgecolor=RED, alpha=0.8))

fig.text(0.5, -0.04,
         "Source: CMS HCRIS HOSP10 FY2023 cost reports. Markup = gross patient charges ÷ operating costs "
         "(Worksheet C ratio). Specialty/psychiatric hospitals excluded. "
         "HCCI peer-reviewed benchmark: median markup 3.5×.",
         ha="center", fontsize=6.5, color=GREY, fontfamily="DejaVu Sans", style="italic")

save(fig, "chart3_markup_distribution.png", extra_bottom=0.10)

# ══════════════════════════════════════════════════════════════════
# CHART 4 — Reference Pricing Savings Scenario
# What commercial hospital spending looks like at 200% vs 254% of Medicare
# ══════════════════════════════════════════════════════════════════
print("\n=== Chart 4: Reference Pricing Savings Scenario ===")

with open(os.path.join(RESDIR, "savings_calculation.json")) as f:
    sav = json.load(f)

fig, ax = plt.subplots(figsize=(7.5, 5.0), facecolor=WHITE)
ax.set_facecolor(WHITE)

commercial_B     = sav["commercial_hospital_spend_B"]
target_spend_B   = commercial_B * (sav["policy_target_ratio"] / sav["rand_commercial_to_medicare"])
# What spending would be if fully at 175% of Medicare (more aggressive target)
aggressive_B     = commercial_B * (1.75 / sav["rand_commercial_to_medicare"])

labels = [
    "Current\n(254% of Medicare)",
    "Policy target\n(200% of Medicare)",
    "Aggressive\n(175% of Medicare)",
]
vals   = [commercial_B, target_spend_B, aggressive_B]
colors = [RED, TEAL, TEAL]
alphas = [1.0, 1.0, 0.55]

bars = ax.bar(range(3), vals, color=colors, alpha=1.0, edgecolor=WHITE,
              linewidth=0.5, width=0.55)
for bar, alpha in zip(bars, alphas):
    bar.set_alpha(alpha)

# Savings annotations
for i in range(1, 3):
    savings = commercial_B - vals[i]
    ax.annotate("",
                xy=(i, vals[i]),
                xytext=(i, commercial_B),
                arrowprops=dict(arrowstyle="-[", color=GOLD, lw=2.0,
                                connectionstyle="arc3,rad=0.0"))
    ax.text(i, (vals[i] + commercial_B) / 2,
            f"  −${savings:.0f}B",
            va="center", ha="left", fontsize=11, color=GOLD,
            fontweight="bold", fontfamily="DejaVu Sans")

# Value labels on bars
for bar, val, label in zip(bars, vals, labels):
    ax.text(bar.get_x() + bar.get_width()/2, val + 5,
            f"${val:.0f}B",
            ha="center", va="bottom", fontsize=11, color=NAVY,
            fontweight="bold", fontfamily="DejaVu Sans")

ax.set_ylim(0, commercial_B * 1.25)
ax.set_xticks(range(3))
ax.set_xticklabels(labels, fontsize=9, color=NAVY, fontfamily="DejaVu Sans")
ax.set_ylabel("US commercial hospital spending ($B)", fontsize=10,
              color=NAVY, fontfamily="DejaVu Sans")
ax.set_title("What Commercial Reference Pricing Would Save\n"
             "(Capping commercial hospital rates at a multiple of Medicare)",
             fontsize=11, fontweight="bold", color=NAVY,
             fontfamily="DejaVu Sans", pad=10, linespacing=1.4)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)
ax.spines["bottom"].set_color(LGREY)
ax.tick_params(left=False, bottom=False, labelsize=9)
ax.yaxis.grid(True, color=LGREY, linewidth=0.6)
ax.set_axisbelow(True)

# Booked savings callout
booked = sav["booked_savings_B"]
ax.text(0.98, 0.95,
        f"Booked savings: ${booked:.0f}B/year",
        transform=ax.transAxes, ha="right", va="top",
        fontsize=9.5, color=TEAL, fontweight="bold",
        fontfamily="DejaVu Sans", linespacing=1.4,
        bbox=dict(boxstyle="round,pad=0.4", facecolor=WHITE,
                  edgecolor=TEAL, alpha=0.9))

fig.text(0.5, -0.04,
         f"Sources: CMS NHE 2023 (total US hospital spending $1.36T; private insurance share "
         f"{sav['private_insurance_share']:.0%}). RAND Round 5.1 (2023): commercial payers pay "
         f"{sav['rand_commercial_to_medicare']:.0%}% of Medicare for equivalent hospital services. "
         f"Policy target: cap at 200% of Medicare "
         f"(used in Montana Medicaid and thousands of self-insured employer contracts). Conservative "
         f"estimate: {sav['addressability_fraction']:.0%} of commercial spending addressable at full RAND premium.",
         ha="center", fontsize=6.5, color=GREY, fontfamily="DejaVu Sans",
         style="italic", wrap=True)

save(fig, "chart4_savings_scenario.png", extra_bottom=0.12)

# ══════════════════════════════════════════════════════════════════
# CHART 5 — Updated Savings Tracker (redesigned: vertical stack)
# Running total: $0.6B + $25.0B + $73.0B = $98.6B
# Top panel: $100B zoom (main view). Bottom panel: $3T context.
# ══════════════════════════════════════════════════════════════════
print("\n=== Chart 5: Updated Savings Tracker ===")

issues = [
    {"num": "#1", "label": "OTC Drug Overspending",     "savings": 0.6,                    "color": TEAL},
    {"num": "#2", "label": "Drug Reference Pricing",    "savings": 25.0,                   "color": TEAL},
    {"num": "#3", "label": "Hospital Pricing Reform",   "savings": sav["booked_savings_B"], "color": RED},
]
total_B = sum(i["savings"] for i in issues)
gap_B   = 3000.0

# Two rows stacked: zoom (top, taller) + full-scale context (bottom, shorter)
fig, (ax_zoom, ax_full) = plt.subplots(
    2, 1, figsize=(10, 6.5), facecolor=WHITE,
    gridspec_kw={"height_ratios": [3, 1.4], "hspace": 0.65}
)
fig.patch.set_facecolor(WHITE)

# ── TOP: Zoom panel ($100B) ────────────────────────────────────
xlim_z = 100.0
ax_zoom.set_facecolor(WHITE)
ax_zoom.set_xlim(0, xlim_z)
ax_zoom.set_ylim(0, 1)

# Background fill
ax_zoom.barh(0.5, xlim_z, height=0.72, color=LGREY, alpha=0.25, zorder=1)

# Stacked bars
left = 0.0
for iss in issues:
    ax_zoom.barh(0.5, iss["savings"], left=left, height=0.72,
                 color=iss["color"], edgecolor=WHITE, linewidth=0.6, zorder=2)
    mid = left + iss["savings"] / 2
    if iss["savings"] / xlim_z > 0.055:   # label inside if bar is wide enough
        ax_zoom.text(mid, 0.5,
                     f"Issue {iss['num']}\n${iss['savings']:.1f}B",
                     ha="center", va="center", fontsize=9, color=WHITE,
                     fontweight="bold", fontfamily="DejaVu Sans", linespacing=1.35)
    left += iss["savings"]

# Dashed total marker + label
ax_zoom.axvline(total_B, color=GOLD, linewidth=1.8, linestyle="--", zorder=3)
ax_zoom.text(total_B + xlim_z * 0.015, 0.86,
             f"${total_B:.1f}B total  ({total_B/gap_B:.1%} of $3T gap)",
             ha="left", va="center", fontsize=9.5, color=NAVY,
             fontweight="bold", fontfamily="DejaVu Sans")

# Axis
ax_zoom.set_yticks([])
ax_zoom.set_xlabel("Identified savings ($ billion)", fontsize=9.5,
                   color=NAVY, fontfamily="DejaVu Sans")
ax_zoom.xaxis.set_major_formatter(
    mticker.FuncFormatter(lambda x, p: f"${int(x)}B"))
for spine in ["top", "right", "left"]:
    ax_zoom.spines[spine].set_visible(False)
ax_zoom.spines["bottom"].set_color(LGREY)
ax_zoom.tick_params(labelsize=9, bottom=True, left=False)
ax_zoom.set_title("Per-Issue Contributions — Zoom: First $100B",
                  fontsize=11, fontweight="bold", color=RED,
                  fontfamily="DejaVu Sans", pad=8, loc="left")

# ── Legend (axes-level, below zoom bar) ───────────────────────
legend_patches = [
    mpatches.Patch(color=TEAL, label="Issue #1: OTC Drug Overspending ($0.6B)"),
    mpatches.Patch(color=TEAL, label="Issue #2: Drug Reference Pricing ($25.0B)"),
    mpatches.Patch(color=RED,  label=f"Issue #3: Hospital Pricing Reform (${sav['booked_savings_B']:.0f}B)"),
]
ax_zoom.legend(handles=legend_patches, loc="lower center",
               bbox_to_anchor=(0.5, -0.42), ncol=1,
               fontsize=8.5, frameon=False,
               prop={"family": "DejaVu Sans"})

# ── BOTTOM: Full $3T context panel ────────────────────────────
ax_full.set_facecolor(WHITE)
ax_full.set_xlim(0, gap_B)
ax_full.set_ylim(0, 1)

# Full-scale background
ax_full.barh(0.5, gap_B, height=0.55, color=LGREY, alpha=0.25, zorder=1)

# Stacked bars (tiny but real)
left = 0.0
for iss in issues:
    ax_full.barh(0.5, iss["savings"], left=left, height=0.55,
                 color=iss["color"], edgecolor="none", zorder=2)
    left += iss["savings"]

# Annotate total
ax_full.axvline(total_B, color=GOLD, linewidth=1.5, linestyle="--", zorder=3)
ax_full.text(total_B + gap_B * 0.005, 0.82,
             f"${total_B:.1f}B\n({total_B/gap_B:.1%})",
             ha="left", va="center", fontsize=8, color=NAVY,
             fontweight="bold", fontfamily="DejaVu Sans", linespacing=1.25)
ax_full.text(gap_B * 0.99, 0.5, "$3T target",
             ha="right", va="center", fontsize=8, color=GREY,
             fontfamily="DejaVu Sans", style="italic")

# Axis
ax_full.set_yticks([])
ax_full.set_xlabel("Full scale — identified vs. $3 trillion total gap",
                   fontsize=9, color=NAVY, fontfamily="DejaVu Sans")
def _fmt_large(x, p):
    if x == 0: return "$0"
    if x >= 1000:
        v = x / 1000
        return f"${v:.1f}T".replace(".0T", "T")
    return f"${int(x)}B"
ax_full.xaxis.set_major_formatter(mticker.FuncFormatter(_fmt_large))
ax_full.set_xticks([0, 500, 1000, 1500, 2000, 2500, 3000])
for spine in ["top", "right", "left"]:
    ax_full.spines[spine].set_visible(False)
ax_full.spines["bottom"].set_color(LGREY)
ax_full.tick_params(labelsize=8.5, bottom=True, left=False)
ax_full.set_title("Full Scale: vs. $3 Trillion Gap",
                  fontsize=10, fontweight="bold", color=NAVY,
                  fontfamily="DejaVu Sans", pad=6, loc="left")

# ── Figure title + footnote ────────────────────────────────────
fig.suptitle("The American Healthcare Conundrum — Running Savings Tracker\n"
             r"Total identified: \$98.6B of the \$3T annual US-Japan spending gap",
             fontsize=12, fontweight="bold", color=NAVY,
             fontfamily="DejaVu Sans", y=1.01, linespacing=1.4)

fig.text(0.5, -0.04,
         "Tracker books exact calculated savings. Issues #1–2: drug pricing (CMS Part D). "
         "Issue #3: commercial hospital reference pricing (CMS NHE + RAND Round 5.1). "
         "$3T gap = US minus Japan per-capita spending × 335M population (CMS/OECD).",
         ha="center", fontsize=7, color=GREY, fontfamily="DejaVu Sans", style="italic",
         wrap=True)

save(fig, "chart5_savings_tracker.png", extra_bottom=0.08)

print("\n✓ All 5 charts generated.")
print(f"  Figures in: {FIGDIR}")
