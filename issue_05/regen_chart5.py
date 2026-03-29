"""
Regenerate Chart 5: National Cost of Prior Authorization
Fixes:
- Bracket annotation moved higher with more clearance above tallest bar
- Larger bar value labels
- Better footnote wrapping
- Hatched bar description clearer
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import os

BASE = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.join(BASE, "figures")

NAVY = '#1A1F2E'
TEAL = '#0E8A72'
RED  = '#B7182A'
GOLD = '#D4AF37'
WHITE = '#F8F8F6'
LIGHT_NAVY = '#2A3048'

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'text.color': WHITE,
    'axes.labelcolor': WHITE,
    'xtick.color': WHITE,
    'ytick.color': WHITE,
})

fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
fig.patch.set_facecolor(NAVY)
ax.set_facecolor(NAVY)

methods = ['Bottom-Up\n(AMA Survey)', 'Top-Down\n(Bingham TDABC)', 'Total System\n(Health Affairs)']
values_pa = [20.7, 72.5, 93.3]
colors_pa = [TEAL, TEAL, GOLD]

bars = ax.bar(methods, values_pa, color=colors_pa, width=0.5, edgecolor=NAVY, linewidth=0.5)
bars[2].set_hatch('//')
bars[2].set_edgecolor('#888')

# Value labels on top of bars
for bar, val in zip(bars, values_pa):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
            f'${val:.1f}B', ha='center', va='bottom', fontsize=14,
            fontweight='bold', color=WHITE)

# Provider-side range bracket — well above the tallest provider bar ($72.5B)
bracket_y = 82
ax.annotate('', xy=(-0.25, bracket_y), xytext=(1.25, bracket_y),
            arrowprops=dict(arrowstyle='|-|', color=GOLD, lw=1.5,
                            mutation_scale=8))
ax.text(0.5, bracket_y + 3, 'Provider-side range: $21 \u2013 $73B / year',
        ha='center', va='bottom', fontsize=10, color=GOLD, fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.3', facecolor=NAVY, edgecolor=GOLD, alpha=0.9))

# Annotation on the hatched bar explaining what "Total System" includes
ax.annotate('Includes payer ($6B),\nmanufacturer ($25B),\nphysician ($27B),\npatient ($35B)',
            xy=(2, 93.3), xytext=(2.55, 65),
            fontsize=7.5, color='#ccc', ha='left', va='top',
            arrowprops=dict(arrowstyle='->', color='#888', lw=0.8),
            bbox=dict(boxstyle='round,pad=0.3', facecolor=LIGHT_NAVY, edgecolor='#555', alpha=0.9))

ax.set_ylabel('Annual Cost ($ Billions)', fontsize=11)
ax.set_ylim(0, 115)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:.0f}B'))

ax.grid(axis='y', color='#333', linewidth=0.3, alpha=0.4)
ax.set_axisbelow(True)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_color('#444')
ax.spines['left'].set_color('#444')

fig.suptitle('National Cost of Prior Authorization', fontsize=15,
             fontweight='bold', color=WHITE, y=0.97)
ax.set_title('Two Provider-Side Estimates + Total System Cost (Including Patient Time)',
             fontsize=10, color=GOLD, pad=12)

fig.text(0.12, 0.02,
         'Sources: AMA 2024 PA Physician Survey; Bingham et al. 2022 (JCO Oncology Practice); '
         'Health Affairs 2025 (drug PA total system cost).',
         fontsize=6, color='#999', ha='left')
fig.text(0.88, 0.02, 'The American Healthcare Conundrum \u00b7 Issue #5',
         fontsize=6, color='#999', ha='right')

plt.subplots_adjust(left=0.10, right=0.95, top=0.85, bottom=0.10)
fig.savefig(os.path.join(FIG_DIR, 'chart5_prior_auth_cost.png'), dpi=150,
            facecolor=NAVY, edgecolor='none')
plt.close(fig)
print("Saved chart5_prior_auth_cost.png")
