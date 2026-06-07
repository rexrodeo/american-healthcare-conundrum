"""
generate_all_charts.py -- Issue #15: The Facility Fee Scam
Single entry-point: wipe figures/*.png and regenerate all 5 charts + hero.
Run from any directory: python3 /path/to/issue_15/generate_all_charts.py

Chart list (1:1 with *[Chart N: ...]* placeholders in newsletter_issue_15.md):
  chart1_site_differential.png   -- Same code, different building: payment differentials
  chart2_regulatory_timeline.png -- OPPS/site-neutral regulatory timeline 1997-2026
  chart3_savings_waterfall.png   -- Savings build from $1.967B Medicare to $2.55B booked
  chart4_savings_by_lever.png    -- Savings by policy lever (estimated ranges)
  chart5_savings_tracker.png     -- Cumulative tracker through Issue #15 ($519.35B)
  hero_cover.png                 -- $2.55B / The Facility Fee Scam
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# -- Paths -------------------------------------------------------------------
ROOT    = Path(__file__).resolve().parent
FIGURES = ROOT / "figures"
FIGURES.mkdir(exist_ok=True)

wiped = 0
for f in FIGURES.glob("*.png"):
    try:
        f.unlink(); wiped += 1
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


# =============================================================================
# CHART 1 -- Same code, different building: selected Medicare payment differentials
# Grouped vertical bars (HOPD total vs PFS office), ordered by differential desc.
# 5 codes from results/per_hcpcs_savings.csv + echocardiogram (prose approx values).
# =============================================================================
def generate_chart1_site_differential(outpath: Path):
    # (label, code, HOPD_total, PFS_office, is_booked_category)
    rows = [
        ("Nuclear stress\ntest (78452)",  1377.61, 408.86, False),
        ("Echocardiogram\n(93306)",        614.00, 188.00, False),
        ("Joint injection\n(20610)",       339.18,  63.40, True),
        ("Brain MRI\n(70553)",             461.93, 314.08, False),
        ("Office visit\n(99214)",          222.67, 125.18, True),
        ("Chest X-ray\n(71045)",            96.46,  25.23, False),
    ]
    labels = [r[0] for r in rows]
    hopd   = [r[1] for r in rows]
    office = [r[2] for r in rows]
    diffs  = [r[1] - r[2] for r in rows]

    x = np.arange(len(rows))
    w = 0.38

    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)

    bars_h = ax.bar(x - w/2, hopd,   w, color=RED,  zorder=3, label="HOPD total payment")
    bars_o = ax.bar(x + w/2, office, w, color=TEAL, zorder=3, label="Independent office (PFS)")

    ax.set_ylim(0, 1620)  # headroom above 1377.61 for labels

    # Value labels above each bar
    for b, v in zip(bars_h, hopd):
        ax.text(b.get_x() + b.get_width()/2, v + 18, f"${v:,.0f}",
                ha="center", va="bottom", color=WHITE, fontsize=8, fontweight="bold")
    for b, v in zip(bars_o, office):
        ax.text(b.get_x() + b.get_width()/2, v + 18, f"${v:,.0f}",
                ha="center", va="bottom", color=LTGRAY, fontsize=8)

    # Differential callout above each group (clear of both value labels)
    for xi, d, hv in zip(x, diffs, hopd):
        ax.text(xi, hv + 95, f"+${d:,.0f}", ha="center", va="bottom",
                color=GOLD, fontsize=9.5, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, color=WHITE, fontsize=8.5)
    ax.set_ylabel("Medicare payment ($, CY2025 rates)", color=WHITE, fontsize=9.5)
    ax.tick_params(axis="y", colors=WHITE, labelsize=8.5)
    ax.tick_params(axis="x", colors=WHITE, length=0)
    for sp in ax.spines.values():
        sp.set_edgecolor(LTGRAY)
    ax.grid(axis="y", color=LTGRAY, alpha=0.2, linewidth=0.6)

    fig.suptitle("Same Code, Different Building", color=WHITE, fontsize=15,
                 fontweight="bold", x=0.5, y=0.975)
    ax.set_title("Selected Medicare Payment Differentials (CY2025 Rates)",
                 color=LTGRAY, fontsize=10, pad=8)

    leg = ax.legend(loc="upper right", fontsize=8.5, facecolor=NAVY,
                    edgecolor=LTGRAY, labelcolor=WHITE, framealpha=0.95)
    leg.set_zorder(5)

    fig.text(0.085, 0.015,
             "Booked savings cover office visits and minor procedures (joint injection, office visit). Imaging codes are\n"
             "illustrative differentials, not included in the booked figure (see methodology). Echocardiogram values approximate.",
             color=LTGRAY, fontsize=6.5, ha="left", va="bottom", linespacing=1.3)

    plt.subplots_adjust(top=0.88, bottom=0.18, left=0.085, right=0.97)
    fig.savefig(outpath, dpi=150, facecolor=NAVY, bbox_inches=None)
    plt.close(fig)
    print(f"Saved {outpath}")


# =============================================================================
# CHART 2 -- Regulatory timeline 1997-2026
# =============================================================================
def generate_chart2_regulatory_timeline(outpath: Path):
    events = [
        (1997, "OPPS created\n(BBA 1997)",            "up"),
        (2000, "OPPS\nimplemented",                   "down"),
        (2014, "MedPAC site-neutral\nrecommendation", "up"),
        (2015, "BBA Sec. 603\npartial fix",           "down"),
        (2019, "CY2019 OPPS\nclinic-visit cut",        "up"),
        (2023, "Lower Costs Act\nHouse passage",       "down"),
        (2025, "SITE Act\n(119th Congress)",           "up"),
    ]

    fig, ax = plt.subplots(figsize=(10, 5.2), dpi=100)
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)

    x0, x1 = 1995.5, 2026.5
    ax.set_xlim(x0, x1)
    ax.set_ylim(-3.2, 3.4)

    # Shaded region: HOPD volume growing at OPPS rates (2000-present)
    ax.axvspan(2000, 2026.5, ymin=0.0, ymax=0.40, color=RED, alpha=0.13, zorder=1)
    ax.text(2007.0, -2.80, "HOPD volume growing at OPPS rates",
            color=RED, fontsize=8.5, ha="center", va="center", style="italic")

    # Narrow notch: post-2015 new off-campus HOPDs at PFS
    ax.axvspan(2015, 2026.5, ymin=0.40, ymax=0.46, color=TEAL, alpha=0.30, zorder=1)
    ax.text(2019.0, -0.62, "Post-2015 new off-campus HOPDs paid at PFS",
            color=TEAL, fontsize=7.2, ha="center", va="center", style="italic")

    # Main timeline axis
    ax.axhline(0, color=WHITE, linewidth=2.2, zorder=2)
    for yr in range(1996, 2027, 2):
        ax.plot([yr, yr], [-0.08, 0.08], color=LTGRAY, linewidth=0.8, zorder=2)
    for yr in (1997, 2000, 2005, 2010, 2015, 2020, 2025):
        ax.text(yr, -0.32, str(yr), color=LTGRAY, fontsize=8, ha="center", va="top")

    for yr, label, direction in events:
        y_stem = 1.55 if direction == "up" else -1.55
        y_text = 2.05 if direction == "up" else -2.05
        va = "bottom" if direction == "up" else "top"
        ax.plot([yr, yr], [0, y_stem], color=GOLD, linewidth=1.4, zorder=3)
        ax.plot(yr, 0, "o", color=GOLD, markersize=6, zorder=4)
        ax.text(yr, y_text, label, color=WHITE, fontsize=8, ha="center", va=va,
                zorder=4, linespacing=1.15)

    ax.axis("off")
    fig.suptitle("Three Decades of Partial Fixes", color=WHITE, fontsize=15,
                 fontweight="bold", y=0.97)
    ax.set_title("Hospital outpatient (OPPS) payment and site-neutral reform, 1997-2026",
                 color=LTGRAY, fontsize=10, pad=10)

    fig.text(0.09, 0.02,
             "OPPS = Outpatient Prospective Payment System; HOPD = Hospital Outpatient Department; "
             "PFS = Physician Fee Schedule. Section 603 grandfathered existing off-campus HOPDs.",
             color=LTGRAY, fontsize=6.5, ha="left", va="bottom")

    plt.subplots_adjust(top=0.86, bottom=0.10, left=0.04, right=0.97)
    fig.savefig(outpath, dpi=150, facecolor=NAVY, bbox_inches=None)
    plt.close(fig)
    print(f"Saved {outpath}")


# =============================================================================
# CHART 3 -- Savings waterfall
# =============================================================================
def generate_chart3_savings_waterfall(outpath: Path):
    # (label, delta, kind)  kind in {start, add, sub, total}
    steps = [
        ("Medicare\ncomputed",           1.967, "start"),
        ("+ Commercial\next. (1.5x)",     2.950, "add"),
        ("- Issue #3\noverlap",          -0.443, "sub"),
        ("- Issue #12\noverlap",         -0.224, "sub"),
        ("- Recoverability\nfriction",   -1.700, "sub"),
        ("Booked\nIssue #15",             2.550, "total"),
    ]

    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)

    x = np.arange(len(steps))
    running = 0.0
    bar_w = 0.62
    for xi, (label, delta, kind) in zip(x, steps):
        if kind == "start":
            bottom, height, color = 0, delta, TEAL
            top = height
            running = delta
        elif kind == "total":
            bottom, height, color = 0, delta, GOLD
            top = height
            running = delta
        elif kind == "add":
            bottom, height, color = running, delta, TEAL
            top = running + delta
            running += delta
        else:  # sub
            bottom, height, color = running + delta, -delta, RED
            top = running
            running += delta

        ax.bar(xi, height, bottom=bottom, width=bar_w, color=color, zorder=3)

        # Connector line to next bar
        if kind != "total":
            ax.plot([xi + bar_w/2, xi + 1 - bar_w/2], [running, running],
                    color=LTGRAY, linewidth=0.9, linestyle=(0, (4, 3)), zorder=2)

        # Delta label above/below each bar
        lab_y = top + 0.12 if kind in ("start", "add", "total") else bottom - 0.16
        va = "bottom" if kind in ("start", "add", "total") else "top"
        sign = "" if kind in ("start", "total") else ("+" if delta > 0 else "-")
        ax.text(xi, lab_y, f"{sign}${abs(delta):.2f}B", ha="center", va=va,
                color=WHITE, fontsize=8.5, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels([s[0] for s in steps], color=WHITE, fontsize=8.5, linespacing=1.15)
    ax.set_ylabel("Annual savings ($B)", color=WHITE, fontsize=9.5)
    ax.tick_params(axis="y", colors=WHITE, labelsize=8.5)
    ax.tick_params(axis="x", colors=WHITE, length=0)
    ax.set_ylim(0, 5.4)
    for sp in ax.spines.values():
        sp.set_edgecolor(LTGRAY)
    ax.grid(axis="y", color=LTGRAY, alpha=0.2, linewidth=0.6)

    fig.suptitle("From Computed Base to Booked Figure", color=WHITE, fontsize=15,
                 fontweight="bold", y=0.975)
    ax.set_title("Issue #15 savings build (annual, $B)", color=LTGRAY, fontsize=10, pad=8)

    fig.text(0.09, 0.02,
             "Medicare counterfactual ($1.967B) covers clinic visits + minor procedures. Commercial extension "
             "is a modeled 1.5x layer, net of overlap with Issues #3 and #12, then a 40% recoverability discount.",
             color=LTGRAY, fontsize=6.5, ha="left", va="bottom")

    plt.subplots_adjust(top=0.88, bottom=0.16, left=0.08, right=0.97)
    fig.savefig(outpath, dpi=150, facecolor=NAVY, bbox_inches=None)
    plt.close(fig)
    print(f"Saved {outpath}")


# =============================================================================
# CHART 4 -- Savings by policy lever (estimated ranges, floating bars)
# =============================================================================
def generate_chart4_savings_by_lever(outpath: Path):
    # (label, lo, hi)
    levers = [
        ("CMS regulatory\n(clinic visits +\nminor procedures)", 1.2, 1.8),
        ("Congressional full\nMedicare site-neutral\n(+ on-campus, imaging,\ndrug admin if data unlocked)", 2.0, 6.6),
        ("Commercial extension\n(1.5x conservative to\n2.54x RAND 5.1 ratio)", 2.5, 4.2),
    ]
    x = np.arange(len(levers))
    colors = [TEAL, GOLD, RED]

    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)

    for xi, (label, lo, hi), c in zip(x, levers, colors):
        ax.bar(xi, hi - lo, bottom=lo, width=0.5, color=c, zorder=3)
        ax.text(xi, hi + 0.18, f"${lo:.1f}-{hi:.1f}B", ha="center", va="bottom",
                color=WHITE, fontsize=10, fontweight="bold")
        # endpoint ticks
        ax.plot([xi - 0.25, xi + 0.25], [lo, lo], color=WHITE, linewidth=1.0, zorder=4)
        ax.plot([xi - 0.25, xi + 0.25], [hi, hi], color=WHITE, linewidth=1.0, zorder=4)

    ax.set_xticks(x)
    ax.set_xticklabels([l[0] for l in levers], color=WHITE, fontsize=8.5, linespacing=1.2)
    ax.set_ylabel("Estimated annual savings ($B)", color=WHITE, fontsize=9.5)
    ax.tick_params(axis="y", colors=WHITE, labelsize=8.5)
    ax.tick_params(axis="x", colors=WHITE, length=0)
    ax.set_ylim(0, 7.6)
    for sp in ax.spines.values():
        sp.set_edgecolor(LTGRAY)
    ax.grid(axis="y", color=LTGRAY, alpha=0.2, linewidth=0.6)

    fig.suptitle("Savings by Policy Lever", color=WHITE, fontsize=15,
                 fontweight="bold", y=0.975)
    ax.set_title("Estimated Medicare and Commercial Combined (scenario ranges)",
                 color=LTGRAY, fontsize=10, pad=8)

    fig.text(0.08, 0.015,
             "Scenario estimates by policy scope, not strictly additive (scopes overlap). The Congressional full Medicare lever\n"
             "bridges toward the MedPAC ambulatory aggregate (~$6.6B) if imaging and drug administration are unlocked with claims data.",
             color=LTGRAY, fontsize=6.5, ha="left", va="bottom", linespacing=1.3)

    plt.subplots_adjust(top=0.88, bottom=0.23, left=0.08, right=0.97)
    fig.savefig(outpath, dpi=150, facecolor=NAVY, bbox_inches=None)
    plt.close(fig)
    print(f"Saved {outpath}")


# =============================================================================
# CHART 5 -- Cumulative savings tracker (through Issue #15)
# =============================================================================
def generate_chart5_savings_tracker(outpath: Path):
    issues = [
        ("OTC",       0.6),  ("Drug Px",  25.0), ("Hosp Px", 73.0),
        ("PBMs",      30.0), ("Admin",   200.0), ("Supply",  28.0),
        ("GLP-1",     40.0), ("Denial",   32.0), ("Employer", 6.6),
        ("Procedure",  7.6), ("MA",       28.0), ("Consol.", 13.0),
        ("Nonprofit",  5.4), ("Spec Tax", 27.6), ("Facility",  2.55),
    ]
    values_i = [x[1] for x in issues]
    total_b  = sum(values_i)   # 519.35
    gap_b    = 3240.0
    pct      = total_b / gap_b * 100

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5.5), dpi=100,
                                   gridspec_kw={"width_ratios": [3, 1], "wspace": 0.50})
    fig.patch.set_facecolor(NAVY); ax1.set_facecolor(NAVY); ax2.set_facecolor(NAVY)

    fig.suptitle(f"Cumulative Savings Identified: ${total_b:.2f}B  ({pct:.1f}% of US-Japan Gap)",
                 color=WHITE, fontsize=11.5, fontweight="bold", y=0.98)

    colors_i = [RED if i == len(issues) - 1 else TEAL for i in range(len(issues))]
    bars = ax1.bar(range(len(issues)), values_i, color=colors_i, zorder=3, width=0.72)
    last_idx = len(issues) - 1
    for i, (bar, val) in enumerate(zip(bars, values_i)):
        h = bar.get_height()
        if h >= 25:
            ax1.text(bar.get_x() + bar.get_width()/2, h/2, f"${val:.0f}B",
                     ha="center", va="center", color=WHITE, fontsize=7.2, fontweight="bold")
        else:
            if i == last_idx:
                txt = f"${val:.2f}B"          # highlighted current issue: precise booked figure
            elif val < 10:
                txt = f"${val:.1f}B"
            else:
                txt = f"${val:.0f}B"
            ax1.text(bar.get_x() + bar.get_width()/2, h + 3, txt,
                     ha="center", va="bottom", color=WHITE, fontsize=6.8, fontweight="bold")

    xtick_labels = [f"#{i+1} {s}" for i, (s, _) in enumerate(issues)]
    ax1.set_xticks(range(len(issues)))
    ax1.set_xticklabels(xtick_labels, color=WHITE, fontsize=7, rotation=40, ha="right")
    ax1.set_ylabel("Savings ($B)", color=WHITE, fontsize=9)
    ax1.tick_params(axis="y", colors=WHITE, labelsize=8.5)
    ax1.tick_params(axis="x", colors=WHITE, pad=2)
    for sp in ax1.spines.values():
        sp.set_edgecolor(LTGRAY)
    ax1.grid(axis="y", color=LTGRAY, alpha=0.2, linewidth=0.6)
    ax1.set_ylim(0, 240)
    ax1.set_title("Per-Issue Savings", color=WHITE, fontsize=10, pad=6)

    ax2.bar([0], [total_b], color=TEAL, width=0.5, zorder=3)
    ax2.bar([0], [gap_b - total_b], bottom=[total_b], color=LTGRAY, alpha=0.3, width=0.5, zorder=3)
    ax2.text(0, total_b/2 + 120, f"${total_b:.1f}B\nidentified", ha="center", va="center",
             color=WHITE, fontsize=9.5, fontweight="bold")
    ax2.text(0, total_b + (gap_b - total_b)/2, f"${(gap_b-total_b)/1000:.2f}T\nremaining",
             ha="center", va="center", color=LTGRAY, fontsize=9)
    ax2.set_ylim(0, gap_b * 1.05)
    ax2.set_xlim(-0.6, 0.6)
    ax2.set_xticks([])
    ax2.set_ylabel("$ Billions", color=WHITE, fontsize=9)
    ax2.tick_params(axis="y", colors=WHITE, labelsize=8)
    for sp in ax2.spines.values():
        sp.set_edgecolor(LTGRAY)
    ax2.set_title(f"{pct:.1f}% of\n$3.24T gap", color=GOLD, fontsize=10, fontweight="bold", pad=6)

    fig.text(0.02, 0.01,
             "Sources: Published Issues #1-#15. Full-scale gap: CMS NHE 2024 + OECD Health at a Glance 2025 ($3.24T).",
             color=LTGRAY, fontsize=6.5, va="bottom", ha="left")

    plt.subplots_adjust(bottom=0.26, left=0.08, right=0.97, top=0.85)
    fig.savefig(outpath, dpi=150, facecolor=NAVY, bbox_inches=None)
    plt.close(fig)
    print(f"Saved {outpath}")


# =============================================================================
# HERO -- hero_cover.png (figsize 14.56x10.48 @ 100dpi -> 2184x1572 @ 150dpi)
# =============================================================================
def generate_hero(outpath: Path):
    FW, FH = 14.56, 10.48
    fig = plt.figure(figsize=(FW, FH), dpi=100)
    fig.patch.set_facecolor(NAVY)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, FW); ax.set_ylim(0, FH); ax.axis("off"); ax.set_facecolor(NAVY)

    for gx in np.arange(0, FW + 1, 1.0):
        ax.axvline(gx, color=WHITE, alpha=0.03, linewidth=0.5)
    for gy in np.arange(0, FH + 1, 1.0):
        ax.axhline(gy, color=WHITE, alpha=0.03, linewidth=0.5)

    CX = FW / 2
    SZ_X_LO = CX - FW * 0.31
    SZ_X_HI = CX + FW * 0.31
    SZ_Y_LO = FH * 0.24
    SZ_Y_HI = FH * 0.76

    banner_y = SZ_Y_HI + 0.20
    ax.text(CX, banner_y, "THE AMERICAN HEALTHCARE CONUNDRUM",
            color=RED, fontsize=22, fontweight="bold", ha="center", va="center",
            fontfamily="DejaVu Sans")
    ax.text(CX, banner_y - 0.65, "ISSUE #15", color=GOLD, fontsize=18, fontweight="bold",
            ha="center", va="center", fontfamily="DejaVu Sans")
    rule_y = banner_y - 1.10
    ax.plot([SZ_X_LO, SZ_X_HI], [rule_y, rule_y], color=RED, linewidth=2.5)

    hook_y = rule_y - 1.30
    ax.text(CX, hook_y, "$2.55 BILLION", color=GOLD, fontsize=70, fontweight="bold",
            ha="center", va="center", fontfamily="DejaVu Sans")

    sub_y = hook_y - 1.55
    ax.text(CX, sub_y, "The Facility Fee Scam", color=WHITE, fontsize=36, fontweight="bold",
            ha="center", va="center", fontfamily="DejaVu Sans")

    comp_y = sub_y - 0.98
    ax.text(CX, comp_y, "Same code, hospital-owned building: Medicare pays up to 3.8x more",
            color=TEAL, fontsize=16, ha="center", va="center", fontfamily="DejaVu Sans")

    stats_y = SZ_Y_LO + 0.15
    stats_text = ("SITE-NEUTRAL PAYMENT  ·  CMS OPPS + PFS CY2025 RATES  ·  "
                  "MEDPAC 2014-2026  ·  $519.35B TOTAL IDENTIFIED")
    ax.text(CX, stats_y, stats_text, color=LTGRAY, fontsize=10.5,
            ha="center", va="center", fontfamily="DejaVu Sans")

    fig.savefig(outpath, dpi=150, facecolor=NAVY, bbox_inches=None)
    plt.close(fig)
    print(f"Saved {outpath}")


if __name__ == "__main__":
    generate_chart1_site_differential(FIGURES / "chart1_site_differential.png")
    generate_chart2_regulatory_timeline(FIGURES / "chart2_regulatory_timeline.png")
    generate_chart3_savings_waterfall(FIGURES / "chart3_savings_waterfall.png")
    generate_chart4_savings_by_lever(FIGURES / "chart4_savings_by_lever.png")
    generate_chart5_savings_tracker(FIGURES / "chart5_savings_tracker.png")
    generate_hero(FIGURES / "hero_cover.png")

    print("\nAll 6 PNGs generated.")
    for f in sorted(FIGURES.glob("*.png")):
        print(f"  {f.name}: {f.stat().st_size:,} bytes")
