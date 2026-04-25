"""
Issue #09: The Employer Trap
Chart generation entry-point script.

Run as: python3 /path/to/issue_09/generate_all_charts.py

Produces:
  chart1_peer_group_variance.png
  chart2_schedule_a_c_scatter.png
  chart3_savings_decomposition.png
  chart4_savings_tracker.png  (also copied to ../figures/savings_tracker.png)
  hero_cover.png

Also copies hero to: ../figures/hero_issue_09.png
"""

import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['text.parse_math'] = False
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd
import json
import csv
from pathlib import Path

# === Paths ===
ISSUE_DIR = Path(__file__).resolve().parent
FIG_DIR = ISSUE_DIR / "figures"
RESULTS_DIR = ISSUE_DIR / "results"
FIGURES_GLOBAL = ISSUE_DIR.parent / "figures"

# Brand colors
NAVY = '#1A1F2E'
TEAL = '#0E8A72'
RED = '#B7182A'
GOLD = '#D4AF37'
WHITE = '#F8F8F6'
DARK_NAVY = '#111520'
MID_NAVY = '#252B3D'
LIGHT_GRAY = '#8890A0'

DPI_WORK = 100
DPI_SAVE = 150

# === Wipe figures directory ===
FIG_DIR.mkdir(exist_ok=True)
wiped = 0
for f in FIG_DIR.glob("*.png"):
    try:
        f.unlink()
        wiped += 1
    except PermissionError:
        pass  # will be overwritten on save
print(f"Figures directory wiped {wiped} files: {FIG_DIR}")


