"""
Issue #18 -- Coding for Dollars
Single entry-point chart generator.

Wipes figures/*.png first (preserving hero_cover.png by name),
then regenerates all 5 charts + hero image.

Usage:
    cd issue_18/
    python3 generate_all_charts.py

Rules enforced:
- figsize <= (10, 6) at dpi=100; save at dpi=150
- plt.close(fig) after every savefig
- Relative paths via Path(__file__).resolve().parent
- No hardcoded /sessions/... paths
- Dollar signs escaped as needed in LaTeX-off mode
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import numpy as np

# ── Paths ────────────────────────────────────────────────────────────────────
HERE    = Path(__file__).resolve().parent
RESULTS = HERE / "results"
FIGURES = HERE / "figures"
FIGURES.mkdir(exist_ok=True)

# ── Wipe existing PNGs (preserve hero by re-saving it last) ──────────────────
for _f in FIGURES.glob("*.png"):
    try:
        _f.unlink()
    except PermissionError:
        pass

# ── Brand colours ─────────────────────────────────────────────────────────────
NAVY   = "#1A1F2E"
TEAL   = "#0E8A72"
RED    = "#B7182A"
GOLD   = "#D4AF37"
WHITE  = "#F8F8F6"
LGRAY  = "#8899AA"
ORANGE = "#E07030"
BG2    = "#2A3048"

plt.rcParams.update({
    "font.family":       "DejaVu Sans",
    "figure.facecolor":  NAVY,
    "axes.facecolor":    NAVY,
    "savefig.facecolor": NAVY,
    "text.color":        WHITE,
    "axes.labelcolor":   WHITE,
    "xtick.color":       WHITE,
    "ytick.color":       WHITE,
    "axes.edgecolor":    LGRAY,
    "grid.color":        BG2,
    "grid.linewidth":    0.6,
    "text.usetex":       False,
})

# ══════════════════════════════════════════════════════════════════════════════
# Load data from results/
# ══════════════════════════════════════════════════════════════════════════════
with open(RESULTS / "savings_estimate.json") as _fh:
    EST = json.load(_fh)

# drg_complexity_trend.csv
TREND_ROWS = []
with open(RESULTS / "drg_complexity_trend.csv") as _fh:
    for row in csv.DictReader(_fh):
        TREND_ROWS.append({
            "year":         int(row["fiscal_year"]),
            "fisher":       float(row["growth_fisher"]),
            "caseshift_idx": float(row["caseshift_index"]),
        })

# risk_score_counterfactual.csv
RISK_ROWS = []
with open(RESULTS / "risk_score_counterfactual.csv") as _fh:
    for row in csv.DictReader(_fh):
        RISK_ROWS.append({
            "year":       int(row["fiscal_year"]),
            "risk_index": float(row["risk_index"]),
            "risk_growth": float(row["risk_growth_vs_base"]),
        })

# mechanism_specific_upcoding.csv
MECH_ROWS = []
with open(RESULTS / "mechanism_specific_upcoding.csv") as _fh:
    for row in csv.DictReader(_fh):
        MECH_ROWS.append({
            "mechanism":   row["mechanism"],
            "label":       row["label"],
            "base_share":  float(row["base_top_tier_share"]),
            "anch_share":  float(row["anchor_top_tier_share"]),
            "shift_pp":    float(row["top_share_shift_pp"]),
        })

# fca_settlement_panel.csv
FCA_ROWS = []
with open(RESULTS / "fca_settlement_panel.csv") as _fh:
    for row in csv.DictReader(_fh):
        FCA_ROWS.append({
            "case":    row["case_name"],
            "amt_mil": float(row["settlement_amount_mil"]),
            "year":    int(str(row["settlement_date"]).split("-")[0]),
        })


# ══════════════════════════════════════════════════════════════════════════════
# CHART 1 -- Coded Severity vs Measured Sickness (2013-2024 dual-line)
# ══════════════════════════════════════════════════════════════════════════════

def chart1_cmi_vs_hcc():
    """
    Dual-line chart: Fixed-weight Fisher case-mix migration index (teal)
    vs FFS HCC risk-score index (gold), 2013-2024, both indexed to 1.000.
    Shaded band between lines = raw coding-intensity signal.
    Vertical dashed marker at 2020 labeled 'COVID acuity step'.
    """
    years_t = [r["year"]         for r in TREND_ROWS]
    fisher   = [r["caseshift_idx"] for r in TREND_ROWS]   # index (1.000 = 2013)

    years_r = [r["year"]       for r in RISK_ROWS]
    risk     = [r["risk_index"] for r in RISK_ROWS]        # index (1.000 = 2013)

    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)

    # Teal: Fisher case-mix index
    ax.plot(years_t, fisher, color=TEAL, linewidth=2.5, marker="o",
            markersize=5, zorder=5, label="Coded severity (Fisher case-mix index)")

    # Gold: HCC risk-score index
    ax.plot(years_r, risk, color=GOLD, linewidth=2.5, marker="s",
            markersize=5, zorder=5, label="Measured sickness (HCC risk-score index)")

    # Shaded band between the two lines (only where Fisher > risk)
    yr_min = min(min(years_t), min(years_r))
    yr_max = max(max(years_t), max(years_r))
    # Use the union of years (both have same range 2013-2024)
    shared_years = sorted(set(years_t) & set(years_r))
    fisher_dict = dict(zip(years_t, fisher))
    risk_dict   = dict(zip(years_r, risk))
    sy   = np.array(shared_years)
    sf   = np.array([fisher_dict[y] for y in shared_years])
    sr   = np.array([risk_dict[y]   for y in shared_years])
    ax.fill_between(sy, sr, sf, where=(sf > sr),
                    alpha=0.18, color=TEAL, label="Coding-intensity signal (gap)")

    # COVID marker at 2020
    ax.axvline(2020, color=RED, linestyle="--", linewidth=1.2, zorder=4, alpha=0.85)
    # Place label above the shaded band, in clear space near the top of the axis
    ax.text(2020.1, 1.205,
            "COVID\nacuity step",
            fontsize=8, color=RED, va="center", ha="left",
            bbox=dict(boxstyle="round,pad=0.18", facecolor=NAVY, edgecolor=RED,
                      linewidth=0.6, alpha=0.95),
            zorder=8)

    # Endpoint labels (right side)
    # Fisher ends at index 1.155 in 2024
    final_fisher = fisher[-1]
    final_risk   = risk[-1]
    # Fisher label: placed above end point with offset to avoid overlap
    ax.text(2024 + 0.15, final_fisher + 0.003,
            f"+{(final_fisher-1)*100:.1f}%",
            fontsize=9, color=TEAL, fontweight="bold", va="bottom", ha="left", zorder=7,
            bbox=dict(boxstyle="round,pad=0.15", facecolor=NAVY, edgecolor="none", alpha=0.9))
    # Risk label: placed below end point
    ax.text(2024 + 0.15, final_risk - 0.003,
            f"+{(final_risk-1)*100:.1f}%",
            fontsize=9, color=GOLD, fontweight="bold", va="top", ha="left", zorder=7,
            bbox=dict(boxstyle="round,pad=0.15", facecolor=NAVY, edgecolor="none", alpha=0.9))

    ax.set_xlim(2012.5, 2025.5)
    ax.set_ylim(0.97, 1.23)
    ax.set_xticks(range(2013, 2025))
    ax.set_xticklabels([str(y) for y in range(2013, 2025)],
                       fontsize=8, color=WHITE, rotation=45, ha="right")
    ax.set_yticks([1.00, 1.04, 1.08, 1.12, 1.16, 1.20])
    ax.set_yticklabels(["1.000", "1.040", "1.080", "1.120", "1.160", "1.200"],
                       fontsize=8.5)
    ax.set_ylabel("Index (2013 = 1.000)", fontsize=10, labelpad=5)

    ax.set_title("Coded Severity vs. Measured Sickness, Medicare FFS 2013-2024",
                 fontsize=11, color=WHITE, pad=10)

    ax.legend(fontsize=8.5, loc="upper left",
              framealpha=0.88, facecolor=NAVY, edgecolor=LGRAY, labelcolor=WHITE)
    ax.grid(True, alpha=0.25, zorder=0)
    ax.set_axisbelow(True)

    footnote = (
        "Fixed-weight Fisher case-mix index: DRG weights held at DY2024 values;\n"
        "geometric mean of Laspeyres (2013-anchor) and Paasche (2024-anchor). "
        "HCC risk-score index: FFS beneficiary-weighted avg HCC score (CMS by-Provider PUF).\n"
        "Source: CMS Medicare Inpatient DRG PUF DY2013-DY2024; CMS by-Provider PUF DY2013-DY2024."
    )
    fig.text(0.09, 0.01, footnote, fontsize=5.5, color=LGRAY, ha="left", va="bottom")
    fig.subplots_adjust(top=0.88, bottom=0.22, left=0.09, right=0.91)

    out = FIGURES / "chart1_cmi_vs_hcc.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Saved: {out}")
    return out


# ══════════════════════════════════════════════════════════════════════════════
# CHART 2 -- Top-Tier MCC Share by Condition Family, 2013 vs 2024
# ══════════════════════════════════════════════════════════════════════════════

def chart2_condition_families():
    """
    Grouped bar chart: six condition families (heart failure excluded).
    Gold bar = 2013 top-tier share; Teal bar = 2024 top-tier share.
    Percentage-point shift labeled above each group.
    Heart failure excluded note at bottom.
    """
    # Exclude heart_failure per the draft
    rows = [r for r in MECH_ROWS if r["mechanism"] != "heart_failure"]
    # Sort by shift descending for visual impact
    rows.sort(key=lambda r: r["shift_pp"], reverse=True)

    # Short display labels (strip the DRG code detail)
    DISPLAY_LABELS = {
        "sepsis":           "Severe\nSepsis",
        "simple_pneumonia": "Simple\nPneumonia",
        "copd":             "COPD",
        "nutrition_metab":  "Nutrition /\nMetabolic",
        "kidney_uti":       "Kidney\n& UTI",
        "renal_failure":    "Renal\nFailure",
        "cellulitis":       "Cellulitis",
    }

    # Take top 6 by shift (excluding cellulitis if we have 7)
    rows = rows[:6]

    labels = [DISPLAY_LABELS.get(r["mechanism"], r["mechanism"]) for r in rows]
    base_shares = [r["base_share"] * 100 for r in rows]   # convert to %
    anch_shares = [r["anch_share"] * 100 for r in rows]
    shifts      = [r["shift_pp"]         for r in rows]

    n = len(rows)
    x = np.arange(n)
    bar_width = 0.32

    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)

    bars_2013 = ax.bar(x - bar_width / 2, base_shares, bar_width,
                       color=GOLD, alpha=0.88, label="2013 share", zorder=3,
                       edgecolor=WHITE, linewidth=0.4)
    bars_2024 = ax.bar(x + bar_width / 2, anch_shares, bar_width,
                       color=TEAL, alpha=0.88, label="2024 share", zorder=3,
                       edgecolor=WHITE, linewidth=0.4)

    # Value labels inside bars (or above if bar is short)
    for bar, val in zip(bars_2013, base_shares):
        y_pos = bar.get_height() / 2 if bar.get_height() > 8 else bar.get_height() + 1.5
        va_str = "center" if bar.get_height() > 8 else "bottom"
        ax.text(bar.get_x() + bar.get_width() / 2, y_pos,
                f"{val:.0f}%",
                ha="center", va=va_str, fontsize=8.5, color=NAVY if bar.get_height() > 8 else WHITE,
                fontweight="bold", zorder=5)

    for bar, val in zip(bars_2024, anch_shares):
        y_pos = bar.get_height() / 2 if bar.get_height() > 8 else bar.get_height() + 1.5
        va_str = "center" if bar.get_height() > 8 else "bottom"
        ax.text(bar.get_x() + bar.get_width() / 2, y_pos,
                f"{val:.0f}%",
                ha="center", va=va_str, fontsize=8.5, color=NAVY if bar.get_height() > 8 else WHITE,
                fontweight="bold", zorder=5)

    # Shift label above each group -- centered between paired bars, well above tallest bar
    for i, (shift, b13, b24) in enumerate(zip(shifts, base_shares, anch_shares)):
        top = max(b13, b24)
        label_y = top + 4.0
        ax.text(x[i], label_y,
                f"+{shift:.1f} pp",
                ha="center", va="bottom", fontsize=8.5, color=WHITE, fontweight="bold",
                zorder=6,
                bbox=dict(boxstyle="round,pad=0.15", facecolor=BG2, edgecolor="none", alpha=0.80))

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9, color=WHITE)
    ax.set_ylim(0, 105)
    ax.set_ylabel("Top-Tier MCC Share (%)", fontsize=10, labelpad=5)
    ax.set_title("Top-Tier (MCC) Share by Condition Family, 2013 vs. 2024",
                 fontsize=11, color=WHITE, pad=10)

    ax.legend(fontsize=9, loc="upper right",
              framealpha=0.88, facecolor=NAVY, edgecolor=LGRAY, labelcolor=WHITE)
    ax.grid(True, axis="y", alpha=0.25, zorder=0)
    ax.set_axisbelow(True)

    # Heart failure excluded note moved to footnote area (below the axis, not inside the plot)
    footnote = (
        "Source: CMS Medicare Inpatient DRG by-Provider PUF DY2013 and DY2024. "
        "Top-tier share = fraction of condition-family discharges in highest MS-DRG tier (MCC).\n"
        "Shift in percentage points (pp) shown above each group. "
        "Heart failure not shown: CC/MCC classification changes over this window "
        "make family-level comparison unreliable for 2013-2024."
    )
    fig.text(0.09, 0.01, footnote, fontsize=5.5, color=LGRAY, ha="left", va="bottom")
    fig.subplots_adjust(top=0.88, bottom=0.20, left=0.09, right=0.97)

    out = FIGURES / "chart2_condition_families.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Saved: {out}")
    return out


# ══════════════════════════════════════════════════════════════════════════════
# CHART 3 -- Savings Waterfall: $107B pool -> $1.04B booked
#
# Scale problem: $107B vs $1B on one axis makes the booked bar invisible.
# Solution: TWO-PANEL design.
#   Left panel: funnel/step diagram (labeled steps, no proportional bars)
#               using a funnel-like descending-step layout with labels
#               carrying the numbers.
#   Right panel: zoom-in bar showing the $1.04B booked with
#                floor/ceiling brackets.
# ══════════════════════════════════════════════════════════════════════════════

def chart3_savings_waterfall():
    """
    Two-panel waterfall solving the $107B vs $1B scale problem.
    Left panel: labeled step-funnel (text-forward, no misleading bars).
                All $ signs escaped to avoid matplotlib mathtext.
                No description overflow (descriptions removed from left panel;
                the funnel labels carry the numbers, steps are self-explanatory).
    Right panel: zoom bar with floor/ceiling bracket.
    """
    import math

    pool_full   = EST["ffs_ipps_pool_anchor_full_bil"]          # 107.04
    pool_opnet  = EST["ffs_ipps_pool_operating_netted_bil"]     # 95.27
    gross       = EST["gross_excess_central_bil"]               # 1.905
    after_recv  = round(gross * 0.55, 3)                        # 1.048
    booked      = EST["booked_bil"]                             # 1.045
    floor_v     = EST["range_lo_bil"]                           # 0.726
    ceil_v      = EST["range_hi_bil"]                           # 5.153

    fig, (ax_l, ax_r) = plt.subplots(
        1, 2, figsize=(10, 6), dpi=100,
        gridspec_kw={"width_ratios": [1.4, 1.0], "wspace": 0.35}
    )
    fig.patch.set_facecolor(NAVY)

    # ── Left panel: step-funnel ───────────────────────────────────────────────
    ax_l.set_facecolor(NAVY)
    ax_l.axis("off")
    ax_l.set_xlim(0, 10)
    ax_l.set_ylim(0, 10)

    # Title: avoid $ signs in title to prevent mathtext rendering issues.
    ax_l.set_title("From the 107B Pool to 1.04B Booked:\nThe Coding for Dollars Waterfall",
                   fontsize=10.5, color=WHITE, pad=10, loc="center")

    # Steps: (display_label, value, sub_desc, color)
    steps = [
        ("FFS IPPS Full Pool",    pool_full,  "incl. outlier + capital",   TEAL),
        ("Operating-Netted Pool", pool_opnet, "minus non-scaling add-ons", TEAL),
        ("Gross Coding Excess",   gross,      "Crespin 2.0% x netted pool", TEAL),
        ("After Recoverability",  after_recv, "x 0.55",                    TEAL),
        ("Booked Central",        booked,     "less DOJ/FCA overlap",      GOLD),
    ]

    n_steps = len(steps)
    y_tops = [9.5 - i * (9.5 - 0.3) / n_steps for i in range(n_steps + 1)]

    # Widths: log-proportional so small values are still visible
    log_vals = [math.log10(max(s[1], 0.01)) + 3 for s in steps]
    max_lv   = log_vals[0]
    half_widths = [4.2 * lv / max_lv for lv in log_vals]

    for i, (lbl, val, subdesc, col) in enumerate(steps):
        y_bot   = y_tops[i + 1]
        y_top   = y_tops[i]
        hw      = half_widths[i]
        hw_next = half_widths[i + 1] if i + 1 < len(half_widths) else half_widths[i] * 0.8

        poly_x = [5 - hw, 5 + hw, 5 + hw_next, 5 - hw_next]
        poly_y = [y_top,  y_top,  y_bot,       y_bot]
        ax_l.fill(poly_x, poly_y, color=col, alpha=0.78, zorder=3)
        ax_l.plot(poly_x + [poly_x[0]], poly_y + [poly_y[0]],
                  color=WHITE, linewidth=0.5, zorder=4)

        mid_y   = (y_top + y_bot) / 2
        # Format value -- use unicode dollar sign to avoid mathtext interpretation
        dol = "$"
        val_str = f"{dol}{val:.2f}B" if val < 10 else f"{dol}{val:.1f}B"

        ax_l.text(5, mid_y + 0.20, val_str,
                  ha="center", va="center", fontsize=10.5, color=WHITE,
                  fontweight="bold", zorder=6)
        ax_l.text(5, mid_y - 0.25, lbl,
                  ha="center", va="center", fontsize=7.5, color=WHITE, zorder=6)
        # sub-description: white text inside the trapezoid (LGRAY is too low-contrast on GOLD)
        if subdesc and (y_top - y_bot) > 1.0:
            ax_l.text(5, mid_y - 0.62, subdesc,
                      ha="center", va="center", fontsize=6.0, color=WHITE,
                      style="italic", zorder=6)

    # ── Right panel: zoom bar with range ─────────────────────────────────────
    ax_r.set_facecolor(NAVY)

    y_bar = 2.2
    bar_h = 0.80

    # Track
    ax_r.barh(y_bar, ceil_v * 1.25, height=bar_h, color=BG2, alpha=1.0, zorder=2, left=0)
    # Booked bar
    ax_r.barh(y_bar, booked, height=bar_h, color=GOLD, alpha=0.90, zorder=3, left=0)

    # Floor and ceiling tick marks
    for tick_x in [floor_v, ceil_v]:
        ax_r.plot([tick_x, tick_x],
                  [y_bar - bar_h / 2 - 0.08, y_bar + bar_h / 2 + 0.08],
                  color=WHITE, linewidth=1.8, zorder=5)

    dol = "$"
    # Booked value label: placed ABOVE the gold bar with a contrasting bbox to ensure
    # full legibility regardless of what is underneath (gold bar or dark range band).
    ax_r.annotate(f"{dol}{booked:.2f}B booked",
                  xy=(booked, y_bar + bar_h / 2),
                  xytext=(booked / 2, y_bar + bar_h / 2 + 0.50),
                  ha="center", va="bottom", fontsize=9.5, color=WHITE,
                  fontweight="bold", zorder=8,
                  bbox=dict(boxstyle="round,pad=0.18", facecolor=NAVY,
                            edgecolor=GOLD, linewidth=0.8, alpha=0.96),
                  arrowprops=dict(arrowstyle="-", color=GOLD, lw=1.0))

    # Floor label below bar
    ax_r.text(floor_v, y_bar - bar_h / 2 - 0.22,
              f"Floor\n{dol}{floor_v:.2f}B",
              ha="center", va="top", fontsize=8, color=WHITE, zorder=6,
              bbox=dict(boxstyle="round,pad=0.14", facecolor=NAVY, edgecolor=LGRAY,
                        linewidth=0.6, alpha=0.92))

    # Ceiling label above bar
    ax_r.text(ceil_v, y_bar + bar_h / 2 + 0.22,
              f"Ceiling\n{dol}{ceil_v:.2f}B",
              ha="center", va="bottom", fontsize=8, color=WHITE, zorder=6,
              bbox=dict(boxstyle="round,pad=0.14", facecolor=NAVY, edgecolor=LGRAY,
                        linewidth=0.6, alpha=0.92))

    ax_r.set_xlim(0, ceil_v * 1.25)
    ax_r.set_ylim(0.8, 4.0)
    ax_r.set_yticks([])
    ax_r.set_xlabel("USD Billions / year", fontsize=9, labelpad=4)
    ax_r.set_title(f"Booked Central\nwith Floor / Ceiling Range",
                   fontsize=10, color=WHITE, pad=8)
    ax_r.tick_params(axis="x", labelsize=8, labelcolor=WHITE)
    ax_r.grid(True, axis="x", alpha=0.20, zorder=0)
    ax_r.set_axisbelow(True)

    ax_r.text(0.5, 0.055,
              "Ceiling uses cruder risk-net residual\n(over-attributes to coding); see text.",
              transform=ax_r.transAxes,
              ha="center", va="bottom", fontsize=6.5, color=LGRAY, style="italic")

    footnote = (
        "Central: Crespin 2024 (Health Affairs) 2.0% coding-intensity share x $95.3B netted pool"
        " x 0.55 recoverability. Floor: Crespin CI-low (1.7%) x 0.45 recov.\n"
        "Ceiling: Fisher migration (15.5%) net of HCC risk rise (7.8%) = 7.2% residual x 0.75 recov."
        " Left panel: log-proportional funnel (funnel widths for readability, not scale)."
    )
    fig.text(0.04, 0.01, footnote, fontsize=5.5, color=LGRAY, ha="left", va="bottom")
    fig.subplots_adjust(top=0.85, bottom=0.16, left=0.03, right=0.97)

    out = FIGURES / "chart3_savings_waterfall.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Saved: {out}")
    return out


# ══════════════════════════════════════════════════════════════════════════════
# CHART 4 -- Confirmed Fraud vs Gray-Zone Coding Intensity (two-panel)
#
# Scale: FCA settlements ~$12.5M/yr vs booked $1.04B/yr (~83x).
# Solution: different x-axis scales per panel, clearly labeled.
# ══════════════════════════════════════════════════════════════════════════════

def chart4_fraud_vs_grayzone():
    """
    Two-panel comparison.
    Left panel: FCA confirmed hospital DRG-upcoding settlements 2018-2025.
                Stacked horizontal bar by case + $12.5M/yr annualized label.
    Right panel: Booked gray-zone coding intensity $1.04B/yr.
                 Single bar with range bracket.
    Different x-scales per panel; panels clearly titled.
    """
    # Build FCA data sorted by year ascending; label maps by defendant name
    fca_data = sorted(FCA_ROWS, key=lambda r: r["year"])
    fca_amts_s = [r["amt_mil"] for r in fca_data]
    fca_total  = sum(fca_amts_s)
    fca_annual = EST["fca_confirmed_annualized_bil"] * 1000  # $M = 12.5

    # Generate short labels from the sorted defendant names
    def short_label(case_str, year):
        if "Prime" in case_str:
            return f"Prime Healthcare\n({year})"
        if "IPC" in case_str or "Hospitalist" in case_str:
            return f"IPC Hospitalists\n({year})"
        if "Silver" in case_str:
            return f"Silver Lake Hosp.\n({year})"
        return f"{case_str[:20]}\n({year})"

    short_labels = [short_label(r["case"], r["year"]) for r in fca_data]

    booked  = EST["booked_bil"]         # 1.045
    floor_v = EST["range_lo_bil"]       # 0.726
    ceil_v  = EST["range_hi_bil"]       # 5.153

    fig, (ax_l, ax_r) = plt.subplots(
        1, 2, figsize=(10, 6), dpi=100,
        gridspec_kw={"width_ratios": [1.1, 1.0], "wspace": 0.45}
    )
    fig.patch.set_facecolor(NAVY)

    # ── Left panel: FCA settlements ───────────────────────────────────────────
    ax_l.set_facecolor(NAVY)
    y_pos = np.arange(len(short_labels))
    colors_fca = [RED, RED, RED]

    bars = ax_l.barh(y_pos, fca_amts_s, height=0.52,
                     color=colors_fca[:len(fca_amts_s)], alpha=0.88, zorder=3,
                     edgecolor=WHITE, linewidth=0.4)

    for bar, val in zip(bars, fca_amts_s):
        ax_l.text(val + 1.5, bar.get_y() + bar.get_height() / 2,
                  f"${val:.1f}M",
                  va="center", ha="left", fontsize=8.5, color=WHITE, fontweight="bold", zorder=5)

    ax_l.set_yticks(y_pos)
    ax_l.set_yticklabels(short_labels, fontsize=8, color=WHITE)
    ax_l.set_xlim(0, max(fca_amts_s) * 2.2)
    ax_l.set_xlabel("Settlement Amount (USD Millions)", fontsize=9, labelpad=4)
    ax_l.set_title("DOJ FCA-Confirmed\nHospital DRG Upcoding\n(2018-2025 Settlements)",
                   fontsize=9.5, color=WHITE, pad=8)
    ax_l.grid(True, axis="x", alpha=0.22, zorder=0)
    ax_l.set_axisbelow(True)

    # Total and annualized note
    ax_l.text(0.50, -0.20,
              f"Total: ${fca_total:.0f}M  |  Annualized: ~${fca_annual:.1f}M/yr",
              transform=ax_l.transAxes,
              ha="center", va="top", fontsize=8, color=LGRAY, style="italic")

    # ── Right panel: gray-zone booked ─────────────────────────────────────────
    ax_r.set_facecolor(NAVY)

    y_bar = 1.5
    bar_h = 0.65

    # Track
    ax_r.barh(y_bar, ceil_v * 1.22, height=bar_h, color=BG2, alpha=1.0, zorder=2, left=0)
    # Booked bar
    ax_r.barh(y_bar, booked, height=bar_h, color=TEAL, alpha=0.90, zorder=3, left=0)

    # Floor and ceiling ticks
    for tick_x in [floor_v, ceil_v]:
        ax_r.plot([tick_x, tick_x],
                  [y_bar - bar_h / 2 - 0.05, y_bar + bar_h / 2 + 0.05],
                  color=WHITE, linewidth=1.5, zorder=5)

    # Booked label inside bar
    ax_r.text(booked / 2, y_bar, f"${booked:.2f}B/yr",
              ha="center", va="center", fontsize=10.5, color=WHITE,
              fontweight="bold", zorder=7)

    ax_r.text(floor_v, y_bar - bar_h / 2 - 0.20,
              f"Floor ${floor_v:.2f}B",
              ha="center", va="top", fontsize=7.5, color=WHITE, zorder=6,
              bbox=dict(boxstyle="round,pad=0.12", facecolor=NAVY, edgecolor=LGRAY,
                        linewidth=0.5, alpha=0.90))
    ax_r.text(ceil_v, y_bar + bar_h / 2 + 0.20,
              f"Ceiling ${ceil_v:.2f}B",
              ha="center", va="bottom", fontsize=7.5, color=WHITE, zorder=6,
              bbox=dict(boxstyle="round,pad=0.12", facecolor=NAVY, edgecolor=LGRAY,
                        linewidth=0.5, alpha=0.90))

    ax_r.set_xlim(0, ceil_v * 1.22)
    ax_r.set_ylim(0.5, 2.8)
    ax_r.set_yticks([])
    ax_r.set_xlabel("USD Billions / year", fontsize=9, labelpad=4)
    ax_r.set_title("Booked Gray-Zone\nCoding Intensity\n(Medicare FFS Inpatient, 2024)",
                   fontsize=9.5, color=WHITE, pad=8)
    ax_r.tick_params(axis="x", labelsize=8, labelcolor=WHITE)
    ax_r.grid(True, axis="x", alpha=0.22, zorder=0)
    ax_r.set_axisbelow(True)

    # Comparison note below right panel
    ax_r.text(0.5, -0.20,
              "~83x the confirmed-fraud total\n\"Most of the $1.0B is legal.\"",
              transform=ax_r.transAxes,
              ha="center", va="top", fontsize=8, color=LGRAY, style="italic")

    fig.suptitle(
        "Confirmed Fraud vs. Gray-Zone Coding Intensity (Medicare FFS Inpatient, 2024)",
        fontsize=12, color=WHITE, y=0.955, fontweight="bold"
    )

    footnote = (
        "FCA settlements: DOJ press releases Jan 2024 (Silver Lake $30.6M), Aug 2018 (Prime Healthcare $65M), "
        "Oct 2023 (IPC Hospitalists $4.38M). Annualized over 7-year window.\n"
        "Gray-zone booked: Crespin 2024 (Health Affairs) 2.0% x $95.3B pool x 0.55 recoverability. "
        "Different x-axis scales; see titles."
    )
    fig.text(0.05, 0.01, footnote, fontsize=5.5, color=LGRAY, ha="left", va="bottom")
    fig.subplots_adjust(top=0.80, bottom=0.22, left=0.15, right=0.97)

    out = FIGURES / "chart4_fraud_vs_grayzone.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Saved: {out}")
    return out


# ══════════════════════════════════════════════════════════════════════════════
# CHART 5 -- Savings Tracker (all 18 issues)
# ══════════════════════════════════════════════════════════════════════════════

def chart5_savings_tracker():
    """All 18 issues; Issue #18 highlighted in gold. Running total $542.92B."""
    issues = [
        ("#1",  "OTC Drugs",          0.6),
        ("#2",  "Drug Pricing",       25.0),
        ("#3",  "Hospital Pricing",   73.0),
        ("#4",  "PBM Reform",         30.0),
        ("#5",  "Admin Waste",       200.0),
        ("#6",  "Supply Waste",       28.0),
        ("#7",  "GLP-1 Pricing",      40.0),
        ("#8",  "Denial Machine",     32.0),
        ("#9",  "Employer Trap",       6.6),
        ("#10", "Procedure Mill",      7.6),
        ("#11", "MA Overpayment",     28.0),
        ("#12", "Consolidation Tax",  13.0),
        ("#13", "Nonprofit Lie",       5.4),
        ("#14", "Specialist Tax",     27.6),
        ("#15", "Facility Fee Scam",   2.55),
        ("#16", "Other 100 Drugs",    16.36),
        ("#17", "Part B Premium",      6.17),
        ("#18", "Coding for Dollars",  1.04),
    ]

    nums    = [i[0] for i in issues]
    labels  = [i[1] for i in issues]
    savings = [i[2] for i in issues]

    running_total = 542.92
    target = 3240.0
    pct = running_total / target * 100   # 16.76... -> 16.8%

    fig, (ax_left, ax_right) = plt.subplots(
        1, 2, figsize=(10, 6.5), dpi=100,
        gridspec_kw={"width_ratios": [2, 1], "wspace": 0.52}
    )
    fig.patch.set_facecolor(NAVY)
    fig.subplots_adjust(top=0.88, bottom=0.09, left=0.22, right=0.97)

    # ── Left: per-issue bars ──────────────────────────────────────────────────
    ax_left.set_facecolor(NAVY)
    y_pos = np.arange(len(issues))
    bar_colors = [GOLD if n == "#18" else TEAL for n in nums]
    bars = ax_left.barh(y_pos, savings, color=bar_colors, height=0.68, alpha=0.90, zorder=3)

    ax_left.set_yticks(y_pos)
    ax_left.set_yticklabels([f"{n}  {lbl}" for n, lbl in zip(nums, labels)],
                            fontsize=6.8, color=WHITE)

    max_s = max(savings)
    for i, (bar, val) in enumerate(zip(bars, savings)):
        lbl_txt = f"{val:.1f}B" if val >= 1.0 else f"{val:.2f}B"
        ax_left.text(val + max_s * 0.018, i, lbl_txt,
                     va="center", ha="left", fontsize=7.0, color=WHITE)

    ax_left.set_xlim(0, max_s * 1.38)
    ax_left.set_xlabel("Savings (USD Billions/year)", fontsize=9, labelpad=4)
    ax_left.set_title("Per-Issue Savings, Issues #1-#18", fontsize=10, color=WHITE, pad=7)
    ax_left.grid(True, axis="x", alpha=0.22, zorder=0)
    ax_left.set_axisbelow(True)

    # ── Right: running total — two stacked sub-panels with independent x-scales ──
    # Hide the outer ax_right frame; we'll draw two inset axes inside it.
    ax_right.set_facecolor(NAVY)
    ax_right.axis("off")
    ax_right.set_title("Running Total\n542.92B / 3.24T (16.8%)",
                       fontsize=10, color=WHITE, pad=7)

    # --- Full-scale panel (top half of ax_right) ---
    # bbox_to_anchor in axes fraction: [x0, y0, width, height]
    ax_full = inset_axes(ax_right, width="100%", height="42%",
                         bbox_to_anchor=(0.0, 0.50, 1.0, 0.50),
                         bbox_transform=ax_right.transAxes,
                         loc="lower left", borderpad=0)
    ax_full.set_facecolor(NAVY)
    ax_full.barh(0, target,        height=0.55, color=BG2,  alpha=1.0, zorder=2)
    ax_full.barh(0, running_total, height=0.55, color=TEAL, alpha=0.90, zorder=3)
    ax_full.set_xlim(0, target * 1.05)
    ax_full.set_ylim(-0.55, 0.90)
    ax_full.set_yticks([])
    ax_full.set_xlabel("USD Billions (full scale)", fontsize=7.5, labelpad=3, color=WHITE)
    ax_full.tick_params(axis="x", labelsize=7, labelcolor=WHITE)
    ax_full.set_xticks([0, 1000, 2000, 3000])
    ax_full.set_xticklabels(["0", "1000", "2000", "3000"], fontsize=7, color=WHITE)
    for spine in ["top", "right", "left"]:
        ax_full.spines[spine].set_visible(False)
    ax_full.spines["bottom"].set_color(LGRAY)
    ax_full.grid(True, axis="x", alpha=0.22, zorder=0)
    ax_full.set_axisbelow(True)
    # "Full scale" label on y axis
    ax_full.text(-0.04, 0, "Full scale\nvs 3.24T", transform=ax_full.transAxes,
                 fontsize=7.5, color=WHITE, ha="right", va="center", rotation=0)
    # Running total annotation above full-scale bar
    ax_full.text(running_total / 2.0, 0.45,
                 f"{running_total:.2f}B = {pct:.1f}%",
                 va="bottom", ha="center", fontsize=8.5, color=WHITE, fontweight="bold",
                 zorder=6,
                 bbox=dict(boxstyle="round,pad=0.20", facecolor=NAVY, alpha=0.88,
                           edgecolor=TEAL, linewidth=0.8))

    # --- Zoom panel (bottom half of ax_right, own 0-100B axis) ---
    zoom_max = 100.0
    ax_zoom = inset_axes(ax_right, width="100%", height="42%",
                         bbox_to_anchor=(0.0, 0.0, 1.0, 0.42),
                         bbox_transform=ax_right.transAxes,
                         loc="lower left", borderpad=0)
    ax_zoom.set_facecolor(NAVY)
    # Track bar = full 100B window
    ax_zoom.barh(0, zoom_max, height=0.55, color=BG2,  alpha=1.0, zorder=2)
    # Filled bar = min(running_total, 100) = 100 (running_total > 100)
    ax_zoom.barh(0, min(running_total, zoom_max), height=0.55, color=GOLD, alpha=0.90, zorder=3)
    ax_zoom.set_xlim(0, zoom_max * 1.05)
    ax_zoom.set_ylim(-0.55, 0.90)
    ax_zoom.set_yticks([])
    ax_zoom.set_xlabel("USD Billions (0-100B zoom)", fontsize=7.5, labelpad=3, color=WHITE)
    ax_zoom.tick_params(axis="x", labelsize=7, labelcolor=WHITE)
    ax_zoom.set_xticks([0, 25, 50, 75, 100])
    ax_zoom.set_xticklabels(["0", "25", "50", "75", "100"], fontsize=7, color=WHITE)
    for spine in ["top", "right", "left"]:
        ax_zoom.spines[spine].set_visible(False)
    ax_zoom.spines["bottom"].set_color(LGRAY)
    ax_zoom.grid(True, axis="x", alpha=0.22, zorder=0)
    ax_zoom.set_axisbelow(True)
    ax_zoom.text(-0.04, 0, "Zoom:\n0-100B", transform=ax_zoom.transAxes,
                 fontsize=7.5, color=WHITE, ha="right", va="center", rotation=0)
    # Label inside the gold zoom bar (NAVY text on gold bar, centered)
    ax_zoom.text(50.0, 0,
                 "First 100B filled",
                 va="center", ha="center", fontsize=7.5, color=NAVY, fontweight="bold",
                 zorder=6)

    fig.suptitle("AHC Savings Tracker -- After Issue #18",
                 fontsize=12, color=WHITE, y=0.975, fontweight="bold")

    fig.text(0.04, 0.01,
             "Target: 3.24T US-Japan per-capita gap (CMS NHE 2024; OECD 2023). "
             "Issue #18 adds 1.04B. Cumulative: 542.92B (16.8%). "
             "All figures per-year booked savings.",
             fontsize=5.5, color=LGRAY, ha="left", va="bottom")

    out = FIGURES / "chart5_savings_tracker.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Saved: {out}")
    return out


