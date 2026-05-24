"""
generate_all_charts.py -- Issue #13: The Nonprofit Lie
Single entry-point to wipe figures/*.png and regenerate all 5 charts + hero.
Run from any directory: python3 /path/to/healthcare/issue_13/generate_all_charts.py
"""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

# -- Paths --------------------------------------------------------------------
ROOT    = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
FIGURES.mkdir(exist_ok=True)

# Wipe existing PNGs before regenerating
wiped = 0
for f in FIGURES.glob("*.png"):
    try:
        f.unlink()
        wiped += 1
    except PermissionError:
        pass
print(f"Wiped {wiped} existing PNGs")

# -- Brand colors -------------------------------------------------------------
NAVY   = "#1A1F2E"
TEAL   = "#0E8A72"
RED    = "#B7182A"
GOLD   = "#D4AF37"
WHITE  = "#F8F8F6"
LTGRAY = "#8090A0"
MID_NAVY = "#252B3D"

# -- Load data ----------------------------------------------------------------
with open(RESULTS / "savings_estimate.json") as f:
    est = json.load(f)

state_df = pd.read_csv(RESULTS / "savings_by_state.csv")

# For Chart 1 ownership breakdown, compute from gap_panel.csv
# ctrl_type: 1,2 = nonprofit; 3-6 = for-profit; 7-13 = government
# We use the validated numbers from cross_validation.csv (Anchors B,C,D)
# Government 3.56%, For-profit 3.14%, Nonprofit 1.86% (our FY2023 panel)
# Bai/Anderson 2021 reference: Gov 4.1%, FP 3.8%, NP 2.3%


# =============================================================================
# CHART 1 -- Charity Share by Ownership, FY2023
# =============================================================================

def chart1_charity_share():
    # Redesigned 2026-05-24: removed floating annotation box (was overlapping
    # right spine and arrow crossed the "2021: 2.3%" reference label) and removed
    # legend (redundant — colored bars + inline reference markers carry the
    # encoding). The dollar anchor ($46.4B) moves into the subtitle.
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=100)
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)

    categories = ["Government", "For-Profit", "Nonprofit"]
    our_vals   = [3.56, 3.14, 1.86]
    ref_vals   = [4.10, 3.80, 2.30]   # Bai/Anderson 2021

    x = np.array([0, 1, 2])
    width = 0.48

    # FY2023 bars: gold (government), teal (for-profit), red (nonprofit)
    bar_colors = [GOLD, TEAL, RED]
    our_bars = ax.bar(
        x, our_vals, width,
        color=bar_colors, zorder=3,
        edgecolor=NAVY, linewidth=1.0
    )

    # Reference markers: thin horizontal dash at the 2021 value, labeled to the
    # right. Replaces the faded gray "reference bars" approach, which was visually
    # busy and required a legend to decode.
    ref_line_half_width = width / 2 + 0.02
    for rx, rv in zip(x, ref_vals):
        ax.hlines(
            y=rv, xmin=rx - ref_line_half_width, xmax=rx + ref_line_half_width,
            color=LTGRAY, linestyle=(0, (4, 3)), linewidth=1.4, zorder=4, alpha=0.85
        )
        ax.text(
            rx + ref_line_half_width + 0.04, rv,
            f"Bai/Anderson 2021: {rv:.1f}%",
            ha="left", va="center",
            color=LTGRAY, fontsize=7.5
        )

    # Value labels INSIDE our bars (white, bold)
    for bar, val in zip(our_bars, our_vals):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            val / 2,
            f"{val:.2f}%",
            ha="center", va="center",
            color=WHITE, fontsize=14, fontweight="bold"
        )

    ax.set_xticks(x)
    ax.set_xticklabels(categories, color=WHITE, fontsize=12)
    ax.set_ylabel("Charity care as % of operating expenses", color=WHITE, fontsize=10)
    ax.tick_params(axis="y", colors=WHITE, labelsize=9.5)
    ax.tick_params(axis="x", colors=WHITE, pad=4)
    for spine in ax.spines.values():
        spine.set_edgecolor(LTGRAY)
    ax.grid(axis="y", color=LTGRAY, alpha=0.22, linewidth=0.6)
    ax.set_ylim(0, 5.0)
    ax.set_xlim(-0.55, 2.85)

    # Title + subtitle. The dollar anchor ($46.4B) lives in the subtitle.
    fig.suptitle(
        "Charity Care as % of Operating Expenses, by Ownership",
        color=WHITE, fontsize=14, fontweight="bold", y=0.96
    )
    ax.set_title(
        "Nonprofit hospitals, exempted from $46.4B in annual taxes, deliver less per dollar than for-profit chains paying full taxes (FY2023)",
        color=LTGRAY, fontsize=8.5, pad=8
    )

    # Footnote: 2 lines, fully within the figure width per CLAUDE.md rule #8.
    fig.text(
        0.09, 0.04,
        "Source: Authors' analysis of CMS HCRIS HOSP10 FY2023, Worksheet S-10 and Worksheet A; 3,005 hospitals.\n"
        "Reference values: Bai G, Yehia F, Chen W, Anderson GF. Health Affairs 2021;40(4):629-636.",
        color=LTGRAY, fontsize=7, va="bottom", ha="left"
    )

    plt.subplots_adjust(bottom=0.16, left=0.09, right=0.97, top=0.84)
    out = FIGURES / "chart1_charity_share_by_ownership.png"
    fig.savefig(out, dpi=150, facecolor=NAVY, bbox_inches=None)
    plt.close(fig)
    print(f"Saved {out}")
    return out


