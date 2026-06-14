"""
Issue #16 — The Other 100 Drugs (Part D)
Single entry-point chart generator.

Wipes figures/*.png first, then regenerates all 5 charts + hero image.

Usage:
    cd issue_16/
    python3 generate_all_charts.py

Rules enforced:
- figsize <= (10, 6) at dpi=100; save at dpi=150
- plt.close(fig) after every savefig
- Relative paths via Path(__file__).resolve().parent
- No hardcoded /sessions/... paths
- Dollar signs escaped as r'\\$' to prevent matplotlib math-mode stripping
"""

from __future__ import annotations

import json
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import numpy as np

# ── Paths ───────────────────────────────────────────────────────────────────
HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
FIGURES = HERE / "figures"
FIGURES.mkdir(exist_ok=True)

# ── Wipe existing PNGs (overwrite-safe: try unlink, fall back to truncate) ──
for f in FIGURES.glob("*.png"):
    try:
        f.unlink()
    except PermissionError:
        # On some mounted filesystems unlink is blocked; overwrite at save time
        pass

# ── Brand colours ────────────────────────────────────────────────────────────
NAVY   = "#1A1F2E"
TEAL   = "#0E8A72"
RED    = "#B7182A"
GOLD   = "#D4AF37"
WHITE  = "#F8F8F6"
LGRAY  = "#8899AA"
ORANGE = "#E07030"
BG2    = "#2A3048"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "figure.facecolor": NAVY,
    "axes.facecolor": NAVY,
    "savefig.facecolor": NAVY,
    "text.color": WHITE,
    "axes.labelcolor": WHITE,
    "xtick.color": WHITE,
    "ytick.color": WHITE,
    "axes.edgecolor": LGRAY,
    "grid.color": BG2,
    "grid.linewidth": 0.6,
    "text.usetex": False,
})

# ══════════════════════════════════════════════════════════════════════════════
# Load data
# ══════════════════════════════════════════════════════════════════════════════
with open(RESULTS / "savings_estimate.json") as fh:
    est = json.load(fh)

drugs = []
with open(RESULTS / "per_drug_savings.csv") as fh:
    reader = csv.DictReader(fh)
    for row in reader:
        drugs.append(row)

for d in drugs:
    for col in ["rank", "gross", "nhs_gap_ratio", "net_spend_bil",
                "net_savings_bil", "booked_savings_bil", "medicare_per_unit"]:
        try:
            d[col] = float(d[col]) if d[col] else None
        except (ValueError, KeyError):
            d[col] = None
    d["nhs_match"] = d.get("nhs_match", "False") == "True"


# ══════════════════════════════════════════════════════════════════════════════
# CHART 1 — 11 directly-priced drugs vs. RAND blanket reference
#
# REDESIGN: only the 11 NHS-matched drugs are plotted as horizontal bars.
# The 89 RAND-assigned drugs are NOT drawn as individual dots -- they were
# never measured and showing 89 dots implied measurement that never happened.
# The RAND 3.22x net reference is shown as a single vertical dashed line,
# labeled to make clear it is the blanket assumption for the other 89.
# Brilinta (107.4x) is capped at 60x with an annotation noting the true value.
# ══════════════════════════════════════════════════════════════════════════════

