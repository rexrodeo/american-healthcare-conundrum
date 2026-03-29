"""
Issue #5 Chart Generation — All 6 charts for "The Paper Chase"
Uses hospital_admin_costs_fy2023.csv (4,518 hospitals)
Brand colors: Navy #1A1F2E, Teal #0E8A72, Red #B7182A, Gold #D4AF37, White #F8F8F6
"""
import csv, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

# ── Paths ──
BASE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE, "hospital_admin_costs_fy2023.csv")
FIG_DIR = os.path.join(BASE, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# ── Brand ──
NAVY = '#1A1F2E'
TEAL = '#0E8A72'
RED  = '#B7182A'
GOLD = '#D4AF37'
WHITE = '#F8F8F6'
LIGHT_TEAL = '#16B898'
LIGHT_NAVY = '#2A3048'

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'text.color': WHITE,
    'axes.labelcolor': WHITE,
    'xtick.color': WHITE,
    'ytick.color': WHITE,
})

# ── Load data ──
hospitals = []
with open(CSV_PATH, 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            h = {
                'state': row['state'],
                'ownership': row['ownership'],
                'beds': int(float(row['beds'])) if row['beds'] else 0,
                'discharges': int(float(row['discharges'])) if row['discharges'] else 0,
                'cmi': float(row['cmi']) if row['cmi'] else 1.0,
                'ag_cost': float(row['ag_cost_total']) if row['ag_cost_total'] else 0,
                'full_overhead': float(row['full_overhead']) if row['full_overhead'] else 0,
                'total_costs': float(row['total_hospital_costs']) if row['total_hospital_costs'] else 0,
                'admin_per_dc': float(row['admin_per_discharge']) if row['admin_per_discharge'] else 0,
                'overhead_per_dc': float(row['overhead_per_discharge']) if row['overhead_per_discharge'] else 0,
                'admin_pct': float(row['admin_pct_of_total']) if row['admin_pct_of_total'] else 0,
                'commercial_pct': float(row['commercial_payer_pct']) if row['commercial_payer_pct'] else 0,
                'med_records': float(row['med_records_cost']) if row['med_records_cost'] else 0,
                'nursing_admin': float(row['nursing_admin_cost']) if row['nursing_admin_cost'] else 0,
            }
            if h['discharges'] >= 100 and h['ag_cost'] > 0:
                hospitals.append(h)
        except (ValueError, KeyError):
            continue

print(f"Loaded {len(hospitals)} hospitals")

# ── Bed-size groups ──
def bed_group(beds):
    if beds < 100: return 'Small\n(1-99 beds)'
    elif beds < 300: return 'Medium\n(100-299)'
    elif beds < 500: return 'Large\n(300-499)'
    else: return 'Very Large\n(500+)'

# ══════════════════════════════════════════════════════════════
# CHART 1: National Overhead Decomposition ($268.5B)
# ══════════════════════════════════════════════════════════════
print("\n--- Chart 1: Overhead Decomposition ---")

# We need the individual cost center totals from the newsletter text
# The CSV has ag_cost_total, med_records_cost, nursing_admin_cost, full_overhead
# For the decomposition, we use the newsletter's validated figures
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

# Horizontal bar chart, sorted by size
y_pos = np.arange(len(labels))
bars = ax.barh(y_pos, values, color=[TEAL if i > 0 else GOLD for i in range(len(values))],
               edgecolor=NAVY, height=0.7)

# Labels inside bars for large bars, outside for small
for i, (bar, val, label) in enumerate(zip(bars, values, labels)):
    w = bar.get_width()
    if w > 15:
        ax.text(w - 0.5, bar.get_y() + bar.get_height()/2,
                f'${val:.1f}B ({val/total*100:.0f}%)', ha='right', va='center',
                fontsize=10, fontweight='bold', color=WHITE)
    else:
        ax.text(w + 1.0, bar.get_y() + bar.get_height()/2,
                f'${val:.1f}B ({val/total*100:.0f}%)', ha='left', va='center',
                fontsize=8.5, color=WHITE)

ax.set_yticks(y_pos)
ax.set_yticklabels(labels, fontsize=9)
ax.invert_yaxis()
ax.set_xlabel('National Total ($ Billions)', fontsize=10, color=WHITE)
ax.set_xlim(0, 170)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_color('#444')
ax.spines['left'].set_color('#444')
ax.tick_params(axis='x', colors=WHITE)

fig.suptitle('National Hospital Overhead Decomposition', fontsize=14, fontweight='bold',
             color=WHITE, y=0.97)
ax.set_title(f'$268.5 Billion Across 4,518 Hospitals (32.2% of Total Costs)',
             fontsize=10, color=GOLD, pad=10)

fig.text(0.12, 0.02, 'Source: CMS HCRIS FY2023 Worksheet A, Col 700. Author analysis of 4,518 hospitals.',
         fontsize=6, color='#999', ha='left')
fig.text(0.88, 0.02, 'The American Healthcare Conundrum · Issue #5',
         fontsize=6, color='#999', ha='right')

plt.subplots_adjust(left=0.28, right=0.95, top=0.88, bottom=0.08)
fig.savefig(os.path.join(FIG_DIR, 'chart1_overhead_decomposition.png'), dpi=150,
            facecolor=NAVY, edgecolor='none')
plt.close(fig)
print("  Saved chart1_overhead_decomposition.png")

# ══════════════════════════════════════════════════════════════
# CHART 2: Variance by Peer Group (P25/P50/P75 bars)
# ══════════════════════════════════════════════════════════════
print("\n--- Chart 2: Variance by Peer Group ---")

groups_order = ['Small\n(1-99 beds)', 'Medium\n(100-299)', 'Large\n(300-499)', 'Very Large\n(500+)']
grouped = {g: [] for g in groups_order}
for h in hospitals:
    g = bed_group(h['beds'])
    grouped[g].append(h['admin_per_dc'])

fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
fig.patch.set_facecolor(NAVY)
ax.set_facecolor(NAVY)

x = np.arange(len(groups_order))
width = 0.22

p25s, p50s, p75s, counts = [], [], [], []
for g in groups_order:
    vals = sorted(grouped[g])
    p25s.append(np.percentile(vals, 25))
    p50s.append(np.percentile(vals, 50))
    p75s.append(np.percentile(vals, 75))
    counts.append(len(vals))

bars_25 = ax.bar(x - width, p25s, width, color=TEAL, label='P25', edgecolor=NAVY)
bars_50 = ax.bar(x, p50s, width, color=GOLD, label='Median (P50)', edgecolor=NAVY)
bars_75 = ax.bar(x + width, p75s, width, color=RED, label='P75', edgecolor=NAVY)

# Label values on top of bars
for bars, vals in [(bars_25, p25s), (bars_50, p50s), (bars_75, p75s)]:
    for bar, val in zip(bars, vals):
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, yval + 40,
                f'${val:,.0f}', ha='center', va='bottom', fontsize=8, color=WHITE)