# ══════════════════════════════════════════════════════════════════════════════
# HERO IMAGE -- 1456x1048, safe zone 900x550 centered
# ══════════════════════════════════════════════════════════════════════════════

def chart_hero():
    """
    1456x1048 hero. Navy background, series branding, hook centered
    in ~900x550 safe zone (x: 278-1178, y: 249-799).
    Hook: "+15% CODED vs +8% SICKER" / "$1.0B/year".
    """
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
    # Series branding top-center (within safe zone)
    ax.text(728, 755,
            "THE AMERICAN HEALTHCARE CONUNDRUM",
            fontsize=17, color=RED, ha="center", va="center",
            fontweight="bold", zorder=5)
    ax.text(728, 722,
            "Issue #18",
            fontsize=23, color=GOLD, ha="center", va="center",
            fontweight="bold", zorder=5)

    # Red divider line
    ax.plot([300, 1156], [698, 698], color=RED, linewidth=2.5, zorder=5)

    # Main hook: the coding/sickness gap in large text
    # Two large numbers side by side with comparison operator
    ax.text(500, 605, "+15%",
            fontsize=88, color=TEAL, ha="center", va="center",
            fontweight="bold", zorder=5)
    ax.text(728, 605, "vs",
            fontsize=32, color=LGRAY, ha="center", va="center",
            fontweight="bold", zorder=5)
    ax.text(960, 605, "+8%",
            fontsize=88, color=GOLD, ha="center", va="center",
            fontweight="bold", zorder=5)

    # Labels below the numbers
    ax.text(500, 545, "CODED SEVERITY",
            fontsize=16, color=TEAL, ha="center", va="center",
            fontweight="bold", zorder=5)
    ax.text(960, 545, "MEASURED\nSICKNESS",
            fontsize=16, color=GOLD, ha="center", va="center",
            fontweight="bold", zorder=5)

    # Subtitle line
    ax.text(728, 500,
            "THE CODING FOR DOLLARS GAP",
            fontsize=22, color=WHITE, ha="center", va="center",
            fontweight="bold", zorder=5)

    ax.text(728, 468,
            "Coded severity rose twice as fast as measured sickness",
            fontsize=15, color=WHITE, ha="center", va="center", zorder=5)
    ax.text(728, 442,
            "across Medicare FFS inpatient (2013-2024).",
            fontsize=15, color=WHITE, ha="center", va="center", zorder=5)

    # Stat bar (within safe zone) -- taller to fit 2-line sub-labels
    rect = FancyBboxPatch(
        (270, 285), 920, 110,
        boxstyle="round,pad=4", linewidth=0, facecolor="#0E2040", zorder=4
    )
    ax.add_patch(rect)

    stats = [
        ("$1.0B/yr",    "recoverable excess\n(booked central)"),
        ("2.0%",        "coding-intensity share\nof MS-DRG weights"),
        ("$542.92B",    "cumulative savings\n(16.8% of $3.24T gap)"),
    ]
    xs = [430, 728, 1026]
    for (stat, sub), x in zip(stats, xs):
        # Stat number at y=368
        ax.text(x, 368, stat, fontsize=15, color=GOLD, ha="center", va="center",
                fontweight="bold", zorder=6)
        # Sub-label at y=335 (lower, with 2 lines)
        ax.text(x, 333, sub, fontsize=9.0, color=LGRAY, ha="center", va="center",
                zorder=6, linespacing=1.3)

    for xd in [580, 876]:
        ax.plot([xd, xd], [292, 390], color=LGRAY, linewidth=0.8, zorder=5)

    # Bottom branding
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
    print("Generating Issue #18 charts ...")
    chart1_cmi_vs_hcc()
    chart2_condition_families()
    chart3_savings_waterfall()
    chart4_fraud_vs_grayzone()
    chart5_savings_tracker()
    chart_hero()

    pngs = sorted(FIGURES.glob("*.png"))
    print(f"\nTotal PNGs in figures/: {len(pngs)}")
    for p in pngs:
        print(f"  {p.name}")