# =============================================================================
# CHART 2 -- Narrow vs Broad Test Fail Rates with $ Gap
# =============================================================================

def chart2_narrow_vs_broad():
    narrow_pct  = 86.0
    broad_pct   = 44.0
    narrow_gap  = 31.3
    broad_gap   = 11.9
    booked      = 5.38

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5.5), dpi=100,
                                    gridspec_kw={"wspace": 0.45})
    fig.patch.set_facecolor(NAVY)
    ax1.set_facecolor(NAVY)
    ax2.set_facecolor(NAVY)

    fig.suptitle(
        "Two Tests, Same Panel: 86% vs 44%",
        color=WHITE, fontsize=14, fontweight="bold", y=0.97
    )
    fig.text(
        0.5, 0.90,
        "Different tests of the same gap -- one counts only audited charity, the other includes Medicaid shortfall",
        color=LTGRAY, fontsize=8.5, ha="center", va="top"
    )

    # Left panel -- fail rates
    bars1 = ax1.bar(
        [0, 1], [narrow_pct, broad_pct],
        color=[RED, TEAL], width=0.50, zorder=3
    )
    for bar, val in zip(bars1, [narrow_pct, broad_pct]):
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            val / 2,
            f"{val:.0f}%",
            ha="center", va="center",
            color=WHITE, fontsize=18, fontweight="bold"
        )
    ax1.set_xticks([0, 1])
    ax1.set_xticklabels(["Narrow test\n(HCRIS audited\ncharity only)",
                          "Broad test\n(Bai/Anderson subset\n+ Medicaid shortfall)"],
                         color=WHITE, fontsize=9.5)
    ax1.set_ylabel("% of nonprofit hospitals failing test", color=WHITE, fontsize=9.5)
    ax1.set_ylim(0, 110)
    ax1.tick_params(axis="y", colors=WHITE, labelsize=9)
    ax1.tick_params(axis="x", colors=WHITE)
    for spine in ax1.spines.values():
        spine.set_edgecolor(LTGRAY)
    ax1.grid(axis="y", color=LTGRAY, alpha=0.22, linewidth=0.6)
    ax1.set_title("Hospitals Failing Fair-Share Test", color=WHITE, fontsize=10, pad=8)

    ax1.text(
        0.5, 0.97,
        "86% fail the charity-only test\n(Herring 2018 reproduced on FY2023 data)",
        transform=ax1.transAxes, color=RED, fontsize=8,
        ha="center", va="top",
        bbox=dict(boxstyle="round,pad=0.3", facecolor=NAVY, edgecolor=RED,
                  alpha=0.90, linewidth=1.0)
    )

    # Right panel -- raw gap $
    bars2 = ax2.bar(
        [0, 1], [narrow_gap, broad_gap],
        color=[RED, TEAL], width=0.50, zorder=3
    )
    for bar, val in zip(bars2, [narrow_gap, broad_gap]):
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            val / 2,
            f"${val:.1f}B",
            ha="center", va="center",
            color=WHITE, fontsize=15, fontweight="bold"
        )
    # Booked annotation -- place ABOVE the broad bar to avoid obscuring the label
    ax2.annotate(
        f"${booked:.2f}B booked\n(53% recoverability,\nafter overlap)",
        xy=(1, broad_gap), xytext=(1.30, broad_gap + 8),
        color=GOLD, fontsize=8.5,
        ha="left", va="center",
        bbox=dict(boxstyle="round,pad=0.35", facecolor=NAVY, edgecolor=GOLD,
                  alpha=0.95, linewidth=1.1),
        arrowprops=dict(arrowstyle="->", color=GOLD, lw=1.2,
                        connectionstyle="arc3,rad=0.3")
    )
    ax2.set_xticks([0, 1])
    ax2.set_xticklabels(["Narrow test\ngap", "Broad test\ngap"],
                         color=WHITE, fontsize=9.5)
    ax2.set_ylabel("Raw fair-share gap ($ billions)", color=WHITE, fontsize=9.5)
    ax2.set_ylim(0, 42)
    ax2.set_xlim(-0.5, 2.1)
    ax2.tick_params(axis="y", colors=WHITE, labelsize=9)
    ax2.tick_params(axis="x", colors=WHITE)
    for spine in ax2.spines.values():
        spine.set_edgecolor(LTGRAY)
    ax2.grid(axis="y", color=LTGRAY, alpha=0.22, linewidth=0.6)
    ax2.set_title("Aggregate Fair-Share Gap", color=WHITE, fontsize=10, pad=8)

    fig.text(
        0.12, 0.02,
        "Source: Authors' analysis of CMS HCRIS HOSP10 FY2023 (S-10 line 23 col 3) and IRS Form 990 Schedule H Part I "
        "lines 7a+7b+7c+7e+7g+7i, FY2023. Panel: 3,005 nonprofit hospitals.",
        color=LTGRAY, fontsize=6.5, va="bottom", ha="left"
    )

    plt.subplots_adjust(bottom=0.14, left=0.09, right=0.97, top=0.83)
    out = FIGURES / "chart2_narrow_vs_broad_test.png"
    fig.savefig(out, dpi=150, facecolor=NAVY, bbox_inches=None)
    plt.close(fig)
    print(f"Saved {out}")
    return out