def chart1():
    # Pull the 11 NHS-matched drugs and sort descending by ratio
    nhs_drugs = sorted(
        [d for d in drugs if d["nhs_match"] and d["nhs_gap_ratio"] is not None],
        key=lambda d: d["nhs_gap_ratio"],
        reverse=True,
    )

    DISPLAY_CAP = 60.0
    RAND_REF    = 3.22   # net-to-net ratio -- matches the issue's method

    names  = [d["Brnd_Name"] for d in nhs_drugs]
    ratios = [min(d["nhs_gap_ratio"], DISPLAY_CAP) for d in nhs_drugs]
    actual = [d["nhs_gap_ratio"] for d in nhs_drugs]

    # Horizontal bar chart: drug name on y-axis, gap multiple on x-axis
    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)
    fig.subplots_adjust(top=0.88, bottom=0.17, left=0.16, right=0.96)

    y_pos  = np.arange(len(names))
    # Color bars that exceed the RAND reference in gold; bars below in teal
    bar_colors = [GOLD if r > RAND_REF else TEAL for r in ratios]

    bars = ax.barh(y_pos, ratios, color=bar_colors, height=0.60, alpha=0.90,
                   zorder=3, edgecolor=NAVY, linewidth=0.4)

    # Value labels: for the capped bar (Brilinta) place the label INSIDE the bar
    # so it is guaranteed to be visible regardless of right-margin space.
    # For all other bars, place outside to the right.
    for i, (bar, r, a) in enumerate(zip(bars, ratios, actual)):
        if a > DISPLAY_CAP:
            # Capped bar: label inside, left-anchored near the left side of the bar
            lbl = "107.4x (capped at {:.0f})".format(DISPLAY_CAP)
            ax.text(r * 0.05, i, lbl,
                    va="center", ha="left", fontsize=8.5, color=NAVY, fontweight="bold",
                    zorder=9)
        else:
            lbl = "{:.1f}x".format(a)
            ax.text(r + 0.6, i, lbl,
                    va="center", ha="left", fontsize=8.5, color=WHITE, fontweight="bold")

    # RAND 3.22x vertical reference line
    ax.axvline(RAND_REF, color=ORANGE, linewidth=2.0, linestyle="--", zorder=4,
               label="RAND net brand reference: 3.22x")

    # Annotation for the reference line -- placed in the upper-right open space
    # at x=32, y=7.5 (between Invokana y=7 and Trintellix y=6; bars end at ~12x
    # so x=32 is clear). Arrow curves up to the reference line at y=8 (Prezcobix row).
    ax.annotate(
        "RAND 3.22x net reference\n(blanket assumption for\nthe other 89 products\nwith no individual\ninternational price)",
        xy=(RAND_REF, 8.0),
        xytext=(30.0, 7.0),
        fontsize=7.0,
        color=ORANGE,
        ha="left",
        va="center",
        bbox=dict(boxstyle="round,pad=0.30", facecolor=NAVY, alpha=0.95,
                  edgecolor=ORANGE, linewidth=0.8),
        arrowprops=dict(arrowstyle="->", color=ORANGE, lw=0.9,
                       connectionstyle="arc3,rad=-0.25"),
        zorder=8,
    )

    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=9.5, color=WHITE)
    ax.set_xlim(0, DISPLAY_CAP * 1.65)   # extra room for Brilinta "107.4x (capped)" label
    ax.set_ylim(-0.6, len(names) - 0.4)
    ax.set_xlabel("US Medicare Price as a Multiple of NHS Reference Price", fontsize=10, labelpad=6)
    ax.set_title(
        "The 11 Directly-Priced Drugs Run Far Above the RAND 3.22x Reference (CY2023)",
        fontsize=11, color=WHITE, pad=10)
    ax.grid(True, axis="x", alpha=0.30, zorder=0)
    ax.set_axisbelow(True)

    legend_patches = [
        mpatches.Patch(color=GOLD, label="Above RAND 3.22x reference"),
        mpatches.Patch(color=TEAL, label="At or below RAND reference"),
        Line2D([0], [0], color=ORANGE, linewidth=2, linestyle="--",
               label="RAND 3.22x net (blanket for 89 un-priced drugs)"),
    ]
    ax.legend(handles=legend_patches, fontsize=8, loc="lower right",
              framealpha=0.90, facecolor=NAVY, edgecolor=LGRAY, labelcolor=WHITE)

    footnote = (
        "Only the 11 drugs with a direct NHS Drug Tariff Part VIIIA price are plotted. "
        "The remaining 89 products in the analysis have no individual international price;\n"
        "they use the RAND RR-A788-3 net brand ratio of 3.22x (shown as dashed line). "
        "Brilinta actual ratio 107.4x, capped at 60x for legibility.\n"
        "Sources: CMS Part D PUF CY2023; NHS Drug Tariff Apr 2026; RAND RR-A788-3 (Mulcahy et al. 2024)."
    )
    fig.text(0.04, 0.01, footnote, fontsize=5.5, color=LGRAY, ha="left", va="bottom")

    out = FIGURES / "chart1_price_gap_distribution.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Saved: {out}")
    return out


# ══════════════════════════════════════════════════════════════════════════════
# CHART 2 — Top 10 drugs by booked savings
# ══════════════════════════════════════════════════════════════════════════════

