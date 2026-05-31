"""
generate_all_charts.py -- Issue #14: The Specialist Tax
Single entry-point to wipe figures/*.png and regenerate all 5 charts + hero.
Run from any directory: python3 /path/to/issue_14/generate_all_charts.py
"""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

# -- Paths -------------------------------------------------------------------
ROOT    = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
FIGURES.mkdir(exist_ok=True)

# Wipe existing PNGs
wiped = 0
for f in FIGURES.glob("*.png"):
    try:
        f.unlink()
        wiped += 1
    except PermissionError:
        pass
print(f"Wiped {wiped} existing PNGs")

# -- Brand colors ------------------------------------------------------------
NAVY   = "#1A1F2E"
TEAL   = "#0E8A72"
RED    = "#B7182A"
GOLD   = "#D4AF37"
WHITE  = "#F8F8F6"
LTGRAY = "#8090A0"

# -- Load data ---------------------------------------------------------------
with open(RESULTS / "savings_estimate.json") as fh:
    est = json.load(fh)

comp_a_df  = pd.read_csv(RESULTS / "component_a_per_specialty.csv")
comp_c_df  = pd.read_csv(RESULTS / "component_c_family_breakdown.csv")
overlap_df = pd.read_csv(RESULTS / "overlap_subtractions.csv")

# =============================================================================
# CHART 1 -- US vs OECD-18 specialist compensation panel
# Horizontal bar chart: top contributing specialties, US vs OECD-18 median
# =============================================================================
def generate_chart1_oecd18_comp(outpath: Path):
    # Specialties to show (exclude "Physicians, all other" and keep top contributors)
    exclude = {"Physicians, all other", "Pathology", "Neurology", "Dermatology"}
    df = comp_a_df[~comp_a_df["canonical_specialty"].isin(exclude)].copy()
    df = df.sort_values("total_gap_bil", ascending=False).head(9)
    df = df.sort_values("us_comp_per_fte_usd", ascending=True)  # ascending for horiz bar

    specialties = df["canonical_specialty"].tolist()
    us_vals  = df["us_comp_per_fte_usd"].values / 1000   # in $K
    pc_flags = df["primary_care_flag"].values

    oecd_spec_median = est["key_observations"]["oecd_specialist_median_usd_ppp"] / 1000  # $176.7K
    oecd_gp_median   = est["key_observations"]["oecd_gp_median_usd_ppp"] / 1000          # $154.7K

    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)

    y_pos = np.arange(len(specialties))
    bar_colors = [TEAL if not pc else GOLD for pc in pc_flags]

    bars = ax.barh(y_pos, us_vals, color=bar_colors, height=0.55, zorder=3)

    # OECD-18 specialist median reference line
    ax.axvline(oecd_spec_median, color=RED, linewidth=2.0, linestyle="--",
               zorder=4, label=f"OECD-18 specialist median: ${oecd_spec_median:.0f}K")
    # OECD-18 GP median reference line
    ax.axvline(oecd_gp_median, color=GOLD, linewidth=1.8, linestyle=":",
               zorder=4, label=f"OECD-18 GP median: ${oecd_gp_median:.0f}K")

    # Value labels on bars -- place to the right of each bar
    max_val = us_vals.max()
    for bar, val, pc in zip(bars, us_vals, pc_flags):
        label = f"${val:.0f}K"
        x_text = val + max_val * 0.01
        ax.text(x_text, bar.get_y() + bar.get_height() / 2,
                label, va="center", ha="left",
                color=WHITE, fontsize=9, fontweight="bold")

    # Y-axis: specialty labels
    ax.set_yticks(y_pos)
    ax.set_yticklabels(specialties, color=WHITE, fontsize=9.5)
    ax.tick_params(axis="x", colors=WHITE, labelsize=9)
    ax.tick_params(axis="y", colors=WHITE)

    # X axis: USD in $K
    ax.set_xlabel("Annual compensation (USD PPP, productivity-normalized, $K)", color=WHITE, fontsize=9)
    ax.set_xlim(0, max_val * 1.22)

    for spine in ax.spines.values():
        spine.set_edgecolor(LTGRAY)
    ax.grid(axis="x", color=LTGRAY, alpha=0.20, linewidth=0.6, zorder=0)

    # Legend -- place inside clear space top-right
    legend_handles = [
        mpatches.Patch(color=TEAL,  label="US specialist pay (BLS OEWS May 2024)"),
        mpatches.Patch(color=GOLD,  label="US primary care pay (BLS OEWS May 2024)"),
        plt.Line2D([0], [0], color=RED,  linewidth=2, linestyle="--",
                   label=f"OECD-18 specialist median: ${oecd_spec_median:.0f}K"),
        plt.Line2D([0], [0], color=GOLD, linewidth=1.8, linestyle=":",
                   label=f"OECD-18 GP median: ${oecd_gp_median:.0f}K"),
    ]
    ax.legend(handles=legend_handles, loc="lower right",
              fontsize=7.5, framealpha=0.85,
              facecolor=NAVY, edgecolor=LTGRAY, labelcolor=WHITE)

    ax.set_title("US Specialty Pay vs OECD-18 Peer Median",
                 color=WHITE, fontsize=13, fontweight="bold", pad=10)

    # Footnote -- one line, left-aligned, wrapped to avoid clipping
    footnote = (
        "Source: BLS OEWS May 2024 + OECD DF_REMUN 2025 (OECD-18 peer median, USD PPP).\n"
        "Productivity-normalized (0.77x) to adjust for US vs OECD physician density difference."
    )
    fig.text(0.10, 0.01, footnote, color=LTGRAY, fontsize=6.5, va="bottom", ha="left")

    plt.subplots_adjust(left=0.20, right=0.96, top=0.91, bottom=0.14)
    fig.savefig(outpath, dpi=150, facecolor=NAVY, bbox_inches=None)
    plt.close(fig)
    print(f"Saved {outpath}")