# =============================================================================
# CHART 3 -- State Concentration of Fair-Share Gap (top 10)
# =============================================================================

def chart3_state_concentration():
    # Top 10 by broad gap from newsletter / cross-validated state data
    top10 = state_df.nlargest(10, "gap_broad_bil").copy()
    top10 = top10.sort_values("gap_broad_bil", ascending=True)

    states     = top10["state"].tolist()
    gaps       = top10["gap_broad_bil"].tolist()
    fail_rates = (top10["pct_fails_broad"]).tolist()

    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=100)
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)

    y = np.arange(len(states))

    # Color KY (highest fail rate) in gold to flag it
    bar_colors = [GOLD if s == "KY" else TEAL for s in states]
    bars = ax.barh(y, gaps, color=bar_colors, height=0.55, zorder=3)

    # Dollar labels to the right of bars
    for i, (bar, gap, fr) in enumerate(zip(bars, gaps, fail_rates)):
        bw = bar.get_width()
        # Gap amount
        ax.text(
            bw + 0.02, bar.get_y() + bar.get_height() / 2,
            f"${gap:.2f}B",
            ha="left", va="center",
            color=WHITE, fontsize=9.5, fontweight="bold"
        )
        # Fail rate (secondary, muted)
        ax.text(
            bw + 0.25, bar.get_y() + bar.get_height() / 2,
            f"({fr:.0f}% fail)",
            ha="left", va="center",
            color=LTGRAY, fontsize=8.5
        )

    # KY annotation -- place text box in upper right where there's airspace
    ky_idx = states.index("KY")
    ax.annotate(
        "Kentucky: 81% fail rate\nhighest among large states",
        xy=(gaps[ky_idx], ky_idx),
        xytext=(1.55, ky_idx + 2.5),
        color=GOLD, fontsize=8.5,
        ha="left", va="center",
        bbox=dict(boxstyle="round,pad=0.35", facecolor=NAVY, edgecolor=GOLD,
                  alpha=0.95, linewidth=1.1),
        arrowprops=dict(arrowstyle="->", color=GOLD, lw=1.2,
                        connectionstyle="arc3,rad=-0.30")
    )

    ax.set_yticks(y)
    ax.set_yticklabels(states, color=WHITE, fontsize=11)
    ax.set_xlabel("Broad-test fair-share gap ($ billions)", color=WHITE, fontsize=10)
    ax.set_xlim(0, 2.55)
    ax.tick_params(axis="x", colors=WHITE, labelsize=9)
    ax.tick_params(axis="y", colors=WHITE)
    for spine in ax.spines.values():
        spine.set_edgecolor(LTGRAY)
    ax.grid(axis="x", color=LTGRAY, alpha=0.22, linewidth=0.6)

    fig.suptitle(
        "Where the Gap Lives: Top 10 States by Broad-Test Fair-Share Gap",
        color=WHITE, fontsize=13, fontweight="bold", y=0.97
    )
    ax.set_title(
        "California, Pennsylvania, and Illinois carry the largest dollar gaps; Kentucky leads in fail rate",
        color=LTGRAY, fontsize=8.5, pad=6
    )

    fig.text(
        0.08, 0.03,
        "Source: Authors' analysis aggregated by state from FY2023 panel (3,005 nonprofit hospitals).\n"
        "Broad test = Bai/Anderson community-benefit subset including Medicaid shortfall vs. tax-exemption value.",
        color=LTGRAY, fontsize=6.5, va="bottom", ha="left", linespacing=1.4
    )

    plt.subplots_adjust(bottom=0.17, left=0.08, right=0.88, top=0.84)
    out = FIGURES / "chart3_state_concentration.png"
    fig.savefig(out, dpi=150, facecolor=NAVY, bbox_inches=None)
    plt.close(fig)
    print(f"Saved {out}")
    return out


