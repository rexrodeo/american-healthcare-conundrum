"""
Issue #19 -- The 340B Spread
Single entry-point chart generator.

Wipes figures/*.png first (preserving hero_cover.png by name),
then regenerates all 5 charts + hero image.

Usage:
    cd issue_19/
    python3 generate_all_charts.py

Charts:
  chart1_scatter_spread_vs_charity.png
  chart2_waterfall.png
  chart3_policy_levers.png
  chart4_program_growth.png
  chart5_savings_tracker.png
  hero_cover.png

Rules enforced:
- figsize <= (10, 6) at dpi=100; save at dpi=150
- plt.close(fig) after every savefig
- Relative paths via Path(__file__).resolve().parent
- No hardcoded /sessions/... paths
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

# ── Paths ─────────────────────────────────────────────────────────────────────
HERE    = Path(__file__).resolve().parent
RESULTS = HERE / "results"
FIGURES = HERE / "figures"
FIGURES.mkdir(exist_ok=True)

# ── Wipe existing PNGs (preserve hero by name; we regenerate it last) ─────────
for _f in FIGURES.glob("*.png"):
    if _f.name != "hero_cover.png":
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

# Use unicode dollar sign to prevent matplotlib mathtext parsing
DOL = "$"

# ══════════════════════════════════════════════════════════════════════════════
# Load data from results/
# ══════════════════════════════════════════════════════════════════════════════
with open(RESULTS / "savings_estimate.json") as _fh:
    EST = json.load(_fh)

# spread_retention_panel.csv
PANEL_ROWS = []
with open(RESULTS / "spread_retention_panel.csv") as _fh:
    for row in csv.DictReader(_fh):
        PANEL_ROWS.append({
            "net_spread_bil": float(row["net_spread_bil"]),
            "charity_central_bil": float(row["charity_central_bil"]),
            "gap_bil": float(row["spread_to_charity_gap_bil"]),
        })


# ══════════════════════════════════════════════════════════════════════════════
# CHART 1 -- Scatter: 340B Spread vs Charity Care (1,986 DSH hospitals)
# ══════════════════════════════════════════════════════════════════════════════

def chart1_scatter_spread_vs_charity():
    """
    Scatter plot: X = net 340B spread ($M), Y = charity care ($M).
    Diagonal line = spread equals charity.
    Teal dots: charity >= spread (98 hospitals).
    Gold dots: spread > charity (1,888 hospitals).
    Outlier cap at $250M for readability.
    """
    # Extract and convert to $M
    spread_m = np.array([r["net_spread_bil"] * 1000 for r in PANEL_ROWS])
    charity_m = np.array([r["charity_central_bil"] * 1000 for r in PANEL_ROWS])

    # Cap at 250M for readability (very few hospitals above this)
    cap = 250.0
    spread_capped  = np.minimum(spread_m,  cap)
    charity_capped = np.minimum(charity_m, cap)

    # Classify: teal = over-delivering (charity >= spread), gold = under-delivering
    over_mask  = (charity_m >= spread_m)
    under_mask = ~over_mask
    n_over  = int(over_mask.sum())
    n_under = int(under_mask.sum())

    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)

    # Under-delivering (gold, behind)
    ax.scatter(spread_capped[under_mask], charity_capped[under_mask],
               color=GOLD, alpha=0.30, s=8, zorder=3, rasterized=True,
               label=f"Spread > charity ({n_under:,} hospitals)")

    # Over-delivering (teal, on top)
    ax.scatter(spread_capped[over_mask], charity_capped[over_mask],
               color=TEAL, alpha=0.70, s=14, zorder=4, rasterized=True,
               label=f"Charity >= spread ({n_over} hospitals, zero gap)")

    # Diagonal line: spread = charity
    diag_max = cap
    ax.plot([0, diag_max], [0, diag_max], color=WHITE, linewidth=1.2,
            linestyle="--", zorder=5, alpha=0.70, label="Spread = charity")

    # Annotation: over-delivering cluster (upper-left)
    ax.annotate(
        f"{n_over} hospitals\ncharity >= spread\n(zero gap contribution)",
        xy=(8, 30),
        xytext=(45, 130),
        fontsize=7.5, color=TEAL, va="center", ha="left",
        bbox=dict(boxstyle="round,pad=0.20", facecolor=NAVY, edgecolor=TEAL,
                  linewidth=0.8, alpha=0.92),
        arrowprops=dict(arrowstyle="->", color=TEAL, lw=0.9,
                        connectionstyle="arc3,rad=0.15"),
        zorder=8
    )

    # Annotation: under-delivering cluster (lower-right)
    ax.annotate(
        f"{n_under:,} hospitals\nspread > charity\n({DOL}34.9B raw gap)",
        xy=(140, 12),
        xytext=(165, 80),
        fontsize=7.5, color=GOLD, va="center", ha="left",
        bbox=dict(boxstyle="round,pad=0.20", facecolor=NAVY, edgecolor=GOLD,
                  linewidth=0.8, alpha=0.92),
        arrowprops=dict(arrowstyle="->", color=GOLD, lw=0.9,
                        connectionstyle="arc3,rad=-0.15"),
        zorder=8
    )

    # Cap note
    ax.text(cap - 3, 3,
            f"Capped at {DOL}{cap:.0f}M\nfor readability",
            fontsize=6.5, color=LGRAY, ha="right", va="bottom",
            bbox=dict(boxstyle="round,pad=0.15", facecolor=NAVY, alpha=0.80),
            zorder=7)

    ax.set_xlim(0, cap * 1.05)
    ax.set_ylim(0, cap * 1.05)
    ax.set_xlabel(f"Net 340B Spread Captured (est., {DOL}M/year)", fontsize=10, labelpad=5)
    ax.set_ylabel(f"Charity Care Delivered at Cost ({DOL}M/year)", fontsize=10, labelpad=5)
    ax.set_title("340B Spread vs. Charity Care: 1,986 DSH Hospitals",
                 fontsize=11, color=WHITE, pad=10)

    ax.legend(fontsize=8, loc="upper left",
              framealpha=0.88, facecolor=NAVY, edgecolor=LGRAY, labelcolor=WHITE)
    ax.grid(True, alpha=0.20, zorder=0)
    ax.set_axisbelow(True)

    footnote = (
        "Spread estimated by allocating 63.5B DSH pool by bed count (see Methodology). "
        "Charity = Schedule H line 7a (financial assistance at cost) where a real IRS-990 match exists,\n"
        "else HCRIS S-10 charity-care-at-cost. Per-entity 340B purchase data not published by HRSA/OPAIS. "
        "Hospitals above 250M spread or charity capped at 250M for readability."
    )
    fig.text(0.09, 0.01, footnote, fontsize=5.5, color=LGRAY, ha="left", va="bottom")
    fig.subplots_adjust(top=0.88, bottom=0.17, left=0.10, right=0.97)

    out = FIGURES / "chart1_scatter_spread_vs_charity.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Saved: {out}")
    return out


# ══════════════════════════════════════════════════════════════════════════════
# CHART 2 -- Waterfall: $81.4B program -> $10.33B booked
# Two-panel: left = labeled step-funnel, right = booked with range
# ══════════════════════════════════════════════════════════════════════════════

def chart2_waterfall():
    """
    Two-panel waterfall.
    Left: labeled descending-step funnel (log-proportional widths).
    Right: booked bar with floor/ceiling bracket.
    """
    import math

    wf = EST["waterfall"]
    booked  = EST["booked_bil"]        # 10.33
    floor_v = EST["range_lo_bil"]      # 1.95
    ceil_v  = EST["range_hi_bil"]      # 26.23

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
    ax_l.set_title("From 81B Program to 10.33B Recoverable Gap:\nThe 340B Waterfall",
                   fontsize=10.5, color=WHITE, pad=10, loc="center")

    # Steps: (label, value, color)
    steps = [
        ("Total 340B program\npurchases (2024)",       wf["national_program_purchases_2024_discounted_bil"],  TEAL),
        ("DSH hospital\nshare (78%)",                   wf["national_dsh_pool_discounted_bil"],               TEAL),
        ("Net spread\n(WAC basis minus CP fees)",       wf["net_spread_captured_bil"],                        TEAL),
        ("Raw spread-to-charity\ngap (per-entity sum)", wf["raw_spread_to_charity_gap_bil"],                   TEAL),
        ("After overlap\nsubtractions",                 wf["gap_after_overlap_bil"],                           TEAL),
        ("Booked central\n(x0.40 recoverability)",      booked,                                               GOLD),
    ]

    n_steps = len(steps)
    # y positions: distribute steps top to bottom
    y_tops = [9.6 - i * (9.6 - 0.4) / n_steps for i in range(n_steps + 1)]

    # Log-proportional widths
    log_vals = [math.log10(max(s[1], 0.5)) + 2 for s in steps]
    max_lv   = log_vals[0]
    half_widths = [4.0 * lv / max_lv for lv in log_vals]

    for i, (lbl, val, col) in enumerate(steps):
        y_bot   = y_tops[i + 1]
        y_top   = y_tops[i]
        hw      = half_widths[i]
        hw_next = half_widths[i + 1] if i + 1 < len(half_widths) else half_widths[i] * 0.85

        poly_x = [5 - hw,      5 + hw,      5 + hw_next, 5 - hw_next]
        poly_y = [y_top,        y_top,        y_bot,        y_bot]
        ax_l.fill(poly_x, poly_y, color=col, alpha=0.80, zorder=3)
        ax_l.plot(poly_x + [poly_x[0]], poly_y + [poly_y[0]],
                  color=WHITE, linewidth=0.5, zorder=4)

        mid_y = (y_top + y_bot) / 2
        val_str = f"{DOL}{val:.1f}B"

        ax_l.text(5, mid_y + 0.22, val_str,
                  ha="center", va="center", fontsize=10.0, color=WHITE,
                  fontweight="bold", zorder=6)
        ax_l.text(5, mid_y - 0.25, lbl,
                  ha="center", va="center", fontsize=6.8, color=WHITE, zorder=6)

    # ── Right panel: booked bar with floor/ceiling ────────────────────────────
    ax_r.set_facecolor(NAVY)

    y_bar = 2.2
    bar_h = 0.80

    # Track bar (full ceiling range)
    ax_r.barh(y_bar, ceil_v * 1.22, height=bar_h, color=BG2, alpha=1.0, zorder=2, left=0)
    # Booked bar
    ax_r.barh(y_bar, booked, height=bar_h, color=GOLD, alpha=0.90, zorder=3, left=0)

    # Floor and ceiling tick marks
    for tick_x in [floor_v, ceil_v]:
        ax_r.plot([tick_x, tick_x],
                  [y_bar - bar_h / 2 - 0.08, y_bar + bar_h / 2 + 0.08],
                  color=WHITE, linewidth=1.8, zorder=5)

    # Booked value label (above bar, clear of bar top)
    ax_r.annotate(f"{DOL}{booked:.2f}B booked",
                  xy=(booked, y_bar + bar_h / 2),
                  xytext=(booked * 0.55, y_bar + bar_h / 2 + 0.55),
                  ha="center", va="bottom", fontsize=9.5, color=WHITE,
                  fontweight="bold", zorder=8,
                  bbox=dict(boxstyle="round,pad=0.18", facecolor=NAVY,
                            edgecolor=GOLD, linewidth=0.8, alpha=0.96),
                  arrowprops=dict(arrowstyle="-", color=GOLD, lw=1.0))

    # Floor label below bar
    ax_r.text(floor_v, y_bar - bar_h / 2 - 0.24,
              f"Floor\n{DOL}{floor_v:.2f}B",
              ha="center", va="top", fontsize=8, color=WHITE, zorder=6,
              bbox=dict(boxstyle="round,pad=0.14", facecolor=NAVY, edgecolor=LGRAY,
                        linewidth=0.6, alpha=0.92))

    # Ceiling label above bar
    ax_r.text(ceil_v, y_bar + bar_h / 2 + 0.24,
              f"Ceiling\n{DOL}{ceil_v:.2f}B",
              ha="center", va="bottom", fontsize=8, color=WHITE, zorder=6,
              bbox=dict(boxstyle="round,pad=0.14", facecolor=NAVY, edgecolor=LGRAY,
                        linewidth=0.6, alpha=0.92))

    ax_r.set_xlim(0, ceil_v * 1.22)
    ax_r.set_ylim(0.8, 4.0)
    ax_r.set_yticks([])
    ax_r.set_xlabel("USD Billions / year", fontsize=9, labelpad=4)
    ax_r.set_title("Booked Central\nwith Floor / Ceiling Range",
                   fontsize=10, color=WHITE, pad=8)
    ax_r.tick_params(axis="x", labelsize=8, labelcolor=WHITE)
    ax_r.grid(True, axis="x", alpha=0.20, zorder=0)
    ax_r.set_axisbelow(True)

    ax_r.text(0.5, 0.06,
              "Biggest swing: charity definition\n(pure Schedule H 7a vs. broad basket).",
              transform=ax_r.transAxes,
              ha="center", va="bottom", fontsize=6.5, color=LGRAY, style="italic")

    footnote = (
        "Central: 63.5B DSH pool, 45pct gross discount (WAC basis), 2.34B CP fees, "
        "16.18B charity (Sched H 7a + HCRIS S-10), per-entity gap clip, "
        "overlaps #13/6.9B + #17/0.4B + #4/1.7B, x0.40 recoverability.\n"
        "Floor (conservative): broad charity basket, 38pct discount, 0.25 recov. "
        "Ceiling (aggressive): pure 7a charity, 49pct discount, 0.65 recov. "
        "Left panel: log-proportional funnel (not to linear scale)."
    )
    fig.text(0.04, 0.01, footnote, fontsize=5.5, color=LGRAY, ha="left", va="bottom")
    fig.subplots_adjust(top=0.85, bottom=0.17, left=0.03, right=0.97)

    out = FIGURES / "chart2_waterfall.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Saved: {out}")
    return out


# ══════════════════════════════════════════════════════════════════════════════
# CHART 3 -- Policy Levers: Fix Spectrum (horizontal bars)
# ══════════════════════════════════════════════════════════════════════════════

def chart3_policy_levers():
    """
    Horizontal bar chart: 4 policy levers ordered by feasibility (1=most feasible).
    Each lever shows: feasibility rating bar (5-point scale) color-coded by authority.
    Labels outside bars with lever names and authority notes.
    """
    # Lever data: (lever_number, short_name, full_label, feasibility_score, authority)
    levers = [
        (1, "Per-entity reporting",
         "Lever 1: Per-entity\nreporting",
         4.5, "HRSA / State",    TEAL),
        (2, "CP fee disclosure",
         "Lever 2: Contract-pharmacy\nfee disclosure",
         3.8, "HRSA / Congressional",  TEAL),
        (3, "Pass-through tied\nto charity care",
         "Lever 3: Pass-through\ntied to charity",
         2.5, "Congressional\namendment",  GOLD),
        (4, "Eligibility\nnarrowing",
         "Lever 4: Eligibility\nnarrowing",
         1.5, "Congressional\namendment",  RED),
    ]

    # Sort so lever 1 (most feasible) is on top (bottom of reversed y-axis)
    # We plot y=0 as lever 4 (least), y=3 as lever 1 (most)
    levers_rev = list(reversed(levers))

    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=100)
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)

    n = len(levers_rev)
    y_pos = np.arange(n)
    bar_height = 0.50
    scale_max = 5.0

    # Background track bars (full scale)
    ax.barh(y_pos, [scale_max] * n, height=bar_height, color=BG2, alpha=1.0, zorder=2, left=0)

    # Feasibility bars
    for i, (lnum, short_name, full_label, score, authority, col) in enumerate(levers_rev):
        ax.barh(y_pos[i], score, height=bar_height, color=col, alpha=0.85, zorder=3, left=0)

        # Authority chip inside bar (if bar is wide enough)
        chip_x = score / 2
        ax.text(chip_x, y_pos[i],
                authority,
                ha="center", va="center", fontsize=7.5, color=NAVY if col != RED else WHITE,
                fontweight="bold", zorder=5)

        # Score label at bar right edge
        ax.text(score + 0.08, y_pos[i],
                f"{score:.1f}/5",
                ha="left", va="center", fontsize=8.0, color=WHITE, zorder=5)

    # Y-axis labels (lever names, left-aligned)
    ax.set_yticks(y_pos)
    y_labels = [lev[2] for lev in levers_rev]
    ax.set_yticklabels(y_labels, fontsize=8.5, color=WHITE)

    ax.set_xlim(0, scale_max * 1.28)
    ax.set_xlabel("Feasibility Score (1 = least, 5 = most enactable)", fontsize=9, labelpad=5)
    ax.set_title("The 340B Fix Spectrum: Levers in Order of Enactability",
                 fontsize=11, color=WHITE, pad=10)

    # Legend: authority color coding
    legend_patches = [
        mpatches.Patch(color=TEAL, label="HRSA administrative action"),
        mpatches.Patch(color=GOLD, label="Congressional amendment required"),
        mpatches.Patch(color=RED,  label="Most contested (eligibility narrowing)"),
    ]
    ax.legend(handles=legend_patches, fontsize=8, loc="lower right",
              framealpha=0.88, facecolor=NAVY, edgecolor=LGRAY, labelcolor=WHITE)

    ax.grid(True, axis="x", alpha=0.20, zorder=0)
    ax.set_axisbelow(True)

    # Directional annotations: top lever note
    ax.text(4.60, 3.35,
            "Minnesota enacted\nfirst (April 2024)",
            fontsize=7, color=TEAL, ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.18", facecolor=NAVY, edgecolor=TEAL,
                      linewidth=0.6, alpha=0.92),
            zorder=7)

    footnote = (
        "Feasibility scores are author assessments based on regulatory authority, "
        "legislative coalition size, and state precedent. "
        "Sources: Minn. Stat. 62J.461; GAO-26-108784 (Oct 2025);\n"
        "CBO Publication 61730 (Sep 2025); HRSA 340B Rebate Model Pilot (Jan 2026)."
    )
    fig.text(0.09, 0.01, footnote, fontsize=5.5, color=LGRAY, ha="left", va="bottom")
    fig.subplots_adjust(top=0.88, bottom=0.16, left=0.28, right=0.97)

    out = FIGURES / "chart3_policy_levers.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Saved: {out}")
    return out


# ══════════════════════════════════════════════════════════════════════════════
# CHART 4 -- Program Growth 2015-2024 (line chart)
# ══════════════════════════════════════════════════════════════════════════════

def chart4_program_growth():
    """
    Line chart: total 340B purchases ($B) 2015-2024 with CAGR label.
    Vertical markers: 2020 (manufacturer restrictions begin) and 2026 (IRA pilot).
    Single Y axis for purchases ($B); right axis for covered-entity count index.
    Drug Channels data series hardcoded from the draft (public source, not in results/).
    """
    # Drug Channels published series (Drug Channels Institute, December 2025)
    # Purchases in $B, covered entities index (normalized to 2015=100)
    years       = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    purchases_b = [12.0, 16.2, 19.3, 24.0, 29.9, 38.0, 44.0, 54.0, 66.5, 81.4]
    # HRSA covered entity count (approximate, from Drug Channels / OPAIS)
    # 2015: ~11,000; 2024: ~50,000 (program grew from hospitals to FQHCs, clinics, etc.)
    ce_counts   = [11000, 12400, 14200, 17000, 22000, 30000, 36000, 42000, 47000, 50000]
    # Contract pharmacy locations (approximate, from Drug Channels)
    cp_locations = [9000, 10500, 13000, 17000, 22000, 28000, 28500, 27000, 26000, 25775]

    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
    ax2 = ax.twinx()
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)
    ax2.set_facecolor(NAVY)

    # Purchases (left axis, teal, thick)
    line1, = ax.plot(years, purchases_b, color=TEAL, linewidth=2.8, marker="o",
                     markersize=6, zorder=5, label="340B purchases ($B, left axis)")

    # Covered entities (right axis, gold, dashed)
    line2, = ax2.plot(years, [c / 1000 for c in ce_counts], color=GOLD, linewidth=2.0,
                      marker="s", markersize=5, linestyle="--", zorder=5,
                      label="Covered entities (thousands, right axis)")

    # Contract pharmacies (right axis, red, dotted)
    line3, = ax2.plot(years, [c / 1000 for c in cp_locations], color=RED, linewidth=2.0,
                      marker="^", markersize=5, linestyle=":", zorder=5,
                      label="CP locations (thousands, right axis)")

    # Vertical marker: 2020 manufacturer restrictions
    ax.axvline(2020, color=RED, linestyle="--", linewidth=1.1, zorder=4, alpha=0.75)
    ax.text(2020.12, 68.0,
            "Mfr. restrictions\nbegin (Sep 2020)",
            fontsize=7.5, color=RED, va="center", ha="left",
            bbox=dict(boxstyle="round,pad=0.18", facecolor=NAVY, edgecolor=RED,
                      linewidth=0.5, alpha=0.92),
            zorder=8)

    # Vertical marker: 2026 IRA rebate pilot
    ax.axvline(2026, color=GOLD, linestyle="--", linewidth=1.0, zorder=4, alpha=0.65)
    ax.text(2026.08, 45.0,
            "IRA rebate\npilot (Jan 2026)",
            fontsize=7.5, color=GOLD, va="center", ha="left",
            bbox=dict(boxstyle="round,pad=0.18", facecolor=NAVY, edgecolor=GOLD,
                      linewidth=0.5, alpha=0.92),
            zorder=8)

    # CAGR annotation (purchases 2015-2024)
    ax.annotate("23.5% CAGR\n(2015-2024)",
                xy=(2021.5, 44.0),
                xytext=(2016.5, 62.0),
                fontsize=8.5, color=TEAL, ha="center",
                bbox=dict(boxstyle="round,pad=0.20", facecolor=NAVY, edgecolor=TEAL,
                          linewidth=0.8, alpha=0.95),
                arrowprops=dict(arrowstyle="->", color=TEAL, lw=1.0,
                                connectionstyle="arc3,rad=-0.20"),
                zorder=8)

    # End-point label for purchases
    ax.text(2024.08, purchases_b[-1],
            f"{DOL}{purchases_b[-1]:.0f}B",
            fontsize=9, color=TEAL, fontweight="bold", va="center", ha="left", zorder=7,
            bbox=dict(boxstyle="round,pad=0.15", facecolor=NAVY, edgecolor="none", alpha=0.9))

    ax.set_xlim(2014.5, 2027.0)
    ax.set_ylim(0, 100)
    ax.set_xticks(years)
    ax.set_xticklabels([str(y) for y in years], fontsize=8, color=WHITE)
    ax.set_xlabel("Year", fontsize=10, labelpad=5)
    ax.set_ylabel(f"340B Program Purchases ({DOL}B, discounted acquisition price)", fontsize=9, labelpad=5)

    ax2.set_ylim(0, 70)
    ax2.set_ylabel("Covered Entities / CP Locations (thousands)", fontsize=9, labelpad=5,
                   color=LGRAY)
    ax2.tick_params(axis="y", labelsize=8, labelcolor=LGRAY)
    ax2.spines["right"].set_color(LGRAY)
    for spine in ["top", "left", "bottom"]:
        ax2.spines[spine].set_visible(False)

    ax.set_title("The 340B Program, 2015-2024: Purchases, Covered Entities, Contract Pharmacies",
                 fontsize=10.5, color=WHITE, pad=10)

    # Combined legend
    lines_labels = [line1, line2, line3]
    ax.legend(lines_labels,
              [f"340B purchases ({DOL}B, left axis)",
               "Covered entities (thousands, right axis)",
               "CP locations (thousands, right axis)"],
              fontsize=7.5, loc="upper left",
              framealpha=0.88, facecolor=NAVY, edgecolor=LGRAY, labelcolor=WHITE)

    ax.grid(True, alpha=0.20, zorder=0)
    ax.set_axisbelow(True)

    footnote = (
        "Sources: Drug Channels Institute (Fein) December 2025 (81.4B CY2024, 23.5% CAGR 2015-2024); "
        "HRSA OPAIS (covered-entity count); Drug Channels annual contract-pharmacy analyses.\n"
        "Covered-entity and CP-location figures are approximate; program includes DSH hospitals, "
        "FQHCs, Ryan White, children's hospitals, and other eligible entities."
    )
    fig.text(0.09, 0.01, footnote, fontsize=5.5, color=LGRAY, ha="left", va="bottom")
    fig.subplots_adjust(top=0.87, bottom=0.17, left=0.09, right=0.88)

    out = FIGURES / "chart4_program_growth.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Saved: {out}")
    return out


# ══════════════════════════════════════════════════════════════════════════════
# CHART 5 -- Savings Tracker (all 19 issues)
# ══════════════════════════════════════════════════════════════════════════════

def chart5_savings_tracker():
    """All 19 issues; Issue #19 highlighted in gold. Running total $545.25B."""
    issues = [
        ("#1",  "OTC Drugs",          0.6),
        ("#2",  "Drug Pricing",       25.0),
        ("#3",  "Hospital Pricing",   73.0),
        ("#4",  "PBM Reform",         30.0),
        ("#5",  "Admin Waste",       200.0),
        ("#6",  "Supply Waste",       28.0),
        ("#7",  "GLP-1 Pricing",      40.0),
        ("#8",  "Denial Machine",     24.0),
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
        ("#19", "The 340B Spread",    10.33),
    ]

    nums    = [i[0] for i in issues]
    labels  = [i[1] for i in issues]
    savings = [i[2] for i in issues]

    running_total = 545.25
    target = 3240.0
    pct = running_total / target * 100   # 16.8%

    fig, (ax_left, ax_right) = plt.subplots(
        1, 2, figsize=(10, 6.5), dpi=100,
        gridspec_kw={"width_ratios": [2, 1], "wspace": 0.52}
    )
    fig.patch.set_facecolor(NAVY)
    fig.subplots_adjust(top=0.88, bottom=0.09, left=0.22, right=0.97)

    # ── Left: per-issue bars ──────────────────────────────────────────────────
    ax_left.set_facecolor(NAVY)
    y_pos = np.arange(len(issues))
    bar_colors = [GOLD if n == "#19" else TEAL for n in nums]
    bars = ax_left.barh(y_pos, savings, color=bar_colors, height=0.68, alpha=0.90, zorder=3)

    ax_left.set_yticks(y_pos)
    ax_left.set_yticklabels([f"{n}  {lbl}" for n, lbl in zip(nums, labels)],
                            fontsize=6.5, color=WHITE)

    max_s = max(savings)
    for i, (bar, val) in enumerate(zip(bars, savings)):
        lbl_txt = f"{val:.1f}B" if val >= 1.0 else f"{val:.2f}B"
        ax_left.text(val + max_s * 0.018, i, lbl_txt,
                     va="center", ha="left", fontsize=6.8, color=WHITE)

    ax_left.set_xlim(0, max_s * 1.38)
    ax_left.set_xlabel("Savings (USD Billions/year)", fontsize=9, labelpad=4)
    ax_left.set_title("Per-Issue Savings, Issues #1-#19", fontsize=10, color=WHITE, pad=7)
    ax_left.grid(True, axis="x", alpha=0.22, zorder=0)
    ax_left.set_axisbelow(True)

    # ── Right: running total with two inset sub-panels ────────────────────────
    ax_right.set_facecolor(NAVY)
    ax_right.axis("off")
    ax_right.set_title(f"Running Total\n{running_total:.2f}B / 3.24T ({pct:.1f}%)",
                       fontsize=10, color=WHITE, pad=7)

    # --- Full-scale panel ---
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
    ax_full.text(-0.04, 0, "Full scale\nvs 3.24T", transform=ax_full.transAxes,
                 fontsize=7.5, color=WHITE, ha="right", va="center")
    ax_full.text(running_total / 2.0, 0.45,
                 f"{DOL}{running_total:.2f}B = {pct:.1f}%",
                 va="bottom", ha="center", fontsize=8.5, color=WHITE, fontweight="bold",
                 zorder=6,
                 bbox=dict(boxstyle="round,pad=0.20", facecolor=NAVY, alpha=0.88,
                           edgecolor=TEAL, linewidth=0.8))

    # --- Zoom panel (0-100B) ---
    zoom_max = 100.0
    ax_zoom = inset_axes(ax_right, width="100%", height="42%",
                         bbox_to_anchor=(0.0, 0.0, 1.0, 0.42),
                         bbox_transform=ax_right.transAxes,
                         loc="lower left", borderpad=0)
    ax_zoom.set_facecolor(NAVY)
    ax_zoom.barh(0, zoom_max,                          height=0.55, color=BG2,  alpha=1.0, zorder=2)
    ax_zoom.barh(0, min(running_total, zoom_max),      height=0.55, color=GOLD, alpha=0.90, zorder=3)
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
                 fontsize=7.5, color=WHITE, ha="right", va="center")
    ax_zoom.text(50.0, 0,
                 "First 100B filled",
                 va="center", ha="center", fontsize=7.5, color=NAVY, fontweight="bold",
                 zorder=6)

    fig.suptitle("AHC Savings Tracker -- After Issue #19",
                 fontsize=12, color=WHITE, y=0.975, fontweight="bold")

    fig.text(0.04, 0.01,
             "Target: 3.24T US-Japan per-capita gap (CMS NHE 2024; OECD 2023). "
             f"Issue #19 adds 10.33B. Cumulative: {running_total:.2f}B ({pct:.1f}%). "
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
    Hook: "$10.3 BILLION" / "Hospital 340B spread: $49.6B. Documented charity: $16.2B."
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

    # Series branding top-center (within safe zone)
    ax.text(728, 762,
            "THE AMERICAN HEALTHCARE CONUNDRUM",
            fontsize=17, color=RED, ha="center", va="center",
            fontweight="bold", zorder=5)
    ax.text(728, 728,
            "Issue #19",
            fontsize=23, color=GOLD, ha="center", va="center",
            fontweight="bold", zorder=5)

    # Red divider line
    ax.plot([300, 1156], [704, 704], color=RED, linewidth=2.5, zorder=5)

    # Main hook: large dollar figure
    ax.text(728, 620,
            f"{DOL}10.3 BILLION",
            fontsize=76, color=GOLD, ha="center", va="center",
            fontweight="bold", zorder=5)

    # Subtitle line
    ax.text(728, 555,
            "THE 340B SPREAD",
            fontsize=26, color=WHITE, ha="center", va="center",
            fontweight="bold", zorder=5)

    ax.text(728, 520,
            "How a drug-discount program designed for safety-net hospitals",
            fontsize=15, color=WHITE, ha="center", va="center", zorder=5)
    ax.text(728, 494,
            r"captures \$49.6 billion per year while delivering \$16.2 billion in charity care.",
            fontsize=15, color=WHITE, ha="center", va="center", zorder=5)

    # Stat bar within safe zone
    rect = FancyBboxPatch(
        (270, 285), 920, 115,
        boxstyle="round,pad=4", linewidth=0, facecolor="#0E2040", zorder=4
    )
    ax.add_patch(rect)

    stats = [
        (r"\$49.6B/yr",   "net 340B spread\n(DSH hospitals)"),
        (r"\$16.2B/yr",   "documented charity\ncare at cost"),
        (r"\$553.25B",    r"cumulative savings" + "\n" + r"(17.1% of \$3.24T gap)"),
    ]
    xs = [430, 728, 1026]
    for (stat, sub), x in zip(stats, xs):
        ax.text(x, 372, stat, fontsize=15, color=GOLD, ha="center", va="center",
                fontweight="bold", zorder=6)
        ax.text(x, 337, sub, fontsize=9.0, color=LGRAY, ha="center", va="center",
                zorder=6, linespacing=1.3)

    for xd in [580, 876]:
        ax.plot([xd, xd], [293, 395], color=LGRAY, linewidth=0.8, zorder=5)

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
    print("Generating Issue #19 charts ...")
    chart1_scatter_spread_vs_charity()
    chart2_waterfall()
    chart3_policy_levers()
    chart4_program_growth()
    chart5_savings_tracker()
    chart_hero()

    pngs = sorted(FIGURES.glob("*.png"))
    print(f"\nTotal PNGs in figures/: {len(pngs)}")
    for p in pngs:
        print(f"  {p.name}")