# =============================================================================
# CHART 2 -- Workforce specialty mix: US vs OECD-18 median vs COGME target
# Two-panel side-by-side stacked bar
# =============================================================================
def generate_chart2_workforce_mix(outpath: Path):
    # Data
    us_spec = 0.72
    us_pc   = 0.28
    oecd_spec = 0.50
    oecd_pc   = 0.50
    cogme_target_pc = 0.45

    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=100)
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)

    x_pos = [0.0, 1.0]
    width = 0.45

    # Specialist bars (bottom)
    bar_spec = ax.bar(x_pos, [us_spec * 100, oecd_spec * 100],
                      width, color=RED, alpha=0.85, label="Specialists", zorder=3)
    # Primary care bars (top)
    bar_pc = ax.bar(x_pos, [us_pc * 100, oecd_pc * 100],
                    width, bottom=[us_spec * 100, oecd_spec * 100],
                    color=TEAL, alpha=0.90, label="Primary Care / GP", zorder=3)

    # COGME target reference line
    ax.axhline(cogme_target_pc * 100, color=GOLD, linewidth=2.0,
               linestyle="--", zorder=4,
               label=f"COGME target: {cogme_target_pc*100:.0f}% primary care")

    # Inside labels for segments large enough to fit
    for i, (bar_s, bar_p, spec_pct, pc_pct) in enumerate(
            zip(bar_spec, bar_pc, [us_spec, oecd_spec], [us_pc, oecd_pc])):
        # Specialist label inside bottom segment
        ax.text(bar_s.get_x() + bar_s.get_width() / 2,
                spec_pct * 50,
                f"{spec_pct*100:.0f}%\nSpecialists",
                ha="center", va="center",
                color=WHITE, fontsize=11, fontweight="bold")
        # Primary care label inside top segment
        ax.text(bar_p.get_x() + bar_p.get_width() / 2,
                spec_pct * 100 + pc_pct * 50,
                f"{pc_pct*100:.0f}%\nPrimary Care",
                ha="center", va="center",
                color=WHITE, fontsize=11, fontweight="bold")

    # X axis labels
    ax.set_xticks(x_pos)
    ax.set_xticklabels(
        ["US (BLS FTE basis)\n777,420 total FTEs",
         "OECD-18 median\n(Health at a Glance 2025)"],
        color=WHITE, fontsize=10
    )
    ax.set_ylabel("Share of physician workforce (%)", color=WHITE, fontsize=9.5)
    ax.set_ylim(0, 115)
    ax.tick_params(axis="y", colors=WHITE, labelsize=9)
    ax.tick_params(axis="x", colors=WHITE)
    for spine in ax.spines.values():
        spine.set_edgecolor(LTGRAY)
    ax.grid(axis="y", color=LTGRAY, alpha=0.20, linewidth=0.6, zorder=0)

    # COGME label -- to the right of the dashed line
    ax.text(1.28, cogme_target_pc * 100 + 1.5,
            f"COGME target: {cogme_target_pc*100:.0f}% PC",
            color=GOLD, fontsize=9, fontweight="bold", va="bottom", ha="center")

    # Legend
    legend_handles = [
        mpatches.Patch(color=RED,  label="Specialists", alpha=0.85),
        mpatches.Patch(color=TEAL, label="Primary Care / GP", alpha=0.90),
        plt.Line2D([0], [0], color=GOLD, linewidth=2, linestyle="--",
                   label="COGME 45% primary care target"),
    ]
    ax.legend(handles=legend_handles, loc="upper left",
              fontsize=8.5, framealpha=0.85,
              facecolor=NAVY, edgecolor=LTGRAY, labelcolor=WHITE)

    ax.set_title("US Physician Workforce: More Specialists, Fewer Primary Care",
                 color=WHITE, fontsize=13, fontweight="bold", pad=10)

    # Note: AAMC headcount basis differs
    footnote = (
        "Source: BLS OEWS May 2024 (FTE basis); OECD Health at a Glance 2025 Indicator 8.5.\n"
        "Note: AAMC headcount basis shows 65.8% specialist / 34.2% primary care (different denominator).\n"
        "BLS FTE basis (72/28) used in Component B of savings computation."
    )
    fig.text(0.10, 0.01, footnote, color=LTGRAY, fontsize=6.5, va="bottom", ha="left")

    plt.subplots_adjust(left=0.10, right=0.90, top=0.90, bottom=0.20)
    fig.savefig(outpath, dpi=150, facecolor=NAVY, bbox_inches=None)
    plt.close(fig)
    print(f"Saved {outpath}")


