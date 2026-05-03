"""
Issue #10 Chart Generation -- All 5 charts + hero for "The Procedure Mill"
Brand colors: Navy #1A1F2E, Teal #0E8A72, Red #B7182A, Gold #D4AF37, White #F8F8F6
Font: DejaVu Sans (no emoji glyphs)
Rules: figsize <= (10,6) at dpi=100; savefig at dpi=150; plt.close(fig) after every save.
"""
import csv
import json
import os
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

# ── Paths ──
HERE = Path(__file__).resolve().parent
FIG  = HERE / "figures"
RES  = HERE / "results"
FIG.mkdir(exist_ok=True)

# ── Wipe existing PNGs ──
for f in FIG.glob("*.png"):
    f.unlink()
print(f"Wiped figures/*.png — ready for clean build")

# ── Brand colors ──
NAVY       = '#1A1F2E'
TEAL       = '#0E8A72'
RED        = '#B7182A'
GOLD       = '#D4AF37'
WHITE      = '#F8F8F6'
LIGHT_TEAL = '#16B898'
LIGHT_NAVY = '#2A3048'
MID_GRAY   = '#555A6A'

plt.rcParams.update({
    'font.family':    'DejaVu Sans',
    'text.color':     WHITE,
    'axes.labelcolor':WHITE,
    'xtick.color':    WHITE,
    'ytick.color':    WHITE,
})


# ════════════════════════════════════════════════════════════════
# CHART 1: State Variance -- horizontal bar of 51 states
# ════════════════════════════════════════════════════════════════
def chart1_state_variance():
    print("\n--- Chart 1: State Variance ---")

    states_data = []
    with open(RES / "component_b_state_variance.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            states_data.append({
                'postal': row['state_postal'],
                'per_bene': float(row['per_bene_lv_pymt']),
            })

    # Sort lowest to highest (so highest is at top when inverted)
    states_data.sort(key=lambda x: x['per_bene'])
    labels  = [d['postal'] for d in states_data]
    values  = [d['per_bene'] for d in states_data]
    n       = len(labels)

    national_median = 53.42
    p10  = 36.41
    p90  = 92.50

    # Colors: highlight NY (highest) = RED, VT (lowest) = TEAL, rest = gradient
    def bar_color(v, postal):
        if postal == 'NY':  return RED
        if postal == 'VT':  return TEAL
        if v >= p90:        return '#C44040'
        if v <= p10:        return '#1AA888'
        # interpolate between LIGHT_NAVY and mid color
        return '#4A6080'

    colors = [bar_color(v, p) for v, p in zip(values, labels)]

    fig, ax = plt.subplots(figsize=(10, 13), dpi=100)
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)

    y_pos = np.arange(n)
    bars = ax.barh(y_pos, values, color=colors, height=0.75, edgecolor=NAVY)

    # National median vertical line
    ax.axvline(x=national_median, color=GOLD, linestyle='--', linewidth=1.5, zorder=4)
    ax.text(national_median + 0.8, n - 1.5, f'Median\n${national_median:.0f}',
            fontsize=7, color=GOLD, fontweight='bold', va='center')

    # Label NY and VT bars explicitly
    ny_idx = labels.index('NY')
    vt_idx = labels.index('VT')
    ax.text(values[ny_idx] + 1.0, y_pos[ny_idx],
            f'NY  ${values[ny_idx]:.0f}/bene', ha='left', va='center',
            fontsize=8, color=RED, fontweight='bold')
    ax.text(values[vt_idx] + 1.0, y_pos[vt_idx],
            f'VT  ${values[vt_idx]:.0f}/bene', ha='left', va='center',
            fontsize=8, color=TEAL, fontweight='bold')

    # P10 / P90 region shading
    ax.axvspan(p10, p90, alpha=0.06, color=GOLD, zorder=0)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=6.5)
    ax.invert_yaxis()
    ax.set_xlabel('Low-Value Medicare Paid per FFS Beneficiary ($)', fontsize=9, color=WHITE, labelpad=14)
    ax.set_xlim(0, 130)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}'))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#555')
    ax.spines['left'].set_color('#555')

    fig.suptitle('Low-Value Care per Medicare FFS Beneficiary, by State (CY2023)',
                 fontsize=12, fontweight='bold', color=WHITE, y=0.995)
    ax.set_title('P90/P10 spread 2.54x  |  NY-to-VT ratio 6.7x  |  Shaded band = P10-P90 range',
                 fontsize=7.5, color=GOLD, pad=4)

    fig.text(0.12, 0.005,
             'Source: CMS Provider Utilization PUF CY2023 + CMS HOPD PUF CY2023. '
             'Schwartz/Mafi 31 measures, mean-share dedup (Pass 3). Author analysis.',
             fontsize=5.5, color='#999', ha='left')
    fig.text(0.88, 0.005, 'The American Healthcare Conundrum  Issue #10',
             fontsize=5.5, color='#999', ha='right')

    plt.subplots_adjust(left=0.08, right=0.82, top=0.972, bottom=0.055)
    out = FIG / 'chart1_state_variance.png'
    fig.savefig(out, dpi=150, facecolor=NAVY, edgecolor='none')
    plt.close(fig)
    print(f"  Saved {out}")
    return out