# P75/P25 ratio annotations
for i, g in enumerate(groups_order):
    ratio = p75s[i] / p25s[i] if p25s[i] > 0 else 0
    ax.text(x[i], max(p75s[i], p50s[i], p25s[i]) + 250,
            f'{ratio:.1f}x gap\n({counts[i]:,} hospitals)',
            ha='center', va='bottom', fontsize=8, color=GOLD, fontweight='bold')

ax.set_xticks(x)
ax.set_xticklabels(groups_order, fontsize=9)
ax.set_ylabel('A&G Cost Per Discharge ($)', fontsize=10)
ax.set_ylim(0, max(p75s) + 800)
ax.legend(loc='upper right', fontsize=9, facecolor=LIGHT_NAVY, edgecolor='#444',
          labelcolor=WHITE)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_color('#444')
ax.spines['left'].set_color('#444')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:,.0f}'))

fig.suptitle('Hospital Administrative Cost Variance by Peer Group',
             fontsize=14, fontweight='bold', color=WHITE, y=0.97)
ax.set_title('P25 / Median / P75 of A&G Cost Per Discharge Within Bed-Size Groups',
             fontsize=10, color=GOLD, pad=10)

fig.text(0.12, 0.02, 'Source: CMS HCRIS FY2023. Author analysis. Hospitals with ≥100 discharges, nonzero A&G.',
         fontsize=6, color='#999', ha='left')