# ============================================================
# CHART 3 — Booked and Bounded Savings Decomposition
# (final summary chart; appears last in newsletter reading order)
# ============================================================
def chart3_savings_decomposition():
    with open(RESULTS_DIR / "savings_estimate_v2.json") as fh:
        data = json.load(fh)

    comp = data["components"]
    a = comp["A_direct_broker_excess"]["usd_bn"]        # 2.18
    b = comp["B_self_insured_broker_extension"]["usd_bn"]  # 2.77
    c_in = comp["C_v2_sch_c_admin_variance_in_sample"]["booked_usd_bn"]  # 1.68
    booked = a + b + c_in  # ~6.63

    # Range-high additions
    c_aggressive = comp["C_v2_sch_c_admin_variance_in_sample"]["aggressive_usd_bn"]  # 2.8
    c_extra = c_aggressive - c_in  # 1.12

    extrap = comp["C_v2_extrapolation_bounded"]["bounded_conservative_usd_bn"]  # 4.47
    range_high = booked + c_extra + extrap   # ~12.22

    print(f"Chart 3: booked={booked:.2f}B, range_high={range_high:.2f}B")

    # Use figsize with extra right margin for annotation
    fig, ax = plt.subplots(figsize=(10, 6), dpi=DPI_WORK)
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)

    bar_width = 0.5
    x_booked = 0.7
    x_range = 2.0

    # --- Booked bar (stacked: A + B + C) ---
    bottoms = [0, a, a + b]
    heights = [a, b, c_in]
    seg_colors = [TEAL, GOLD, RED]
    seg_short = ['A: $2.18B', 'B: $2.77B', 'C: $1.68B']

    for i, (bot, ht, col) in enumerate(zip(bottoms, heights, seg_colors)):
        ax.bar(x_booked, ht, bottom=bot, width=bar_width, color=col,
               edgecolor=NAVY, linewidth=1.5, zorder=3)
        mid = bot + ht / 2
        if ht >= 0.5:
            ax.text(x_booked, mid, seg_short[i],
                    ha='center', va='center', fontsize=9.5, fontweight='bold',
                    color=NAVY if col == GOLD else WHITE, zorder=4)

    # Booked total label above bar — at y=booked+0.5 to clear bar top
    ax.text(x_booked, booked + 0.55, '$6.6B BOOKED',
            ha='center', va='bottom', fontsize=13, fontweight='bold',
            color=WHITE, zorder=5)

    # --- Range ceiling bar ---
    for i, (bot, ht, col) in enumerate(zip(bottoms, heights, seg_colors)):
        ax.bar(x_range, ht, bottom=bot, width=bar_width, color=col,
               edgecolor=NAVY, linewidth=1.5, alpha=0.40, zorder=3)

    # C at 50% reducibility extension
    c_ext_bot = booked
    ax.bar(x_range, c_extra, bottom=c_ext_bot, width=bar_width,
           color=RED, edgecolor=NAVY, linewidth=1.5, alpha=0.80,
           hatch='///', zorder=3)
    ax.text(x_range, c_ext_bot + c_extra / 2,
            '+$1.12B  (C at 50%)',
            ha='center', va='center', fontsize=8, fontweight='bold',
            color=WHITE, zorder=4)

    # Bounded extrapolation extension
    extrap_bot = booked + c_extra
    ax.bar(x_range, extrap, bottom=extrap_bot, width=bar_width,
           color=TEAL, edgecolor=NAVY, linewidth=1.5, alpha=0.55,
           hatch='xxx', zorder=3)

    # Range ceiling label above bar — shifted right to avoid legend
    ax.text(x_range, range_high + 0.55, '$12.2B RANGE CEILING',
            ha='center', va='bottom', fontsize=13, fontweight='bold',
            color=TEAL, zorder=5)

    # Extrapolation annotation to the RIGHT of range bar
    ax.annotate('+$4.5B extrapolation\n(63M out-of-sample\nparticipants, NOT booked)',
                xy=(x_range + bar_width / 2, extrap_bot + extrap / 2),
                xytext=(x_range + 0.62, extrap_bot + extrap / 2),
                ha='left', va='center', fontsize=8, color=WHITE, zorder=6,
                arrowprops=dict(arrowstyle='->', color=TEAL, lw=1.0,
                                connectionstyle='arc3,rad=0.0'),
                bbox=dict(facecolor=DARK_NAVY, alpha=0.92, boxstyle='round,pad=0.35',
                          edgecolor=TEAL, linewidth=0.8))

    # Arrow from booked bar top to range bar at same level
    ax.annotate('',
                xy=(x_range - bar_width / 2 - 0.04, booked + 0.2),
                xytext=(x_booked + bar_width / 2 + 0.04, booked + 0.2),
                arrowprops=dict(arrowstyle='->', color=GOLD, lw=1.5))

    # Axis formatting
    ax.set_xlim(0.1, 3.7)
    ax.set_ylim(0, 15.5)
    ax.set_xticks([x_booked, x_range])
    ax.set_xticklabels(['Booked\n(Computed from data)',
                        'Range Ceiling\n(Bounded estimate)'],
                       fontsize=10, color=WHITE)
    ax.set_ylabel('Dollars (billions)', fontsize=10, color=WHITE, labelpad=8)
    ax.tick_params(colors=WHITE, labelsize=9)
    for spine in ax.spines.values():
        spine.set_edgecolor(MID_NAVY)
    ax.yaxis.grid(True, color=MID_NAVY, linewidth=0.5, alpha=0.6, zorder=0)
    ax.set_axisbelow(True)

    # Title — no subtitle line, just title at top with enough clearance
    ax.set_title('The Employer Trap: Booked and Bounded Savings Estimates\n'
                 'Issue #9  |  DOL Form 5500 Sch A and Sch C, 2023  |  8,180 health welfare plans',
                 fontsize=11, color=WHITE, fontweight='bold', pad=10,
                 linespacing=1.8)

    # Legend — placed BELOW the axis to avoid overlapping bars
    legend_items = [
        patches.Patch(color=TEAL, label='A: Broker commission above 3% DOL benchmark  ($2.18B)'),
        patches.Patch(color=GOLD, label='B: Self-insured broker extension  ($2.77B)'),
        patches.Patch(color=RED, label='C: Admin fee variance at 30% reducibility  ($1.68B booked; $2.80B at 50%)'),
        patches.Patch(facecolor=TEAL, hatch='xxx', alpha=0.55,
                      label='Bounded extrapolation to out-of-sample ERISA participants  (NOT booked)'),
    ]
    leg = ax.legend(handles=legend_items, loc='upper center',
                    bbox_to_anchor=(0.42, -0.10),
                    framealpha=0.9, frameon=True, fontsize=7.5,
                    edgecolor=MID_NAVY, facecolor=DARK_NAVY,
                    ncol=2)
    for text in leg.get_texts():
        text.set_color(WHITE)

    fig.text(0.10, 0.012,
             'Sources: DOL Form 5500 Sch A (7,036 plans) and Sch C (8,180 plans), 2023 Latest file. '
             'Range-high adds C at 50% reducibility ($1.12B) plus conservative bounded extrapolation '
             'to 63M out-of-sample ERISA participants ($4.47B). Not extrapolated to full ESI.',
             ha='left', fontsize=5.5, color=LIGHT_GRAY)

    plt.subplots_adjust(bottom=0.22, top=0.86, left=0.09, right=0.97)

    out_path = FIG_DIR / "chart3_savings_decomposition.png"
    fig.savefig(out_path, dpi=DPI_SAVE, facecolor=NAVY, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {out_path}")
    return out_path


# ============================================================
# CHART 1 — Admin Fees Per Participant by Peer Group
# (variance evidence; appears first in newsletter reading order)
# ============================================================
def chart1_peer_group_variance():
    df = pd.read_csv(RESULTS_DIR / "schedule_c_admin_variance.csv")

    # Build compact peer group labels (single-line to prevent overlap)
    size_short = {
        '1_micro (<100)': 'Micro',
        '2_small (100-499)': 'Small',
        '3_medium (500-2499)': 'Medium',
        '4_large (2500-9999)': 'Large',
        '5_jumbo (10000+)': 'Jumbo',
    }
    fund_short = {
        'fully_insured': 'FI',
        'mixed': 'Mixed',
        'self_insured': 'SI',
    }
    df['peer_label'] = df['size_band'].map(size_short) + ' / ' + df['fund_type'].map(fund_short)
    df['p75_p25'] = df['p75_over_p25_ratio']

    # Sort by p75/p25 ascending (extremes at top of horizontal chart)
    df = df.sort_values('p75_p25', ascending=True).reset_index(drop=True)

    # Overall weighted median
    overall_median = (df['admin_per_p_p50'] * df['n_plans']).sum() / df['n_plans'].sum()
    print(f"Chart 1: overall weighted median p50 = ${overall_median:.0f}")

    n_rows = len(df)
    # Taller figure: 0.45" per row + margins
    fig_h = min(9.0, max(6.0, n_rows * 0.45 + 2.5))
    fig, ax = plt.subplots(figsize=(10, fig_h), dpi=DPI_WORK)
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)

    y_positions = np.arange(n_rows)
    bar_height = 0.55

    for idx in range(n_rows):
        row = df.iloc[idx]
        y = y_positions[idx]
        p10 = row['admin_per_p_p10']
        p25 = row['admin_per_p_p25']
        p50 = row['admin_per_p_p50']
        p75 = row['admin_per_p_p75']
        p90 = row['admin_per_p_p90']
        ratio = row['p75_p25']

        iqr_color = RED if ratio > 20 else (GOLD if ratio > 8 else TEAL)
        ax.barh(y, p75 - p25, left=p25, height=bar_height * 0.55,
                color=iqr_color, alpha=0.80, zorder=3)

        ax.plot([p10, p25], [y, y], color=WHITE, linewidth=1.5, alpha=0.5, zorder=4)
        ax.plot([p75, p90], [y, y], color=WHITE, linewidth=1.5, alpha=0.5, zorder=4)
        ax.plot([p50, p50],
                [y - bar_height * 0.3, y + bar_height * 0.3],
                color=WHITE, linewidth=2.5, zorder=5)
        for cap_x in [p10, p90]:
            ax.plot([cap_x, cap_x],
                    [y - bar_height * 0.18, y + bar_height * 0.18],
                    color=WHITE, linewidth=1.2, alpha=0.5, zorder=4)

    # P75/P25 ratio annotations for top 2 only
    top2_idx = df['p75_p25'].nlargest(2).index.tolist()
    # Stagger annotations vertically
    xytext_offsets = [(3200, 0), (3200, 0)]  # will be adjusted below
    for rank, ti in enumerate(top2_idx):
        row = df.loc[ti]
        y = y_positions[ti]
        ratio = row['p75_p25']
        p90 = row['admin_per_p_p90']
        # Place annotation text at fixed x=3100 to avoid overlap with data
        ann_x = 3100
        ann_y = y + (0.5 if rank == 0 else -0.5)  # stagger vertically
        ax.annotate(f'P75/P25 = {ratio:.1f}x',
                    xy=(min(p90, 2800), y),
                    xytext=(ann_x, ann_y),
                    fontsize=8, color=RED, fontweight='bold',
                    va='center', ha='left',
                    arrowprops=dict(arrowstyle='->', color=RED, lw=1.0,
                                    connectionstyle='arc3,rad=0.2'),
                    bbox=dict(facecolor=DARK_NAVY, alpha=0.92,
                              boxstyle='round,pad=0.3', edgecolor=RED, linewidth=0.8),
                    zorder=7)

    # Overall median reference line — clipped to data range only (y=-0.5 to n_rows-0.5)
    ax.plot([overall_median, overall_median], [-0.4, n_rows - 0.5],
            color=GOLD, linewidth=1.5, linestyle='--', alpha=0.85, zorder=6)
    # Place median label at bottom
    ax.text(overall_median + 30, -0.75,
            f'Overall median: ${overall_median:.0f}/participant',
            ha='left', va='top', fontsize=7.5, color=GOLD,
            bbox=dict(facecolor=DARK_NAVY, alpha=0.90, boxstyle='round,pad=0.3',
                      edgecolor=GOLD, linewidth=0.7), zorder=7)

    ax.set_yticks(y_positions)
    ax.set_yticklabels(df['peer_label'], fontsize=8.5, color=WHITE)
    ax.set_xlabel('Admin Fees per Participant per Year (USD)', fontsize=10, color=WHITE, labelpad=8)
    ax.set_xlim(0, 4000)
    ax.set_ylim(-1.2, n_rows)
    ax.tick_params(colors=WHITE, labelsize=9)
    for spine in ax.spines.values():
        spine.set_edgecolor(MID_NAVY)
    ax.xaxis.grid(True, color=MID_NAVY, linewidth=0.5, alpha=0.5, zorder=0)
    ax.set_axisbelow(True)

    ax.set_title('')
    fig.suptitle('Plans of the Same Size and Type Pay Wildly Different Admin Fees',
                 fontsize=12, color=WHITE, fontweight='bold', y=0.997)
    fig.text(0.5, 0.960,
             'P10 / P25 / Median / P75 / P90 by peer group  |  8,180 health welfare plans  |  DOL Form 5500 Schedule C 2023',
             ha='center', fontsize=7.5, color=LIGHT_GRAY, va='top')

    # Legend (bottom-center below plot)
    from matplotlib.lines import Line2D
    legend_handles = [
        patches.Patch(color=TEAL, label='IQR: moderate variance (<8x)'),
        patches.Patch(color=GOLD, label='IQR: high variance (8-20x)'),
        patches.Patch(color=RED, label='IQR: extreme variance (>20x)'),
        Line2D([0], [0], color=WHITE, linewidth=2.5, label='Median (P50)'),
        Line2D([0], [0], color=GOLD, linewidth=1.5, linestyle='--', label='Overall weighted median'),
    ]
    leg = ax.legend(handles=legend_handles, loc='upper center',
                    bbox_to_anchor=(0.42, -0.10),
                    framealpha=0.90, frameon=True, fontsize=7.5,
                    edgecolor=MID_NAVY, facecolor=DARK_NAVY, ncol=5)
    for text in leg.get_texts():
        text.set_color(WHITE)

    fig.text(0.12, 0.005,
             'Source: DOL Form 5500 Schedule C, 2023. 8,180 health and medical benefit welfare plans (plan type 4A). '
             'Peer groups: participant-count band x funding type. FI=Fully Insured, SI=Self-Insured. '
             'Red cells (>20x P75/P25) reflect genuine within-peer fee variance.',
             ha='left', fontsize=5.5, color=LIGHT_GRAY)

    plt.subplots_adjust(bottom=0.14, top=0.93, left=0.15, right=0.97)

    out_path = FIG_DIR / "chart1_peer_group_variance.png"
    fig.savefig(out_path, dpi=DPI_SAVE, facecolor=NAVY, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {out_path}")
    return out_path


# ============================================================
# CHART 2 — Admin Fee by Broker Rate Quartile (boxplot)
# (appears second in newsletter reading order)
#
# Replaces the prior scatter design after reader feedback that the
# scatter was hard to interpret. The data actually shows a weak but
# real monotonic trend (Spearman rho = 0.20): Q1 median admin fee is
# $117, Q4 median is $376 (3.2x). The story is not "no relationship"
# — it's "the trend exists but within-quartile spread is much larger
# than the between-quartile shift, so broker rate is a weak predictor
# of admin fee." A boxplot communicates both pieces at once.
# ============================================================
def chart2_schedule_a_c_scatter():
    df = pd.read_csv(RESULTS_DIR / "schedule_a_c_linkage.csv")
    df = df.copy()
    df['broker_pct_disp'] = df['broker_pct'] * 100
    df['broker_q'] = pd.qcut(df['broker_pct'], 4, labels=['Q1', 'Q2', 'Q3', 'Q4'])

    pearson_r = float(df['broker_pct'].corr(df['admin_per_p'], method='pearson'))
    # Spearman = Pearson on ranks (avoids scipy dependency in the sandbox)
    spearman_rho = float(np.corrcoef(
        df['broker_pct'].rank().values,
        df['admin_per_p'].rank().values
    )[0, 1])

    quartiles = []
    for q, grp in df.groupby('broker_q', observed=True):
        admin = np.sort(grp['admin_per_p'].values)
        broker = grp['broker_pct_disp'].values
        quartiles.append({
            'q': q,
            'broker_min': float(broker.min()),
            'broker_max': float(broker.max()),
            'admin': admin,
            'p10': float(np.percentile(admin, 10)),
            'p25': float(np.percentile(admin, 25)),
            'p50': float(np.percentile(admin, 50)),
            'p75': float(np.percentile(admin, 75)),
            'p90': float(np.percentile(admin, 90)),
            'n': int(len(grp)),
        })

    print(f"Chart 2: medians by broker quartile = {[round(q['p50']) for q in quartiles]}")
    print(f"Chart 2: Pearson r={pearson_r:.3f}, Spearman rho={spearman_rho:.3f}")

    # ---- Figure ----
    Y_CAP = 1500  # cap visualization; whiskers/labels still indicate range above
    fig, ax = plt.subplots(figsize=(11, 6.5), dpi=DPI_WORK)
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)

    # Light gold tint highlighting the upward trend region — anchored by Q1 median
    ax.axhspan(quartiles[0]['p50'], quartiles[3]['p50'], xmin=0.05, xmax=0.95,
               facecolor=GOLD, alpha=0.05, zorder=1)

    # Box width and x positions
    box_x = [0.7, 1.7, 2.7, 3.7]
    half_w = 0.28

    for x_center, qd in zip(box_x, quartiles):
        # Strip plot — actual plan dots, jittered slightly
        rng = np.random.default_rng(seed=int(qd['n']) * 7919)
        jitter = rng.uniform(-half_w * 0.55, half_w * 0.55, size=qd['n'])
        admin_clipped = np.clip(qd['admin'], 0, Y_CAP)
        ax.scatter(x_center + jitter, admin_clipped, s=10, alpha=0.30,
                   c=TEAL, edgecolors='none', rasterized=True, zorder=2)

        # IQR box
        ax.add_patch(plt.Rectangle((x_center - half_w, qd['p25']),
                                    half_w * 2, qd['p75'] - qd['p25'],
                                    facecolor=TEAL, alpha=0.55,
                                    edgecolor=WHITE, linewidth=1.4, zorder=3))

        # Median line
        ax.plot([x_center - half_w, x_center + half_w], [qd['p50'], qd['p50']],
                color=WHITE, linewidth=2.4, zorder=5)

        # Whiskers (P10-P25 and P75-P90)
        ax.plot([x_center, x_center], [qd['p10'], qd['p25']],
                color=WHITE, linewidth=1.0, alpha=0.65, zorder=4)
        ax.plot([x_center, x_center], [qd['p75'], min(qd['p90'], Y_CAP)],
                color=WHITE, linewidth=1.0, alpha=0.65, zorder=4)
        for cap_y in [qd['p10'], min(qd['p90'], Y_CAP)]:
            ax.plot([x_center - half_w * 0.4, x_center + half_w * 0.4],
                    [cap_y, cap_y], color=WHITE, linewidth=1.0,
                    alpha=0.65, zorder=4)

        # Median value label
        ax.text(x_center, qd['p50'] - 35, f"${qd['p50']:.0f}",
                ha='center', va='top', fontsize=11, fontweight='bold',
                color=GOLD, zorder=7,
                bbox=dict(facecolor=DARK_NAVY, alpha=0.93,
                          boxstyle='round,pad=0.25',
                          edgecolor=GOLD, linewidth=0.8))

        # X-axis bin label (sample size + broker range)
        ax.text(x_center, -120,
                f"n = {qd['n']}\n{qd['broker_min']:.1f}% - {qd['broker_max']:.1f}%",
                ha='center', va='top', fontsize=8, color=LIGHT_GRAY, zorder=5)

    # Trend line connecting medians
    medians = [qd['p50'] for qd in quartiles]
    ax.plot(box_x, medians, color=GOLD, linewidth=2.0, alpha=0.9,
            marker='o', markersize=8, markeredgecolor=NAVY,
            markerfacecolor=GOLD, zorder=6)

    # "Median climbs from $X to $Y" callout — top right
    ax.annotate(
        f"Median climbs from ${quartiles[0]['p50']:.0f} to ${quartiles[3]['p50']:.0f}\n"
        f"(a {quartiles[3]['p50'] / quartiles[0]['p50']:.1f}x range)",
        xy=(box_x[3], quartiles[3]['p50']),
        xytext=(3.3, Y_CAP * 0.93),
        ha='right', va='top', fontsize=9.5, fontweight='bold', color=GOLD,
        bbox=dict(facecolor=DARK_NAVY, alpha=0.93,
                  boxstyle='round,pad=0.4',
                  edgecolor=GOLD, linewidth=1.1),
        arrowprops=dict(arrowstyle='->', color=GOLD, lw=1.2,
                        connectionstyle='arc3,rad=-0.18'),
        zorder=10)

    # "But within-quartile spread..." callout — left side
    spread_q4 = quartiles[3]['p90'] - quartiles[3]['p10']
    shift_q1_to_q4 = quartiles[3]['p50'] - quartiles[0]['p50']
    ax.text(1.1, Y_CAP * 0.65,
            "But within-quartile spread\nis larger than the trend.\n\n"
            f"Q4 spans ${quartiles[3]['p10']:.0f} to ${min(quartiles[3]['p90'], Y_CAP):.0f}+ (P10-P90).\n"
            f"Median shift across all four\nquartiles: ${shift_q1_to_q4:.0f}.",
            ha='left', va='top', fontsize=9, color=WHITE,
            bbox=dict(facecolor=DARK_NAVY, alpha=0.92,
                      boxstyle='round,pad=0.4',
                      edgecolor=MID_NAVY, linewidth=0.8),
            zorder=10)

    # Axis formatting
    ax.set_xlim(0.0, 4.4)
    ax.set_ylim(-180, Y_CAP * 1.03)
    ax.set_xticks(box_x)
    ax.set_xticklabels(['Q1\n(lowest broker)', 'Q2', 'Q3', 'Q4\n(highest broker)'],
                       color=WHITE, fontsize=10, fontweight='bold')
    ax.set_ylabel('Admin fee per participant per year ($)',
                  fontsize=10, color=WHITE, labelpad=8)
    ax.set_xlabel('Broker rate quartile  (% of premium, Schedule A)',
                  fontsize=10, color=WHITE, labelpad=24)
    ax.tick_params(colors=WHITE, labelsize=9)
    for spine in ax.spines.values():
        spine.set_edgecolor(MID_NAVY)
    ax.yaxis.grid(True, color=MID_NAVY, linewidth=0.45, alpha=0.45, zorder=0)
    ax.set_axisbelow(True)

    # Title and subtitle
    fig.suptitle("Plans That Pay More for Brokers Pay Modestly More for Admin",
                 fontsize=13, color=WHITE, fontweight='bold', y=0.985)
    fig.text(0.5, 0.935,
             f"n=425 plans grouped into broker-rate quartiles. "
             f"Within-group spread dominates the between-group trend. "
             f"Pearson r = {pearson_r:.3f}, Spearman rho = {spearman_rho:.3f}.",
             ha='center', va='top', fontsize=8.5, color=LIGHT_GRAY)

    # Footer / source
    fig.text(0.07, 0.013,
             "Source: DOL Form 5500 Schedule A and Schedule C, 2023 Latest file. n=425 plans filing both disclosures. "
             "Boxes show IQR (P25-P75); white horizontal line is the median; whiskers extend to P10 and P90. "
             f"Y-axis capped at ${Y_CAP:,}; Q4's P90 reaches above the cap. Each dot is one plan.",
             ha='left', fontsize=5.5, color=LIGHT_GRAY)

    plt.subplots_adjust(bottom=0.16, top=0.85, left=0.085, right=0.985)

    out_path = FIG_DIR / "chart2_schedule_a_c_scatter.png"
    fig.savefig(out_path, dpi=DPI_SAVE, facecolor=NAVY, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {out_path}")
    return out_path


# ============================================================
# CHART 4 — Running Savings Tracker
# (cumulative $435.2B across 9 issues; appears in the closing
#  Savings Tracker section of the newsletter)
# Adapted from issue_08/chart4_savings_tracker.py with:
#   - new $3.24T denominator (CMS NHE 2024 final)
#   - Issue #9 Employer Trap segment ($6.6B) appended
#   - 9-segment palette
# ============================================================
def chart4_savings_tracker():
    import matplotlib.patches as mpatches
    from matplotlib.lines import Line2D

    # White-background palette (this chart uses the published-tracker
    # white-background look, distinct from the dark-navy charts above)
    BLUE      = '#1B6CA8'
    BLUE_DARK = '#154E80'
    BLUE_LITE = '#D6E8F7'
    RED2      = '#B7182A'
    RED2_DARK = '#8A1020'
    TEAL2     = '#0E8A72'
    TEAL2_DK  = '#096B59'
    GOLD2     = '#E8A020'
    GOLD2_LT  = '#FFF3CC'
    PURPLE    = '#6B46C1'
    PURPLE_DK = '#553C9A'
    ORANGE2   = '#D97706'
    ORANGE2_DK= '#B45309'
    EMERALD   = '#059669'
    EMERALD_DK= '#047857'
    CRIMSON2  = '#DC2626'
    CRIMSON_DK= '#991B1B'
    INDIGO    = '#4338CA'
    INDIGO_DK = '#3730A3'
    DARK2     = '#1A202C'
    MID       = '#4A5568'
    WHITE_W   = '#FFFFFF'

    TARGET_TRILLIONS = 3.24
    TARGET_B = TARGET_TRILLIONS * 1000  # 3240

    issues = [
        {"num": 1, "title": "OTC",        "savings": 0.6,  "fill": BLUE_DARK,  "label_col": BLUE_DARK},
        {"num": 2, "title": "Drug",       "savings": 25.0, "fill": BLUE,       "label_col": BLUE_DARK},
        {"num": 3, "title": "Hospitals",  "savings": 73.0, "fill": RED2,       "label_col": RED2_DARK},
        {"num": 4, "title": "PBM",        "savings": 30.0, "fill": TEAL2,      "label_col": TEAL2_DK},
        {"num": 5, "title": "Admin",      "savings": 200.0,"fill": PURPLE,     "label_col": PURPLE_DK},
        {"num": 6, "title": "Supply",     "savings": 28.0, "fill": ORANGE2,    "label_col": ORANGE2_DK},
        {"num": 7, "title": "GLP-1",      "savings": 40.0, "fill": EMERALD,    "label_col": EMERALD_DK},
        {"num": 8, "title": "Denial",     "savings": 32.0, "fill": CRIMSON2,   "label_col": CRIMSON_DK},
        {"num": 9, "title": "Employer",   "savings": 6.6,  "fill": INDIGO,     "label_col": INDIGO_DK},
    ]

    cum = 0.0
    milestones = []
    for it in issues:
        cum += it["savings"]
        milestones.append({**it, "cumulative": cum, "pct": cum / TARGET_B * 100})

    total_b = milestones[-1]["cumulative"]   # 435.2
    total_pct = milestones[-1]["pct"]        # 13.4

    ZOOM_B = 500.0  # zoom window for the bottom panel

    fig = plt.figure(figsize=(14, 5.8))
    fig.patch.set_facecolor(WHITE_W)

    ax_ctx  = fig.add_axes([0.04, 0.72, 0.88, 0.13])
    ax_zoom = fig.add_axes([0.04, 0.14, 0.88, 0.34])
    for ax in (ax_ctx, ax_zoom):
        ax.set_facecolor(WHITE_W)
        ax.axis('off')

    # ── Panel A: full $3.24T context bar ────────────────────────────────
    ax_ctx.set_xlim(0, TARGET_B)
    ax_ctx.set_ylim(0, 1)
    CTX_Y, CTX_H = 0.15, 0.60

    # Background goal bar
    ax_ctx.add_patch(mpatches.FancyBboxPatch(
        (0, CTX_Y), TARGET_B, CTX_H, boxstyle="round,pad=0",
        linewidth=0.8, facecolor=BLUE_LITE, edgecolor=BLUE_DARK, zorder=1))

    # Per-issue stacked slivers (min width so smallest issues are visible)
    seg_start = 0.0
    for m in milestones:
        seg_w = max(m["savings"], TARGET_B * 0.003)
        ax_ctx.add_patch(mpatches.FancyBboxPatch(
            (seg_start, CTX_Y), seg_w, CTX_H, boxstyle="round,pad=0",
            linewidth=0, facecolor=m["fill"], zorder=2))
        seg_start += m["savings"]

    # Gold zoom-window highlight (covers the $0-$500B range that's expanded below)
    ax_ctx.add_patch(mpatches.FancyBboxPatch(
        (0, CTX_Y - 0.04), ZOOM_B, CTX_H + 0.08, boxstyle="round,pad=0",
        linewidth=1.5, facecolor=GOLD2_LT, edgecolor=GOLD2, alpha=0.70, zorder=3))

    # Re-draw slivers on top of the gold tint so they remain saturated
    seg_start = 0.0
    for m in milestones:
        seg_w = max(m["savings"], TARGET_B * 0.003)
        ax_ctx.add_patch(mpatches.FancyBboxPatch(
            (seg_start, CTX_Y), seg_w, CTX_H, boxstyle="round,pad=0",
            linewidth=0, facecolor=m["fill"], zorder=4))
        seg_start += m["savings"]

    ax_ctx.text(ZOOM_B / 2, CTX_Y + CTX_H + 0.08, '↓ zoomed below',
                ha='center', va='bottom', fontsize=7.5, color=GOLD2,
                fontweight='bold', zorder=6)
    ax_ctx.text(0, CTX_Y - 0.08, '$0',
                ha='left', va='top', fontsize=8, color=MID, fontweight='bold')
    ax_ctx.text(TARGET_B, CTX_Y + CTX_H / 2, '  $3.24T\n  goal',
                ha='left', va='center', fontsize=8.5, color=MID,
                fontweight='bold', linespacing=1.3)
    ax_ctx.text(total_b + TARGET_B * 0.006, CTX_Y + CTX_H / 2,
                f'${total_b:.1f}B\n({total_pct:.1f}%)',
                ha='left', va='center', fontsize=8, color=BLUE_DARK,
                fontweight='bold')

    # ── Panel B: zoomed $500B window ────────────────────────────────────
    ax_zoom.set_xlim(0, ZOOM_B)
    ax_zoom.set_ylim(0, 1)
    ZM_Y, ZM_H = 0.34, 0.28

    ax_zoom.add_patch(mpatches.FancyBboxPatch(
        (0, ZM_Y), ZOOM_B, ZM_H, boxstyle="round,pad=0",
        linewidth=0.8, facecolor=BLUE_LITE, edgecolor=BLUE_DARK, zorder=1))

    seg_start = 0.0
    for m in milestones:
        ax_zoom.add_patch(mpatches.FancyBboxPatch(
            (seg_start, ZM_Y), m["savings"], ZM_H, boxstyle="round,pad=0",
            linewidth=0, facecolor=m["fill"], zorder=2))
        seg_start += m["savings"]

    # White segment dividers (between each issue's segment in the zoom)
    seg_start = 0.0
    for m in milestones[:-1]:
        seg_start += m["savings"]
        ax_zoom.plot([seg_start, seg_start],
                     [ZM_Y - 0.04, ZM_Y + ZM_H + 0.04],
                     color=WHITE_W, linewidth=2, zorder=4)

    # Per-issue labels alternating above/below the bar to avoid collision
    seg_start = 0.0
    for i, m in enumerate(milestones):
        seg_end = seg_start + m["savings"]
        above = (i % 2 == 0)
        x_mid = seg_start + m["savings"] / 2

        ax_zoom.scatter([seg_end], [ZM_Y + ZM_H / 2], s=90,
                        color=WHITE_W, edgecolors=m["label_col"],
                        linewidths=1.8, zorder=5)

        MARGIN = ZOOM_B * 0.04
        x_label = max(min(x_mid, ZOOM_B - MARGIN), MARGIN)

        if above:
            label_y = ZM_Y + ZM_H + 0.05
            va = 'bottom'
            line_y0, line_y1 = ZM_Y + ZM_H + 0.02, label_y - 0.01
        else:
            label_y = ZM_Y - 0.05
            va = 'top'
            line_y0, line_y1 = ZM_Y - 0.02, label_y + 0.01

        ax_zoom.plot([x_label, x_label], [line_y0, line_y1],
                     color=m["label_col"], linewidth=1.2,
                     linestyle='dotted', zorder=3)

        delta_txt = f'+${m["savings"]:.1f}B' if i > 0 else f'${m["savings"]:.1f}B'
        # Mark Issue #9 (current) with bold "(this issue)" tag for emphasis
        suffix = '\n(this issue)' if m["num"] == 9 else ''
        label_txt = f'#{m["num"]}  {delta_txt}\n= ${m["cumulative"]:.1f}B{suffix}'
        ax_zoom.text(x_label, label_y, label_txt,
                     ha='center', va=va, fontsize=8, fontweight='bold',
                     color=m["label_col"], linespacing=1.3,
                     bbox=dict(boxstyle='round,pad=0.3', facecolor=WHITE_W,
                               edgecolor=m["label_col"],
                               linewidth=1.6 if m["num"] == 9 else 1.1),
                     zorder=6)

        seg_start = seg_end

    # Running total annotation at end of bar
    ax_zoom.text(total_b + ZOOM_B * 0.01, ZM_Y + ZM_H / 2,
                 f'${total_b:.1f}B\n({total_pct:.1f}%)',
                 ha='left', va='center', fontsize=9,
                 fontweight='bold', color=DARK2, zorder=6)

    # Remaining space label only when the empty tail is wide enough that
    # the italic label doesn't collide with the running-total badge to its
    # left. At ~13% remaining ($435B of $500B) the badges overlap, so the
    # threshold sits at 18%.
    remaining = ZOOM_B - total_b
    if remaining > ZOOM_B * 0.18:
        ax_zoom.text(total_b + remaining / 2, ZM_Y + ZM_H / 2,
                     f'...{remaining:.0f}B more\nto fill this window',
                     ha='center', va='center', fontsize=8, color=MID,
                     style='italic', zorder=3)

    # Axis labels for zoom panel
    ax_zoom.text(0, ZM_Y - 0.17, '$0',
                 ha='left', va='top', fontsize=8.5, color=MID,
                 fontweight='bold')
    ax_zoom.text(ZOOM_B, ZM_Y - 0.17, f'${ZOOM_B:.0f}B',
                 ha='right', va='top', fontsize=8.5, color=MID,
                 fontweight='bold')
    ax_zoom.text(ZOOM_B / 2, ZM_Y - 0.17,
                 f'Savings Tracker -- Zoom: ${ZOOM_B:.0f}B Window',
                 ha='center', va='top', fontsize=8, color=GOLD2,
                 fontweight='bold')

    # Bracket lines connecting context bar zoom region to the expanded panel
    fig.canvas.draw()
    fig_w_px, fig_h_px = fig.get_size_inches() * fig.dpi
    ctx_left_px  = ax_ctx.transData.transform((0,      CTX_Y))
    ctx_right_px = ax_ctx.transData.transform((ZOOM_B, CTX_Y))
    zm_left_px   = ax_zoom.transData.transform((0,      ZM_Y + ZM_H))
    zm_right_px  = ax_zoom.transData.transform((ZOOM_B, ZM_Y + ZM_H))
    def to_frac(px): return (px[0] / fig_w_px, px[1] / fig_h_px)
    for ctx_px, zm_px in [(ctx_left_px, zm_left_px), (ctx_right_px, zm_right_px)]:
        cx, cy = to_frac(ctx_px); zx, zy = to_frac(zm_px)
        fig.add_artist(Line2D([cx, zx], [cy, zy], transform=fig.transFigure,
                              color=GOLD2, linewidth=1.2, linestyle='--',
                              alpha=0.75))

    fig.text(0.50, 0.985,
             'The American Healthcare Conundrum -- Running Savings Tracker',
             ha='center', va='top', fontsize=13, fontweight='bold', color=DARK2)
    fig.text(0.50, 0.952,
             f'Total identified: ${total_b:.1f}B / ~$3.24T annual US-Japan spending gap '
             f'({total_pct:.1f}%) -- denominator updated CMS NHE 2024 final',
             ha='center', va='top', fontsize=9, color=MID)

    fig.text(0.50, 0.01,
             'Issue #1: OTC step therapy ($0.6B)  |  Issue #2: International drug reference pricing ($25.0B)  |  '
             'Issue #3: Commercial hospital reference pricing ($73.0B)  |  Issue #4: PBM reform ($30.0B)  |  '
             'Issue #5: Admin waste reduction ($200.0B)  |  Issue #6: Hospital supply waste ($28.0B)  |  '
             'Issue #7: GLP-1 pricing ($40.0B)  |  Issue #8: Denial machine ($32.0B)  |  '
             'Issue #9: Employer broker and admin-fee variance ($6.6B; this issue).  '
             'Savings are non-overlapping; conservative estimates.',
             ha='center', va='bottom', fontsize=6.0, color=MID, style='italic')

    out_local  = FIG_DIR / "chart4_savings_tracker.png"
    out_global = FIGURES_GLOBAL / "savings_tracker.png"
    FIGURES_GLOBAL.mkdir(exist_ok=True)
    for out_path in (out_local, out_global):
        fig.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=WHITE_W)
        print(f"Saved: {out_path}")
    plt.close(fig)
    print(f"  Total: ${total_b:.1f}B  ({total_pct:.1f}% of $3.24T)")
    return out_local