# ════════════════════════════════════════════════════════════════
# CHART 2: Top 10 Schwartz Measures by Medicare Paid
# ════════════════════════════════════════════════════════════════
def chart2_top_measures():
    print("\n--- Chart 2: Top Schwartz Measures ---")

    # Aggregate lv_paid_mean by measure from pass3 CSV
    measure_totals = {}
    measure_total_paid = {}
    measure_mean_share = {}

    with open(RES / "pass3" / "component_a_pass3.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            combined = float(row['combined_paid'])
            lv_mean  = float(row['lv_paid_mean'])
            ms       = float(row['mean_share'])
            if row['n_measures'] == '1':
                mkey = row['measures_list']
            else:
                # dual-mapped: attribute to the primary measure (first listed)
                mkey = row['measures_list'].strip('"').split(',')[0]
            if mkey not in measure_totals:
                measure_totals[mkey]     = 0.0
                measure_total_paid[mkey] = 0.0
                measure_mean_share[mkey] = ms
            measure_totals[mkey]     += lv_mean
            measure_total_paid[mkey] += combined

    # Human-readable measure labels and mean shares
    measure_labels = {
        'cncr':    'Cancer screening (low-risk)',
        'colon':   'Colonoscopy (low-risk)',
        'preopec': 'Preop echocardiogram',
        'preopst': 'Preop stress test',
        'backscan':'Back imaging (low back pain)',
        'head':    'Head imaging (syncope)',
        'sync':    'Head imaging (syncope) HOPD',
        'spinj':   'Spinal injections',
        'bmd':     'Bone density screening',
        'ctdasym': 'Carotid imaging (asymptomatic)',
        'pci':     'PCI for stable CAD',
        'psa':     'PSA screening',
        'stress':  'Stress test (stable CAD)',
        'pth':     'PTH lab test',
        'plant':   'Plantar fascia imaging',
        'cerv':    'Cervical cancer screening',
        'rhcath':  'Right heart catheterization',
        'ivc':     'IVC filter',
        'cea':     'Carotid endarterectomy',
        'arth':    'Knee arthroscopy (OA)',
        't3':      'T3 measurement',
        'eeg':     'EEG (headache)',
        'vert':    'Vertebroplasty',
        'renlstent':'Renal artery stenting',
        'homocy':  'Homocysteine lab test',
        'hyperco': 'Hypercoagulability testing',
        'pft':     'Pulmonary function tests',
        'rhinoct': 'Sinus CT (rhinosinusitis)',
        'vitd':    'Vitamin D testing',
    }
    share_labels = {
        'cncr': '0.10', 'colon': '0.13', 'preopec': '0.50', 'preopst': '0.45',
        'backscan': '0.50', 'head': '0.50', 'spinj': '0.35', 'bmd': '0.30',
        'ctdasym': '0.55', 'pci': '0.45', 'psa': '0.45', 'stress': '0.45',
        'pth': '0.40', 'plant': '0.35', 'cerv': 'var', 'rhcath': 'var',
        'ivc': '0.55', 'cea': '0.30', 'arth': '0.65', 't3': '0.50',
        'eeg': 'var', 'vert': '0.55', 'renlstent': '0.70',
        'homocy': 'var', 'hyperco': 'var', 'pft': 'var', 'rhinoct': '0.50',
        'vitd': '0.35',
    }

    # Merge sync into head (same HCPCS, different context)
    if 'sync' in measure_totals:
        measure_totals['head'] = measure_totals.get('head', 0) + measure_totals.pop('sync')
        measure_total_paid['head'] = measure_total_paid.get('head', 0) + measure_total_paid.pop('sync', 0)
    if 'ctdsync' in measure_totals:
        measure_totals['ctdasym'] = measure_totals.get('ctdasym', 0) + measure_totals.pop('ctdsync')
        measure_total_paid['ctdasym'] = measure_total_paid.get('ctdasym', 0) + measure_total_paid.pop('ctdsync', 0)
    if 'stress' in measure_totals and 'preopst' in measure_totals:
        # stress and preopst share HCPCS: already deduped in pass3; show preopst only
        del measure_totals['stress']
        del measure_total_paid['stress']

    # Sort and take top 10 by lv_paid_mean
    sorted_measures = sorted(
        [(k, v) for k, v in measure_totals.items() if v > 0],
        key=lambda x: x[1], reverse=True
    )[:10]

    m_keys  = [m[0] for m in sorted_measures]
    lv_vals = [m[1] / 1e6 for m in sorted_measures]  # in $M
    tot_paid= [measure_total_paid[k] / 1e6 for k in m_keys]
    # "clean" portion = total paid minus low-value
    clean_vals = [max(0, t - lv) for t, lv in zip(tot_paid, lv_vals)]
    labels_full = [measure_labels.get(k, k) for k in m_keys]
    shares      = [share_labels.get(k, '') for k in m_keys]

    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)

    y_pos = np.arange(len(m_keys))

    # Stacked: clean (teal) + low-value (red)
    bars_clean = ax.barh(y_pos, clean_vals, color=TEAL, height=0.65,
                         edgecolor=NAVY, label='Total Medicare paid (clean portion)')
    bars_lv    = ax.barh(y_pos, lv_vals, left=clean_vals, color=RED, height=0.65,
                         edgecolor=NAVY, label='Low-value share (mean-share dedup)')

    # Labels: measure name on y-axis side, LV dollar on end of bar
    for i, (lv, tot, clean, lbl, sh) in enumerate(zip(lv_vals, tot_paid, clean_vals, labels_full, shares)):
        # Measure label
        ax.text(-1, y_pos[i], lbl, ha='right', va='center', fontsize=8, color=WHITE)
        # LV share label at end of full bar
        end_x = tot
        share_str = f'share={sh}' if sh else ''
        ax.text(end_x + 5, y_pos[i],
                f'${lv:.0f}M LV  ({share_str})',
                ha='left', va='center', fontsize=7.5, color=RED)

    ax.set_yticks(y_pos)
    ax.set_yticklabels([''] * len(y_pos))  # suppress default labels (we draw custom)
    ax.invert_yaxis()
    ax.set_xlabel('Medicare Paid ($ Millions)', fontsize=9)
    ax.set_xlim(-185, max(tot_paid) * 1.45)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}M' if x >= 0 else ''))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#555')
    ax.spines['left'].set_visible(False)

    legend_handles = [
        mpatches.Patch(color=TEAL, label='Total paid (clean portion)'),
        mpatches.Patch(color=RED,  label='Low-value share'),
    ]
    ax.legend(handles=legend_handles, loc='lower right', fontsize=8,
              facecolor=LIGHT_NAVY, edgecolor='#555', labelcolor=WHITE)

    fig.suptitle('Top 10 Schwartz/Mafi Measures by Medicare Paid (CY2023)',
                 fontsize=13, fontweight='bold', color=WHITE, y=0.98)
    ax.set_title('Mean-share dedup applied to dual-mapped HCPCS codes. Red = low-value share.',
                 fontsize=8.5, color=GOLD, pad=8)

    fig.text(0.12, 0.02,
             'Source: CMS Provider Utilization PUF + CMS HOPD PUF CY2023. '
             'Schwartz/Mafi/Mathematica 31 measures. Mean-share dedup (Pass 3). Author analysis.',
             fontsize=5.5, color='#999', ha='left')
    fig.text(0.88, 0.02, 'The American Healthcare Conundrum  Issue #10',
             fontsize=5.5, color='#999', ha='right')

    plt.subplots_adjust(left=0.30, right=0.85, top=0.88, bottom=0.10)
    out = FIG / 'chart2_top_measures.png'
    fig.savefig(out, dpi=150, facecolor=NAVY, edgecolor='none')
    plt.close(fig)
    print(f"  Saved {out}")
    return out


