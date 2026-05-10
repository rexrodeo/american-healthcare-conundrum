"""
generate_all_charts.py — Issue #11: The MA Overpayment
=======================================================
Single entry-point script that wipes figures/*.png and regenerates
all charts for Issue #11.

Charts produced:
  chart1_v24_v28_band.png       — V24/V28/blended coding-intensity by year 2023-2026
  chart2_hra_share_trajectory.png — HRA yield share of coding-intensity overpayment
  chart3_state_allocation.png   — Top-10 state allocation, 2025 anchor year
  chart4_qui_tam_timeline.png   — MA risk-adjustment FCA settlement timeline 2018-2026
  chart5_savings_tracker.png    — Running total across all 11 issues
  hero_cover.png                — 1456x1048 social preview hero image

Usage:
  python3 /Users/minirex/healthcare/issue_11/generate_all_charts.py
"""

import matplotlib
matplotlib.use('Agg')
# Disable LaTeX and mathtext so $ signs render as literal dollar signs
matplotlib.rcParams['text.usetex'] = False
matplotlib.rcParams['text.parse_math'] = False
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.ticker as mticker
import numpy as np
import csv
import json
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
FIGURES = HERE / "figures"
FIGURES.mkdir(exist_ok=True)

# Wipe existing PNGs (clean rebuild)
# Note: on overlayfs mounts, deletion may be blocked; we overwrite in-place.
import os
import subprocess
existing = list(FIGURES.glob("*.png"))
removed = 0
for f in existing:
    try:
        f.unlink()
        removed += 1
    except OSError:
        pass  # overlayfs: file will be overwritten by savefig
print(f"Wiped {removed}/{len(existing)} figures/*.png — remainder will be overwritten")

# ── Brand Colors ─────────────────────────────────────────────────────────────
NAVY     = '#1A1F2E'
TEAL     = '#0E8A72'
RED      = '#B7182A'
GOLD     = '#D4AF37'
WHITE    = '#F8F8F6'
MID_NAVY = '#252B3D'
LIGHT    = '#8B9DC3'

# ── Helper: footnote placement ────────────────────────────────────────────────
def add_footnote(fig, text, y=0.02):
    fig.text(0.12, y, text, ha='left', va='bottom',
             fontsize=6.0, color=LIGHT, fontfamily='sans-serif', wrap=True)