fig.text(0.88, 0.02, 'The American Healthcare Conundrum · Issue #5',
         fontsize=6, color='#999', ha='right')

plt.subplots_adjust(left=0.12, right=0.95, top=0.86, bottom=0.12)
fig.savefig(os.path.join(FIG_DIR, 'chart2_variance_peer_group.png'), dpi=150,
            facecolor=NAVY, edgecolor='none')
plt.close(fig)
print("  Saved chart2_variance_peer_group.png")

# ══════════════════════════════════════════════════════════════
# CHART 3: Payer Mix Scatter (Admin vs Commercial Share)
# ══════════════════════════════════════════════════════════════
print("\n--- Chart 3: Payer Mix Scatter ---")

fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
fig.patch.set_facecolor(NAVY)
ax.set_facecolor(NAVY)

# Color by ownership
colors_map = {'For-Profit': RED, 'Nonprofit': TEAL, 'Government': GOLD}
for own_type, color in colors_map.items():
    subset = [h for h in hospitals if h['ownership'] == own_type]
    xs = [h['commercial_pct'] * 100 for h in subset]
    ys = [min(h['admin_per_dc'], 8000) for h in subset]  # Cap for readability
    ax.scatter(xs, ys, c=color, alpha=0.25, s=8, label=f'{own_type} ({len(subset):,})',
               edgecolors='none')

# Quintile medians
comm_pcts = [h['commercial_pct'] for h in hospitals]
quintile_edges = np.percentile(comm_pcts, [0, 20, 40, 60, 80, 100])
quintile_data = [
    (34.2, 2142),  # Q1
    (52.4, 1712),  # Q2
    (62.9, 1565),  # Q3
    (71.5, 1476),  # Q4
    (85.6, 748),   # Q5
]
qx = [q[0] for q in quintile_data]
qy = [q[1] for q in quintile_data]

ax.plot(qx, qy, 'o-', color=WHITE, markersize=8, linewidth=2, zorder=5,
        label='Quintile medians')

# Annotate quintiles
for i, (qxi, qyi) in enumerate(zip(qx, qy)):
    offset_y = 350 if i != 4 else -350
    ax.annotate(f'Q{i+1}: ${qyi:,}/DC', xy=(qxi, qyi),
                xytext=(qxi, qyi + offset_y),
                fontsize=7.5, color=WHITE, ha='center', va='bottom',
                arrowprops=dict(arrowstyle='-', color='#666', lw=0.5))

# Correlation annotation
ax.text(0.98, 0.95, 'r = −0.174\n(negative correlation)',
        transform=ax.transAxes, fontsize=10, color=GOLD, fontweight='bold',
        ha='right', va='top',
        bbox=dict(boxstyle='round,pad=0.4', facecolor=LIGHT_NAVY, edgecolor=GOLD, alpha=0.9))

ax.set_xlabel('Commercial Payer Share (%)', fontsize=10)
ax.set_ylabel('A&G Cost Per Discharge ($)', fontsize=10)
ax.set_xlim(0, 100)
ax.set_ylim(0, 8500)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:,.0f}'))
ax.legend(loc='upper left', fontsize=8, facecolor=LIGHT_NAVY, edgecolor='#444',
          labelcolor=WHITE, markerscale=2)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_color('#444')
ax.spines['left'].set_color('#444')

fig.suptitle('Admin Cost vs. Commercial Payer Share', fontsize=14,
             fontweight='bold', color=WHITE, y=0.97)
ax.set_title('4,518 Hospitals: More Commercial Payers ≠ Higher Admin Costs',
             fontsize=10, color=GOLD, pad=10)