# ════════════════════════════════════════════════════════════════
# CHART 3: Kim & Fendrick Comparison
# ════════════════════════════════════════════════════════════════
def chart3_kim_fendrick():
    print("\n--- Chart 3: Kim & Fendrick Comparison ---")

    studies = [
        {
            'name': 'Kim & Fendrick 2025\n(JAMA Health Forum)',
            'services': '47 services',
            'sample':   '5% sample',
            'year':     'CY2018-2020',
            'scope':    'Medicare FFS only',
            'dollars':  3.6,
            'color':    TEAL,
            'note':     'Diagnosis-code filtered\n(claim-level precision)',
        },
        {
            'name': 'AHC Issue #10\n(This analysis)',
            'services': '31 Schwartz measures',
            'sample':   '100% PUF',
            'year':     'CY2023',
            'scope':    'Multi-payer + def. medicine',
            'dollars':  7.63,
            'color':    GOLD,
            'note':     'Published-multiplier extension\n(no claim-level dx codes)',
        },
    ]

    fig, ax = plt.subplots(figsize=(9, 5), dpi=100)
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)

    x_pos = [0, 1.6]
    bar_w = 0.7

    for i, s in enumerate(studies):
        bar = ax.bar(x_pos[i], s['dollars'], width=bar_w, color=s['color'],
                     edgecolor=NAVY, zorder=3)
        # Dollar label on top of bar -- use contrasting color for visibility
        label_color = WHITE if s['color'] == TEAL else NAVY
        ax.text(x_pos[i], s['dollars'] + 0.18,
                f"${s['dollars']:.1f}B",
                ha='center', va='bottom', fontsize=16, fontweight='bold', color=s['color'])
        # Study name below x-axis
        ax.text(x_pos[i], -0.35, s['name'],
                ha='center', va='top', fontsize=9, color=WHITE, fontweight='bold')

    # Attribute table
    row_y   = [6.5, 5.9, 5.3, 4.7, 4.1]
    row_keys= ['services', 'sample', 'year', 'scope', 'note']
    row_labels_text = ['Services:', 'Sample:', 'Year:', 'Scope:', 'Method note:']
    for ry, rk, rlbl in zip(row_y, row_keys, row_labels_text):
        ax.text(-0.45, ry, rlbl, ha='right', va='center', fontsize=7.5, color='#AAA')
        for i, s in enumerate(studies):
            ax.text(x_pos[i], ry, s[rk], ha='center', va='center',
                    fontsize=7.5, color=WHITE,
                    bbox=dict(boxstyle='round,pad=0.2', facecolor=LIGHT_NAVY, alpha=0.7,
                              edgecolor='none'))

    ax.set_xlim(-0.7, 2.5)
    ax.set_ylim(-1.0, 8.5)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    # Connector note
    ax.annotate('', xy=(1.6 - bar_w/2 - 0.05, 3.6), xytext=(0 + bar_w/2 + 0.05, 3.6),
                arrowprops=dict(arrowstyle='->', color='#888', lw=1.5))
    ax.text(0.8, 3.75, 'Different scope -- both valid', ha='center', va='bottom',
            fontsize=7.5, color='#AAA', style='italic')

    fig.suptitle('Issue #10 vs. Kim & Fendrick 2025: Same Framework, Wider Scope',
                 fontsize=12, fontweight='bold', color=WHITE, y=0.98)
    ax.set_title('Teal = peer-reviewed prior estimate.  Gold = this analysis (wider scope, later year).',
                 fontsize=8, color=GOLD, pad=6)

    fig.text(0.12, 0.015,
             'Kim DD, Fendrick AM. JAMA Health Forum. 2025;6(8):e253050. '
             'AHC Issue #10 analysis: CMS PUF CY2023, Schwartz/Mafi 31 measures, multi-payer extension.',
             fontsize=5.5, color='#999', ha='left', wrap=True)

    plt.subplots_adjust(left=0.10, right=0.92, top=0.88, bottom=0.14)
    # Right-side attribution -- placed separately to avoid collision with citation
    fig.text(0.88, 0.003, 'The American Healthcare Conundrum  Issue #10',
             fontsize=5.5, color='#999', ha='right')
    out = FIG / 'chart3_kim_fendrick.png'
    fig.savefig(out, dpi=150, facecolor=NAVY, edgecolor='none')
    plt.close(fig)
    print(f"  Saved {out}")
    return out