# =============================================================================
# CHART 3 -- RVU misvaluation residual by code family
# Shows Medicare + commercial impact of MedPAC June 2025 directional revaluation
# =============================================================================
def generate_chart3_rvu_misvaluation(outpath: Path):
    df = comp_c_df.copy()

    # Filter to families with a non-zero revaluation direction
    actionable = df[df["revaluation_direction"] != "neutral"].copy()

    family_labels = {
        "EM":         "E&M\n(office visits,\npreventive care)",
        "PROC_ORTHO": "Procedural:\nOrthopedics",
        "PROC_CARD":  "Procedural:\nCardiology",
        "PROC_GI":    "Procedural:\nGI",
        "PROC_OPHTH": "Procedural:\nOphthalmology",
    }
    actionable["label"] = actionable["family"].map(lambda x: family_labels.get(x, x))

    # Display value logic:
    #   commercial_savings_usd is already signed correctly in the data:
    #     Downward revaluation (procedural) => positive value (payers save)
    #     Upward revaluation (E&M) => negative value (E&M is already negative in CSV = cost to payers)
    #   So we use the raw value directly -- no sign flip needed.
    actionable["display_val_bil"] = actionable["commercial_savings_usd"] / 1e9

    # Sort from most negative to most positive (left to right)
    plot_df = actionable.sort_values("display_val_bil").reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=100)
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)

    x_pos = np.arange(len(plot_df))
    colors = [RED if v < 0 else TEAL for v in plot_df["display_val_bil"]]

    bars = ax.bar(x_pos, plot_df["display_val_bil"], color=colors,
                  width=0.55, zorder=3)

    # Zero baseline
    ax.axhline(0, color=LTGRAY, linewidth=1.2, zorder=4)

    # Value labels outside each bar (above positive, below negative)
    for bar, val in zip(bars, plot_df["display_val_bil"]):
        sign = "+" if val >= 0 else "-"
        label_text = f"{sign}${abs(val):.2f}B"
        y_offset = 0.05 if val >= 0 else -0.05
        va_pos   = "bottom" if val >= 0 else "top"
        ax.text(bar.get_x() + bar.get_width() / 2,
                val + y_offset,
                label_text, ha="center", va=va_pos,
                color=WHITE, fontsize=10, fontweight="bold")

    ax.set_xticks(x_pos)
    ax.set_xticklabels(plot_df["label"], color=WHITE, fontsize=9, ha="center",
                       multialignment="center")
    ax.tick_params(axis="y", colors=WHITE, labelsize=9)
    ax.tick_params(axis="x", colors=WHITE, pad=6)
    for spine in ax.spines.values():
        spine.set_edgecolor(LTGRAY)
    ax.grid(axis="y", color=LTGRAY, alpha=0.20, linewidth=0.6, zorder=0)
    ax.set_ylabel("Net commercial impact ($ billions)", color=WHITE, fontsize=9.5)
    # Set ylim to ensure bar labels have headroom above and below
    max_val = plot_df["display_val_bil"].max()
    min_val = plot_df["display_val_bil"].min()
    ax.set_ylim(min_val * 1.22, max_val * 1.28)

    # Direction labels in a box to the side (not overlapping bars)
    # Legend-style explanation -- placed in clear space in the center-lower portion
    # (below zero line, above the x-axis labels, between bars 1 and 3)
    legend_handles = [
        mpatches.Patch(color=RED,  label="Cost to payers: E&M revalued up\n(primary care pays more)"),
        mpatches.Patch(color=TEAL, label="Savings: Procedural codes revalued down\n(payers save on specialist claims)"),
    ]
    ax.legend(handles=legend_handles, loc="lower center",
              fontsize=7.5, framealpha=0.85, ncol=2,
              facecolor=NAVY, edgecolor=LTGRAY, labelcolor=WHITE)

    ax.set_title("RVU Misvaluation: Which Code Families Would Shift Under Reform",
                 color=WHITE, fontsize=12, fontweight="bold", pad=18)

    # Subtitle placed with enough gap below title (using suptitle + title approach)
    ax.text(0.5, 1.025,
            "Medicare PFS is budget-neutral by statute. Commercial cascade (3.2x procedural; 1.4x E&M) drives real savings.",
            transform=ax.transAxes, color=LTGRAY, fontsize=7.5, ha="center", va="bottom")

    footnote = (
        "Source: CMS PFS RVU CY2025 + Medicare Physician and Other Practitioners by Geography and Service PUF CY2024\n"
        "+ MedPAC June 2025 Report Ch 1 directional revaluation. Net commercial savings: $2.32B recoverable (post-overlap)."
    )
    fig.text(0.10, 0.01, footnote, color=LTGRAY, fontsize=6.5, va="bottom", ha="left")

    plt.subplots_adjust(left=0.10, right=0.97, top=0.87, bottom=0.30)
    fig.savefig(outpath, dpi=150, facecolor=NAVY, bbox_inches=None)
    plt.close(fig)
    print(f"Saved {outpath}")