# =============================================================================
# CHART 4 -- Tax Exemption Component Decomposition (horizontal stacked bar)
# =============================================================================

def chart4_tax_exemption():
    # From savings_estimate.json -- vertical bar chart for label clarity
    components = [
        ("Federal\nincome tax", est["tax_exemption_components_bil"]["fed_income_tax"]),
        ("Sales tax",           est["tax_exemption_components_bil"]["sales_tax"]),
        ("Property tax",        est["tax_exemption_components_bil"]["property_tax"]),
        ("State\nincome tax",   est["tax_exemption_components_bil"]["state_income_tax"]),
        ("Bond\nfinancing",     est["tax_exemption_components_bil"]["bond_interest_subsidy"]),
        ("Charitable\ndeduction", est["tax_exemption_components_bil"]["charitable_deduction"]),
        ("FUTA",                est["tax_exemption_components_bil"]["futa"]),
    ]
    total = est["tax_exemption_components_bil"]["total"]

    labels = [c[0] for c in components]
    values = [c[1] for c in components]
    pcts   = [v / total * 100 for v in values]

    # Design choice: vertical bar chart avoids horizontal stacked-label collision
    comp_colors = [RED, "#1A6B8A", GOLD, "#2E9E84", TEAL, LTGRAY, "#5A6A7A"]

    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=100)
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)

    x = np.arange(len(labels))
    bars = ax.bar(x, values, color=comp_colors, width=0.65, zorder=3,
                  edgecolor=NAVY, linewidth=0.8)

    # Value labels: inside bars for large segments (>=2B), above for small ones
    for bar, val, pct in zip(bars, values, pcts):
        h = bar.get_height()
        if h >= 3.0:
            # Inside the bar
            ax.text(bar.get_x() + bar.get_width() / 2, h / 2,
                    f"${val:.1f}B\n({pct:.1f}%)",
                    ha="center", va="center",
                    color=WHITE, fontsize=9.5, fontweight="bold")
        elif h >= 0.5:
            # Above the bar, with offset
            ax.text(bar.get_x() + bar.get_width() / 2, h + 0.3,
                    f"${val:.1f}B\n({pct:.1f}%)",
                    ha="center", va="bottom",
                    color=WHITE, fontsize=8.5, fontweight="bold")
        else:
            # FUTA (tiny) -- above with more offset
            ax.text(bar.get_x() + bar.get_width() / 2, h + 0.5,
                    f"${val:.2f}B\n({pct:.1f}%)",
                    ha="center", va="bottom",
                    color=LTGRAY, fontsize=7.5)

    # Total annotation -- right of last bar
    ax.text(len(labels) - 0.5 + 0.5, total * 0.85,
            f"Total:\n${total:.1f}B",
            ha="left", va="center",
            color=GOLD, fontsize=11, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.3", facecolor=NAVY, edgecolor=GOLD,
                      alpha=0.9, linewidth=1.1))

    ax.set_xticks(x)
    ax.set_xticklabels(labels, color=WHITE, fontsize=9.5, linespacing=1.3)
    ax.tick_params(axis="x", colors=WHITE, pad=4)
    ax.tick_params(axis="y", colors=WHITE, labelsize=9)
    ax.set_ylabel("Tax exemption value ($ billions)", color=WHITE, fontsize=10)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"${v:.0f}B"))
    ax.set_ylim(0, 22)
    ax.set_xlim(-0.6, len(labels) + 0.3)
    for spine in ax.spines.values():
        spine.set_edgecolor(LTGRAY)
    ax.grid(axis="y", color=LTGRAY, alpha=0.22, linewidth=0.6)

    fig.suptitle(
        "Where the $46.4 Billion Tax Shield Comes From",
        color=WHITE, fontsize=13, fontweight="bold", y=0.97
    )
    ax.set_title(
        "Plummer/Socal/Bai 2024 component method applied to 3,005 nonprofit hospitals, FY2023",
        color=LTGRAY, fontsize=8.5, pad=6
    )

    fig.text(
        0.09, 0.04,
        "Source: Plummer/Socal/Bai 2024 (JAMA, DOI 10.1001/jama.2024.13413) component method,\n"
        "applied to CMS HCRIS HOSP10 FY2023 panel of 3,005 nonprofit hospitals.\n"
        "State and local components (sales, property, state income, bond) account for ~61% of total.",
        color=LTGRAY, fontsize=7, va="bottom", ha="left"
    )

    plt.subplots_adjust(bottom=0.18, left=0.09, right=0.96, top=0.84)
    out = FIGURES / "chart4_tax_exemption_components.png"
    fig.savefig(out, dpi=150, facecolor=NAVY, bbox_inches=None)
    plt.close(fig)
    print(f"Saved {out}")
    return out