# ════════════════════════════════════════════════════════════════
# CHART 4: WISeR Pilot -- 6 states
# ════════════════════════════════════════════════════════════════
def chart4_wiser_pilot():
    print("\n--- Chart 4: WISeR Pilot States ---")

    states = []
    with open(RES / "component_d_wiser_pilot.csv") as f:
        reader = csv.DictReader(f)
        for row in reader:
            states.append({
                'state': row['state'],
                'phys':  float(row['wiser_phys_pymt']),
                'hopd':  float(row['wiser_hopd_pymt']),
                'total': float(row['wiser_pilot_pymt']),
            })

    states.sort(key=lambda x: x['total'], reverse=True)
    s_labels = [s['state'] for s in states]
    phys_vals= [s['phys'] / 1e6 for s in states]
    hopd_vals= [s['hopd'] / 1e6 for s in states]
    tot_vals = [s['total'] / 1e6 for s in states]
    nat_total = sum(tot_vals)

    fig, ax = plt.subplots(figsize=(9, 5), dpi=100)
    fig.patch.set_facecolor(NAVY)
    ax.set_facecolor(NAVY)

    y_pos = np.arange(len(states))
    bars_phys = ax.barh(y_pos, phys_vals, color=TEAL, height=0.6,
                        edgecolor=NAVY, label='Physician-administered (POS phys)')
    bars_hopd = ax.barh(y_pos, hopd_vals, left=phys_vals, color=GOLD, height=0.6,
                        edgecolor=NAVY, label='Hospital outpatient (HOPD)')

    for i, (tv, pv, hv) in enumerate(zip(tot_vals, phys_vals, hopd_vals)):
        # Total label at end
        ax.text(tv + 0.5, y_pos[i],
                f'${tv:.1f}M total',
                ha='left', va='center', fontsize=8.5, color=WHITE)
        # HOPD label inside if wide enough
        if hv > 5:
            ax.text(pv + hv/2, y_pos[i],
                    f'HOPD\n${hv:.0f}M',
                    ha='center', va='center', fontsize=6.5, color=NAVY, fontweight='bold')

    # National total annotation box -- upper right, clear of legend
    ax.text(0.98, 0.97,
            f'6-state total: ${nat_total:.0f}M  (CY2023 baseline)',
            transform=ax.transAxes, fontsize=9, color=GOLD, fontweight='bold',
            ha='right', va='top',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=LIGHT_NAVY,
                      edgecolor=GOLD, alpha=0.95))

    ax.set_yticks(y_pos)
    ax.set_yticklabels(s_labels, fontsize=10, fontweight='bold')
    ax.invert_yaxis()
    ax.set_xlabel('CY2023 Medicare Paid on 17 WISeR Procedures ($ Millions)', fontsize=9)
    ax.set_xlim(0, max(tot_vals) * 1.45)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}M'))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_color('#555')
    ax.spines['left'].set_color('#555')

    ax.legend(loc='lower right', fontsize=8, facecolor=LIGHT_NAVY,
              edgecolor='#555', labelcolor=WHITE)

    fig.suptitle('WISeR Pilot: Medicare Paid on 17 Procedures by State (CY2023 Baseline)',
                 fontsize=12, fontweight='bold', color=WHITE, y=0.98)
    ax.set_title('6 pilot states (AZ, NJ, OH, OK, TX, WA). WISeR launched Jan 1, 2026.',
                 fontsize=8.5, color=GOLD, pad=8)

    fig.text(0.12, 0.02,
             'Source: CMS Provider Utilization PUF + CMS HOPD PUF CY2023. '
             'CMS WISeR Operational Guide v5.0 (Mar 2026). 17 WISeR procedures. '
             'Author analysis.',
             fontsize=5.5, color='#999', ha='left')
    fig.text(0.88, 0.02, 'The American Healthcare Conundrum  Issue #10',
             fontsize=5.5, color='#999', ha='right')

    plt.subplots_adjust(left=0.16, right=0.88, top=0.88, bottom=0.12)
    out = FIG / 'chart4_wiser_pilot.png'
    fig.savefig(out, dpi=150, facecolor=NAVY, edgecolor='none')
    plt.close(fig)
    print(f"  Saved {out}")
    return out


