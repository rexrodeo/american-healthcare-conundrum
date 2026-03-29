"""
Regenerate Chart 3: Admin Cost vs. Commercial Payer Share (scatter)
Fixes:
- Quintile labels manually positioned with staggered y to prevent overlap
- Semi-transparent background boxes on all annotations so text is readable over scatter
- Larger font for quintile labels
- Leader lines from label to data point
"""
import csv, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

BASE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE, "hospital_admin_costs_fy2023.csv")
FIG_DIR = os.path.join(BASE, "figures")

# Brand
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

# Load data
hospitals = []
with open(CSV_PATH, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            h = {
                'ownership': row['ownership'],
                'discharges': int(float(row['discharges'])) if row['discharges'] else 0,
                'ag_cost': float(row['ag_cost_total']) if row['ag_cost_total'] else 0,
                'admin_per_dc': float(row['admin_per_discharge']) if row['admin_per_discharge'] else 0,
                'commercial_pct': float(row['commercial_payer_pct']) if row['commercial_payer_pct'] else 0,
            }
            if h['discharges'] >= 100 and h['ag_cost'] > 0:
                hospitals.append(h)
        except (ValueError, KeyError):
            continue

print(f"Loaded {len(hospitals)} hospitals")

fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
fig.patch.set_facecolor(NAVY)
ax.set_facecolor(NAVY)

# Scatter by ownership — lower alpha, smaller dots for less visual noise
colors_map = {'For-Profit': RED, 'Nonprofit': TEAL, 'Government': GOLD}
for own_type, color in colors_map.items():
    subset = [h for h in hospitals if h['ownership'] == own_type]
    xs = [h['commercial_pct'] * 100 for h in subset]
    ys = [min(h['admin_per_dc'], 8000) for h in subset]
    ax.scatter(xs, ys, c=color, alpha=0.20, s=6, label=f'{own_type} ({len(subset):,})',
               edgecolors='none', rasterized=True)

# Quintile medians (from newsletter data)
quintile_data = [
    ('Q1', 34.2, 2142),
    ('Q2', 52.4, 1712),
    ('Q3', 62.9, 1565),
    ('Q4', 71.5, 1476),
    ('Q5', 85.6, 748),
]
qx = [q[1] for q in quintile_data]
qy = [q[2] for q in quintile_data]

# Plot the quintile trend line + dots
ax.plot(qx, qy, 'o-', color=WHITE, markersize=9, linewidth=2.5, zorder=5,
        label='Quintile medians', markeredgecolor=NAVY, markeredgewidth=1)

# MANUAL label positions — staggered to avoid any overlap
# (label_x, label_y) for each annotation, computed to spread vertically
# Key constraint: min ~600 data-units vertical gap between adjacent labels at 150dpi
label_bbox = dict(boxstyle='round,pad=0.3', facecolor=NAVY, edgecolor='#555',
                  alpha=0.92)

label_positions = [
    # Q1: data at (34.2, 2142) — label above and slightly right
    (28, 3200),
    # Q2: data at (52.4, 1712) — label high, shifted left to avoid Q1's arrow
    (42, 4200),
    # Q3: data at (62.9, 1565) — label above, centered
    (58, 5200),
    # Q4: data at (71.5, 1476) — label high right
    (78, 3800),
    # Q5: data at (85.6, 748) — label below the trend, plenty of room
    (92, 2400),
]

for i, (qlabel, qxi, qyi) in enumerate(quintile_data):
    lx, ly = label_positions[i]
    ax.annotate(
        f'{qlabel}: ${qyi:,}/DC',
        xy=(qxi, qyi),
        xytext=(lx, ly),
        fontsize=9, fontweight='bold', color=WHITE,
        ha='center', va='center',
        bbox=label_bbox,
        arrowprops=dict(arrowstyle='->', color='#aaa', lw=1.2,
                        connectionstyle='arc3,rad=0.15'),
        zorder=6
    )

# Correlation annotation — top right
ax.text(0.98, 0.95, 'r = −0.174\n(negative correlation)',
        transform=ax.transAxes, fontsize=11, color=GOLD, fontweight='bold',
        ha='right', va='top',
        bbox=dict(boxstyle='round,pad=0.5', facecolor=LIGHT_NAVY, edgecolor=GOLD, alpha=0.95))

ax.set_xlabel('Commercial Payer Share (%)', fontsize=10)
ax.set_ylabel('A&G Cost Per Discharge ($)', fontsize=10)
ax.set_xlim(0, 100)
ax.set_ylim(0, 8500)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:,.0f}'))
ax.legend(loc='upper left', fontsize=8.5, facecolor=LIGHT_NAVY, edgecolor='#444',
          labelcolor=WHITE, markerscale=2.5)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_color('#444')
ax.spines['left'].set_color('#444')

# Light grid for readability
ax.grid(axis='both', color='#333', linewidth=0.3, alpha=0.4)
ax.set_axisbelow(True)

fig.suptitle('Admin Cost vs. Commercial Payer Share', fontsize=14,
             fontweight='bold', color=WHITE, y=0.97)
ax.set_title('4,518 Hospitals: More Commercial Payers ≠ Higher Admin Costs',
             fontsize=10, color=GOLD, pad=10)

fig.text(0.12, 0.02,
         'Source: CMS HCRIS FY2023 Worksheets A & S-3. Each dot = one hospital. '
         'Y-axis capped at $8,000 for readability.',
         fontsize=6, color='#999', ha='left')
fig.text(0.88, 0.02, 'The American Healthcare Conundrum \u00b7 Issue #5',
         fontsize=6, color='#999', ha='right')

plt.subplots_adjust(left=0.12, right=0.95, top=0.86, bottom=0.08)
fig.savefig(os.path.join(FIG_DIR, 'chart3_payer_mix_scatter.png'), dpi=150,
            facecolor=NAVY, edgecolor='none')
plt.close(fig)
print("Saved chart3_payer_mix_scatter.png")