def chart2():
    sorted_drugs = sorted(drugs, key=lambda d: d["booked_savings_bil"] or 0, reverse=True)
    top10 = sorted_drugs[:10]

    names        = [d["Brnd_Name"]   for d in top10]
    values       = [d["booked_savings_bil"] for d in top10]
    manufacturers = [d["manufacturer"] for d in top10]
    drug_classes  = [d["drug_class"]  for d in top10]

    tier_label = {
        "top_brand": "Top brand (49% rebate)",
        "mid_brand": "Mid brand (27.5% rebate)",
        "biologic":  "Biologic (20% rebate)",
        "insulin":   "Insulin (70% rebate)",
    }
    tier_colors = {
        "top_brand": GOLD,
        "mid_brand": TEAL,
        "biologic":  ORANGE,
        "insulin":   "#9966CC",
    }

    # Reverse for horizontal bar (lowest at bottom → #1 at top)
    names_r   = names[::-1]
    values_r  = values[::-1]
    mfr_r     = manufacturers[::-1]
    classes_r = drug_classes[::-1]
    colors_r  = [tier_colors[c] for c in classes_r]

    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)

    y_pos = np.arange(len(names_r))
    bars = ax.barh(y_pos, values_r, color=colors_r, height=0.62, alpha=0.9, zorder=3)

    max_val = max(values_r)
    for i, (bar, val, mfr) in enumerate(zip(bars, values_r, mfr_r)):
        short_mfr = (mfr.replace(" US LLC", "").replace(" US Pharm", "")
                        .replace(" Inc.", "").replace(" Corporat", "")
                        .replace(" Sciences", ""))[:14]
        # Use format() to avoid f-string/r-string conflict with dollar sign
        lbl_str = "{:.2f}B  {}".format(val, short_mfr)
        ax.text(val + 0.015, i, lbl_str,
                va="center", ha="left", fontsize=8.5, color=WHITE, fontweight="bold")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(names_r, fontsize=9.5, color=WHITE)
    ax.set_xlim(0, max_val * 1.72)
    ax.set_xlabel("Booked Savings (USD Billions/year)", fontsize=10, labelpad=6)
    ax.set_title("Top 10 Brand Products by Booked Savings (CY2023 Part D Data)",
                 fontsize=11, color=WHITE, pad=10)
    ax.grid(True, axis="x", alpha=0.35, zorder=0)
    ax.set_axisbelow(True)

    total_top10 = sum(values)
    ax.text(max_val * 1.65, len(names_r) - 1,
            "Top 10 total\n{:.2f}B".format(total_top10),
            fontsize=9, color=GOLD, ha="right", va="top",
            bbox=dict(boxstyle="round,pad=0.3", facecolor=NAVY, edgecolor=GOLD,
                      linewidth=0.8))

    legend_patches = [
        mpatches.Patch(color=tier_colors[t], label=tier_label[t])
        for t in ["top_brand", "mid_brand", "biologic", "insulin"]
        if t in drug_classes
    ]
    ax.legend(handles=legend_patches, fontsize=8, loc="lower right",
              framealpha=0.88, facecolor=NAVY, edgecolor=LGRAY, labelcolor=WHITE)

    fig.text(0.12, 0.01,
             "Booked savings = net spend x 68.9% RAND net gap x 0.55 recoverability. "
             "Rebate applied once to gross CMS PUF spend. Source: CMS Part D PUF CY2023.",
             fontsize=5.5, color=LGRAY, ha="left", va="bottom")
    fig.tight_layout(rect=[0, 0.06, 1, 1])

    out = FIGURES / "chart2_top10_booked_savings.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Saved: {out}")
    return out


# ══════════════════════════════════════════════════════════════════════════════
# CHART 3 — Savings waterfall
# ══════════════════════════════════════════════════════════════════════════════