# ══════════════════════════════════════════════════════════════════════════════
# CHART 1 — V24/V28/Blended coding-intensity band, 2023–2026
# ══════════════════════════════════════════════════════════════════════════════
def chart1_v24_v28_band():
    # Load data
    rows = []
    with open(RESULTS / "coding_intensity_timeseries.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yr = int(row['year'])
            if yr >= 2023:
                rows.append({
                    'year': yr,
                    'blended': float(row['coding_post_statutory_bn']) if row['coding_post_statutory_bn'] else None,
                    'v24': float(row['coding_v24only_bn']) if row['coding_v24only_bn'] else None,
                    'v28': float(row['coding_v28only_bn']) if row['coding_v28only_bn'] else None,
                })
    rows.sort(key=lambda r: r['year'])

    years   = [r['year'] for r in rows]
    blended = [r['blended'] for r in rows]
    v24     = [r['v24']     for r in rows]
    v28     = [r['v28']     for r in rows]

    # For fill_between: only use years where both v24 and v28 exist (2024-2026)
    band_rows = [r for r in rows if r['v24'] is not None and r['v28'] is not None]
    band_x   = np.array([r['year']    for r in band_rows])
    band_v24 = np.array([r['v24']     for r in band_rows], dtype=float)
    band_v28 = np.array([r['v28']     for r in band_rows], dtype=float)

    # For line plots: filter out None values per series
    years_all    = [r['year']    for r in rows]
    blended_all  = [r['blended'] for r in rows]   # all years have blended
    v24_rows     = [(r['year'], r['v24'])  for r in rows if r['v24'] is not None]
    v28_rows     = [(r['year'], r['v28'])  for r in rows if r['v28'] is not None]

    v24_x = [t[0] for t in v24_rows]
    v24_y = [t[1] for t in v24_rows]
    v28_x = [t[0] for t in v28_rows]
    v28_y = [t[1] for t in v28_rows]

    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=100, facecolor=NAVY)
    ax.set_facecolor(NAVY)
    fig.patch.set_facecolor(NAVY)

    # Shaded band between v28 and v24 (only where both exist: 2024-2026)
    ax.fill_between(band_x, band_v28, band_v24, color=TEAL, alpha=0.15, label='_nolegend_')

    # Three lines — use filtered arrays to avoid plotting None values
    ax.plot(v24_x, v24_y, color=RED, linewidth=2.5, marker='o', markersize=7,
            label='V24-only (upper bound)', zorder=5)
    ax.plot(years_all, blended_all, color=GOLD, linewidth=2.8, marker='D', markersize=8,
            label='Blended / MedPAC booked', zorder=6, linestyle='--')
    ax.plot(v28_x, v28_y, color=TEAL, linewidth=2.5, marker='s', markersize=7,
            label='V28-only (lower bound)', zorder=5)

    # ── Explicit annotations at 2025 highlight ────────────────────────────────
    # 2025 values: V24=$44.8B, blended=$28.0B, V28=$19.2B
    anno_x = 2025
    anno_idx = v24_x.index(anno_x)

    # Lookup y-values at 2025 by index
    v24_2025     = v24_y[anno_idx]
    blended_2025 = blended_all[years_all.index(anno_x)]
    v28_idx_2025 = v28_x.index(anno_x)
    v28_2025     = v28_y[v28_idx_2025]

    # V24 label — above the point
    ax.annotate('$44.8B\n(V24-only)',
                xy=(anno_x, v24_2025),
                xytext=(anno_x - 0.55, v24_2025 + 4.5),
                fontsize=8.5, fontweight='bold', color=RED, ha='center',
                arrowprops=dict(arrowstyle='->', color=RED, lw=1.2),
                bbox=dict(boxstyle='round,pad=0.3', facecolor=NAVY, alpha=0.9, edgecolor=RED, lw=0.8))

    # Blended label — placed below the V28 line in clear space; leader points up to the gold dot
    ax.annotate('$28.0B\n(blended)',
                xy=(anno_x, blended_2025),
                xytext=(anno_x + 0.55, 11),
                fontsize=8.5, fontweight='bold', color=GOLD, ha='center',
                arrowprops=dict(arrowstyle='->', color=GOLD, lw=1.2),
                bbox=dict(boxstyle='round,pad=0.3', facecolor=NAVY, alpha=0.9, edgecolor=GOLD, lw=0.8))

    # V28 label — below the point
    ax.annotate('$19.2B\n(V28-only)',
                xy=(anno_x, v28_2025),
                xytext=(anno_x - 0.55, v28_2025 - 6.0),
                fontsize=8.5, fontweight='bold', color=TEAL, ha='center',
                arrowprops=dict(arrowstyle='->', color=TEAL, lw=1.2),
                bbox=dict(boxstyle='round,pad=0.3', facecolor=NAVY, alpha=0.9, edgecolor=TEAL, lw=0.8))

    # Band width callout for 2025
    ax.annotate('', xy=(anno_x + 0.08, v28_2025),
                xytext=(anno_x + 0.08, v24_2025),
                arrowprops=dict(arrowstyle='<->', color=WHITE, lw=1.0, alpha=0.5))
    ax.text(anno_x + 0.25, (v24_2025 + v28_2025) / 2,
            '$25.6B\nband',
            fontsize=7, color=WHITE, alpha=0.7, ha='left', va='center',
            fontfamily='sans-serif')

    # Axes styling
    ax.set_xticks(years)
    ax.set_xticklabels([str(y) for y in years], color=WHITE, fontsize=11)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v:.0f}B'))
    ax.tick_params(colors=WHITE, labelsize=10)
    ax.spines[:].set_color(MID_NAVY)
    ax.set_facecolor(NAVY)
    ax.yaxis.label.set_color(WHITE)
    ax.xaxis.label.set_color(WHITE)
    ax.set_ylim(0, 60)
    ax.set_xlim(2022.5, 2026.7)
    ax.set_ylabel('$ Billions / Year', color=WHITE, fontsize=10, labelpad=8)

    # Grid
    ax.yaxis.set_minor_locator(mticker.MultipleLocator(5))
    ax.grid(axis='y', color=MID_NAVY, linewidth=0.6, alpha=0.7)

    # Legend — moved to lower-left to avoid the V24 line approaching $51B at 2026
    leg = ax.legend(loc='lower left', fontsize=8.5, framealpha=0.85,
                    facecolor=MID_NAVY, edgecolor=LIGHT, labelcolor=WHITE)

    # Titles
    fig.suptitle('Medicare Advantage Coding-Intensity Overpayment\nV24 vs. V28 Model Sensitivity Band, 2023–2026',
                 fontsize=12, fontweight='bold', color=WHITE, y=0.97,
                 fontfamily='sans-serif')

    plt.subplots_adjust(top=0.87, bottom=0.13, left=0.10, right=0.97)

    add_footnote(fig,
        'Sources: MedPAC March 2026 Report Ch.12 (blended/booked values); '
        'V24-only and V28-only counterfactuals computed by this analysis '
        'from CMS Rate Announcement trend applied to Part C payment pool. '
        'The American Healthcare Conundrum  Issue #11',
        y=0.02)

    out = FIGURES / "chart1_v24_v28_band.png"
    fig.savefig(out, dpi=150, facecolor=NAVY, bbox_inches=None)
    plt.close(fig)
    print(f"Saved {out.name}")
    return out