# ════════════════════════════════════════════════════════════════
# CHART 5: Savings Tracker (cumulative Issues #1-#10)
# ════════════════════════════════════════════════════════════════
def chart5_savings_tracker():
    print("\n--- Chart 5: Savings Tracker ---")

    issues = [
        ('#1  OTC Drugs',     0.6),
        ('#2  Drug Pricing',  25.0),
        ('#3  Hospitals',     73.0),
        ('#4  PBMs',          30.0),
        ('#5  Admin Waste',  200.0),
        ('#6  Supply Waste',  28.0),
        ('#7  GLP-1',         40.0),
        ('#8  Denial Machine',32.0),
        ('#9  Employer Trap',  6.6),
        ('#10 Procedure Mill', 7.6),
    ]

    target   = 3240.0  # $3.24T in billions
    total_b  = sum(v for _, v in issues)
    pct      = total_b / target * 100

    # Color gradient: teal for #1-9, gold for #10
    colors_issues = [TEAL] * 9 + [GOLD]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5.5), dpi=100,
                                   gridspec_kw={'width_ratios': [1, 1.7], 'wspace': 0.45})
    fig.patch.set_facecolor(NAVY)
    ax1.set_facecolor(NAVY)
    ax2.set_facecolor(NAVY)

    # LEFT: Full $3.24T scale single bar
    ax1.barh([0], [total_b],  color=GOLD,  height=0.45, label=f'Identified: ${total_b:.1f}B')
    ax1.barh([0], [target - total_b], left=[total_b], color='#2A3048',
             height=0.45, label=f'Remaining: ${target - total_b:.0f}B')

    ax1.set_xlim(0, target)
    ax1.set_yticks([])
    ax1.set_xlabel('$ Billions', fontsize=8)
    ax1.set_title('Full $3.24T Scale', fontsize=9, color=GOLD, pad=8)
    # Label outside the bar (gold bar too narrow to fit text inside)
    ax1.text(total_b + 40, 0, f'${total_b:.1f}B\n({pct:.1f}%)',
             ha='left', va='center', fontsize=9, fontweight='bold', color=GOLD)
    ax1.legend(fontsize=6.5, facecolor=LIGHT_NAVY, edgecolor='#444',
               labelcolor=WHITE, loc='upper right')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['bottom'].set_color('#555')
    ax1.spines['left'].set_visible(False)
    ax1.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x/1000:.1f}T' if x >= 1000 else f'${x:.0f}B'))

    # RIGHT: Per-issue breakdown
    labels_r = [i[0] for i in issues]
    vals_r   = [i[1] for i in issues]
    y_pos    = np.arange(len(issues))

    bars = ax2.barh(y_pos, vals_r, color=colors_issues, height=0.65, edgecolor=NAVY)

    for bar, val in zip(bars, vals_r):
        w = bar.get_width()
        if w >= 15:
            ax2.text(w - 1.5, bar.get_y() + bar.get_height()/2,
                     f'${val:.1f}B', ha='right', va='center',
                     fontsize=9, fontweight='bold', color=NAVY)
        else:
            ax2.text(w + 2, bar.get_y() + bar.get_height()/2,
                     f'${val:.1f}B', ha='left', va='center',
                     fontsize=8.5, color=WHITE)

    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(labels_r, fontsize=8)
    ax2.invert_yaxis()
    ax2.set_xlim(0, 230)
    ax2.set_xlabel('$ Billions / Year', fontsize=8)
    ax2.set_title(f'Per-Issue Breakdown (Total: ${total_b:.1f}B)', fontsize=9,
                  color=GOLD, pad=8)
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['bottom'].set_color('#555')
    ax2.spines['left'].set_color('#555')
    ax2.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:.0f}B'))

    fig.suptitle(f'Savings Tracker: ${total_b:.1f} Billion and Counting',
                 fontsize=14, fontweight='bold', color=WHITE, y=0.99)
    fig.text(0.5, 0.945,
             f'{pct:.1f}% of the $3.24T Annual US-Japan Per-Capita Spending Gap  (10 issues)',
             fontsize=9, color=GOLD, ha='center')

    fig.text(0.12, 0.02,
             'US per-capita: $15,474 (CMS NHE 2024). Japan: $5,790 (OECD 2025). '
             'Gap x 336M population = $3.24T.',
             fontsize=5.5, color='#999', ha='left')
    fig.text(0.88, 0.02, 'The American Healthcare Conundrum  Issue #10',
             fontsize=5.5, color='#999', ha='right')

    plt.subplots_adjust(left=0.14, right=0.96, top=0.90, bottom=0.10)
    out = FIG / 'chart5_savings_tracker.png'
    fig.savefig(out, dpi=150, facecolor=NAVY, edgecolor='none')
    plt.close(fig)
    print(f"  Saved {out}")
    return out