def chart3():
    gross_bil       = est["universe_gross_bil"]
    net_spend_bil   = est["universe_net_spend_bil"]
    net_savings_bil = est["net_total_before_recoverability_bil"]
    booked_bil      = est["booked_bil"]
    range_lo        = est["range_lo_bil"]
    range_hi        = est["range_hi_bil"]

    steps = [
        ("Universe\nGross Spend", gross_bil),
        ("After\nRebates\n(Net Spend)", net_spend_bil),
        ("Net\nSavings\n(68.9% gap)", net_savings_bil),
        ("Booked\n(x0.55 recov.)", booked_bil),
    ]
    labels = [s[0] for s in steps]
    values = [s[1] for s in steps]
    bar_colors = [TEAL, TEAL, TEAL, GOLD]

    fig, ax = plt.subplots(figsize=(9, 6), dpi=100)
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)

    x = np.arange(len(steps))
    for i, (lbl, val) in enumerate(steps):
        ax.bar(i, val, width=0.55, color=bar_colors[i], alpha=0.88, zorder=3,
               edgecolor=WHITE, linewidth=0.5)
        ax.text(i, val + 0.8, f"{val:.1f}B",
                ha="center", va="bottom", fontsize=11, color=WHITE, fontweight="bold")

    for i in range(len(steps) - 1):
        x_mid = i + 0.55 / 2 + 0.05
        y_top = values[i]
        y_bot = values[i + 1]
        ax.annotate("", xy=(i + 1 - 0.55 / 2, y_bot + 0.3), xytext=(x_mid, y_top - 0.3),
                    arrowprops=dict(arrowstyle="->", color=LGRAY, lw=1.2,
                                   connectionstyle="arc3,rad=0.0"), zorder=6)
        reduction = values[i] - values[i + 1]
        ax.text(i + 0.5, (values[i] + values[i + 1]) / 2, f"-{reduction:.1f}B",
                ha="center", va="center", fontsize=8, color=LGRAY, style="italic",
                bbox=dict(boxstyle="round,pad=0.15", facecolor=NAVY, alpha=0.85,
                          edgecolor="none"))

    ax.errorbar(3, booked_bil,
                yerr=[[booked_bil - range_lo], [range_hi - booked_bil]],
                fmt="none", color=WHITE, capsize=8, capthick=2, elinewidth=2.0, zorder=7)
    ax.text(3 + 0.55 / 2 + 0.06, booked_bil,
            f"Range:\n{range_lo:.1f}B - {range_hi:.1f}B",
            ha="left", va="center", fontsize=8.5, color=WHITE,
            bbox=dict(boxstyle="round,pad=0.28", facecolor=NAVY, edgecolor=GOLD,
                      linewidth=0.8, alpha=0.92))

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10, color=WHITE)
    ax.set_ylim(0, gross_bil * 1.18)
    ax.set_ylabel("USD Billions", fontsize=10, labelpad=6)
    ax.set_title("From Universe Spend to Booked Savings: 16.4B/Year (CY2023)",
                 fontsize=11, color=WHITE, pad=10)
    ax.grid(True, axis="y", alpha=0.30, zorder=0)
    ax.set_axisbelow(True)

    footnote = (
        "Gross spend: CMS Part D PUF CY2023. Net spend: gross minus tiered rebate\n"
        "(top brand 49%, mid brand 27.5%, biologic 20%, insulin 70%). "
        "Net savings: net spend x 68.9% RAND net gap (3.22x ratio).\n"
        "Booked: net savings x 0.55 recoverability. "
        "Range: recov. 0.45 (low) to NHS-floor upper 0.85 (high)."
    )
    fig.text(0.09, 0.01, footnote, fontsize=5.5, color=LGRAY, ha="left", va="bottom")
    fig.subplots_adjust(top=0.90, bottom=0.18, left=0.10, right=0.82)

    out = FIGURES / "chart3_savings_waterfall.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Saved: {out}")
    return out


# ══════════════════════════════════════════════════════════════════════════════
# CHART 4 — IRA rounds vs residual
# ══════════════════════════════════════════════════════════════════════════════