# ══════════════════════════════════════════════════════════════════════════════
# CHART 2 — HRA share of coding-intensity overpayment, 2017–2026
# ══════════════════════════════════════════════════════════════════════════════
def chart2_hra_share_trajectory():
    rows = []
    with open(RESULTS / "hra_decomposition.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                'year': int(row['year']),
                'share': float(row['hra_share_of_national_coding_pct']),
                'status': row['status'],
                'total_hra': float(row['total_hra_yield_bn']),
            })

    years  = [r['year']  for r in rows]
    shares = [r['share'] for r in rows]

    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=100, facecolor=NAVY)
    ax.set_facecolor(NAVY)
    fig.patch.set_facecolor(NAVY)

    # Shade "small denominator / qualified" era (2017 only) vs "stable" (2023+)
    # NOTE: italic "Small-denominator era" caption removed because the data line
    # passed through it; the same qualifier is in the 65% callout box instead.
    ax.axvspan(2016.5, 2020.5, color=MID_NAVY, alpha=0.5, label='_nolegend_')
    ax.axvspan(2020.5, 2026.5, color=NAVY, alpha=1.0, label='_nolegend_')
    # Phase-out label shifted right of the dashed line to avoid overlap
    ax.text(2025.6, 43,
            'CMS-4185-F2\nphase-out\nbegins 2025',
            fontsize=7.5, color=GOLD, ha='center', va='center',
            fontstyle='italic', fontfamily='sans-serif',
            bbox=dict(boxstyle='round,pad=0.2', facecolor=NAVY, alpha=0.85,
                      edgecolor='none'))

    # Phase-out start vertical line
    ax.axvline(2024.5, color=GOLD, linewidth=1.4, linestyle=':', alpha=0.8)

    # Main line
    ax.plot(years, shares, color=TEAL, linewidth=2.8, marker='o', markersize=9,
            zorder=5)

    # Annotate observed points
    obs_style = dict(fontsize=8.5, fontweight='bold', color=WHITE,
                     fontfamily='sans-serif')

    # 2017: 65% — label above, flag as qualified
    ax.annotate('65.0%\n(OIG observed;\nsmall denominator)',
                xy=(2017, 65.0), xytext=(2018.7, 62),
                fontsize=7.5, color=LIGHT, ha='center',
                arrowprops=dict(arrowstyle='->', color=LIGHT, lw=0.9),
                bbox=dict(boxstyle='round,pad=0.25', facecolor=MID_NAVY, alpha=0.9,
                          edgecolor=LIGHT, lw=0.7))

    # 2023: 19.7% — observed; placed below the line in clear space, leader points up-right
    ax.annotate('19.7%\n(OIG observed\n2023)',
                xy=(2023, 19.7), xytext=(2021.5, 9),
                fontsize=8.0, color=TEAL, fontweight='bold', ha='center',
                arrowprops=dict(arrowstyle='->', color=TEAL, lw=1.1),
                bbox=dict(boxstyle='round,pad=0.3', facecolor=NAVY, alpha=0.95,
                          edgecolor=TEAL, lw=0.8))

    # 2025: 19.1%
    ax.annotate('19.1%\n(2025 projected\n50% retained)',
                xy=(2025, 19.1), xytext=(2025, 32),
                fontsize=8.0, color=WHITE, ha='center',
                arrowprops=dict(arrowstyle='->', color=WHITE, lw=1.0),
                bbox=dict(boxstyle='round,pad=0.3', facecolor=NAVY, alpha=0.9,
                          edgecolor=WHITE, lw=0.7))

    # 2026: 11.6% — key endpoint
    ax.annotate('11.6%\n(2026 projected\n20% retained)',
                xy=(2026, 11.6), xytext=(2025.0, 4),
                fontsize=8.5, color=GOLD, fontweight='bold', ha='center',
                arrowprops=dict(arrowstyle='->', color=GOLD, lw=1.2),
                bbox=dict(boxstyle='round,pad=0.3', facecolor=NAVY, alpha=0.95,
                          edgecolor=GOLD, lw=0.9))

    ax.set_xticks(years)
    ax.set_xticklabels([str(y) for y in years], color=WHITE, fontsize=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{v:.0f}%'))
    ax.tick_params(colors=WHITE, labelsize=10)
    ax.spines[:].set_color(MID_NAVY)
    ax.set_ylim(0, 72)
    ax.set_xlim(2016.5, 2026.5)
    ax.set_ylabel('HRA Yield as % of\nCoding-Intensity Overpayment', color=WHITE,
                  fontsize=9.5, labelpad=8)
    ax.grid(axis='y', color=MID_NAVY, linewidth=0.6, alpha=0.7)

    fig.suptitle('HRA-Only Yield as Share of Coding-Intensity Overpayment\n'
                 '2017–2026 (with CMS-4185-F2 Phase-Out)',
                 fontsize=12, fontweight='bold', color=WHITE, y=0.97,
                 fontfamily='sans-serif')

    plt.subplots_adjust(top=0.87, bottom=0.13, left=0.12, right=0.97)

    add_footnote(fig,
        'Sources: OIG OEI-03-17-00474 (2017 observed); OIG OEI-03-23-00380 (2023 observed); '
        '2024–2026 projected using OIG CAGR (19.3% total; 8.6% in-home) with CMS-4185-F2 '
        'phase-out fractions (50% retained 2025, 20% retained 2026). '
        'The American Healthcare Conundrum  Issue #11',
        y=0.02)

    out = FIGURES / "chart2_hra_share_trajectory.png"
    fig.savefig(out, dpi=150, facecolor=NAVY, bbox_inches=None)
    plt.close(fig)
    print(f"Saved {out.name}")
    return out


# ══════════════════════════════════════════════════════════════════════════════
# CHART 3 — Top-10 state allocation, 2025 anchor year
# ══════════════════════════════════════════════════════════════════════════════
def chart3_state_allocation():
    # Load and sort states by overpayment
    rows = []
    with open(RESULTS / "state_level_decomposition.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['geo_lvl'] == 'State' and row['geo_desc'] not in ('PR', 'VI', 'DC'):
                rows.append({
                    'state': row['geo_desc'],
                    'overpay': float(row['coding_overpayment_bn']),
                    'per_enrollee': float(row['coding_overpayment_per_enrollee_usd']),
                    'ma_count': float(row['BENES_MA_CNT']),
                    'ma_rate': float(row['MA_PRTCPTN_RATE']),
                })
    rows.sort(key=lambda r: r['overpay'], reverse=True)
    top10 = rows[:10]

    states   = [r['state']      for r in top10]
    overpay  = [r['overpay']    for r in top10]
    per_enr  = [r['per_enrollee'] for r in top10]

    # Single-panel chart (per-enrollee panel removed: per-enrollee variation is a
    # baseline allocation artifact driven by local FFS risk-score level, not a
    # plan-coding-behavior signal, so showing it implied a comparison the
    # methodology cannot support).
    fig, ax1 = plt.subplots(figsize=(9, 5.5), dpi=100, facecolor=NAVY)
    ax1.set_facecolor(NAVY)
    fig.patch.set_facecolor(NAVY)

    # Total allocation, top 10 states
    colors_left = [GOLD if i == 0 else TEAL for i in range(len(states))]
    bars1 = ax1.barh(states[::-1], overpay[::-1], color=colors_left[::-1],
                     height=0.65, zorder=3)

    # Labels inside bars when wide enough, else outside
    for i, (bar, val) in enumerate(zip(bars1, overpay[::-1])):
        w = bar.get_width()
        label = f'${val:.1f}B'
        if w > 0.6:
            ax1.text(w - 0.05, bar.get_y() + bar.get_height() / 2,
                     label, ha='right', va='center',
                     fontsize=9.5, fontweight='bold', color=NAVY,
                     fontfamily='sans-serif')
        else:
            ax1.text(w + 0.04, bar.get_y() + bar.get_height() / 2,
                     label, ha='left', va='center',
                     fontsize=9.5, fontweight='bold', color=WHITE,
                     fontfamily='sans-serif')

    ax1.set_xlim(0, 3.6)
    ax1.set_xticks([0, 1, 2, 3])
    ax1.set_xlabel('$ Billions / Year (allocated)', color=WHITE, fontsize=10, labelpad=6)
    ax1.tick_params(colors=WHITE, labelsize=10)
    ax1.spines[:].set_color(MID_NAVY)
    ax1.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v:.0f}B'))
    ax1.grid(axis='x', color=MID_NAVY, linewidth=0.6, alpha=0.7)

    fig.suptitle('Top 10 States: Coding-Intensity Overpayment Distribution\n'
                 'National Total: $28B (allocated by MA enrollment, 2025 anchor year)',
                 fontsize=12, fontweight='bold', color=WHITE, y=0.97,
                 fontfamily='sans-serif')

    plt.subplots_adjust(top=0.86, bottom=0.14, left=0.10, right=0.97)

    add_footnote(fig,
        'Note: This is allocation (enrollment-weighted), not an independent state-level estimate. '
        'It shows where the dollars are, not which states have higher or lower coding intensity. '
        'Sources: CMS Geographic Variation PUFs (FFS and MA), 2023. '
        'National $28B anchor: MedPAC March 2026. '
        'The American Healthcare Conundrum  Issue #11',
        y=0.02)

    out = FIGURES / "chart3_state_allocation.png"
    fig.savefig(out, dpi=150, facecolor=NAVY, bbox_inches=None)
    plt.close(fig)
    print(f"Saved {out.name}")
    return out


# ══════════════════════════════════════════════════════════════════════════════
# CHART 4 — Qui tam FCA settlement timeline 2018–2026 + open DOJ probe
# ══════════════════════════════════════════════════════════════════════════════
def chart4_qui_tam_timeline():
    # Data from CSV
    settlements = []
    with open(RESULTS / "qui_tam_settlements.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            settlements.append({
                'year': int(row['year']),
                'defendant': row['defendant'],
                'amount': float(row['amount_usd_m']),
            })

    # Add DOJ-UNH probe as open-ended (no amount, just marker)
    doj_year = 2025  # probe publicly acknowledged July 2025

    fig, ax = plt.subplots(figsize=(10, 6), dpi=100, facecolor=NAVY)
    ax.set_facecolor(NAVY)
    fig.patch.set_facecolor(NAVY)

    # Build x positions: spread settlements by year
    # Years with data: 2018, 2021, 2023, 2024, 2026
    years = [s['year'] for s in settlements]
    amounts = [s['amount'] for s in settlements]
    defendants = [s['defendant'] for s in settlements]

    bar_colors = [TEAL] * len(settlements)
    bar_colors[4] = GOLD   # Kaiser 2026 is the record — highlight in gold

    bars = ax.bar(years, amounts, width=0.55, color=bar_colors, zorder=3, alpha=0.92)

    # Labels above each bar
    label_specs = [
        # (year, amount, defendant_short, y_offset, align)
        (2018, 270.0, 'DaVita / HealthCare Partners\n$270M', 20, 'center'),
        (2021, 90.0,  'Sutter Health\n$90M', 20, 'center'),
        (2023, 172.0, 'Cigna\n$172M', 20, 'center'),
        (2024, 98.0,  'Indep. Health\nup to $98M*', 20, 'center'),
        (2026, 556.0, 'Kaiser Permanente\n$556M (record)', 20, 'center'),
    ]

    for (yr, amt, label, yoff, ha), bar in zip(label_specs, bars):
        if yr == 2024:
            # place label directly above the bar, centered, smaller font
            ax.text(yr, amt + yoff, label,
                    ha='center', va='bottom', fontsize=7.5, color=WHITE,
                    fontfamily='sans-serif', linespacing=1.3)
        else:
            ax.text(yr, amt + yoff, label,
                    ha='center', va='bottom', fontsize=8.5, color=WHITE,
                    fontfamily='sans-serif',
                    fontweight='bold' if yr == 2026 else 'normal',
                    linespacing=1.4)

    # DOJ-UNH open probe marker — placed between 2024 and 2026 bars
    ax.annotate('DOJ-UNH\nProbe (active,\nunresolved)',
                xy=(doj_year, 0),
                xytext=(doj_year + 0.4, 200),
                fontsize=8.5, color=RED, ha='center', fontweight='bold',
                arrowprops=dict(arrowstyle='->', color=RED, lw=1.5),
                bbox=dict(boxstyle='round,pad=0.35', facecolor=NAVY, alpha=0.95,
                          edgecolor=RED, lw=1.0))

    # Dashed "open" extension line from 2025 rightward
    ax.annotate('', xy=(2026.4, 60), xytext=(doj_year, 60),
                arrowprops=dict(arrowstyle='->', color=RED, lw=1.2,
                                linestyle='dashed'))
    ax.text(2025.7, 75, 'Open', fontsize=8, color=RED, ha='center',
            fontfamily='sans-serif', fontstyle='italic')

    # Running total annotation
    total = sum(amounts)
    ax.text(0.97, 0.97, f'Total settled & recovered:\n${total/1000:.2f}B across 5 closed actions',
            transform=ax.transAxes, ha='right', va='top',
            fontsize=9, color=GOLD, fontfamily='sans-serif',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=MID_NAVY, alpha=0.9,
                      edgecolor=GOLD, lw=0.8))

    ax.set_xlim(2016.5, 2027.0)
    ax.set_ylim(0, 720)
    ax.set_xticks([2018, 2021, 2023, 2024, 2025, 2026])
    ax.set_xticklabels(['2018', '2021', '2023', '2024', '2025', '2026'],
                       color=WHITE, fontsize=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v:.0f}M'))
    ax.tick_params(colors=WHITE, labelsize=10)
    ax.spines[:].set_color(MID_NAVY)
    ax.set_ylabel('Settlement Amount ($ Millions)', color=WHITE, fontsize=10, labelpad=8)
    ax.grid(axis='y', color=MID_NAVY, linewidth=0.6, alpha=0.7)

    fig.suptitle('MA Risk-Adjustment FCA Settlement Timeline\n2018–2026  •  $1.19B Recovered  •  DOJ-UNH Probe Active',
                 fontsize=12, fontweight='bold', color=WHITE, y=0.97,
                 fontfamily='sans-serif')

    plt.subplots_adjust(top=0.87, bottom=0.14, left=0.09, right=0.97)

    # Two-line footnote to prevent right-edge clipping
    fig.text(0.12, 0.045, '* Independent Health: up to $98M; guaranteed minimum $34.5M; remainder contingent on multi-year performance. '
             'DOJ-UNH probe publicly acknowledged July 24, 2025; no charges filed as of publication.',
             ha='left', va='bottom', fontsize=5.8, color=LIGHT, fontfamily='sans-serif')
    fig.text(0.12, 0.02, 'Sources: DOJ press releases; WSJ reporting. The American Healthcare Conundrum  Issue #11',
             ha='left', va='bottom', fontsize=5.8, color=LIGHT, fontfamily='sans-serif')

    out = FIGURES / "chart4_qui_tam_timeline.png"
    fig.savefig(out, dpi=150, facecolor=NAVY, bbox_inches=None)
    plt.close(fig)
    print(f"Saved {out.name}")
    return out