# =============================================================================
# CHART 4 -- GME allocation vs COGME target
# Stacked bar: current allocation, 2024 CAA expansion, COGME target
# =============================================================================
def generate_chart4_gme_allocation(outpath: Path):
    # Data (approximate from AAMC Report on Residents 2024 + CAA 2024 reauthorization)
    categories = [
        "Current Medicare GME\n(~132,000 slots/yr)",
        "2024 CAA Expansion\n(+200 new slots)",
        "COGME 45%\nTarget (illustrative)",
    ]

    # Current: ~30% primary care, 70% specialty
    current_pc_pct   = 30.0
    current_spec_pct = 70.0

    # 2024 CAA: 70% of new slots to primary care + psychiatry
    caa_pc_pct   = 70.0
    caa_spec_pct = 30.0

    # COGME target: 45% primary care
    cogme_pc_pct   = 45.0
    cogme_spec_pct = 55.0

    pc_vals   = [current_pc_pct,   caa_pc_pct,   cogme_pc_pct]
    spec_vals = [current_spec_pct, caa_spec_pct, cogme_spec_pct]

    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=100)
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)

    x_pos = np.arange(len(categories))
    width = 0.45

    bar_spec = ax.bar(x_pos, spec_vals, width,
                      color=RED, alpha=0.85, label="Specialty residency slots", zorder=3)
    bar_pc   = ax.bar(x_pos, pc_vals,   width,
                      bottom=spec_vals,
                      color=TEAL, alpha=0.90, label="Primary care residency slots", zorder=3)

    # Labels inside bars
    for bar_s, bar_p, sv, pv in zip(bar_spec, bar_pc, spec_vals, pc_vals):
        # Specialty label
        if sv >= 8:
            ax.text(bar_s.get_x() + bar_s.get_width() / 2,
                    sv / 2,
                    f"{sv:.0f}%",
                    ha="center", va="center",
                    color=WHITE, fontsize=12, fontweight="bold")
        # Primary care label
        if pv >= 8:
            ax.text(bar_p.get_x() + bar_p.get_width() / 2,
                    sv + pv / 2,
                    f"{pv:.0f}%",
                    ha="center", va="center",
                    color=WHITE, fontsize=12, fontweight="bold")

    ax.set_xticks(x_pos)
    ax.set_xticklabels(categories, color=WHITE, fontsize=9.5)
    ax.set_ylabel("Share of residency slots (%)", color=WHITE, fontsize=9.5)
    ax.set_ylim(0, 120)
    ax.tick_params(axis="y", colors=WHITE, labelsize=9)
    ax.tick_params(axis="x", colors=WHITE)
    for spine in ax.spines.values():
        spine.set_edgecolor(LTGRAY)
    ax.grid(axis="y", color=LTGRAY, alpha=0.20, linewidth=0.6, zorder=0)

    # Annotation: gap to COGME target from current
    gap_label = "Gap: 15pp to\nCOGME target"
    ax.annotate(gap_label,
                xy=(2, cogme_pc_pct + cogme_spec_pct),
                xytext=(2.35, 108),
                color=GOLD, fontsize=8.5, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=GOLD, connectionstyle="arc3,rad=0.1"),
                ha="center")

    legend_handles = [
        mpatches.Patch(color=TEAL, label="Primary care residency slots", alpha=0.90),
        mpatches.Patch(color=RED,  label="Specialty residency slots",   alpha=0.85),
    ]
    # Place legend inside the data area, lower-left, below the legend title
    ax.legend(handles=legend_handles, loc="lower left",
              fontsize=8.5, framealpha=0.85,
              facecolor=NAVY, edgecolor=LTGRAY, labelcolor=WHITE)

    ax.set_title("Federal GME Spending: $21B, Allocated for the Wrong Workforce",
                 color=WHITE, fontsize=12, fontweight="bold", pad=12)

    footnote = (
        "Source: AAMC Report on Residents 2024; 2024 Consolidated Appropriations Act (CAA) Medicare GME\n"
        "expansion; COGME recommendations. Medicare DGME outlays ~$15B + IME ~$6B = ~$21B annually."
    )
    fig.text(0.10, 0.01, footnote, color=LTGRAY, fontsize=6.5, va="bottom", ha="left")

    plt.subplots_adjust(left=0.10, right=0.85, top=0.92, bottom=0.20)
    fig.savefig(outpath, dpi=150, facecolor=NAVY, bbox_inches=None)
    plt.close(fig)
    print(f"Saved {outpath}")