def chart4():
    ira_data = [
        ("IRA Round 1\n(10 drugs)\neff. Jan 2026", 6.0,  TEAL,  "~6B/yr\n(CMS est.)"),
        ("IRA Round 2\n(15 drugs)\neff. Jan 2027", 12.0, TEAL,  "~12B/yr\n(CMS est.)"),
        ("IRA Round 3\n(15 drugs)\neff. Jan 2028", 8.0,  LGRAY, "~8B/yr\n(est. pending)"),
        ("Residual\n100 drugs\n(this analysis)", 16.36, GOLD,  "16.4B/yr\n(booked)"),
    ]

    labels  = [d[0] for d in ira_data]
    values  = [d[1] for d in ira_data]
    colors  = [d[2] for d in ira_data]
    callouts = [d[3] for d in ira_data]

    fig, ax = plt.subplots(figsize=(9, 6), dpi=100)
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)

    x = np.arange(len(labels))
    ax.bar(x, values, width=0.58, color=colors, alpha=0.90, zorder=3,
           edgecolor=WHITE, linewidth=0.5)

    for i, (val, callout) in enumerate(zip(values, callouts)):
        ax.text(i, val + 0.25, callout,
                ha="center", va="bottom", fontsize=9, color=WHITE, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.2", facecolor=NAVY, alpha=0.82,
                          edgecolor="none"))

    total_ira = sum(values[:3])
    ax.annotate(
        f"IRA total\n~{total_ira:.0f}B/yr",
        xy=(2, values[2] + 1.8),
        xytext=(0.5, max(values) * 0.85),
        fontsize=9, color=WHITE, ha="center", va="bottom",
        bbox=dict(boxstyle="round,pad=0.3", facecolor=NAVY, edgecolor=TEAL,
                  linewidth=0.8, alpha=0.92),
        arrowprops=dict(arrowstyle="-|>", color=TEAL, lw=1.0,
                       connectionstyle="arc3,rad=-0.25"),
        zorder=8,
    )

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9.5, color=WHITE)
    ax.set_ylim(0, max(values) * 1.60)
    ax.set_ylabel("Estimated Annual Medicare Savings (USD Billions)", fontsize=10, labelpad=6)
    ax.set_title("The IRA Captures 25 Drugs. The Next 100 Carry 16.4B/Year.",
                 fontsize=11, color=WHITE, pad=10)
    ax.grid(True, axis="y", alpha=0.30, zorder=0)
    ax.set_axisbelow(True)

    legend_patches = [
        mpatches.Patch(color=TEAL,  label="IRA negotiated (Rounds 1 & 2, confirmed)"),
        mpatches.Patch(color=LGRAY, label="IRA Round 3 (negotiation in progress)"),
        mpatches.Patch(color=GOLD,  label="Residual pool -- this analysis"),
    ]
    ax.legend(handles=legend_patches, fontsize=8, loc="upper left",
              framealpha=0.88, facecolor=NAVY, edgecolor=LGRAY, labelcolor=WHITE)

    fig.text(0.12, 0.01,
             "IRA Round 1/2 savings: CMS IPAY 2026 and IPAY 2027 MFP fact sheets. "
             "Round 3 savings: analyst estimate (negotiation completes 2027). "
             "Residual: this analysis (CMS Part D PUF CY2023, RAND RR-A788-3).",
             fontsize=5.5, color=LGRAY, ha="left", va="bottom")
    fig.tight_layout(rect=[0, 0.07, 1, 1])

    out = FIGURES / "chart4_ira_vs_residual.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Saved: {out}")
    return out


# ══════════════════════════════════════════════════════════════════════════════
# CHART 5 — Savings tracker (all 16 issues)
# ══════════════════════════════════════════════════════════════════════════════

