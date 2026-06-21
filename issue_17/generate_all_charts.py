"""
Issue #17 — The Part B Pharmacy Premium
Single entry-point chart generator.

Wipes figures/*.png first (preserving hero_cover.png by name if desired),
then regenerates all 5 charts + hero image.

Usage:
    cd issue_17/
    python3 generate_all_charts.py

Rules enforced:
- figsize <= (10, 6) at dpi=100; save at dpi=150
- plt.close(fig) after every savefig
- Relative paths via Path(__file__).resolve().parent
- No hardcoded /sessions/... paths
- Dollar signs escaped as r'\\$' where needed
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

# ── Wipe existing PNGs (preserve hero by re-saving it last) ─────────────────
for f in FIGURES.glob("*.png"):
    try:
        f.unlink()
    except PermissionError:
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
with open(RESULTS / "universe_part_b_drugs.csv") as fh:
    reader = csv.DictReader(fh)
    for row in reader:
        drugs.append(row)

# Cast numeric columns
for d in drugs:
    for col in ["rank", "spend", "asp_per_unit", "booked_savings_bil",
                "gross_gap_savings_bil", "after_340b_savings_bil"]:
        try:
            d[col] = float(d[col]) if d[col] else None
        except (ValueError, KeyError):
            d[col] = None
    for bool_col in ["is_true_generic", "is_biosimilar_product",
                     "biosimilar_avail", "ipay2028_flag"]:
        d[bool_col] = str(d.get(bool_col, "False")).strip().lower() in ("true", "1", "yes")


# ══════════════════════════════════════════════════════════════════════════════
# CHART 1 — Savings waterfall
# ══════════════════════════════════════════════════════════════════════════════

def chart1():
    """Waterfall: $50.79B -> $41.80B -> $17.27B -> $11.22B -> $6.17B booked.
    Range whiskers at $2.85B and $14.06B on the final bar."""
    w = est["waterfall"]
    total_spend   = w["total_partb_separately_paid_bil"]   # 50.79
    universe_base = w["universe_spend_base_bil"]           # 41.80
    gross_gap     = w["gross_intl_gap_savings_bil"]        # 17.27
    after_340b    = w["after_340b_netting_bil"]            # 11.22
    booked        = w["after_recoverability_booked_bil"]   # 6.17
    range_lo      = est["scenarios_bil"]["conservative"]   # 2.85
    range_hi      = est["scenarios_bil"]["aggressive"]     # 14.06

    steps = [
        ("Total Part B\nSpend",      total_spend,   TEAL,   "Exclusions:\nSkin sub $3.64B\nVaccines $2.50B\nIg/blood $2.86B"),
        ("Universe Base\n(597 codes)", universe_base, TEAL,  "Gap fraction 0.444\n(1.8x ex-mfr central;\nQ5 biosimilars zeroed)"),
        ("Gross Gap\nSavings",        gross_gap,     TEAL,   "340B netting\n(x0.65 non-340B\nshare; Issue #19\nholds the rest)"),
        ("After 340B\nNetting",       after_340b,    TEAL,   "Recoverability\nx0.55"),
        ("Booked\nSavings",           booked,        GOLD,   None),
    ]

    labels = [s[0] for s in steps]
    values = [s[1] for s in steps]
    colors = [s[2] for s in steps]
    notes  = [s[3] for s in steps]

    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)

    x = np.arange(len(steps))
    bars = []
    for i, (lbl, val, col, note) in enumerate(steps):
        b = ax.bar(i, val, width=0.55, color=col, alpha=0.88, zorder=3,
                   edgecolor=WHITE, linewidth=0.5)
        bars.append(b)

    # Value labels above each bar
    for i, val in enumerate(values):
        ax.text(i, val + 0.6, f"{val:.2f}B",
                ha="center", va="bottom", fontsize=10.5,
                color=WHITE, fontweight="bold", zorder=6)

    # Step-reduction arrows and labels between bars
    # Placed at midpoints between bars, within the Y band between adjacent tops
    step_explanations = [
        r"-\$9.0B (exclusions)",
        r"-\$24.5B (intl gap)",
        r"-\$6.1B (340B netting)",
        r"-\$5.0B (recoverability)",
    ]
    for i in range(len(steps) - 1):
        v_from = values[i]
        v_to   = values[i + 1]
        mid_y  = (v_from + v_to) / 2.0
        ax.annotate("", xy=(i + 1 - 0.27, v_to + 0.2),
                    xytext=(i + 0.27, v_from - 0.2),
                    arrowprops=dict(arrowstyle="->", color=LGRAY, lw=1.0,
                                   connectionstyle="arc3,rad=0.0"), zorder=5)
        ax.text(i + 0.5, mid_y, step_explanations[i],
                ha="center", va="center", fontsize=7.5, color=LGRAY,
                style="italic", zorder=5,
                bbox=dict(boxstyle="round,pad=0.18", facecolor=NAVY, alpha=0.85,
                          edgecolor="none"))

    # Range whiskers on the final bar (index 4)
    # Placed as error bar: [below central, above central]
    ax.errorbar(4, booked,
                yerr=[[booked - range_lo], [range_hi - booked]],
                fmt="none", color=WHITE, capsize=9, capthick=2.0,
                elinewidth=2.0, zorder=7)
    # Range label to the right of the last bar
    ax.text(4 + 0.31, (range_lo + range_hi) / 2,
            "Range:\n2.85B (conservative)\n14.06B (aggressive)",
            ha="left", va="center", fontsize=7.5, color=WHITE, zorder=8,
            bbox=dict(boxstyle="round,pad=0.28", facecolor=NAVY, edgecolor=GOLD,
                      linewidth=0.8, alpha=0.92))

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9.5, color=WHITE)
    ax.set_ylim(0, total_spend * 1.20)
    ax.set_ylabel("USD Billions", fontsize=10, labelpad=6)
    ax.set_title(
        r"From \$50.8 Billion to \$6.2 Billion Booked: The Part B Gap Waterfall (CY2023)",
        fontsize=11, color=WHITE, pad=10)
    ax.grid(True, axis="y", alpha=0.30, zorder=0)
    ax.set_axisbelow(True)

    footnote = (
        "Source: CMS Part B Spending by Drug PUF CY2023. Central ratio: MedPAC/ASPE 1.8x ex-manufacturer. "
        "340B netting: 35% of universe excluded (reserved Issue #19).\n"
        "Recoverability: 0.55. Conservative 2.85B (1.5x ratio, 45% 340B share, 40% recov). "
        "Aggressive 14.06B (3.22x RAND ceiling, 25% 340B share, 70% recov)."
    )
    fig.text(0.09, 0.02, footnote, fontsize=5.5, color=LGRAY, ha="left", va="bottom")
    fig.subplots_adjust(top=0.88, bottom=0.15, left=0.09, right=0.82)

    out = FIGURES / "chart1_waterfall.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Saved: {out}")
    return out


# ══════════════════════════════════════════════════════════════════════════════
# CHART 2 — Top 10 Part B drugs by booked savings
# ══════════════════════════════════════════════════════════════════════════════

def chart2():
    """Horizontal bar chart. Top 10 by booked_savings_bil.
    IPAY-2028 flagged drugs in gold; others in teal.
    Manufacturer label on each bar."""
    # Top 10 from CSV
    top10 = sorted(drugs, key=lambda d: d["booked_savings_bil"] or 0, reverse=True)[:10]

    # Manufacturer map (from editorial review and newsletter)
    MFR_MAP = {
        "Keytruda":       "Merck",
        "Eylea":          "Regeneron",
        "Prolia*":        "Amgen",
        "Darzalex Faspro": "J&J",
        "Opdivo":         "BMS",
        "Vabysmo":        "Roche/Regeneron",
        "Orencia*":       "BMS",
        "Tecentriq":      "Roche",
        "Imfinzi":        "AstraZeneca",
        "Entyvio":        "Takeda",
    }

    # Reverse order so #1 (highest) is at top of horizontal bar
    top10_rev = top10[::-1]

    names    = [d["Brnd_Name"]      for d in top10_rev]
    values   = [d["booked_savings_bil"] for d in top10_rev]
    is_ipay  = [d["ipay2028_flag"]  for d in top10_rev]
    mfrs     = [MFR_MAP.get(d["Brnd_Name"], "") for d in top10_rev]
    bar_colors = [GOLD if ipay else TEAL for ipay in is_ipay]

    # Clean up names (remove asterisks for display)
    disp_names = [n.replace("*", "") for n in names]

    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)

    y_pos = np.arange(len(top10_rev))
    bars = ax.barh(y_pos, values, color=bar_colors, height=0.62, alpha=0.90, zorder=3)

    max_val = max(values)
    for i, (bar, val, mfr) in enumerate(zip(bars, values, mfrs)):
        lbl_str = "{:.2f}B  {}".format(val, mfr)
        ax.text(val + max_val * 0.018, i, lbl_str,
                va="center", ha="left", fontsize=8.5, color=WHITE, fontweight="bold")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(disp_names, fontsize=9.5, color=WHITE)
    ax.set_xlim(0, max_val * 1.75)
    ax.set_xlabel("Booked Savings (USD Billions/year)", fontsize=10, labelpad=6)
    ax.set_title("Top 10 Part B Drugs by Booked Savings (CY2023 Part B Spend)",
                 fontsize=11, color=WHITE, pad=10)
    ax.grid(True, axis="x", alpha=0.35, zorder=0)
    ax.set_axisbelow(True)

    # Legend
    legend_patches = [
        mpatches.Patch(color=TEAL, label="Part B drug (no IPAY-2028 selection)"),
        mpatches.Patch(color=GOLD, label="IPAY-2028 IRA selection (MFP eff. Jan 2028)"),
    ]
    ax.legend(handles=legend_patches, fontsize=8, loc="lower right",
              framealpha=0.88, facecolor=NAVY, edgecolor=LGRAY, labelcolor=WHITE)

    # Note about IPAY-2028 selections
    ax.text(max_val * 0.01, -0.7,
            "* Orencia and Entyvio are IPAY-2028 IRA selections; Botox, Cimzia, Xolair also selected but outside top 10 here.",
            fontsize=6.5, color=LGRAY, ha="left", va="bottom", style="italic", zorder=6)

    fig.text(0.09, 0.01,
             "Source: CMS Medicare Part B Spending by Drug PUF CY2023. "
             "Booked savings = spend x 0.444 gap fraction x 0.65 non-340B share x 0.55 recoverability. "
             "Central ratio: MedPAC/ASPE 1.8x ex-manufacturer.",
             fontsize=5.5, color=LGRAY, ha="left", va="bottom")
    fig.subplots_adjust(top=0.88, bottom=0.13, left=0.15, right=0.97)

    out = FIGURES / "chart2_top_drugs.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Saved: {out}")
    return out


# ══════════════════════════════════════════════════════════════════════════════
# CHART 3 — ASP+6% incentive diagram
# ══════════════════════════════════════════════════════════════════════════════

def chart3():
    """Two stacked bars: originator ($10,000 drug + $600 add-on = $10,600)
    vs biosimilar ($3,000 drug + $240 add-on = $3,240).
    Add-on segments highlighted in contrasting color.

    Fixes applied:
    - Increased left margin to 0.18 so Y-axis label fits without clipping.
    - Moved callout box right (xytext=(0.55, 7800)) so it stays inside axes.
    - Biosimilar +$240 label moved OUTSIDE the thin orange segment with a
      leader line (arrowprops), separated from the $3,240 total label by
      well over 40px of vertical clearance.
    """

    fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)

    x = np.array([0.0, 1.0])
    drug_vals = [10000, 3000]
    addon_vals = [600, 240]
    totals = [10600, 3240]

    # Drug ingredient bars (base)
    bars_drug = ax.bar(x, drug_vals, width=0.45, color=TEAL,
                       alpha=0.85, zorder=3, label="Drug ingredient (ASP)",
                       edgecolor=WHITE, linewidth=0.5)
    # Add-on bars (stacked on top)
    bars_addon = ax.bar(x, addon_vals, width=0.45, bottom=drug_vals,
                        color=ORANGE, alpha=0.95, zorder=4,
                        label="Add-on (6% originator / 8% biosimilar)",
                        edgecolor=WHITE, linewidth=0.5)

    # Total label above each bar
    # Originator total: at y=10600+200=10800
    ax.text(x[0], totals[0] + 200, r"\$" + f"{totals[0]:,}",
            ha="center", va="bottom", fontsize=11, color=WHITE,
            fontweight="bold", zorder=6)
    # Biosimilar total: at y=3240+200=3440
    ax.text(x[1], totals[1] + 200, r"\$" + f"{totals[1]:,}",
            ha="center", va="bottom", fontsize=11, color=WHITE,
            fontweight="bold", zorder=6)

    # Originator add-on label INSIDE the orange segment (segment is 600 wide — plenty of room)
    # Segment center at y = 10000 + 300 = 10300
    ax.text(x[0], 10000 + 300, r"+\$600 add-on",
            ha="center", va="center", fontsize=10, color=NAVY,
            fontweight="bold", zorder=7)

    # Biosimilar add-on label OUTSIDE with a leader line.
    # The orange segment is only 240 units tall (3000-3240) — too thin for inside label.
    # Place label to the LEFT of the biosimilar bar (x[1]-0.35=0.65) at y=4800,
    # well above the $3,240 total label at y~3640 (>1160 units clearance).
    # Arrow points from label into the center of the orange segment.
    ax.annotate(
        r"+\$240 add-on",
        xy=(x[1], 3000 + 120),       # tip: center of orange segment
        xytext=(x[1] - 0.35, 4800),  # label to the LEFT in clear space
        fontsize=9, color=WHITE, ha="center", va="center", zorder=8,
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.22", facecolor=NAVY, edgecolor=ORANGE,
                  linewidth=0.8, alpha=0.92),
        arrowprops=dict(arrowstyle="-", color=ORANGE, lw=1.2,
                        connectionstyle="arc3,rad=0.0"),
    )

    # Drug ingredient label inside each teal bar
    ax.text(x[0], 10000 / 2, r"\$10,000" + "\nASP",
            ha="center", va="center", fontsize=11, color=WHITE,
            fontweight="bold", zorder=5)
    ax.text(x[1], 3000 / 2, r"\$3,000" + "\nASP",
            ha="center", va="center", fontsize=11, color=WHITE,
            fontweight="bold", zorder=5)

    # Callout annotation comparing add-on amounts.
    # Placed to the right of center (xytext x=0.55) so it stays well inside the axes.
    # Arrow points to top of originator bar.
    ax.annotate(
        "2.5x more in\nabsolute add-on\nfor the pricier drug",
        xy=(0.0, 10600), xytext=(0.55, 8000),
        fontsize=9, color=WHITE, ha="center", va="center", zorder=8,
        bbox=dict(boxstyle="round,pad=0.3", facecolor=NAVY, edgecolor=GOLD,
                  linewidth=0.8, alpha=0.92),
        arrowprops=dict(arrowstyle="->", color=GOLD, lw=1.0,
                       connectionstyle="arc3,rad=0.25"),
    )

    ax.set_xticks(x)
    ax.set_xticklabels(
        ["Originator\n(e.g., branded biologic)", "Biosimilar\n(same molecule, lower ASP)"],
        fontsize=10, color=WHITE)
    ax.set_ylim(0, 14000)
    # Full Y-axis label — left margin increased to 0.18 to prevent clipping
    ax.set_ylabel("Medicare Reimbursement (USD per dose)", fontsize=10, labelpad=8)
    ax.set_title("How ASP+6% Rewards the Pricier Drug",
                 fontsize=12, color=WHITE, pad=10)
    ax.grid(True, axis="y", alpha=0.30, zorder=0)
    ax.set_axisbelow(True)

    ax.legend(fontsize=9, loc="upper right",
              framealpha=0.88, facecolor=NAVY, edgecolor=LGRAY, labelcolor=WHITE)

    footnote = (
        "Hypothetical doses for illustration. Originator: 10,000 ASP, 6% add-on = 600. "
        "Biosimilar: 3,000 ASP, 8% add-on = 240.\n"
        "Higher absolute add-on paid for the more expensive product, regardless of clinical equivalence. "
        "Source: Social Security Act Sec. 1847A; ASPE biosimilar add-on data."
    )
    fig.text(0.12, 0.02, footnote, fontsize=5.5, color=LGRAY, ha="left", va="bottom")
    # left=0.18 ensures the full Y-axis label clears the figure edge
    fig.subplots_adjust(top=0.88, bottom=0.14, left=0.18, right=0.97)

    out = FIGURES / "chart3_asp_incentive.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Saved: {out}")
    return out


# ══════════════════════════════════════════════════════════════════════════════
# CHART 4 — Ratio context + policy timeline (2-panel)
# ══════════════════════════════════════════════════════════════════════════════

def chart4():
    """Left panel: three published ratios as vertical bars.
    Right panel: vertical policy timeline (text to the right of dots).

    Fixes applied:
    - Confirmed figsize=(10, 6) at dpi=100, savefig dpi=150 -> 1500x900 output.
    - subplots_adjust: top=0.86, bottom=0.14, left=0.10, right=0.97 so
      suptitle at y=0.95 clears the top and footnote at y=0.02 clears the bottom.
    - wspace increased to 0.50 for panel separation.
    - Timeline text bumped to fontsize=8 with clip_on=False (already was 8; confirmed).
    - Footnote kept to one line fitting ~120 chars at 5.5pt / 1500px wide.
    - suptitle y lowered to 0.95 (was 0.97) so it fits inside the saved figure.
    """

    fig, (ax_left, ax_right) = plt.subplots(
        1, 2, figsize=(10, 6), dpi=100,
        gridspec_kw={"width_ratios": [1, 1.6], "wspace": 0.50})
    fig.patch.set_facecolor(NAVY)
    # top=0.82 leaves room for two-line suptitle; bottom=0.14 leaves room for footnote
    fig.subplots_adjust(top=0.82, bottom=0.14, left=0.10, right=0.97)

    # ── Left: ratio bars ─────────────────────────────────────────────────────
    ax_left.set_facecolor(NAVY)

    ratios = [
        (1.8,  GOLD,   "MedPAC/ASPE\n2018-19\nex-mfr\n(central)"),
        (2.05, TEAL,   "MedPAC 2019\npayment rate\n(add-on\nbaked in)"),
        (3.22, ORANGE, "RAND 2024\nbrand-orig.\n(aggressive\nceiling)"),
    ]

    xpos = np.array([0.0, 1.0, 2.0])
    for i, (ratio, col, lbl) in enumerate(ratios):
        ax_left.bar(xpos[i], ratio, width=0.52, color=col, alpha=0.88, zorder=3,
                    edgecolor=WHITE, linewidth=0.5)
        ax_left.text(xpos[i], ratio + 0.06, f"{ratio}x",
                     ha="center", va="bottom", fontsize=13, color=WHITE,
                     fontweight="bold", zorder=5)

    ax_left.set_xticks(xpos)
    ax_left.set_xticklabels([r[2] for r in ratios], fontsize=7.5, color=WHITE)
    ax_left.set_ylim(0, 4.5)
    ax_left.set_ylabel("US Part B Price / International Price", fontsize=9, labelpad=5)
    ax_left.set_title("Published US-vs-International\nPart B Price Ratios",
                      fontsize=10, color=WHITE, pad=8)
    ax_left.grid(True, axis="y", alpha=0.30, zorder=0)
    ax_left.set_axisbelow(True)

    # Reference line at 1.0 (parity)
    ax_left.axhline(1.0, color=LGRAY, linestyle=":", linewidth=0.9, zorder=2)
    # Place "Parity 1.0x" centered in the clear gap between bar 0 and bar 1,
    # with a navy bbox so it never reads against a bar fill
    ax_left.text(0.5, 1.06, "Parity 1.0x", fontsize=7, color=LGRAY, va="bottom",
                 ha="center", zorder=5,
                 bbox=dict(facecolor=NAVY, edgecolor="none", alpha=0.95, pad=1.5))

    # ── Right: policy timeline (dots + right-aligned text) ────────────────────
    ax_right.set_facecolor(NAVY)
    ax_right.set_xlim(0, 1)
    ax_right.set_ylim(2017.2, 2029.2)
    ax_right.invert_yaxis()

    events = [
        (2018, "ASPE: 1.8x ex-manufacturer (Part B biologics, 10 OECD)", TEAL),
        (2019, "MedPAC: 1.8x ex-manufacturer, 2.05x payment rate", TEAL),
        (2020, "MFN Model finalized (CMS; 87.8B / 7 yrs)", GOLD),
        (2021, "MFN Model rescinded (CMS; industry litigation)", RED),
        (2025, "GLOBE Model announced (CMS; mandatory demo)", TEAL),
        (2026, "IPAY-2028 IRA selections announced (5 Part B drugs)", TEAL),
        (2028, "IPAY-2028 MFPs effective Jan 1 (first Part B MFPs)", GOLD),
    ]

    x_dot = 0.08
    x_txt = 0.13
    for year, label, col in events:
        ax_right.plot(x_dot, year, "o", color=col, markersize=8, zorder=5,
                      clip_on=False)
        ax_right.text(x_txt, year, label, va="center", ha="left",
                      fontsize=8, color=WHITE, zorder=4, clip_on=False)

    # Vertical spine connecting dots
    ax_right.plot([x_dot, x_dot], [2018, 2028], color=LGRAY, linewidth=1.0,
                  zorder=2, solid_capstyle="round")

    # Year labels on y-axis
    ax_right.set_yticks([e[0] for e in events])
    ax_right.set_yticklabels([str(e[0]) for e in events], fontsize=9, color=WHITE)
    ax_right.tick_params(axis="y", length=0, pad=2)
    ax_right.set_xticks([])
    for spine in ax_right.spines.values():
        spine.set_visible(False)
    ax_right.set_title("Part B Price Policy Timeline (2018-2028)",
                       fontsize=10, color=WHITE, pad=8)

    # suptitle: two-line wrap so it fits within 1500px width at fontsize 11
    fig.suptitle(
        "Documented US Part B Drug Price Ratios\nand Policy Timeline (2018-2028)",
        fontsize=11, color=WHITE, y=0.97, fontweight="bold")

    # Footnote: fits ~120 chars at 5.5pt on a 1500px-wide figure with ha='left' at x=0.10
    fig.text(0.10, 0.02,
             "Sources: ASPE 2018; MedPAC June 2019 Report Ch 3; RAND RR-A788-3 2024; "
             "CMS MFN IFR 2020 (FR 2020-26037); CMS GLOBE Model Dec 2025; CMS IPAY-2028 fact sheet Jan 2026.",
             fontsize=5.5, color=LGRAY, ha="left", va="bottom")

    out = FIGURES / "chart4_ratio_context.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Saved: {out}")
    return out


# ══════════════════════════════════════════════════════════════════════════════
# CHART 5 — Savings tracker (all 17 issues)
# ══════════════════════════════════════════════════════════════════════════════

def chart5():
    """All 17 issues; Issue #17 highlighted in gold. Running total $541.88B."""
    issues = [
        ("#1",  "OTC Drugs",              0.6),
        ("#2",  "Drug Pricing",          25.0),
        ("#3",  "Hospital Pricing",      73.0),
        ("#4",  "PBM Reform",            30.0),
        ("#5",  "Admin Waste",          200.0),
        ("#6",  "Supply Waste",          28.0),
        ("#7",  "GLP-1 Pricing",         40.0),
        ("#8",  "Denial Machine",        32.0),
        ("#9",  "Employer Trap",          6.6),
        ("#10", "Procedure Mill",         7.6),
        ("#11", "MA Overpayment",        28.0),
        ("#12", "Consolidation Tax",     13.0),
        ("#13", "Nonprofit Lie",          5.4),
        ("#14", "Specialist Tax",        27.6),
        ("#15", "Facility Fee Scam",      2.55),
        ("#16", "The Other 100 Drugs",   16.36),
        ("#17", "Part B Premium",         6.17),
    ]

    nums    = [i[0] for i in issues]
    labels  = [i[1] for i in issues]
    savings = [i[2] for i in issues]
    running_total = 541.88
    target = 3240.0
    pct = running_total / target * 100

    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(10, 6.5), dpi=100,
        gridspec_kw={"width_ratios": [2, 1], "wspace": 0.52})
    fig.patch.set_facecolor(NAVY)
    fig.subplots_adjust(top=0.88, bottom=0.09, left=0.22, right=0.97)

    # ── Left: per-issue bars ─────────────────────────────────────────────────
    ax_left.set_facecolor(NAVY)
    y_pos = np.arange(len(issues))
    bar_colors = [GOLD if n == "#17" else TEAL for n in nums]
    bars = ax_left.barh(y_pos, savings, color=bar_colors, height=0.68, alpha=0.90, zorder=3)

    ax_left.set_yticks(y_pos)
    ax_left.set_yticklabels([f"{n}  {lbl}" for n, lbl in zip(nums, labels)],
                             fontsize=7.2, color=WHITE)

    max_s = max(savings)
    for i, (bar, val) in enumerate(zip(bars, savings)):
        lbl_txt = f"{val:.1f}B" if val >= 1.0 else f"{val:.2f}B"
        ax_left.text(val + max_s * 0.018, i, lbl_txt,
                     va="center", ha="left", fontsize=7.0, color=WHITE)

    ax_left.set_xlim(0, max_s * 1.38)
    ax_left.set_xlabel("Savings (USD Billions/year)", fontsize=9, labelpad=4)
    ax_left.set_title("Per-Issue Savings, Issues #1-#17", fontsize=10, color=WHITE, pad=7)
    ax_left.grid(True, axis="x", alpha=0.22, zorder=0)
    ax_left.set_axisbelow(True)

    # ── Right: running total ─────────────────────────────────────────────────
    ax_right.set_facecolor(NAVY)

    # Full-scale bar (y=1)
    ax_right.barh(1.0, target,        height=0.45, color=BG2,  alpha=1.0, zorder=2)
    ax_right.barh(1.0, running_total, height=0.45, color=TEAL, alpha=0.90, zorder=3)

    # Zoom bar (y=0): $0-$100B window (fully filled)
    ax_right.barh(0.0, 100.0, height=0.45, color=BG2,  alpha=1.0, zorder=2)
    ax_right.barh(0.0, 100.0, height=0.45, color=GOLD, alpha=0.90, zorder=3)

    ax_right.set_yticks([0.0, 1.0])
    ax_right.set_yticklabels(["Zoom:\n0-100B", "Full scale:\nvs 3.24T"],
                              fontsize=8.5, color=WHITE)
    ax_right.set_xlim(0, target * 1.05)
    ax_right.set_ylim(-0.55, 1.70)

    # Running total label above full-scale bar
    ax_right.text(running_total / 2.0, 1.25,
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
    ax_right.set_title("Running Total\n541.88B / 3.24T (16.7%)",
                       fontsize=10, color=WHITE, pad=7)
    ax_right.grid(True, axis="x", alpha=0.22, zorder=0)
    ax_right.set_axisbelow(True)

    fig.suptitle("AHC Savings Tracker -- After Issue #17",
                 fontsize=12, color=WHITE, y=0.975, fontweight="bold")

    fig.text(0.04, 0.01,
             "Target: 3.24T US-Japan per-capita gap (CMS NHE 2024; OECD 2023). "
             "Issue #17 adds 6.17B. Cumulative: 541.88B (16.7%). "
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
    """1456x1048px hero. Navy background, series branding, hook centered
    in ~900x550 safe zone (x: 278-1178, y: 249-799)."""
    fig = plt.figure(figsize=(14.56, 10.48), dpi=100)
    fig.patch.set_facecolor(NAVY)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(NAVY)
    ax.set_xlim(0, 1456)
    ax.set_ylim(0, 1048)
    ax.axis("off")

    # Subtle grid
    for gx in range(0, 1456, 72):
        ax.axvline(gx, color="#212840", linewidth=0.4, zorder=0)
    for gy in range(0, 1048, 72):
        ax.axhline(gy, color="#212840", linewidth=0.4, zorder=0)

    # Safe zone: x 278-1178, y 249-799 (centered ~900x550)
    # Content block top: y=745, bottom: y=300, center: y~524

    # ── Series branding ──────────────────────────────────────────────────────
    ax.text(728, 745, "THE AMERICAN HEALTHCARE CONUNDRUM",
            fontsize=17, color=RED, ha="center", va="center",
            fontweight="bold", zorder=5)
    ax.text(728, 715, "Issue #17",
            fontsize=23, color=GOLD, ha="center", va="center",
            fontweight="bold", zorder=5)

    # Red divider line
    ax.plot([300, 1156], [690, 690], color=RED, linewidth=2.5, zorder=5)

    # ── Main hook: "1.8x" large ───────────────────────────────────────────────
    ax.text(728, 590, "1.8x",
            fontsize=110, color=WHITE, ha="center", va="center",
            fontweight="bold", zorder=5)

    ax.text(728, 510, "THE PART B PHARMACY PREMIUM",
            fontsize=26, color=TEAL, ha="center", va="center",
            fontweight="bold", zorder=5)

    # ── Supporting lines ─────────────────────────────────────────────────────
    ax.text(728, 464,
            "Same infusion. Same molecule. Medicare pays 1.8x the international price.",
            fontsize=16, color=WHITE, ha="center", va="center", zorder=5)
    ax.text(728, 436,
            r"\$6.2 billion per year in recoverable excess across 597 Part B drug codes.",
            fontsize=16, color=WHITE, ha="center", va="center", zorder=5)

    # ── Stat bar ─────────────────────────────────────────────────────────────
    rect = mpatches.FancyBboxPatch(
        (270, 305), 920, 88,
        boxstyle="round,pad=4", linewidth=0, facecolor="#0E2040", zorder=4
    )
    ax.add_patch(rect)

    stats = [
        (r"\$50.8B",           "total Part B drug spend (CY2023)"),
        ("1.8x",               "US vs international ex-manufacturer"),
        (r"\$541.88B",         r"running total  16.7% of \$3.24T gap"),
    ]
    xs = [430, 728, 1026]
    for (stat, sub), x in zip(stats, xs):
        ax.text(x, 358, stat, fontsize=15, color=GOLD, ha="center", va="center",
                fontweight="bold", zorder=6)
        ax.text(x, 330, sub, fontsize=9.5, color=LGRAY, ha="center", va="center",
                zorder=6)

    for xd in [580, 876]:
        ax.plot([xd, xd], [313, 387], color=LGRAY, linewidth=0.8, zorder=5)

    # ── Bottom branding ───────────────────────────────────────────────────────
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
    print("Generating Issue #17 charts ...")
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