# =============================================================================
# CHART 5 -- Cumulative Savings Tracker (through Issue #14)
# =============================================================================
def generate_chart5_savings_tracker(outpath: Path):
    issues = [
        ("#1\nOTC Drugs",      0.6),
        ("#2\nDrug Pricing",   25.0),
        ("#3\nHospital Px",    73.0),
        ("#4\nPBMs",           30.0),
        ("#5\nAdmin Waste",   200.0),
        ("#6\nSupply Waste",   28.0),
        ("#7\nGLP-1",          40.0),
        ("#8\nDenial Mach.",   32.0),
        ("#9\nEmployer",        6.6),
        ("#10\nProcedures",     7.6),
        ("#11\nMA Overpay",    28.0),
        ("#12\nConsol. Tax",   13.0),
        ("#13\nNonprofit",      5.4),
        ("#14\nSpec. Tax",     27.6),
    ]
    labels_i = [x[0] for x in issues]
    values_i = [x[1] for x in issues]
    total_b  = sum(values_i)  # 516.8
    gap_b    = 3240.0         # $3.24T

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5.5), dpi=100,
                                   gridspec_kw={"width_ratios": [3, 1], "wspace": 0.48})
    fig.patch.set_facecolor(NAVY)
    ax1.set_facecolor(NAVY)
    ax2.set_facecolor(NAVY)

    pct = total_b / gap_b * 100

    fig.suptitle(
        f"Cumulative Savings Identified: ${total_b:.1f}B  ({pct:.1f}% of US-Japan Gap)",
        color=WHITE, fontsize=11.5, fontweight="bold", y=0.98
    )

    # Left panel: per-issue bars
    bar_colors_i = [RED if lbl.startswith("#14") else TEAL for lbl in labels_i]
    bars = ax1.bar(range(len(issues)), values_i, color=bar_colors_i, zorder=3, width=0.7)

    # Value labels: inside large bars, above small bars
    for bar, val in zip(bars, values_i):
        h = bar.get_height()
        if h >= 25:
            ax1.text(bar.get_x() + bar.get_width() / 2, h / 2,
                     f"${val:.0f}B", ha="center", va="center",
                     color=WHITE, fontsize=7.5, fontweight="bold")
        else:
            ax1.text(bar.get_x() + bar.get_width() / 2, h + 3,
                     f"${val:.0f}B", ha="center", va="bottom",
                     color=WHITE, fontsize=7, fontweight="bold")

    # X-tick labels (rotated to avoid overlap)
    short_names = ["OTC", "Drug Px", "Hosp Px", "PBMs", "Admin",
                   "Supply", "GLP-1", "Denial", "Employer", "Procedure",
                   "MA", "Consol.", "Nonprofit", "Spec Tax"]
    xtick_labels = [f"#{i+1} {s}" for i, s in enumerate(short_names)]
    ax1.set_xticks(range(len(issues)))
    ax1.set_xticklabels(xtick_labels, color=WHITE, fontsize=7.5, rotation=35, ha="right")
    ax1.set_ylabel("Savings ($B)", color=WHITE, fontsize=9)
    ax1.tick_params(axis="y", colors=WHITE, labelsize=8.5)
    ax1.tick_params(axis="x", colors=WHITE, pad=2)
    for spine in ax1.spines.values():
        spine.set_edgecolor(LTGRAY)
    ax1.grid(axis="y", color=LTGRAY, alpha=0.2, linewidth=0.6)
    ax1.set_ylim(0, 240)
    ax1.set_title("Per-Issue Savings", color=WHITE, fontsize=10, pad=6)

    # Right panel: cumulative gauge
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
        0.02, 0.01,
        "Sources: Published Issues #1-#14. Full-scale gap: CMS NHE 2024 + OECD Health at a Glance 2025 ($3.24T).",
        color=LTGRAY, fontsize=6.5, va="bottom", ha="left"
    )

    plt.subplots_adjust(bottom=0.24, left=0.08, right=0.97, top=0.85)
    fig.savefig(outpath, dpi=150, facecolor=NAVY, bbox_inches=None)
    plt.close(fig)
    print(f"Saved {outpath}")