fig.text(0.12, 0.02,
         'Source: CMS HCRIS FY2023 Worksheets A & S-3. Each dot = one hospital. Y-axis capped at $8,000 for readability.',
         fontsize=6, color='#999', ha='left')
fig.text(0.88, 0.02, 'The American Healthcare Conundrum · Issue #5',
         fontsize=6, color='#999', ha='right')

plt.subplots_adjust(left=0.12, right=0.95, top=0.86, bottom=0.08)
fig.savefig(os.path.join(FIG_DIR, 'chart3_payer_mix_scatter.png'), dpi=150,
            facecolor=NAVY, edgecolor='none')
plt.close(fig)
print("  Saved chart3_payer_mix_scatter.png")

# ══════════════════════════════════════════════════════════════
# CHART 4: 50-State Bar Chart (Admin Cost Per Discharge)
# ══════════════════════════════════════════════════════════════
print("\n--- Chart 4: 50-State Ranking ---")

# Weighted average by state
state_data = {}
for h in hospitals:
    st = h['state']
    if st not in state_data:
        state_data[st] = {'total_ag': 0, 'total_dc': 0, 'count': 0}
    state_data[st]['total_ag'] += h['ag_cost']
    state_data[st]['total_dc'] += h['discharges']
    state_data[st]['count'] += 1

# Filter states with >=5 hospitals
state_avgs = []
for st, d in state_data.items():
    if d['count'] >= 5 and d['total_dc'] > 0:
        state_avgs.append((st, d['total_ag'] / d['total_dc'], d['count']))

state_avgs.sort(key=lambda x: x[1], reverse=True)

fig, ax = plt.subplots(figsize=(10, 9), dpi=100)
fig.patch.set_facecolor(NAVY)
ax.set_facecolor(NAVY)

states = [s[0] for s in state_avgs]
vals = [s[1] for s in state_avgs]
cnts = [s[2] for s in state_avgs]

# National average line
nat_avg = sum(h['ag_cost'] for h in hospitals) / sum(h['discharges'] for h in hospitals)

# Color: above avg = red gradient, below = teal gradient
colors = [RED if v > nat_avg else TEAL for v in vals]

y_pos = np.arange(len(states))
bars = ax.barh(y_pos, vals, color=colors, height=0.7, edgecolor=NAVY)

# National average vertical line
ax.axvline(x=nat_avg, color=GOLD, linestyle='--', linewidth=1.5, zorder=3)
ax.text(nat_avg + 30, len(states) - 2, f'National avg: ${nat_avg:,.0f}',
        fontsize=8, color=GOLD, fontweight='bold', va='center')

# Label top 5 and bottom 5 with values
for i in range(min(5, len(states))):
    ax.text(vals[i] + 20, y_pos[i], f'${vals[i]:,.0f} ({cnts[i]} hosp.)',
            fontsize=6.5, color=WHITE, va='center')
for i in range(max(0, len(states)-5), len(states)):
    ax.text(vals[i] + 20, y_pos[i], f'${vals[i]:,.0f} ({cnts[i]} hosp.)',
            fontsize=6.5, color=WHITE, va='center')

# Highlight Maryland
md_idx = next((i for i, s in enumerate(states) if s == 'MD'), None)
if md_idx is not None:
    bars[md_idx].set_color(GOLD)
    ax.text(vals[md_idx] + 20, y_pos[md_idx], f'${vals[md_idx]:,.0f} (all-payer model)',
            fontsize=6.5, color=GOLD, va='center', fontweight='bold')

ax.set_yticks(y_pos)
ax.set_yticklabels(states, fontsize=6.5)
ax.invert_yaxis()
ax.set_xlabel('Weighted Avg A&G Cost Per Discharge ($)', fontsize=10)
ax.set_xlim(0, max(vals) * 1.25)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:,.0f}'))
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_color('#444')
ax.spines['left'].set_color('#444')

fig.suptitle('Hospital Admin Cost Per Discharge by State', fontsize=14,
             fontweight='bold', color=WHITE, y=0.98)