# ════════════════════════════════════════════════════════════════
# HERO IMAGE: 1456x1048 px output (14:10, save at 150dpi)
# ════════════════════════════════════════════════════════════════
def chart_hero():
    print("\n--- Hero Image ---")

    # Disable mathtext dollar-sign interpretation
    plt.rcParams['text.parse_math'] = False

    FW = 9.71
    FH = 6.99

    fig = plt.figure(figsize=(FW, FH), dpi=100)
    fig.patch.set_facecolor(NAVY)

    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_facecolor(NAVY)
    ax.axis('off')

    # Subtle grid background
    for x in np.arange(0, 1.01, 0.05):
        ax.axvline(x, color='#222840', linewidth=0.4, alpha=0.6, zorder=0)
    for y in np.arange(0, 1.01, 0.05):
        ax.axhline(y, color='#222840', linewidth=0.4, alpha=0.6, zorder=0)

    # Series branding (top center)
    ax.text(0.5, 0.93,
            'THE AMERICAN HEALTHCARE CONUNDRUM',
            ha='center', va='top', fontsize=9, fontweight='bold',
            color=RED, transform=ax.transAxes, zorder=5)
    ax.text(0.5, 0.885,
            'ISSUE  #10',
            ha='center', va='top', fontsize=16, fontweight='bold',
            color=GOLD, transform=ax.transAxes, zorder=5)

    # Red divider line
    ax.axhline(0.86, xmin=0.25, xmax=0.75, color=RED, linewidth=1.8, zorder=5)

    # Main hook: large number without dollar sign (mathtext workaround)
    ax.text(0.5, 0.72,
            '7.6 BILLION',
            ha='center', va='center', fontsize=58, fontweight='bold',
            color=WHITE, transform=ax.transAxes, zorder=5)
    ax.text(0.5, 0.655,
            'U.S. DOLLARS IN LOW-VALUE CARE ANNUALLY',
            ha='center', va='center', fontsize=9, fontweight='bold',
            color='#888', transform=ax.transAxes, zorder=5)

    # Subtitle line
    ax.text(0.5, 0.57,
            'Low-Value Care, Billed Anyway',
            ha='center', va='center', fontsize=18, fontweight='bold',
            color=GOLD, transform=ax.transAxes, zorder=5)

    ax.text(0.5, 0.50,
            '31 Schwartz measures  |  All-payer  |  CY2023  |  Deduplicated',
            ha='center', va='center', fontsize=10.5, color='#C8C8C8',
            transform=ax.transAxes, zorder=5)

    # Comparison callout (avoid dollar sign to prevent mathtext issues)
    ax.axhline(0.435, xmin=0.22, xmax=0.78, color='#3A4060', linewidth=1.0, zorder=5)

    ax.text(0.5, 0.40,
            'NY: 107 per bene             vs.             VT: 16 per bene',
            ha='center', va='center', fontsize=12, color=WHITE,
            transform=ax.transAxes, zorder=5,
            bbox=dict(boxstyle='round,pad=0.4', facecolor=LIGHT_NAVY,
                      edgecolor='#3A4060', alpha=0.95))
    ax.text(0.5, 0.355,
            '6.7x state-level spread in services the evidence says should not be ordered',
            ha='center', va='center', fontsize=9, color='#AAA',
            transform=ax.transAxes, zorder=5)

    # Stats bar at bottom of safe zone
    stats = [
        ('31', 'Schwartz\nmeasures'),
        ('6.7x', 'State\nspread'),
        ('2.54x', 'P90/P10\nratio'),
        ('13.6B', 'Range high'),
    ]
    stat_xs = [0.22, 0.38, 0.62, 0.78]
    for sx, (val, lbl) in zip(stat_xs, stats):
        ax.text(sx, 0.27, val, ha='center', va='bottom', fontsize=14,
                fontweight='bold', color=TEAL, transform=ax.transAxes, zorder=5)
        ax.text(sx, 0.25, lbl, ha='center', va='top', fontsize=6.5,
                color='#AAA', transform=ax.transAxes, zorder=5)

    ax.axhline(0.26, xmin=0.18, xmax=0.82, color='#3A4060', linewidth=0.8, zorder=5)

    # Bottom brand line
    ax.text(0.5, 0.06,
            'andrewrexroad.substack.com',
            ha='center', va='center', fontsize=8, color='#666',
            transform=ax.transAxes, zorder=5)

    out = FIG / 'hero_cover.png'
    fig.savefig(out, dpi=150, facecolor=NAVY, edgecolor='none')
    plt.close(fig)
    print(f"  Saved {out}")
    return out


# ════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    outputs = []
    outputs.append(chart1_state_variance())
    outputs.append(chart2_top_measures())
    outputs.append(chart3_kim_fendrick())
    outputs.append(chart4_wiser_pilot())
    outputs.append(chart5_savings_tracker())
    outputs.append(chart_hero())

    print(f"\n{'='*60}")
    print(f"All {len(outputs)} charts generated in {FIG}/")
    print(f"{'='*60}")
    for p in outputs:
        print(f"  {p.name}")
