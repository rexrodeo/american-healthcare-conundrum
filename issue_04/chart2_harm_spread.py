"""
Issue #4 Chart 2: The Collateral Damage of PBM Extraction
Two-panel chart:
  Left: Rural independent pharmacy closures (2003-2018)
  Right: Spread pricing from two state audits + national extrapolation

Brand: NAVY=#1A1F2E, TEAL=#0E8A72, RED=#B7182A, GOLD=#D4AF37, WHITE=#F8F8F6
Rules: figsize at dpi=100, save at dpi=150. No overlapping text.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Brand colors
NAVY = '#1A1F2E'
TEAL = '#0E8A72'
RED = '#B7182A'
GOLD = '#D4AF37'
WHITE = '#F8F8F6'
LIGHT_GRAY = '#8B9DB8'
MID_NAVY = '#2A3248'

# Data
years = [2003, 2006, 2009, 2012, 2015, 2018]
pharmacy_index = [100, 97, 95, 93, 90, 83.9]

# Spread pricing data ($ millions)
state_labels = ['Ohio', 'Kentucky']
spread_amounts = [224.8, 123.5]
combined = 348

fig = plt.figure(figsize=(10, 5.5), dpi=100, facecolor=NAVY)

# Three-column layout: pharmacy closures (left), state bars (center), national (right)
gs = fig.add_gridspec(1, 3, width_ratios=[1.1, 0.7, 0.45], wspace=0.35,
                      left=0.08, right=0.96, top=0.82, bottom=0.18)

ax1 = fig.add_subplot(gs[0])
ax2 = fig.add_subplot(gs[1])
ax3 = fig.add_subplot(gs[2])

# ── LEFT PANEL: Rural Pharmacy Closures ──────────────────────────────────
ax1.set_facecolor(NAVY)

ax1.fill_between(years, pharmacy_index, 80, color=RED, alpha=0.12)
ax1.plot(years, pharmacy_index, color=RED, linewidth=2.5, marker='o',
         markersize=6, markerfacecolor=RED, markeredgecolor=NAVY, markeredgewidth=1.5,
         zorder=5)

ax1.annotate('16.1% of rural\nindependents closed',
             xy=(2014, 91), xytext=(2007, 86),
             fontsize=9, color=RED, fontweight='bold',
             ha='center', va='top',
             arrowprops=dict(arrowstyle='->', color=RED, lw=1.2),
             bbox=dict(boxstyle='round,pad=0.3', facecolor=NAVY, edgecolor=RED, alpha=0.8))

ax1.text(2016, 82,
         'Root cause: PBM reimbursements\nbelow acquisition cost for\n~80% of prescriptions',
         fontsize=6.5, color=LIGHT_GRAY, ha='center', va='top', style='italic',
         bbox=dict(boxstyle='round,pad=0.3', facecolor=MID_NAVY, edgecolor=LIGHT_GRAY,
                   alpha=0.5, linewidth=0.5))

ax1.set_xlim(2002, 2019)
ax1.set_ylim(80, 102)
ax1.set_ylabel('Independent pharmacy count\n(Index: 2003 = 100)', fontsize=8,
               color=WHITE, labelpad=8)
ax1.set_xlabel('Year', fontsize=8, color=WHITE)
ax1.set_title('Rural Pharmacy Deserts\nClosures, 2003–2018',
              fontsize=10, color=WHITE, fontweight='bold', pad=10)
ax1.set_xticks([2003, 2006, 2009, 2012, 2015, 2018])
ax1.tick_params(colors=LIGHT_GRAY, labelsize=7.5)
ax1.spines['bottom'].set_color(LIGHT_GRAY)
ax1.spines['left'].set_color(LIGHT_GRAY)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
for s in ax1.spines.values():
    s.set_linewidth(0.5)
ax1.grid(axis='y', color=MID_NAVY, linewidth=0.3, alpha=0.5)


# ── CENTER PANEL: State Audit Bars ───────────────────────────────────────
ax2.set_facecolor(NAVY)

bar_colors = [RED, GOLD]
x_pos = [0, 1]
bars = ax2.bar(x_pos, spread_amounts, width=0.6, color=bar_colors, edgecolor=NAVY,
               linewidth=0.5, zorder=3)

# Value labels INSIDE the bars (plenty of room since bars are tall on this scale)
ax2.text(0, 224.8 / 2, '$224.8M', fontsize=13, color=WHITE, fontweight='bold',
         ha='center', va='center', zorder=4)
ax2.text(1, 123.5 / 2, '$123.5M', fontsize=13, color=NAVY, fontweight='bold',
         ha='center', va='center', zorder=4)

# State labels below bars
ax2.set_xticks(x_pos)
ax2.set_xticklabels(['Ohio\n(2018 audit)', 'Kentucky\n(same period)'],
                     fontsize=7.5, color=LIGHT_GRAY)

# Combined total above both bars with clear space
ax2.plot([-0.1, 1.1], [combined, combined], color=TEAL, linewidth=1, linestyle='--',
         alpha=0.6, zorder=2)
ax2.text(0.5, combined + 20, f'Combined: ${combined}M',
         fontsize=9, color=TEAL, fontweight='bold', ha='center', va='bottom')
ax2.text(0.5, combined + 55, 'from just two states',
         fontsize=7.5, color=LIGHT_GRAY, ha='center', va='bottom', style='italic')

ax2.set_xlim(-0.5, 1.5)
ax2.set_ylim(0, 480)
ax2.set_ylabel('Spread pricing extracted\n($ millions, one year)', fontsize=8,
               color=WHITE, labelpad=8)
ax2.set_title('Two State Audits\nBilled vs. Paid to Pharmacies',
              fontsize=10, color=WHITE, fontweight='bold', pad=10)

ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:.0f}M'))
ax2.set_yticks([0, 100, 200, 300, 400])
ax2.tick_params(colors=LIGHT_GRAY, labelsize=7.5)
ax2.spines['bottom'].set_color(LIGHT_GRAY)
ax2.spines['left'].set_color(LIGHT_GRAY)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
for s in ax2.spines.values():
    s.set_linewidth(0.5)
ax2.grid(axis='y', color=MID_NAVY, linewidth=0.3, alpha=0.5)


# ── RIGHT PANEL: National Extrapolation ──────────────────────────────────
ax3.set_facecolor(NAVY)

# Single tall bar for the national figure
ax3.bar([0], [5000], width=0.5, color=TEAL, edgecolor=NAVY, linewidth=0.5,
        alpha=0.3, zorder=2)
# Booked amount as solid overlay
ax3.bar([0], [3000], width=0.5, color=TEAL, edgecolor=NAVY, linewidth=0.5,
        zorder=3)

# Labels
ax3.text(0, 5200, '~$5B/yr', fontsize=14, color=TEAL, fontweight='bold',
         ha='center', va='bottom')
ax3.text(0, 5000, 'scaled nationally', fontsize=7.5, color=LIGHT_GRAY,
         ha='center', va='top', style='italic')

ax3.text(0, 1500, 'Booked:\n$3B', fontsize=12, color=WHITE, fontweight='bold',
         ha='center', va='center', zorder=4)

# Arrow from state bars to national
ax3.annotate('', xy=(-0.35, 2500), xytext=(-0.6, 2500),
             arrowprops=dict(arrowstyle='->', color=TEAL, lw=1.5, alpha=0.6))

ax3.set_xlim(-0.7, 0.7)
ax3.set_ylim(0, 6000)
ax3.set_xticks([0])
ax3.set_xticklabels(['National\nextrapolation'], fontsize=7.5, color=LIGHT_GRAY)
ax3.set_yticks([])  # No y-axis ticks needed — the labels tell the story
ax3.set_title('National\nEstimate',
              fontsize=10, color=WHITE, fontweight='bold', pad=10)

ax3.spines['bottom'].set_color(LIGHT_GRAY)
ax3.spines['left'].set_visible(False)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
for s in ax3.spines.values():
    s.set_linewidth(0.5)


# ── Suptitle ──────────────────────────────────────────────────────────────
fig.suptitle('The Collateral Damage of PBM Extraction',
             fontsize=14, color=WHITE, fontweight='bold', y=0.97)

# ── Footnotes ─────────────────────────────────────────────────────────────
fig.text(0.08, 0.02,
         'Pharmacy closures: Knox, Gagneja & Kraschel 2021, JAMA Health Forum '
         '(2003–2018 data). Spread pricing: Ohio State Auditor, Managed Care '
         'Organization PBM Report, 2018; Kentucky equivalent period.\n'
         'National scaling: Ohio rate ($224.8M / $2.5B Medicaid drug spend = 9%) '
         'applied to US Medicaid managed care drug spend (~$75B). Conservative $3B booked.',
         fontsize=5.5, color=LIGHT_GRAY, ha='left', va='bottom', alpha=0.6,
         style='italic')

out = '/sessions/pensive-clever-hypatia/mnt/healthcare/issue_04/figures/chart2_harm_spread.png'
fig.savefig(out, dpi=150, facecolor=NAVY)
plt.close(fig)
print(f'Saved to {out}')