fig.text(0.5, 0.955, 'Weighted average. Red = above national average. Teal = below. Gold = Maryland (all-payer model).',
         fontsize=8, color=GOLD, ha='center')

fig.text(0.12, 0.01,
         'Source: CMS HCRIS FY2023. States with ≥5 reporting hospitals. Weighted by discharges.',
         fontsize=6, color='#999', ha='left')
fig.text(0.88, 0.01, 'The American Healthcare Conundrum · Issue #5',
         fontsize=6, color='#999', ha='right')

plt.subplots_adjust(left=0.08, right=0.95, top=0.93, bottom=0.05)
fig.savefig(os.path.join(FIG_DIR, 'chart4_state_ranking.png'), dpi=150,
            facecolor=NAVY, edgecolor='none')
plt.close(fig)
print("  Saved chart4_state_ranking.png")

# ══════════════════════════════════════════════════════════════
# CHART 5: Prior Authorization Cost (two-method comparison)
# ══════════════════════════════════════════════════════════════
print("\n--- Chart 5: Prior Auth Costs ---")

fig, ax = plt.subplots(figsize=(10, 5), dpi=100)
fig.patch.set_facecolor(NAVY)
ax.set_facecolor(NAVY)

methods = ['Bottom-Up\n(AMA Survey)', 'Top-Down\n(Bingham TDABC)', 'Total System\n(Health Affairs)']
values_pa = [20.7, 72.5, 93.3]
colors_pa = [TEAL, TEAL, GOLD]
hatches = ['', '', '//']

bars = ax.bar(methods, values_pa, color=colors_pa, width=0.5, edgecolor=NAVY)
# Apply hatch to third bar
bars[2].set_hatch('//')
bars[2].set_edgecolor('#888')

for bar, val in zip(bars, values_pa):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
            f'${val:.1f}B', ha='center', va='bottom', fontsize=13,
            fontweight='bold', color=WHITE)

# Bracket for provider-side range
ax.annotate('', xy=(0, 76), xytext=(1, 76),
            arrowprops=dict(arrowstyle='<->', color=GOLD, lw=1.5))
ax.text(0.5, 79, 'Provider-side range: $21–73B/yr',
        ha='center', va='bottom', fontsize=9, color=GOLD, fontweight='bold')

ax.set_ylabel('Annual Cost ($ Billions)', fontsize=10)
ax.set_ylim(0, 110)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_color('#444')
ax.spines['left'].set_color('#444')

fig.suptitle('National Cost of Prior Authorization', fontsize=14,
             fontweight='bold', color=WHITE, y=0.97)
ax.set_title('Two Provider-Side Estimates + Total System Cost (Including Patient Time)',
             fontsize=10, color=GOLD, pad=10)

fig.text(0.12, 0.02,
         'Sources: AMA 2024 PA Physician Survey; Bingham et al. 2022 (JCO Oncology Practice); Health Affairs 2025 (total system). Hatched bar includes payer, manufacturer, and patient costs.',
         fontsize=5.5, color='#999', ha='left')
fig.text(0.88, 0.02, 'The American Healthcare Conundrum · Issue #5',
         fontsize=6, color='#999', ha='right')

plt.subplots_adjust(left=0.1, right=0.95, top=0.85, bottom=0.12)
fig.savefig(os.path.join(FIG_DIR, 'chart5_prior_auth_cost.png'), dpi=150,
            facecolor=NAVY, edgecolor='none')
plt.close(fig)
print("  Saved chart5_prior_auth_cost.png")

# ══════════════════════════════════════════════════════════════
# CHART 6: Savings Tracker ($328.6B / $3T)
# ══════════════════════════════════════════════════════════════
print("\n--- Chart 6: Savings Tracker ---")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5), dpi=100,
                                gridspec_kw={'width_ratios': [1, 1.5], 'wspace': 0.45})
fig.patch.set_facecolor(NAVY)
ax1.set_facecolor(NAVY)
ax2.set_facecolor(NAVY)