def chart5():
    issues = [
        ("#1",  "OTC Drugs",             0.6),
        ("#2",  "Drug Pricing",         25.0),
        ("#3",  "Hospital Pricing",     73.0),
        ("#4",  "PBM Reform",           30.0),
        ("#5",  "Admin Waste",         200.0),
        ("#6",  "Supply Waste",         28.0),
        ("#7",  "GLP-1 Pricing",        40.0),
        ("#8",  "Denial Machine",       32.0),
        ("#9",  "Employer Trap",         6.6),
        ("#10", "Procedure Mill",        7.6),
        ("#11", "MA Overpayment",       28.0),
        ("#12", "Consolidation Tax",    13.0),
        ("#13", "Nonprofit Lie",         5.4),
        ("#14", "Specialist Tax",       27.6),
        ("#15", "Facility Fee Scam",     2.55),
        ("#16", "The Other 100 Drugs",  16.36),
    ]

    nums    = [i[0] for i in issues]
    labels  = [i[1] for i in issues]
    savings = [i[2] for i in issues]
    running_total = 535.71
    target = 3240.0
    pct = running_total / target * 100

    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(10, 6), dpi=100,
        gridspec_kw={"width_ratios": [2, 1], "wspace": 0.52})
    fig.patch.set_facecolor(NAVY)
    fig.subplots_adjust(top=0.88, bottom=0.11, left=0.21, right=0.97)

    # ── Left: per-issue bars ─────────────────────────────────────────────────
    ax_left.set_facecolor(NAVY)
    y_pos = np.arange(len(issues))
    bar_colors = [GOLD if n == "#16" else TEAL for n in nums]
    bars = ax_left.barh(y_pos, savings, color=bar_colors, height=0.68, alpha=0.90, zorder=3)

    ax_left.set_yticks(y_pos)
    ax_left.set_yticklabels([f"{n}  {lbl}" for n, lbl in zip(nums, labels)],
                             fontsize=7.5, color=WHITE)

    max_s = max(savings)
    for i, (bar, val) in enumerate(zip(bars, savings)):
        lbl_txt = f"{val:.1f}B" if val >= 1.0 else f"{val:.2f}B"
        ax_left.text(val + max_s * 0.018, i, lbl_txt,
                     va="center", ha="left", fontsize=7.2, color=WHITE)

    ax_left.set_xlim(0, max_s * 1.38)
    ax_left.set_xlabel("Savings (USD Billions/year)", fontsize=9, labelpad=4)
    ax_left.set_title("Per-Issue Savings, Issues #1-#16", fontsize=10, color=WHITE, pad=7)
    ax_left.grid(True, axis="x", alpha=0.22, zorder=0)
    ax_left.set_axisbelow(True)

    # ── Right: running total ─────────────────────────────────────────────────
    ax_right.set_facecolor(NAVY)

    # Full-scale bar (y=1)
    ax_right.barh(1.0, target,        height=0.45, color=BG2,  alpha=1.0, zorder=2)
    ax_right.barh(1.0, running_total, height=0.45, color=TEAL, alpha=0.90, zorder=3)

    # Zoom bar (y=0): $0-$100B window
    ax_right.barh(0.0, 100.0, height=0.45, color=BG2,  alpha=1.0, zorder=2)
    ax_right.barh(0.0, 100.0, height=0.45, color=GOLD, alpha=0.90, zorder=3)

    # Y-axis labels
    ax_right.set_yticks([0.0, 1.0])
    ax_right.set_yticklabels(["Zoom:\n0-100B", "Full scale:\nvs 3.24T"],
                              fontsize=8.5, color=WHITE)
    ax_right.set_xlim(0, target * 1.05)
    ax_right.set_ylim(-0.55, 1.70)

    # Label above full-scale bar (inside y-range above bar)
    ax_right.text(running_total / 2.0, 1.22,
                  f"{running_total:.2f}B = {pct:.1f}%",
                  va="bottom", ha="center", fontsize=9, color=WHITE, fontweight="bold",
                  zorder=6,
                  bbox=dict(boxstyle="round,pad=0.22", facecolor=NAVY, alpha=0.88,
                             edgecolor=TEAL, linewidth=0.8))

    # Label inside zoom bar
    ax_right.text(50.0, -0.22,
                  "First 100B filled",
                  va="top", ha="center", fontsize=7.5, color=NAVY, fontweight="bold",
                  zorder=6)

    ax_right.set_xlabel("USD Billions", fontsize=9, labelpad=4)
    ax_right.set_title("Running Total\n535.71B / 3.24T (16.5%)",
                       fontsize=10, color=WHITE, pad=7)
    ax_right.grid(True, axis="x", alpha=0.22, zorder=0)
    ax_right.set_axisbelow(True)

    fig.suptitle("AHC Savings Tracker -- After Issue #16",
                 fontsize=12, color=WHITE, y=0.975, fontweight="bold")

    fig.text(0.04, 0.01,
             "Target: 3.24T US-Japan per-capita gap (CMS NHE 2024; OECD 2023). "
             "Issue #16 adds 16.36B. Cumulative: 535.71B (16.5%). "
             "All figures per-year booked savings.",
             fontsize=5.5, color=LGRAY, ha="left", va="bottom")

    out = FIGURES / "chart5_savings_tracker.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Saved: {out}")
    return out


