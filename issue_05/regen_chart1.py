"""
Regenerate Chart 1: National Hospital Overhead Decomposition
Fixes text overlap on smaller bars by using a clean layout strategy:
- Large bars (>15B): label INSIDE, right-aligned
- Medium bars (8-15B): label INSIDE, left-aligned
- Small bars (<8B): label OUTSIDE at a fixed x position to avoid overlap
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import os

BASE = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.join(BASE, "figures")

# Brand
NAVY = '#1A1F2E'
TEAL = '#0E8A72'
RED  = '#B7182A'
GOLD = '#D4AF37'
WHITE = '#F8F8F6'

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'text.color': WHITE,
    'axes.labelcolor': WHITE,
    'xtick.color': WHITE,
    'ytick.color': WHITE,
})

cost_centers = [
    ('Admin & General', 141.2),
    ('Employee Benefits', 58.7),
    ('Operation of Plant', 19.8),
    ('Comms / Data Processing', 11.7),
    ('Housekeeping', 10.2),
    ('Maintenance & Repairs', 6.9),
    ('Dietary', 6.8),
    ('Medical Records', 4.9),
    ('Central Services', 4.9),
    ('Social Service', 3.4),
]

labels = [c[0] for c in cost_centers]
values = [c[1] for c in cost_centers]
total = sum(values)

fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
fig.patch.set_facecolor(NAVY)
ax.set_facecolor(NAVY)

y_pos = np.arange(len(labels))
colors = [GOLD] + [TEAL] * (len(values) - 1)
bars = ax.barh(y_pos, values, color=colors, edgecolor=NAVY, height=0.7)

# Fixed x position for all external labels — keeps them aligned in a column
EXT_LABEL_X = 28  # all small-bar labels start at the same x

for i, (bar, val, label) in enumerate(zip(bars, values, labels)):
    w = bar.get_width()
    pct = val / total * 100
    txt = f'${val:.1f}B ({pct:.0f}%)'

    if w > 40:
        # Large bar: label inside, right-aligned
        ax.text(w - 1.5, bar.get_y() + bar.get_height()/2,
                txt, ha='right', va='center',
                fontsize=11, fontweight='bold', color=WHITE)
    elif w > 15:
        # Medium bar: label inside, centered
        ax.text(w / 2, bar.get_y() + bar.get_height()/2,
                txt, ha='center', va='center',
                fontsize=9.5, fontweight='bold', color=WHITE)
    else:
        # Small bar: label outside at fixed column position
        ax.annotate(txt,
                    xy=(w, bar.get_y() + bar.get_height()/2),
                    xytext=(EXT_LABEL_X, bar.get_y() + bar.get_height()/2),
                    ha='left', va='center', fontsize=8.5, color=WHITE,
                    arrowprops=dict(arrowstyle='-', color='#666', lw=0.5))

ax.set_yticks(y_pos)
ax.set_yticklabels(labels, fontsize=9.5)
ax.invert_yaxis()
ax.set_xlabel('National Total ($ Billions)', fontsize=10, color=WHITE)
ax.set_xlim(0, 165)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}'))

# Grid for readability
ax.xaxis.set_major_locator(mticker.MultipleLocator(20))
ax.grid(axis='x', color='#333', linewidth=0.5, alpha=0.5)
ax.set_axisbelow(True)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_color('#444')
ax.spines['left'].set_color('#444')

fig.suptitle('National Hospital Overhead Decomposition', fontsize=14, fontweight='bold',
             color=WHITE, y=0.97)
ax.set_title('$268.5 Billion Across 4,518 Hospitals (32.2% of Total Costs)',
             fontsize=10, color=GOLD, pad=10)

fig.text(0.12, 0.02, 'Source: CMS HCRIS FY2023 Worksheet A, Col 700. Author analysis of 4,518 hospitals.',
         fontsize=6, color='#999', ha='left')
fig.text(0.88, 0.02, 'The American Healthcare Conundrum \u00b7 Issue #5',
         fontsize=6, color='#999', ha='right')

plt.subplots_adjust(left=0.28, right=0.95, top=0.88, bottom=0.08)
fig.savefig(os.path.join(FIG_DIR, 'chart1_overhead_decomposition.png'), dpi=150,
            facecolor=NAVY, edgecolor='none')
plt.close(fig)
print("Saved chart1_overhead_decomposition.png")
