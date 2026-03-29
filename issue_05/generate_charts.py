#!/usr/bin/env python3
"""
Issue #5: The Paper Chase — Chart Generation Script
Follows CLAUDE.md Chart Creation Rules strictly.
Run: python3 /Users/minirex/healthcare/issue_05/generate_charts.py
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

OUT = '/Users/minirex/healthcare/issue_05/figures'
os.makedirs(OUT, exist_ok=True)

NAVY  = '#1A1F2E'
TEAL  = '#0E8A72'
RED   = '#B7182A'
GOLD  = '#D4AF37'
WHITE = '#F8F8F6'
LGRAY = '#D0D5DE'
MGRAY = '#8A9099'
DKTEAL = '#0A6B58'

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'figure.facecolor': WHITE,
    'axes.facecolor': WHITE,
    'text.color': NAVY,
    'axes.labelcolor': NAVY,
    'xtick.color': NAVY,
    'ytick.color': NAVY,
    'axes.edgecolor': LGRAY,
})

# ══════════════════════════════════════════════════════════════════════
# CHART 1 — Per-Capita Admin Spending
# ══════════════════════════════════════════════════════════════════════
print("Generating Chart 1 ...")

peers_raw = [
    ("Switzerland",    1369),
    ("Germany",        1071),
    ("Canada",          980),
    ("Netherlands",     937),
    ("France",          906),
    ("Norway",          825),
    ("Australia",       731),
    ("Sweden",          711),
    ("Japan",           695),
    ("United Kingdom",  613),
]
peers_sorted = sorted(peers_raw, key=lambda x: x[1])
us_val = 4983
peer_avg = 884

all_labels = [c[0] for c in peers_sorted] + ["United States"]
all_values = [c[1] for c in peers_sorted] + [us_val]
n = len(all_labels)

fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
fig.patch.set_facecolor(WHITE)
ax.set_facecolor(WHITE)

y_pos = np.arange(n)
bar_colors = [TEAL] * (n - 1) + [RED]
bars = ax.barh(y_pos, all_values, color=bar_colors, height=0.65, zorder=2)

ax.axvline(x=peer_avg, color=GOLD, linewidth=1.8, linestyle='--', zorder=3)

for i, (bar, val) in enumerate(zip(bars, all_values)):
    is_us = (i == n - 1)
    txt = f'${val:,}'
    if val > 700:
        ax.text(val - 55, i, txt, va='center', ha='right',
                fontsize=10, fontweight='bold',
                color=WHITE)
    else:
        ax.text(val + 45, i, txt, va='center', ha='left',
                fontsize=10, fontweight='bold', color=NAVY)

# US excess annotation
ax.annotate(
    'US excess: $4,099/person\nNational total: $1.37T/yr',
    xy=(us_val, n - 1),
    xytext=(3500, n - 3.2),
    fontsize=8.5, color=RED, ha='left', va='center',
    bbox=dict(boxstyle='round,pad=0.35', facecolor='#FAE8E8',
              edgecolor=RED, linewidth=0.8),
    arrowprops=dict(arrowstyle='->', color=RED, lw=1.2,
                    connectionstyle='arc3,rad=-0.2'),
    zorder=5
)

# Peer-average label
ax.text(peer_avg + 55, 4.5, f'Peer\navg\n${peer_avg:,}',
        fontsize=7.5, color='#8B6914', va='center', ha='left',
        fontweight='bold')

ax.set_yticks(y_pos)
ax.set_yticklabels(all_labels, fontsize=10.5)
ax.set_xlabel('Per-Capita Healthcare Administrative Spending (USD)', fontsize=10, labelpad=6)
ax.set_xlim(0, 6400)
ax.xaxis.set_major_formatter(
    plt.FuncFormatter(lambda x, _: f'${int(x):,}' if x > 0 else '$0'))
ax.tick_params(axis='x', labelsize=9)
ax.set_title('Per-Capita Healthcare Administrative Spending:\nUS vs. 10 OECD Peers',
             fontsize=13, fontweight='bold', color=NAVY, pad=10)

legend_patch = mpatches.Patch(color=GOLD, label=f'Peer average: ${peer_avg:,}')
ax.legend(handles=[legend_patch], loc='lower right', fontsize=9,
          framealpha=0.9, edgecolor=LGRAY)

fig.text(0.12, 0.015,
    'Sources: Woolhandler & Himmelstein, Annals of Internal Medicine, 2020; OECD Health at a Glance 2025; '
    'CMS NHE 2023; Commonwealth Fund 2024; author analysis.\n'
    'Non-US estimates derived from OECD SHA data + Commonwealth Fund surveys. '
    'Only the US-Canada comparison uses identical methodology.',
    fontsize=5.5, color=MGRAY, ha='left', va='bottom')

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='x', color=LGRAY, linewidth=0.5, zorder=0)
plt.subplots_adjust(left=0.22, right=0.95, top=0.88, bottom=0.14)
plt.savefig(f'{OUT}/chart1_percapita_comparison.png', dpi=150)
plt.close(fig)
print("  Chart 1 saved.")

# ══════════════════════════════════════════════════════════════════════
# CHART 2 — Woolhandler 2017→2023 Update
# ══════════════════════════════════════════════════════════════════════
print("Generating Chart 2 ...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 6), dpi=100,
                                gridspec_kw={'width_ratios': [1, 1.8], 'wspace': 0.45})
fig.patch.set_facecolor(WHITE)
for ax in (ax1, ax2):
    ax.set_facecolor(WHITE)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

# LEFT panel: 2017 baseline
ax1.bar([0], [812], color=TEAL, width=0.5, zorder=2)
ax1.text(0, 812 + 25, '$812B', ha='center', va='bottom',
         fontsize=14, fontweight='bold', color=TEAL)
ax1.text(0, 812 / 2, '34.2%\nof NHE', ha='center', va='center',
         fontsize=10, fontweight='bold', color=WHITE)
ax1.set_xticks([0])
ax1.set_xticklabels(['2017 Baseline\n(Woolhandler &\nHimmelstein 2020)'],
                     fontsize=9.5)
ax1.set_ylim(0, 1900)
ax1.set_ylabel('Admin Cost ($ Billions)', fontsize=9.5, labelpad=6)
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${int(x):,}B'))
ax1.tick_params(axis='y', labelsize=8.5)
ax1.set_title('2017\nBaseline', fontsize=10, fontweight='bold', color=NAVY, pad=8)
ax1.grid(axis='y', color=LGRAY, linewidth=0.5, zorder=0)

# RIGHT panel: 2023 update methods + cross-val
methods = ['Method B\n(Conservative)', 'Method C\n(32% ratio)', 'Method A\n(34.2% ratio)']
method_vals = [1130, 1557, 1664]
method_colors = [TEAL, DKTEAL, RED]
x_pos = [0, 1, 2]

bars2 = ax2.bar(x_pos, method_vals, color=method_colors, width=0.55, zorder=2)

for x, val, col in zip(x_pos, method_vals, method_colors):
    ax2.text(x, val + 25, f'${val/1000:.2f}T', ha='center', va='bottom',
             fontsize=12, fontweight='bold', color=col)

# Cross-validation floor
ax2.axhline(y=906, color=GOLD, linewidth=2.0, linestyle='--', zorder=3)
ax2.text(2.45, 906 + 28, 'Cross-val floor\n$906B\n(CMS $410B + CAP $496B)',
         ha='right', va='bottom', fontsize=7.5, color='#8B6914', fontweight='bold')

# Range brace annotation
ax2.annotate('', xy=(2.35, 1664), xytext=(2.35, 1130),
             arrowprops=dict(arrowstyle='<->', color=MGRAY, lw=1.2))
ax2.text(2.42, 1397, '$1.13–1.66T\nrange', ha='left', va='center',
         fontsize=8, color=MGRAY)

ax2.set_xticks(x_pos)
ax2.set_xticklabels(methods, fontsize=9)
ax2.set_ylim(0, 1900)
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${int(x):,}B'))
ax2.tick_params(axis='y', labelsize=8.5)
ax2.set_title('2023 Estimates\n(Three Update Methods)', fontsize=10,
              fontweight='bold', color=NAVY, pad=8)
ax2.grid(axis='y', color=LGRAY, linewidth=0.5, zorder=0)

fig.suptitle('US Healthcare Administrative Cost: 2017 Baseline and 2023 Estimates',
             fontsize=13, fontweight='bold', color=NAVY, y=0.97)

fig.text(0.12, 0.015,
    'Sources: Woolhandler & Himmelstein, Annals of Internal Medicine, 2020; CMS NHE Historical Tables 2023; '
    'Center for American Progress BIR analysis 2023; author analysis.\n'
    'Method A: 34.2% x $4.867T NHE. Method B: $812B x NHE growth (1.394x). '
    'Method C: 32% x $4.867T (post-ACA constraint). '
    'Cross-val: CMS "net cost of health insurance" ($410B) + CAP BIR ($496B).',
    fontsize=5.5, color=MGRAY, ha='left', va='bottom')

plt.subplots_adjust(left=0.10, right=0.97, top=0.89, bottom=0.14)
plt.savefig(f'{OUT}/chart2_woolhandler_range.png', dpi=150)
plt.close(fig)
print("  Chart 2 saved.")

# ══════════════════════════════════════════════════════════════════════
# CHART 3 — Prior Authorization National Cost
# ══════════════════════════════════════════════════════════════════════
print("Generating Chart 3 ...")

fig, axes = plt.subplots(1, 3, figsize=(10, 6), dpi=100,
                          gridspec_kw={'width_ratios': [1.2, 1.0, 1.2], 'wspace': 0.50})
fig.patch.set_facecolor(WHITE)
for ax in axes:
    ax.set_facecolor(WHITE)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

ax_l, ax_c, ax_r = axes

# ── LEFT: Bottom-up breakdown
bu_labels  = ['Physician\ntime', 'Staff\ntime']
bu_vals    = [17741, 16915]   # 2hrs×$185×48 = $17,760; 11hrs×$32×48 = $16,896 ≈ rounded
# Re-use exact computed values from analysis script:
# physician: 2 * 185 * 48 = 17,760; staff: 11 * 32 * 48 = 16,896
bu_vals = [17760, 16896]
bu_per_physician = sum(bu_vals)   # = 34,656

ax_l.bar([0, 1], bu_vals, color=[TEAL, DKTEAL], width=0.55, zorder=2)
for i, (lbl, val) in enumerate(zip(bu_labels, bu_vals)):
    ax_l.text(i, val + 400, f'${val:,.0f}', ha='center', va='bottom',
              fontsize=9, fontweight='bold', color=NAVY)

# Total per-physician annotation
ax_l.text(0.5, max(bu_vals) * 0.55, f'= ${bu_per_physician:,}/physician/yr',
          ha='center', va='center', fontsize=9, color=NAVY, style='italic')
ax_l.annotate(
    f'National total:\n$20.7B/yr\n(596K physicians)',
    xy=(0.5, bu_per_physician + 1000),
    xytext=(0.5, bu_per_physician + 6000),
    fontsize=8.5, ha='center', va='bottom', color=TEAL, fontweight='bold',
    bbox=dict(boxstyle='round,pad=0.3', facecolor='#E0F4F0', edgecolor=TEAL, lw=0.8),
    arrowprops=dict(arrowstyle='->', color=TEAL, lw=1.0)
)

ax_l.set_xticks([0, 1])
ax_l.set_xticklabels(bu_labels, fontsize=9.5)
ax_l.set_ylim(0, 46000)
ax_l.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${int(x/1000)}K'))
ax_l.tick_params(axis='y', labelsize=8)
ax_l.set_title('Bottom-Up Model\n(AMA Survey 2024)', fontsize=9.5,
               fontweight='bold', color=NAVY, pad=8)
ax_l.grid(axis='y', color=LGRAY, linewidth=0.5, zorder=0)

# ── CENTER: AMA stats
ax_c.set_xlim(0, 10)
ax_c.set_ylim(0, 10)
ax_c.axis('off')

stats = [
    ('39',  'prior auth requests\nper physician per week'),
    ('13',  'hours of combined\nphysician + staff time/week'),
    ('35%', 'of physicians have hired\nstaff exclusively for PA'),
    ('93%', 'say PA delays\nnecessary care'),
]
y_positions = [8.2, 6.1, 4.0, 1.9]
for (num, desc), yp in zip(stats, y_positions):
    ax_c.text(5, yp + 0.55, num, ha='center', va='bottom',
              fontsize=19, fontweight='bold', color=RED)
    ax_c.text(5, yp, desc, ha='center', va='top',
              fontsize=7.5, color=NAVY, linespacing=1.4)

ax_c.set_title('AMA Prior Auth\nPhysician Survey 2024', fontsize=9.5,
               fontweight='bold', color=NAVY, pad=8)

# ── RIGHT: Top-down
td_labels = ['Cost\nper event', 'Annual PA\nevents (B)', 'National\ntotal']
# Show as a waterfall / equation visual
ax_r.set_xlim(0, 10)
ax_r.set_ylim(0, 10)
ax_r.axis('off')

# Equation layout
ax_r.text(5, 8.8, 'Top-Down Model', ha='center', fontsize=10,
          fontweight='bold', color=NAVY)
ax_r.text(5, 8.1, '(Bingham TDABC 2022)', ha='center', fontsize=8.5,
          color=MGRAY)

# Box-style equation
box_data = [
    ('1.12B', 'annual PA events\n(nationally)'),
    ('×  $65', 'per event\n(Bingham midpoint)'),
    ('=  $72.5B', 'per year\n(provider-side only)'),
]
y_tops = [6.7, 4.5, 2.3]
colors_box = [TEAL, TEAL, RED]
for (val, desc), yt, col in zip(box_data, y_tops, colors_box):
    rect = mpatches.FancyBboxPatch((1.0, yt - 0.5), 8.0, 1.5,
                                    boxstyle='round,pad=0.15',
                                    facecolor='#E0F4F0' if col == TEAL else '#FAE8E8',
                                    edgecolor=col, linewidth=0.9)
    ax_r.add_patch(rect)
    ax_r.text(5.0, yt + 0.28, val, ha='center', va='center',
              fontsize=13, fontweight='bold', color=col)
    ax_r.text(5.0, yt - 0.15, desc, ha='center', va='center',
              fontsize=7.5, color=NAVY)

ax_r.text(5.0, 0.6,
          'Excludes: insurer-side costs,\npatient time, downstream harm',
          ha='center', va='bottom', fontsize=6.5, color=MGRAY, style='italic')

fig.suptitle('Prior Authorization National Cost: Provider Side Only',
             fontsize=13, fontweight='bold', color=NAVY, y=0.97)

fig.text(0.12, 0.015,
    'Sources: AMA Prior Authorization Physician Survey 2024; AAMC Physician Workforce Data 2023; '
    'Bingham et al., JCO Oncology Practice, September 2022;\nBLS OES May 2023; author analysis. '
    'Bottom-up: 596K PA-exposed physicians x $34,656/yr. '
    'Top-down: 1.12B events x $65/event (Bingham midpoint, radiation oncology).',
    fontsize=5.5, color=MGRAY, ha='left', va='bottom')

plt.subplots_adjust(left=0.06, right=0.97, top=0.89, bottom=0.14)
plt.savefig(f'{OUT}/chart3_prior_auth_cost.png', dpi=150)
plt.close(fig)
print("  Chart 3 saved.")

# ══════════════════════════════════════════════════════════════════════
# CHART 4 — The Revenue Cycle Management Industry
# ══════════════════════════════════════════════════════════════════════
print("Generating Chart 4 ...")

fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
fig.patch.set_facecolor(WHITE)
ax.set_facecolor(WHITE)
ax.axis('off')

# Market size range visual at top
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)

# Main title area
ax.text(5, 9.5, 'The Revenue Cycle Management Industry', ha='center', va='top',
        fontsize=14, fontweight='bold', color=NAVY)
ax.text(5, 8.9, 'Annual market size: $55–$172 billion (2024)', ha='center', va='top',
        fontsize=11, color=MGRAY)

# Market bar (scale visualization)
bar_x = 1.0; bar_y = 7.9; bar_w_full = 8.0; bar_h = 0.6
# Draw range bar
rect_bg = mpatches.FancyBboxPatch((bar_x, bar_y), bar_w_full, bar_h,
                                   boxstyle='round,pad=0.05',
                                   facecolor=LGRAY, edgecolor='none')
ax.add_patch(rect_bg)
rect_range = mpatches.FancyBboxPatch((bar_x, bar_y), bar_w_full * 0.55, bar_h,
                                      boxstyle='square,pad=0.0',
                                      facecolor=TEAL, edgecolor='none')
ax.add_patch(rect_range)
rect_hi = mpatches.FancyBboxPatch((bar_x + bar_w_full * 0.55, bar_y),
                                   bar_w_full * 0.45, bar_h,
                                   boxstyle='square,pad=0.0',
                                   facecolor=DKTEAL, alpha=0.45, edgecolor='none')
ax.add_patch(rect_hi)
ax.text(bar_x + 0.1, bar_y + bar_h / 2, '$55B', ha='left', va='center',
        fontsize=8.5, fontweight='bold', color=WHITE)
ax.text(bar_x + bar_w_full - 0.1, bar_y + bar_h / 2, '$172B', ha='right', va='center',
        fontsize=8.5, fontweight='bold', color=WHITE)
ax.text(bar_x + bar_w_full * 0.55, bar_y - 0.25, 'Multiple market estimates reflect\ndefinitional variation, not measurement uncertainty',
        ha='center', va='top', fontsize=6.5, color=MGRAY, style='italic')

# Central annotation
ax.text(5, 6.85,
        '"This industry exists because the system requires it."',
        ha='center', va='center', fontsize=10.5, color=RED,
        style='italic', fontweight='bold')

# Company cards — 3 cards in a row
card_data = [
    {
        'name': 'Change Healthcare / Optum',
        'ticker': 'UNH (parent)',
        'stat1': '15B transactions/yr',
        'stat2': '~1 in 3 US medical claims',
        'stat3': 'Acquired: $13B (2022)',
        'note': 'Parent UHN: $236B revenue\nCEO comp: $26.3M',
        'color': RED,
    },
    {
        'name': 'Waystar',
        'ticker': 'NASDAQ: WAY',
        'stat1': '$797M FY2023 revenue',
        'stat2': '4.5B transactions/yr',
        'stat3': 'IPO Jun 2024: ~$4.4B val.',
        'note': 'Claim submission,\nPA mgmt, denial mgmt',
        'color': TEAL,
    },
    {
        'name': 'R1 RCM',
        'ticker': 'Taken private 2024',
        'stat1': '$2.3B FY2023 revenue',
        'stat2': 'End-to-end RCM outsourcing',
        'stat3': 'PE deal: ~$8.9B (2024)',
        'note': 'Billing, coding, PA,\ncollections for health systems',
        'color': TEAL,
    },
]

card_xs = [0.5, 3.8, 7.1]
card_y_top = 6.35
card_w = 2.8; card_h2 = 2.9

for cd, cx in zip(card_data, card_xs):
    rect = mpatches.FancyBboxPatch((cx, card_y_top - card_h2), card_w, card_h2,
                                    boxstyle='round,pad=0.12',
                                    facecolor=WHITE,
                                    edgecolor=cd['color'], linewidth=1.2)
    ax.add_patch(rect)
    # Header bar
    hdr = mpatches.FancyBboxPatch((cx, card_y_top - 0.52), card_w, 0.52,
                                   boxstyle='square,pad=0.0',
                                   facecolor=cd['color'], edgecolor='none')
    ax.add_patch(hdr)
    ax.text(cx + card_w / 2, card_y_top - 0.26, cd['name'],
            ha='center', va='center', fontsize=8.0, fontweight='bold', color=WHITE)
    # Ticker
    ax.text(cx + card_w / 2, card_y_top - 0.72, cd['ticker'],
            ha='center', va='top', fontsize=7.0, color=MGRAY)
    # Stats
    for i, stat in enumerate([cd['stat1'], cd['stat2'], cd['stat3']]):
        ax.text(cx + 0.15, card_y_top - 1.10 - i * 0.52, stat,
                ha='left', va='top', fontsize=7.5, color=NAVY)
    # Note
    ax.text(cx + card_w / 2, card_y_top - card_h2 + 0.18,
            cd['note'], ha='center', va='bottom', fontsize=6.5,
            color=MGRAY, style='italic', linespacing=1.3)

# Bottom footnote
fig.text(0.12, 0.015,
    'Sources: UnitedHealth Group 10-K FY2024 (SEC EDGAR); Waystar S-1 & 10-K FY2023 (SEC EDGAR); '
    'R1 RCM 10-K FY2023 (SEC EDGAR); Grand View Research 2024; KLAS Research 2024.\n'
    'Market size range ($55-172B) reflects definitional variation across market research firms.',
    fontsize=5.5, color=MGRAY, ha='left', va='bottom')

plt.subplots_adjust(left=0.02, right=0.98, top=0.97, bottom=0.10)
plt.savefig(f'{OUT}/chart4_rcm_industry.png', dpi=150)
plt.close(fig)
print("  Chart 4 saved.")

# ══════════════════════════════════════════════════════════════════════
# CHART 5 — Savings Tracker
# ══════════════════════════════════════════════════════════════════════
print("Generating Chart 5 ...")

issues = [
    ('#1 OTC Drugs',    0.6),
    ('#2 Drug Pricing', 25.0),
    ('#3 Hospitals',    73.0),
    ('#4 PBM Reform',   30.0),
    ('#5 Admin Waste',  200.0),
]
issue_labels = [i[0] for i in issues]
issue_vals   = [i[1] for i in issues]
target_full  = 3000.0
target_zoom  = 400.0
total        = sum(issue_vals)   # 328.6

fig, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(10, 6), dpi=100,
                                      gridspec_kw={'height_ratios': [1, 2.2],
                                                   'hspace': 0.55})
fig.patch.set_facecolor(WHITE)
for ax in (ax_top, ax_bot):
    ax.set_facecolor(WHITE)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

# ── TOP: Full $3T scale
ax_top.set_xlim(0, target_full)
ax_top.set_ylim(-0.5, 1.0)
ax_top.axis('off')

# Background bar
bg_rect = mpatches.FancyBboxPatch((0, 0.1), target_full, 0.55,
                                   boxstyle='round,pad=5',
                                   facecolor=LGRAY, edgecolor='none')
ax_top.add_patch(bg_rect)
# Filled portion
fill_rect = mpatches.FancyBboxPatch((0, 0.1), total, 0.55,
                                     boxstyle='square,pad=0',
                                     facecolor=TEAL, edgecolor='none')
ax_top.add_patch(fill_rect)

ax_top.text(total / 2, 0.375, f'$328.6B identified  (11.0%)',
            ha='center', va='center', fontsize=10, fontweight='bold', color=WHITE)
ax_top.text(0, -0.1, '$0', ha='left', va='top', fontsize=8.5, color=NAVY)
ax_top.text(target_full, -0.1, '$3 Trillion\n(US-Japan gap)', ha='right',
            va='top', fontsize=8.5, color=NAVY)
ax_top.set_title('Running Total: $328.6B / $3T Annual US-Japan Spending Gap (11.0%)',
                 fontsize=12, fontweight='bold', color=NAVY, pad=6)

# ── BOTTOM: $400B zoom — stacked horizontal bar
ax_bot.set_xlim(0, target_zoom)
ax_bot.set_ylim(-0.5, 1.0)
ax_bot.axis('off')

bar_colors_z = ['#5B8DB8', '#3A7CA5', '#0E8A72', '#0A6B58', RED]
cum = 0
for i, (lbl, val, col) in enumerate(zip(issue_labels, issue_vals, bar_colors_z)):
    rect = mpatches.FancyBboxPatch((cum, 0.1), val, 0.7,
                                    boxstyle='square,pad=0',
                                    facecolor=col, edgecolor=WHITE, linewidth=0.8)
    ax_bot.add_patch(rect)
    # Label inside if wide enough, else above
    label_str = f'{lbl}\n${val:.0f}B' if val > 18 else f'{lbl}\n${val:.1f}B'
    center_x = cum + val / 2
    if val >= 25:
        ax_bot.text(center_x, 0.455, label_str, ha='center', va='center',
                    fontsize=8.0, fontweight='bold', color=WHITE, linespacing=1.3)
    elif val >= 5:
        ax_bot.text(center_x, 1.0, label_str, ha='center', va='bottom',
                    fontsize=7.5, color=NAVY, linespacing=1.3)
        ax_bot.plot([center_x, center_x], [0.8, 0.8], color=col, lw=0.8)
    else:
        ax_bot.text(center_x, 1.05, label_str, ha='center', va='bottom',
                    fontsize=7.0, color=NAVY, linespacing=1.3)
    cum += val

# Remaining bar
remaining = target_zoom - total
rect_rem = mpatches.FancyBboxPatch((total, 0.1), remaining, 0.7,
                                    boxstyle='square,pad=0',
                                    facecolor=LGRAY, edgecolor=WHITE, linewidth=0.8)
ax_bot.add_patch(rect_rem)
ax_bot.text(total + remaining / 2, 0.455, f'$71.4B\nremaining\nto $400B',
            ha='center', va='center', fontsize=8.0, color=MGRAY, linespacing=1.3)

ax_bot.text(0, -0.15, '$0', ha='left', va='top', fontsize=8, color=NAVY)
ax_bot.text(target_zoom, -0.15, '$400B\nzoom', ha='right', va='top',
            fontsize=8, color=NAVY)
ax_bot.text(total, -0.15, f'$328.6B', ha='center', va='top',
            fontsize=8.5, fontweight='bold', color=TEAL)

ax_bot.set_title('Per-Issue Contributions (First $400B zoom window)',
                 fontsize=11, fontweight='bold', color=NAVY, pad=6)

fig.text(0.12, 0.015,
    'Issues #1–5: OTC Drug Overspending ($0.6B), Drug Reference Pricing ($25.0B), '
    'Hospital Reference Pricing ($73.0B), PBM Reform ($30.0B),\n'
    'Administrative Waste ($200.0B). '
    'Issue #5 conservative estimate; range $200-600B. '
    'Target: $3T = US-Japan per-capita gap x 335M. '
    'Sources: Issues #1-5, this series.',
    fontsize=5.5, color=MGRAY, ha='left', va='bottom')

plt.subplots_adjust(left=0.04, right=0.97, top=0.93, bottom=0.10)
plt.savefig(f'{OUT}/chart5_savings_tracker.png', dpi=150)
plt.close(fig)
print("  Chart 5 saved.")

print("\nAll 5 charts generated successfully.")
print(f"Output directory: {OUT}")
for fname in sorted(os.listdir(OUT)):
    fpath = os.path.join(OUT, fname)
    size_kb = os.path.getsize(fpath) // 1024
    print(f"  {fname}: {size_kb} KB")