# ══════════════════════════════════════════════════════════════════════════════
# HERO IMAGE — 1456×1048 at dpi=100
# ══════════════════════════════════════════════════════════════════════════════

def chart_hero():
    # 14.56 × 10.48 inches × 100dpi = 1456×1048px
    fig = plt.figure(figsize=(14.56, 10.48), dpi=100)
    fig.patch.set_facecolor(NAVY)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(NAVY)
    ax.set_xlim(0, 1456)
    ax.set_ylim(0, 1048)
    ax.axis("off")

    # Subtle grid
    for x in range(0, 1456, 72):
        ax.axvline(x, color="#212840", linewidth=0.4, zorder=0)
    for y in range(0, 1048, 72):
        ax.axhline(y, color="#212840", linewidth=0.4, zorder=0)

    # Safe zone: x 278-1178, y 249-799 (centered ~900x550)
    # Content block: top y=734, bottom y=314, center=(734+314)/2=524 = canvas center

    # ── Series branding ──────────────────────────────────────────────────────
    ax.text(728, 734, "THE AMERICAN HEALTHCARE CONUNDRUM",
            fontsize=17, color=RED, ha="center", va="center",
            fontweight="bold", zorder=5)
    ax.text(728, 707, "Issue #16",
            fontsize=23, color=GOLD, ha="center", va="center",
            fontweight="bold", zorder=5)

    # Red divider
    ax.plot([300, 1156], [683, 683], color=RED, linewidth=2.5, zorder=5)

    # ── Main hook ────────────────────────────────────────────────────────────
    ax.text(728, 594, r"\$16 Billion",
            fontsize=88, color=WHITE, ha="center", va="center",
            fontweight="bold", zorder=5)
    ax.text(728, 514, "per year, left on the table",
            fontsize=28, color=TEAL, ha="center", va="center", zorder=5)

    # ── Supporting lines ─────────────────────────────────────────────────────
    ax.text(728, 469,
            "After the IRA negotiated 25 drugs, 100 brand products remain.",
            fontsize=17, color=WHITE, ha="center", va="center", zorder=5)
    ax.text(728, 439,
            r"US net prices still run 3.2x international -- on \$43B in Medicare spending.",
            fontsize=17, color=WHITE, ha="center", va="center", zorder=5)

    # ── Stat bar ─────────────────────────────────────────────────────────────
    rect = mpatches.FancyBboxPatch(
        (268, 314), 920, 80,
        boxstyle="round,pad=4", linewidth=0, facecolor="#0E2040", zorder=4
    )
    ax.add_patch(rect)

    stats = [
        ("100 brand products",   "~85 molecules, not yet IRA-negotiated"),
        ("3.22x",                "US net price vs OECD peer nations"),
        (r"\$535.71B",           r"running total  16.5% of \$3.24T gap"),
    ]
    xs = [430, 728, 1025]
    for (stat, sub), x in zip(stats, xs):
        ax.text(x, 364, stat, fontsize=15, color=GOLD, ha="center", va="center",
                fontweight="bold", zorder=6)
        ax.text(x, 336, sub, fontsize=9.5, color=LGRAY, ha="center", va="center",
                zorder=6)

    for xd in [580, 876]:
        ax.plot([xd, xd], [321, 390], color=LGRAY, linewidth=0.8, zorder=5)

    # ── Bottom branding (below safe zone) ────────────────────────────────────
    ax.text(728, 80,
            "americanhealthcareconundrum.com  -  All analysis open-source",
            fontsize=12, color=LGRAY, ha="center", va="center", zorder=5)

    out = FIGURES / "hero_cover.png"
    fig.savefig(out, dpi=100)
    plt.close(fig)
    print(f"Saved: {out}")
    return out


# ══════════════════════════════════════════════════════════════════════════════
# Run all
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Generating Issue #16 charts ...")
    chart1()
    chart2()
    chart3()
    chart4()
    chart5()
    chart_hero()

    pngs = sorted(FIGURES.glob("*.png"))
    print(f"\nTotal PNGs in figures/: {len(pngs)}")
    for p in pngs:
        print(f"  {p.name}")