# =============================================================================
# HERO IMAGE -- hero_cover.png (2184x1572 @ 150dpi = figsize 14.56x10.48 @ 100dpi)
# Safe zone: center 62% wide x 52% tall
# =============================================================================
def generate_hero(outpath: Path):
    FW, FH = 14.56, 10.48
    fig = plt.figure(figsize=(FW, FH), dpi=100)
    fig.patch.set_facecolor(NAVY)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, FW)
    ax.set_ylim(0, FH)
    ax.axis("off")
    ax.set_facecolor(NAVY)

    # Subtle background grid
    for gx in np.arange(0, FW + 1, 1.0):
        ax.axvline(gx, color=WHITE, alpha=0.03, linewidth=0.5)
    for gy in np.arange(0, FH + 1, 1.0):
        ax.axhline(gy, color=WHITE, alpha=0.03, linewidth=0.5)

    CX = FW / 2   # 7.28
    # Safe zone bounds (62% wide x 52% tall, centered)
    SZ_X_LO = CX - FW * 0.31   # ~2.73
    SZ_X_HI = CX + FW * 0.31   # ~11.83
    SZ_Y_LO = FH * 0.24         # ~2.52
    SZ_Y_HI = FH * 0.76         # ~7.96

    # -- Series banner (top-center, inside safe zone) -------------------------
    banner_y = SZ_Y_HI + 0.20
    ax.text(CX, banner_y,
            "THE AMERICAN HEALTHCARE CONUNDRUM",
            color=RED, fontsize=22, fontweight="bold",
            ha="center", va="center",
            fontfamily="DejaVu Sans")

    ax.text(CX, banner_y - 0.65,
            "ISSUE #14",
            color=GOLD, fontsize=18, fontweight="bold",
            ha="center", va="center",
            fontfamily="DejaVu Sans")

    # Red rule
    rule_y = banner_y - 1.10
    ax.plot([SZ_X_LO, SZ_X_HI], [rule_y, rule_y], color=RED, linewidth=2.5)

    # -- Main hook (inside safe zone) ----------------------------------------
    hook_y = rule_y - 1.25
    ax.text(CX, hook_y,
            "$28 BILLION",
            color=GOLD, fontsize=72, fontweight="bold",
            ha="center", va="center",
            fontfamily="DejaVu Sans")

    # -- Sub-headline --------------------------------------------------------
    sub_y = hook_y - 1.50
    ax.text(CX, sub_y,
            "The Specialist Tax",
            color=WHITE, fontsize=36, fontweight="bold",
            ha="center", va="center",
            fontfamily="DejaVu Sans")

    # -- Supporting comparison line ------------------------------------------
    comp_y = sub_y - 0.95
    ax.text(CX, comp_y,
            "US specialists earn 2-3x OECD-18 peer nations",
            color=TEAL, fontsize=18,
            ha="center", va="center",
            fontfamily="DejaVu Sans")

    # -- Stats bar (bottom of safe zone) -------------------------------------
    stats_y = SZ_Y_LO + 0.15
    stats_text = (
        "777K PHYSICIAN FTEs  ·  OECD-18 PEER COMPARISON  ·  "
        "RUC ADMINISTERED PRICES  ·  $516.8B TOTAL IDENTIFIED"
    )
    ax.text(CX, stats_y,
            stats_text,
            color=LTGRAY, fontsize=10.5,
            ha="center", va="center",
            fontfamily="DejaVu Sans")

    fig.savefig(outpath, dpi=150, facecolor=NAVY, bbox_inches=None)
    plt.close(fig)
    print(f"Saved {outpath}")


# =============================================================================
# MAIN
# =============================================================================
if __name__ == "__main__":
    generate_chart1_oecd18_comp(FIGURES / "chart1_oecd18_comp.png")
    generate_chart2_workforce_mix(FIGURES / "chart2_workforce_mix.png")
    generate_chart3_rvu_misvaluation(FIGURES / "chart3_rvu_misvaluation.png")
    generate_chart4_gme_allocation(FIGURES / "chart4_gme_allocation.png")
    generate_chart5_savings_tracker(FIGURES / "chart5_savings_tracker.png")
    generate_hero(FIGURES / "hero_cover.png")

    print("\nAll 6 PNGs generated.")
    print(f"Figures directory: {FIGURES}")
    for f in sorted(FIGURES.glob("*.png")):
        print(f"  {f.name}: {f.stat().st_size:,} bytes")