# ============================================================
# HERO IMAGE — Issue #9
# ============================================================
def hero_issue_09():
    W_IN = 14.56
    H_IN = 10.48
    DPI_WORK_H = 72
    DPI_SAVE_H = 150

    fig = plt.figure(figsize=(W_IN, H_IN), dpi=DPI_WORK_H, facecolor=NAVY)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_facecolor(NAVY)
    ax.axis('off')

    # Subtle grid
    for i in range(0, 101, 5):
        ax.axhline(i, color=MID_NAVY, linewidth=0.3, alpha=0.5)
        ax.axvline(i, color=MID_NAVY, linewidth=0.3, alpha=0.5)

    # Series branding top center (inside safe zone, top edge ~76)
    ax.text(50, 74, 'THE AMERICAN HEALTHCARE CONUNDRUM',
            fontsize=11, color=RED, fontweight='bold', ha='center', va='center',
            fontfamily='sans-serif')
    ax.text(50, 70.5, 'ISSUE #9', fontsize=9, color=GOLD,
            ha='center', va='center', fontfamily='sans-serif')
    ax.plot([30, 70], [67.5, 67.5], color=RED, linewidth=1.5, alpha=0.7)

    # Main hook number
    ax.text(50, 58, '$6.6 BILLION',
            fontsize=50, color=WHITE, fontweight='bold', ha='center', va='center',
            fontfamily='sans-serif')
    ax.text(50, 51, 'PER YEAR',
            fontsize=22, color=GOLD, fontweight='bold', ha='center', va='center',
            fontfamily='sans-serif')

    # Subtitle
    ax.text(50, 44.5, 'THE EMPLOYER TRAP',
            fontsize=17, color=TEAL, fontweight='bold', ha='center', va='center',
            fontfamily='sans-serif')
    ax.text(50, 40.5, 'Employer plans overpaying brokers and administrators,',
            fontsize=11, color=WHITE, ha='center', va='center',
            fontfamily='sans-serif', alpha=0.85)
    ax.text(50, 37.5, 'computed plan-by-plan from 8,180 ERISA health welfare plans.',
            fontsize=11, color=WHITE, ha='center', va='center',
            fontfamily='sans-serif', alpha=0.85)

    # Bottom stats bar (inside safe zone, bottom edge ~24)
    ax.text(50, 29.5, '$12.47B disclosed  |  23.8M participants  |  DOL Form 5500 Schedule C 2023  |  First public plan-level analysis post-CAA 2021',
            fontsize=8.5, color=WHITE, ha='center', va='center',
            fontfamily='sans-serif', alpha=0.5)

    # Running total tag
    ax.text(50, 25.5, 'Running total: $435.2B identified across 9 issues  (13.4% of $3.24T gap)',
            fontsize=9, color=TEAL, ha='center', va='center',
            fontfamily='sans-serif', alpha=0.8)

    out_path = FIG_DIR / "hero_cover.png"
    fig.savefig(out_path, dpi=DPI_SAVE_H, facecolor=NAVY, bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    print(f"Saved: {out_path}")

    # Also copy to global figures directory
    FIGURES_GLOBAL.mkdir(exist_ok=True)
    global_path = FIGURES_GLOBAL / "hero_issue_09.png"
    import shutil
    shutil.copy2(out_path, global_path)
    print(f"Copied to: {global_path}")
    return out_path


# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    print("=== Issue #9 Chart Generation ===\n")
    # Charts numbered by reading order in the newsletter:
    # Chart 1 = peer-group variance, Chart 2 = boxplot by quartile,
    # Chart 3 = savings decomposition, Chart 4 = running savings tracker.
    chart1_peer_group_variance()
    chart2_schedule_a_c_scatter()
    chart3_savings_decomposition()
    chart4_savings_tracker()
    hero_issue_09()
    print(f"\nAll charts saved to: {FIG_DIR}")
    pngs = list(FIG_DIR.glob("*.png"))
    print(f"Files produced: {[p.name for p in sorted(pngs)]}")
    print(f"Count: {len(pngs)} PNGs")