# =============================================================================
# CHART 5 -- Cumulative Savings Tracker ($489.2B of $3.24T)
# =============================================================================

def chart5_savings_tracker():
    issues = [
        ("#1\nOTC Drugs",    0.6),
        ("#2\nDrug Pricing", 25.0),
        ("#3\nHospital Px",  73.0),
        ("#4\nPBMs",         30.0),
        ("#5\nAdmin Waste",  200.0),
        ("#6\nSupply Waste", 28.0),
        ("#7\nGLP-1",        40.0),
        ("#8\nDenial Mach.", 32.0),
        ("#9\nEmployer",      6.6),
        ("#10\nProcedures",   7.6),
        ("#11\nMA Overpay",  28.0),
        ("#12\nConsol. Tax", 13.0),
        ("#13\nNonprofit",    5.38),
    ]
    labels_i = [x[0] for x in issues]
    values_i = [x[1] for x in issues]
    total_b  = sum(values_i)   # 489.18 ~ 489.2
    gap_b    = 3240.0

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5.5), dpi=100,
                                    gridspec_kw={"width_ratios": [3, 1], "wspace": 0.45})
    fig.patch.set_facecolor(NAVY)
    ax1.set_facecolor(NAVY)
    ax2.set_facecolor(NAVY)

    fig.suptitle(
        f"Cumulative Savings Identified: ${total_b:.1f}B  (15.1% of US-Japan Gap)",
        color=WHITE, fontsize=11.5, fontweight="bold", y=0.98
    )

    # Left panel -- per-issue bars
    bar_colors_i = [RED if lbl.startswith("#13") else TEAL for lbl in labels_i]
    bars = ax1.bar(range(len(issues)), values_i, color=bar_colors_i,
                   zorder=3, width=0.70)

    # Value labels: inside for tall bars, above for short ones
    for i, (bar, val) in enumerate(zip(bars, values_i)):
        h = bar.get_height()
        if h >= 20:
            ax1.text(bar.get_x() + bar.get_width() / 2, h / 2,
                     f"${val:.0f}B", ha="center", va="center",
                     color=WHITE, fontsize=7.5, fontweight="bold")
        else:
            ax1.text(bar.get_x() + bar.get_width() / 2, h + 2.5,
                     f"${val:.1f}B", ha="center", va="bottom",
                     color=WHITE, fontsize=6.5, fontweight="bold")

    short_names = ["OTC", "Drug Px", "Hosp Px", "PBMs", "Admin", "Supply",
                   "GLP-1", "Denial", "Employer", "Procedure",
                   "MA Overpay", "Consol.", "Nonprofit"]
    xtick_labels = [f"#{i+1} {s}" for i, s in enumerate(short_names)]
    ax1.set_xticks(range(len(issues)))
    ax1.set_xticklabels(xtick_labels, color=WHITE, fontsize=7.5,
                         rotation=35, ha="right")
    ax1.set_ylabel("Savings ($B)", color=WHITE, fontsize=9)
    ax1.tick_params(axis="y", colors=WHITE, labelsize=8.5)
    ax1.tick_params(axis="x", colors=WHITE, pad=2)
    for spine in ax1.spines.values():
        spine.set_edgecolor(LTGRAY)
    ax1.grid(axis="y", color=LTGRAY, alpha=0.2, linewidth=0.6)
    ax1.set_ylim(0, 240)
    ax1.set_title("Per-Issue Savings (Issue #13 highlighted)", color=WHITE, fontsize=9.5, pad=6)

    # Right panel -- cumulative gauge
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
    ax2.set_title(f"{pct:.1f}% of\n$3.24T gap", color=GOLD, fontsize=10,
                  fontweight="bold", pad=6)

    fig.text(
        0.02, 0.02,
        "Sources: Published Issues #1-#13. Full-scale gap: CMS NHE 2024 + OECD Health at a Glance 2025 ($3.24T).",
        color=LTGRAY, fontsize=6.5, va="bottom", ha="left"
    )

    plt.subplots_adjust(bottom=0.24, left=0.08, right=0.97, top=0.83)
    out = FIGURES / "chart5_savings_tracker.png"
    fig.savefig(out, dpi=150, facecolor=NAVY, bbox_inches=None)
    plt.close(fig)
    print(f"Saved {out}")
    return out


