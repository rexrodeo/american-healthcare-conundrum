"""
Issue #4 Chart 5: The Insulin Price Spiral (1996-2023)
How the rebate system drove a commodity drug to $316/vial

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
ORANGE = '#E8963E'

# ── Price data (approximate from KFF and published reporting) ─────────────
# Humalog (Lilly) — list price per vial
humalog_years =  [1996, 2000, 2003, 2005, 2007, 2009, 2011, 2013, 2015, 2017, 2019, 2020, 2021, 2023]
humalog_prices = [21,   35,   40,   55,   75,   93,  125,  175,  245,  275,  300,  316,  310,   35]

# Lantus (Sanofi) — list price per vial
lantus_years =  [2001, 2003, 2005, 2007, 2009, 2011, 2013, 2015, 2017, 2019, 2020]
lantus_prices = [35,   42,   58,   78,   95,  130,  180,  250,  280,  295,  290]

# Semglee biosimilar (Mylan/Viatris) — launched Nov 2021
semglee_years =  [2021, 2022, 2023]
semglee_prices = [98,   98,   98]

fig, ax = plt.subplots(figsize=(10, 5.5), dpi=100, facecolor=NAVY)
ax.set_facecolor(NAVY)

# Grid
ax.grid(axis='y', color=MID_NAVY, linewidth=0.3, alpha=0.5)
ax.grid(axis='x', color=MID_NAVY, linewidth=0.3, alpha=0.3)

# ── Plot lines ────────────────────────────────────────────────────────────
ax.plot(humalog_years, humalog_prices, color=RED, linewidth=2.5, marker='o',
        markersize=5, markerfacecolor=RED, markeredgecolor=NAVY, markeredgewidth=1,
        label='Humalog (Lilly)', zorder=5)

ax.plot(lantus_years, lantus_prices, color=GOLD, linewidth=2, marker='s',
        markersize=4, markerfacecolor=GOLD, markeredgecolor=NAVY, markeredgewidth=1,
        linestyle='--', label='Lantus (Sanofi)', zorder=4)

ax.plot(semglee_years, semglee_prices, color=TEAL, linewidth=2.5, marker='^',
        markersize=5, markerfacecolor=TEAL, markeredgecolor=NAVY, markeredgewidth=1,
        label='Semglee biosimilar (Nov 2021)', zorder=5)

# ── Shaded peak zone ─────────────────────────────────────────────────────
ax.axhspan(280, 330, color=RED, alpha=0.06, zorder=1)

# ── Annotations (carefully positioned to avoid overlap) ───────────────────

# 1. Launch price (bottom-left, clear space)
ax.annotate('$21/vial\n(1996 launch)',
            xy=(1996, 21), xytext=(1999, 70),
            fontsize=8, color=LIGHT_GRAY, ha='center', va='center',
            arrowprops=dict(arrowstyle='->', color=LIGHT_GRAY, lw=0.8),
            bbox=dict(boxstyle='round,pad=0.3', facecolor=MID_NAVY, edgecolor=LIGHT_GRAY,
                      linewidth=0.5, alpha=0.8))

# 2. Peak price — top-left of the peak, positioned clearly above the line
ax.annotate('$316/vial peak\n1,405% above 1996 price',
            xy=(2020, 316), xytext=(2014, 345),
            fontsize=8, color=RED, fontweight='bold', ha='center', va='bottom',
            arrowprops=dict(arrowstyle='->', color=RED, lw=1),
            bbox=dict(boxstyle='round,pad=0.3', facecolor=NAVY, edgecolor=RED,
                      linewidth=0.8, alpha=0.9))

# 3. Lilly $35 cap — bottom-right
ax.annotate('Lilly $35 cap\n(Apr 2023)',
            xy=(2023, 35), xytext=(2019, 55),
            fontsize=8, color=GOLD, fontweight='bold', ha='center', va='center',
            arrowprops=dict(arrowstyle='->', color=GOLD, lw=1),
            bbox=dict(boxstyle='round,pad=0.3', facecolor=MID_NAVY, edgecolor=GOLD,
                      linewidth=0.8, alpha=0.8))

# 4. Semglee biosimilar — right side, below peak
ax.annotate('Semglee biosimilar: $98\nPBM formularies kept\nbrand preferred',
            xy=(2022, 98), xytext=(2017.5, 170),
            fontsize=7.5, color=TEAL, ha='center', va='center',
            arrowprops=dict(arrowstyle='->', color=TEAL, lw=0.8),
            bbox=dict(boxstyle='round,pad=0.3', facecolor=NAVY, edgecolor=TEAL,
                      linewidth=0.8, alpha=0.9))

# ── Axis formatting ──────────────────────────────────────────────────────
ax.set_xlim(1994, 2024.5)
ax.set_ylim(0, 380)
ax.set_xlabel('Year', fontsize=9, color=WHITE, labelpad=6)
ax.set_ylabel('List price per vial (USD)', fontsize=9, color=WHITE, labelpad=8)

ax.set_xticks([1995, 2000, 2005, 2010, 2015, 2020])
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:.0f}'))

ax.tick_params(colors=LIGHT_GRAY, labelsize=8)
ax.spines['bottom'].set_color(LIGHT_GRAY)
ax.spines['left'].set_color(LIGHT_GRAY)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
for spine in ax.spines.values():
    spine.set_linewidth(0.5)

# ── Legend ─────────────────────────────────────────────────────────────────
legend = ax.legend(loc='upper left', fontsize=8, frameon=True,
                   facecolor=MID_NAVY, edgecolor=LIGHT_GRAY,
                   labelcolor=WHITE, framealpha=0.8)
legend.get_frame().set_linewidth(0.5)

# ── Title ─────────────────────────────────────────────────────────────────
fig.suptitle('The Insulin Price Spiral: 1996–2023',
             fontsize=14, color=WHITE, fontweight='bold', y=0.97)
ax.set_title('How the rebate system drove a commodity drug to $316/vial',
             fontsize=10, color=LIGHT_GRAY, pad=8, style='italic')

fig.subplots_adjust(top=0.85, bottom=0.16, left=0.09, right=0.96)

# ── Footnotes ─────────────────────────────────────────────────────────────
fig.text(0.09, 0.02,
         'Sources: KFF, "Insulin Costs and Out-of-Pocket Spending," 2023. '
         'Humalog list prices from Eli Lilly disclosures and published reporting. '
         'Lantus prices from Sanofi.\n'
         'Semglee (insulin glargine-yfgn, Mylan/Viatris) list price at launch. '
         'FTC v. CVS Caremark, Express Scripts, OptumRx (insulin pricing), filed Sep 2024. '
         '$35 Lilly cap announced March 2023.',
         fontsize=5.5, color=LIGHT_GRAY, ha='left', va='bottom', alpha=0.6,
         style='italic')

out = '/sessions/pensive-clever-hypatia/mnt/healthcare/issue_04/figures/chart5_insulin_prices.png'
fig.savefig(out, dpi=150, facecolor=NAVY)
plt.close(fig)
print(f'Saved to {out}')