issues = [
    ('Issue #1\nOTC Drugs', 0.6),
    ('Issue #2\nDrug Pricing', 25.0),
    ('Issue #3\nHospitals', 73.0),
    ('Issue #4\nPBM Reform', 30.0),
    ('Issue #5\nAdmin Waste', 200.0),
]
total_savings = sum(v for _, v in issues)
target = 3000

# Left panel: Full $3T scale
ax1.barh([0], [total_savings], color=GOLD, height=0.5, label=f'Identified: ${total_savings:.0f}B')
ax1.barh([0], [target - total_savings], left=[total_savings], color='#333',
         height=0.5, label=f'Remaining: ${target - total_savings:.0f}B')
ax1.set_xlim(0, target)
ax1.set_yticks([])
ax1.set_xlabel('$ Billions', fontsize=9)
ax1.set_title('Full Scale: $3 Trillion Target', fontsize=10, color=GOLD, pad=10)
ax1.text(total_savings/2, 0, f'${total_savings:.0f}B\n({total_savings/target*100:.1f}%)',
         ha='center', va='center', fontsize=10, fontweight='bold', color=NAVY)
ax1.legend(fontsize=7, facecolor=LIGHT_NAVY, edgecolor='#444', labelcolor=WHITE,
           loc='upper right')
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.spines['bottom'].set_color('#444')
ax1.spines['left'].set_visible(False)
ax1.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:,.0f}B'))

# Right panel: Zoomed $400B window
issue_labels = [i[0] for i in issues]
issue_vals = [i[1] for i in issues]
issue_colors = [TEAL, TEAL, TEAL, TEAL, GOLD]

y_pos = np.arange(len(issues))
bars = ax2.barh(y_pos, issue_vals, color=issue_colors, height=0.6, edgecolor=NAVY)

for bar, val in zip(bars, issue_vals):
    w = bar.get_width()
    if w > 15:
        ax2.text(w - 1, bar.get_y() + bar.get_height()/2,
                 f'${val:.0f}B', ha='right', va='center', fontsize=10,
                 fontweight='bold', color=WHITE if val < 100 else NAVY)
    else:
        ax2.text(w + 2, bar.get_y() + bar.get_height()/2,
                 f'${val:.1f}B', ha='left', va='center', fontsize=9, color=WHITE)

ax2.set_yticks(y_pos)
ax2.set_yticklabels(issue_labels, fontsize=8)
ax2.invert_yaxis()
ax2.set_xlim(0, 250)
ax2.set_xlabel('$ Billions / Year', fontsize=9)
ax2.set_title(f'Per-Issue Breakdown (Total: ${total_savings:.0f}B)', fontsize=10,
              color=GOLD, pad=10)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['bottom'].set_color('#444')
ax2.spines['left'].set_color('#444')
ax2.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:.0f}B'))

fig.suptitle('Savings Tracker: $328.6 Billion and Counting',
             fontsize=14, fontweight='bold', color=WHITE, y=0.98)
fig.text(0.5, 0.935,
         f'11.0% of the $3 Trillion Annual US-Japan Per-Capita Spending Gap',
         fontsize=9, color=GOLD, ha='center')

fig.text(0.12, 0.02,
         'US per-capita: $14,570 (CMS NHE 2023). Japan: $5,790 (OECD 2025). Gap × 335M population = ~$3T.',
         fontsize=5.5, color='#999', ha='left')
fig.text(0.88, 0.02, 'The American Healthcare Conundrum · Issue #5',
         fontsize=6, color='#999', ha='right')

plt.subplots_adjust(left=0.12, right=0.95, top=0.88, bottom=0.08)
fig.savefig(os.path.join(FIG_DIR, 'chart6_savings_tracker.png'), dpi=150,
            facecolor=NAVY, edgecolor='none')
plt.close(fig)
print("  Saved chart6_savings_tracker.png")

print(f"\n{'='*60}")
print(f"All 6 charts generated in {FIG_DIR}/")
print(f"{'='*60}")