# =============================================================================
# HERO IMAGE -- 1456 x 1048 px (figsize 14.56 x 10.48 @ 100dpi, saved at 150dpi)
# Safe zone: centered 900x550 px = 62% width x 52% height
# =============================================================================

def hero_cover():
    # Canvas: 1456x1048 rendered at 100dpi (14.56 x 10.48 inches), saved at 150dpi
    FW, FH = 14.56, 10.48
    fig = plt.figure(figsize=(FW, FH), dpi=100)
    fig.patch.set_facecolor(NAVY)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, FW)
    ax.set_ylim(0, FH)
    ax.axis("off")
    ax.set_facecolor(NAVY)

    # Subtle background grid (atmospheric, outside safe zone is just decoration)
    for gx in np.arange(0, FW, 0.8):
        ax.axvline(gx, color=WHITE, alpha=0.025, linewidth=0.4)
    for gy in np.arange(0, FH, 0.8):
        ax.axhline(gy, color=WHITE, alpha=0.025, linewidth=0.4)

    CX = FW / 2   # 7.28 in
    # Safe zone: 19% margins L/R, 24% margins T/B
    SZ_X_LO = FW * 0.19   # 2.77
    SZ_X_HI = FW * 0.81   # 11.79
    SZ_Y_LO = FH * 0.24   # 2.52
    SZ_Y_HI = FH * 0.76   # 7.96
    # Safe zone height = 5.44 in, center = 5.24 in

    # ---- Layout plan (top to bottom within safe zone) -----------------------
    # banner text     ~ 7.75 in  (top of safe zone - a little padding)
    # "ISSUE #13"     ~ 7.10 in
    # red rule        ~ 6.60 in
    # main hook text  ~ 5.55 in  (center-ish, large text)
    # line 1 support  ~ 4.40 in
    # line 2 support  ~ 3.75 in
    # stats bar       ~ 2.85 in  (bottom of safe zone + padding)

    # ---- Series banner ------------------------------------------------------
    ax.text(CX, 7.75,
            "THE AMERICAN HEALTHCARE CONUNDRUM",
            color=RED, fontsize=20, fontweight="bold",
            ha="center", va="center",
            fontfamily="DejaVu Sans")

    ax.text(CX, 7.10,
            "ISSUE #13",
            color=GOLD, fontsize=16, fontweight="bold",
            ha="center", va="center",
            fontfamily="DejaVu Sans")

    # Red divider line
    ax.plot([SZ_X_LO + 0.5, SZ_X_HI - 0.5], [6.60, 6.60],
            color=RED, linewidth=2.2)

    # ---- Main hook number ---------------------------------------------------
    ax.text(CX, 5.55,
            "$46 Billion Tax Shield",
            color=GOLD, fontsize=56, fontweight="bold",
            ha="center", va="center",
            fontfamily="DejaVu Sans")

    # ---- Supporting comparison lines ----------------------------------------
    # Unit: cents per dollar of operating expenses (matches the 3.14% / 1.86%
    # percentages in the body and chart 1). Use the cents glyph (¢ = ¢) to
    # avoid the typo-look of a lowercase "c" — Andrew flagged this on 2026-05-24.
    ax.text(CX, 4.40,
            "For-profit chains paying full taxes deliver 3.14¢ of charity per dollar.",
            color=WHITE, fontsize=18, fontweight="bold",
            ha="center", va="center",
            fontfamily="DejaVu Sans")

    ax.text(CX, 3.72,
            "Nonprofits exempt from $46.4B in annual taxes deliver 1.86¢.",
            color=WHITE, fontsize=18,
            ha="center", va="center",
            fontfamily="DejaVu Sans",
            alpha=0.85)

    # ---- Stats bar (bottom of safe zone, well separated from lines above) ---
    ax.text(CX, 2.88,
            "3,005 NONPROFIT HOSPITALS  |  86% FAIL CHARITY-ONLY TEST  |  $46.4B ANNUAL TAX EXEMPTION  |  FY2023",
            color=LTGRAY, fontsize=10,
            ha="center", va="center",
            fontfamily="DejaVu Sans")

    out = FIGURES / "hero_cover.png"
    fig.savefig(out, dpi=150, facecolor=NAVY, bbox_inches=None)
    plt.close(fig)
    print(f"Saved {out}")
    return out


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("\n=== Issue #13: The Nonprofit Lie -- Chart Generation ===\n")

    out1 = chart1_charity_share()
    out2 = chart2_narrow_vs_broad()
    out3 = chart3_state_concentration()
    out4 = chart4_tax_exemption()
    out5 = chart5_savings_tracker()
    out6 = hero_cover()

    print("\nAll 6 PNGs generated.")
    print(f"Figures directory: {FIGURES}")
    for f in sorted(FIGURES.glob("*.png")):
        print(f"  {f.name}: {f.stat().st_size:,} bytes")