# ══════════════════════════════════════════════════════════════════════════════
# CHART 5 — Savings Tracker (all 11 issues)
# ══════════════════════════════════════════════════════════════════════════════
def chart5_savings_tracker():
    issues = [
        ('#1',  'OTC Drugs',       0.6,   TEAL),
        ('#2',  'Drug Pricing',    25.0,  TEAL),
        ('#3',  'Hospitals',       73.0,  TEAL),
        ('#4',  'PBMs',            30.0,  TEAL),
        ('#5',  'Admin Waste',    200.0,  TEAL),
        ('#6',  'Supply Waste',    28.0,  TEAL),
        ('#7',  'GLP-1',           40.0,  TEAL),
        ('#8',  'Denial Machine',  32.0,  TEAL),
        ('#9',  'Employer Trap',    6.6,  TEAL),
        ('#10', 'Procedure Mill',   7.6,  TEAL),
        ('#11', 'MA Overpayment',  28.0,  GOLD),  # this issue
    ]

    total = sum(s[2] for s in issues)
    gap_total = 3240.0  # $3.24T
    pct = total / gap_total * 100

    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(10, 6.5), dpi=100,
                                             facecolor=NAVY,
                                             gridspec_kw={'wspace': 0.38})
    for ax in (ax_left, ax_right):
        ax.set_facecolor(NAVY)
    fig.patch.set_facecolor(NAVY)

    # ── LEFT: Full-scale bar ($3.24T) ────────────────────────────────────────
    bar_h = 0.55
    # Background (full gap)
    ax_left.barh([0], [gap_total], height=bar_h, color=MID_NAVY, zorder=2)
    # Identified
    ax_left.barh([0], [total], height=bar_h, color=GOLD, zorder=3)

    ax_left.set_xlim(0, gap_total * 1.08)
    ax_left.set_ylim(-0.5, 0.5)
    ax_left.set_xticks([0, 1000, 2000, 3000])
    ax_left.set_xticklabels(['$0B', '$1.0T', '$2.0T', '$3.0T'], color=WHITE, fontsize=9.5)
    ax_left.tick_params(left=False, labelleft=False, colors=WHITE)
    ax_left.spines[:].set_color(MID_NAVY)
    ax_left.set_xlabel('$ Billions', color=WHITE, fontsize=9.5, labelpad=6)
    ax_left.set_title('Full $3.24T Scale', color=WHITE, fontsize=10.5, pad=8,
                      fontfamily='sans-serif')

    # Annotation for left panel: the bar is too narrow to put text inside.
    # Place label to the right of the bar with an arrow, matching issue #10 style.
    ax_left.annotate(f'${total:.1f}B\n({pct:.1f}%)',
                     xy=(total, 0),
                     xytext=(total + 280, 0.2),
                     fontsize=11, fontweight='bold', color=GOLD,
                     ha='left', va='center', fontfamily='sans-serif',
                     arrowprops=dict(arrowstyle='->', color=WHITE, lw=0.9),
                     bbox=dict(boxstyle='round,pad=0.35', facecolor=MID_NAVY,
                               alpha=0.9, edgecolor=GOLD, lw=0.8))

    # Remaining label (dimmer, smaller)
    ax_left.text(total + 350, -0.25,
                 f'Remaining: ${gap_total - total:.0f}B',
                 fontsize=8.5, color=LIGHT, ha='left', va='center',
                 fontfamily='sans-serif')

    # ── RIGHT: Per-issue breakdown ────────────────────────────────────────────
    labels  = [f'{s[0]}  {s[1]}' for s in issues]
    vals    = [s[2] for s in issues]
    colors  = [s[3] for s in issues]

    y_pos = list(range(len(issues)))
    bars = ax_right.barh(y_pos, vals, color=colors, height=0.65, zorder=3)

    for i, (bar, val) in enumerate(zip(bars, vals)):
        w = bar.get_width()
        label_str = f'${val:.1f}B'
        fontweight = 'bold' if i == len(issues) - 1 else 'normal'
        # Use inside label only for bars wide enough to fit the text comfortably.
        # With xlim=240, bars < 35 units (~15% of axis) are too narrow for inside labels.
        if w >= 35:
            ax_right.text(w - 1.5, bar.get_y() + bar.get_height() / 2,
                          label_str, ha='right', va='center',
                          fontsize=9.5, fontweight=fontweight, color=NAVY,
                          fontfamily='sans-serif')
        else:
            ax_right.text(w + 1.5, bar.get_y() + bar.get_height() / 2,
                          label_str, ha='left', va='center',
                          fontsize=9, fontweight=fontweight, color=WHITE,
                          fontfamily='sans-serif')

    ax_right.set_yticks(y_pos)
    ax_right.set_yticklabels(labels, color=WHITE, fontsize=9, fontfamily='sans-serif')
    ax_right.set_xlim(0, 240)
    ax_right.set_xlabel('$ Billions / Year', color=WHITE, fontsize=9.5, labelpad=6)
    ax_right.set_title(f'Per-Issue Breakdown (Total: ${total:.1f}B)', color=WHITE,
                       fontsize=10.5, pad=8, fontfamily='sans-serif')
    ax_right.tick_params(colors=WHITE, labelsize=9)
    ax_right.spines[:].set_color(MID_NAVY)
    ax_right.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'${v:.0f}B'))
    ax_right.grid(axis='x', color=MID_NAVY, linewidth=0.6, alpha=0.7)

    # Title
    fig.suptitle(f'Savings Tracker: ${total:.1f} Billion and Counting\n'
                 f'{pct:.1f}% of the $3.24T Annual US-Japan Per-Capita Spending Gap  (11 issues)',
                 fontsize=12.5, fontweight='bold', color=WHITE, y=0.98,
                 fontfamily='sans-serif')

    plt.subplots_adjust(top=0.88, bottom=0.11, left=0.06, right=0.98)

    add_footnote(fig,
        'US per-capita: $15,474 (CMS NHE 2024). Japan: $5,790 (OECD 2025). Gap x 336M population = $3.24T. '
        'The American Healthcare Conundrum  Issue #11',
        y=0.02)

    out = FIGURES / "chart5_savings_tracker.png"
    fig.savefig(out, dpi=150, facecolor=NAVY, bbox_inches=None)
    plt.close(fig)
    print(f"Saved {out.name}")
    return out


