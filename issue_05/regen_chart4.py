"""
Regenerate Chart 4: 50-State Hospital Admin Cost Per Discharge
Fixes:
- Taller figure (10x14 at 72dpi) so state labels have room
- Larger y-axis labels (8pt)
- Dollar values INSIDE bars for top/bottom 5 + Maryland, outside only if bar too short
- Cleaner annotation strategy
- Saved at 150dpi → 1500x2100px output (tall infographic format)
Note: figsize=(10,14) at dpi=72 stays well under memory limits
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
                'state': row['state'],
                'discharges': int(float(row['discharges'])) if row['discharges'] else 0,
                'ag_cost': float(row['ag_cost_total']) if row['ag_cost_total'] else 0,
            }
            if h['discharges'] >= 100 and h['ag_cost'] > 0:
                hospitals.append(h)
        except (ValueError, KeyError):
            continue

print(f"Loaded {len(hospitals)} hospitals")

# Weighted average by state
state_data = {}
for h in hospitals:
    st = h['state']
    if st not in state_data:
        state_data[st] = {'total_ag': 0, 'total_dc': 0, 'count': 0}
    state_data[st]['total_ag'] += h['ag_cost']
    state_data[st]['total_dc'] += h['discharges']
    state_data[st]['count'] += 1

state_avgs = []
for st, d in state_data.items():
    if d['count'] >= 5 and d['total_dc'] > 0:
        state_avgs.append((st, d['total_ag'] / d['total_dc'], d['count']))

state_avgs.sort(key=lambda x: x[1], reverse=True)
n = len(state_avgs)
print(f"{n} states with ≥5 hospitals")

states = [s[0] for s in state_avgs]
vals = [s[1] for s in state_avgs]
cnts = [s[2] for s in state_avgs]

nat_avg = sum(h['ag_cost'] for h in hospitals) / sum(h['discharges'] for h in hospitals)

# Taller figure for 50 bars
fig, ax = plt.subplots(figsize=(10, 14), dpi=72)
fig.patch.set_facecolor(NAVY)
ax.set_facecolor(NAVY)

# Color: above avg = red, below = teal
colors = [RED if v > nat_avg else TEAL for v in vals]

y_pos = np.arange(n)
bars = ax.barh(y_pos, vals, color=colors, height=0.75, edgecolor=NAVY, linewidth=0.3)

# Highlight Maryland
md_idx = next((i for i, s in enumerate(states) if s == 'MD'), None)
if md_idx is not None:
    bars[md_idx].set_color(GOLD)

# National average vertical line
ax.axvline(x=nat_avg, color=GOLD, linestyle='--', linewidth=1.5, zorder=3)

# Place "National avg" label in a clear spot (middle of the chart)
ax.annotate(f'National avg: ${nat_avg:,.0f}',
            xy=(nat_avg, n * 0.45), xytext=(nat_avg + 200, n * 0.45),
            fontsize=9, color=GOLD, fontweight='bold', va='center',
            arrowprops=dict(arrowstyle='->', color=GOLD, lw=1),
            bbox=dict(boxstyle='round,pad=0.3', facecolor=NAVY, edgecolor=GOLD, alpha=0.9))

# Annotate top 5, bottom 5, and Maryland with dollar values
annotate_indices = set(range(5)) | set(range(n-5, n))
if md_idx is not None:
    annotate_indices.add(md_idx)

for i in range(n):
    if i not in annotate_indices:
        continue

    v = vals[i]
    label_parts = [f'${v:,.0f}']
    if i == md_idx:
        label_parts.append('(all-payer)')
    else:
        label_parts.append(f'({cnts[i]} hosp.)')
    label = ' '.join(label_parts)

    # Place inside bar if bar is long enough, otherwise outside
    if v > 800:
        ax.text(v - 15, y_pos[i], label, ha='right', va='center',
                fontsize=7.5, color=WHITE, fontweight='bold')
    else:
        ax.text(v + 15, y_pos[i], label, ha='left', va='center',
                fontsize=7.5, color=WHITE)

ax.set_yticks(y_pos)
ax.set_yticklabels(states, fontsize=8.5, fontfamily='DejaVu Sans Mono')
ax.invert_yaxis()
ax.set_xlabel('Weighted Avg A&G Cost Per Discharge ($)', fontsize=10)
ax.set_xlim(0, max(vals) * 1.2)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:,.0f}'))

# Light grid
ax.grid(axis='x', color='#333', linewidth=0.3, alpha=0.5)
ax.set_axisbelow(True)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_color('#444')
ax.spines['left'].set_color('#444')

plt.subplots_adjust(left=0.08, right=0.95, top=0.94, bottom=0.03)

fig.text(0.5, 0.985, 'Hospital Admin Cost Per Discharge by State',
         fontsize=16, fontweight='bold', color=WHITE, ha='center')
fig.text(0.5, 0.965, 'Weighted average · Red = above national avg · Teal = below · Gold = Maryland (all-payer model)',
         fontsize=9, color=GOLD, ha='center')

fig.text(0.10, 0.008,
         'Source: CMS HCRIS FY2023. States with ≥5 reporting hospitals. Weighted by discharges.',
         fontsize=6.5, color='#999', ha='left')
fig.text(0.90, 0.008, 'The American Healthcare Conundrum · Issue #5',
         fontsize=6.5, color='#999', ha='right')
fig.savefig(os.path.join(FIG_DIR, 'chart4_state_ranking.png'), dpi=150,
            facecolor=NAVY, edgecolor='none')
plt.close(fig)
print("Saved chart4_state_ranking.png")