# ══════════════════════════════════════════════════════════════════════════════
# HERO — 1456x1048 px social preview
# ══════════════════════════════════════════════════════════════════════════════
def hero_cover():
    # Canvas: 1456 x 1048 at 72dpi work, save at 150dpi -> 2184x1572px
    W_IN = 14.56
    H_IN = 10.48
    DPI_WORK = 72
    DPI_SAVE = 150

    DARK_NAVY = '#111520'

    fig = plt.figure(figsize=(W_IN, H_IN), dpi=DPI_WORK, facecolor=NAVY)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_facecolor(NAVY)
    ax.axis('off')

    # Subtle grid (atmospheric)
    for i in range(0, 101, 5):
        ax.axhline(i, color=MID_NAVY, linewidth=0.25, alpha=0.4)
        ax.axvline(i, color=MID_NAVY, linewidth=0.25, alpha=0.4)

    # ── Series branding (top-center, inside safe zone) ─────────────────────
    ax.text(50, 77, 'THE AMERICAN HEALTHCARE CONUNDRUM',
            fontsize=11, color=RED, fontweight='bold', ha='center', va='center',
            fontfamily='sans-serif')
    ax.text(50, 73.2, 'I S S U E   1 1', fontsize=9.5, color=GOLD,
            ha='center', va='center', fontfamily='sans-serif')

    # Divider line
    ax.plot([28, 72], [70.5, 70.5], color=RED, linewidth=1.5, alpha=0.75)

    # ── Main hook ─────────────────────────────────────────────────────────────
    # "$28 BILLION" centered, bold, dominant
    ax.text(50, 59,
            '$28 BILLION',
            fontsize=56, color=GOLD, fontweight='bold', ha='center', va='center',
            fontfamily='sans-serif')

    # Supporting descriptor
    ax.text(50, 51,
            'per year in Medicare Advantage',
            fontsize=19, color=WHITE, ha='center', va='center',
            fontfamily='sans-serif', alpha=0.95)
    ax.text(50, 46.5,
            'coding-intensity overpayment.',
            fontsize=19, color=TEAL, ha='center', va='center',
            fontfamily='sans-serif', fontweight='bold')

    # ── V24 / V28 band sub-line ────────────────────────────────────────────
    ax.text(50, 40.5,
            'V24-only model: $44.8B  •  V28-only model: $19.2B',
            fontsize=10.5, color=WHITE, ha='center', va='center',
            fontfamily='sans-serif', alpha=0.65)

    # ── Bottom stats bar (inside safe zone) ───────────────────────────────
    ax.plot([22, 78], [34.8, 34.8], color=MID_NAVY, linewidth=0.8, alpha=0.6)
    ax.text(50, 32,
            '$28B booked  •  $19B–$45B range  •  $470.8B running total  •  14.5% of $3.24T gap',
            fontsize=9, color=WHITE, ha='center', va='center',
            fontfamily='sans-serif', alpha=0.55)

    # ── Tiny branding footer ───────────────────────────────────────────────
    ax.text(50, 8,
            'andrewrexroad.substack.com',
            fontsize=8, color=LIGHT, ha='center', va='center',
            fontfamily='sans-serif', alpha=0.4)

    out = FIGURES / "hero_cover.png"
    fig.savefig(out, dpi=DPI_SAVE, facecolor=NAVY, bbox_inches=None)
    plt.close(fig)
    print(f"Saved {out.name}")
    return out


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print("=" * 60)
    print("Issue #11 — generate_all_charts.py")
    print("=" * 60)

    paths = []
    paths.append(chart1_v24_v28_band())
    paths.append(chart2_hra_share_trajectory())
    paths.append(chart3_state_allocation())
    paths.append(chart4_qui_tam_timeline())
    paths.append(chart5_savings_tracker())
    paths.append(hero_cover())

    print("\n" + "=" * 60)
    print(f"Done. {len(paths)} PNGs written to {FIGURES}/")
    for p in paths:
        size_kb = p.stat().st_size // 1024
        print(f"  {p.name:40s}  {size_kb:>5} KB")
    print("=" * 60)
