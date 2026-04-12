"""
Issue #7 Chart Generation — GLP-1 Gold Rush
All 5 charts for "The GLP-1 Gold Rush" newsletter
Brand colors: Navy #1A1F2E, Teal #0E8A72, Red #B7182A, Gold #D4AF37, White #F8F8F6

Charts:
1. GLP-1 US Market Growth (2018-2025) — area chart
2. International Price Comparison — horizontal bar
3. BALANCE 10-Year Cost Projection (Low/Mid/High) — stacked area
4. US vs International Pricing Structure — waterfall
5. Savings Tracker (Issues #1-7) — horizontal stacked bar
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ── Paths ──
BASE = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.join(BASE, "figures")
os.makedirs(FIG_DIR, exist_ok=True)

# ── Brand Colors ──
NAVY = '#1A1F2E'
TEAL = '#0E8A72'
RED = '#B7182A'
GOLD = '#D4AF37'
WHITE = '#F8F8F6'
LIGHT_TEAL = '#16B898'
LIGHT_NAVY = '#2A3048'
DARK_GRAY = '#444444'

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'text.color': WHITE,
    'axes.labelcolor': WHITE,
    'xtick.color': WHITE,
    'ytick.color': WHITE,
})

# ════════════════════════════════════════════════════════════════
# CHART 1: GLP-1 US Market Growth (2018-2025)
# ════════════════════════════════════════════════════════════════
print("\n--- Chart 1: GLP-1 Market Growth ---")

# Historical data (2018-2023 actual) + 2024-2025 estimates + 2028 projection
years = np.array([2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028])
spending = np.array([0.057, 0.15, 0.35, 1.2, 5.7, 71.7, 82.0, 95.0, 105.0, 110.0, 115.0])
actual_through = 2023
projected_from = 2024

fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
fig.patch.set_facecolor(NAVY)
ax.set_facecolor(NAVY)

# Plot actual data
actual_mask = years <= actual_through
ax.fill_between(years[actual_mask], 0, spending[actual_mask],
                color=TEAL, alpha=0.7, label='Actual (2018-2023)')
ax.plot(years[actual_mask], spending[actual_mask], color=LIGHT_TEAL, linewidth=2.5)

# Plot projected data (dashed line)
projected_mask = years >= actual_through
ax.plot(years[projected_mask], spending[projected_mask], color=GOLD, linewidth=2.5,
        linestyle='--', label='Projected (2024-2028)')
ax.fill_between(years[projected_mask], 0, spending[projected_mask],
                color=GOLD, alpha=0.3)

# Add key annotations
ax.text(2023, 75, '$71.7B\n2023 Actual', ha='center', va='bottom',
        fontsize=9, fontweight='bold', color=GOLD, bbox=dict(boxstyle='round,pad=0.3',
        facecolor=NAVY, edgecolor=GOLD, linewidth=1.5, alpha=0.9))

ax.text(2028, 118, '$115B+\nProjection', ha='center', va='bottom',
        fontsize=9, fontweight='bold', color=GOLD, bbox=dict(boxstyle='round,pad=0.3',
        facecolor=NAVY, edgecolor=GOLD, linewidth=1.5, alpha=0.9))

# Formatting
ax.set_xlabel('Year', fontsize=10, fontweight='bold')
ax.set_ylabel('Annual Spending ($ Billions)', fontsize=10, fontweight='bold')
ax.set_xlim(2017.5, 2028.5)
ax.set_ylim(0, 130)
ax.set_xticks(range(2018, 2029, 1))
ax.set_xticklabels(range(2018, 2029, 1), fontsize=9)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:.0f}B'))
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_color(DARK_GRAY)
ax.spines['left'].set_color(DARK_GRAY)
ax.grid(axis='y', alpha=0.15, color=WHITE, linestyle='-', linewidth=0.5)

fig.suptitle('GLP-1 US Market Growth: 1,200-Fold Increase in 5 Years',
             fontsize=14, fontweight='bold', color=WHITE, y=0.97)
ax.set_title('From $57M (2018) to $71.7B (2023) — Fastest-Growing Drug Class Ever',
             fontsize=10, color=TEAL, pad=10)

ax.legend(loc='upper left', fontsize=9, framealpha=0.9, facecolor=LIGHT_NAVY, edgecolor=GOLD)

fig.text(0.12, 0.02, 'Sources: CMS Part D spending 2018-2023; JAMA Network Open 2024; manufacturer earnings 2024-2025',
         fontsize=5.5, color='#999', ha='left')
fig.text(0.88, 0.02, 'The American Healthcare Conundrum · Issue #7',
         fontsize=5.5, color='#999', ha='right')

plt.subplots_adjust(left=0.12, right=0.95, top=0.87, bottom=0.10)
fig.savefig(os.path.join(FIG_DIR, 'chart1_market_growth.png'), dpi=150,
            facecolor=NAVY, edgecolor='none')
plt.close(fig)
print("  Saved chart1_market_growth.png")

# ════════════════════════════════════════════════════════════════
# CHART 2: International Price Comparison
# ════════════════════════════════════════════════════════════════
print("\n--- Chart 2: Price Comparison ---")

countries = ['US Retail\nBrand', 'US BALANCE\nNegotiated', 'IRA\nNegotiated\n(Jan 2027)',
             'Germany', 'UK (NHS)', 'Canada', 'India\nCompounded']
prices = [1175, 300, 274, 280, 220, 280, 150]

colors_map = [RED, GOLD, TEAL, LIGHT_TEAL, LIGHT_TEAL, LIGHT_TEAL, TEAL]

fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
fig.patch.set_facecolor(NAVY)
ax.set_facecolor(NAVY)

y_pos = np.arange(len(countries))
bars = ax.barh(y_pos, prices, color=colors_map, edgecolor=NAVY, height=0.65)

# Add value labels on bars
for i, (bar, val, country) in enumerate(zip(bars, prices, countries)):
    w = bar.get_width()
    ax.text(w - 20, bar.get_y() + bar.get_height()/2,
            f'${val}', ha='right', va='center',
            fontsize=11, fontweight='bold', color=WHITE)

ax.set_yticks(y_pos)
ax.set_yticklabels(countries, fontsize=10)
ax.invert_yaxis()
ax.set_xlabel('Per 30-Day Supply ($)', fontsize=10, fontweight='bold')
ax.set_xlim(0, 1300)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_color(DARK_GRAY)
ax.spines['left'].set_color(DARK_GRAY)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:.0f}'))
ax.grid(axis='x', alpha=0.15, color=WHITE, linestyle='-', linewidth=0.5)

fig.suptitle('Why Americans Pay 5-8× More for the Same Molecule',
             fontsize=14, fontweight='bold', color=WHITE, y=0.97)
ax.set_title('GLP-1 Pricing: Semaglutide (Ozempic/Wegovy) by Country — 30-Day Supply',
             fontsize=10, color=TEAL, pad=10)

# Add comparison box
comparison_text = 'US to India: 7.8× markup\nUS to UK: 5.3× markup'
ax.text(0.98, 0.03, comparison_text, transform=ax.transAxes,
        fontsize=9, ha='right', va='bottom', color=GOLD, fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.5', facecolor=NAVY, edgecolor=GOLD, linewidth=1.5, alpha=0.95))

fig.text(0.12, 0.02, 'Sources: NHS Drug Tariff 2026; German AMNOG 2025; Peterson-KFF Health System Tracker; CMS BALANCE documentation',
         fontsize=5.5, color='#999', ha='left')
fig.text(0.88, 0.02, 'The American Healthcare Conundrum · Issue #7',
         fontsize=5.5, color='#999', ha='right')

plt.subplots_adjust(left=0.25, right=0.95, top=0.87, bottom=0.10)
fig.savefig(os.path.join(FIG_DIR, 'chart2_price_comparison.png'), dpi=150,
            facecolor=NAVY, edgecolor='none')
plt.close(fig)
print("  Saved chart2_price_comparison.png")

# ════════════════════════════════════════════════════════════════
# CHART 3: BALANCE 10-Year Cost Projection (Stacked Area)
# ════════════════════════════════════════════════════════════════
print("\n--- Chart 3: BALANCE Cost Projection ---")

years_balance = np.array([2027, 2028, 2029, 2030, 2031, 2032, 2033, 2034, 2035, 2036])
low_scenario = np.array([1.44, 3.46, 5.76, 8.07, 9.80, 10.95, 11.53, 11.53, 11.53, 11.53])
mid_scenario = np.array([2.09, 5.01, 8.35, 11.69, 14.20, 15.87, 16.70, 16.70, 16.70, 16.70])
high_scenario = np.array([2.84, 6.83, 11.38, 15.93, 19.34, 21.61, 22.75, 22.75, 22.75, 22.75])

fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
fig.patch.set_facecolor(NAVY)
ax.set_facecolor(NAVY)

# Stacked areas
ax.fill_between(years_balance, 0, low_scenario, color=TEAL, alpha=0.4, label='Low Scenario ($2,940/yr)')
ax.fill_between(years_balance, low_scenario, low_scenario + (mid_scenario - low_scenario),
                color=LIGHT_TEAL, alpha=0.5, label='Mid Scenario ($3,600/yr)')
ax.fill_between(years_balance, mid_scenario, high_scenario, color=GOLD, alpha=0.4, label='High Scenario ($4,200/yr)')

# Plot outlines for clarity
ax.plot(years_balance, low_scenario, color=TEAL, linewidth=2.0, linestyle=':')
ax.plot(years_balance, mid_scenario, color=LIGHT_TEAL, linewidth=2.5)
ax.plot(years_balance, high_scenario, color=GOLD, linewidth=2.0, linestyle=':')

# Annotations for key milestones
ax.text(2032, 17.2, 'Peak Enrollment\n2032: 4.6M\nbeneficiaries', ha='center', va='bottom',
        fontsize=8, fontweight='bold', color=GOLD,
        bbox=dict(boxstyle='round,pad=0.4', facecolor=NAVY, edgecolor=GOLD, linewidth=1.5, alpha=0.95))

ax.text(2033.5, 18, 'Steady State:\n$16.7B/year\n(mid scenario)', ha='center', va='center',
        fontsize=8, fontweight='bold', color=WHITE,
        bbox=dict(boxstyle='round,pad=0.4', facecolor=LIGHT_NAVY, edgecolor=TEAL, linewidth=1.5, alpha=0.95))

# 10-year totals
ax.text(2036.5, 11.53/2, '$86.2B\n10-year', ha='left', va='center',
        fontsize=7.5, color=TEAL, fontweight='bold')
ax.text(2036.5, (low_scenario[-1] + mid_scenario[-1])/2, '$124.8B\n10-year', ha='left', va='center',
        fontsize=7.5, color=LIGHT_TEAL, fontweight='bold')
ax.text(2036.5, (mid_scenario[-1] + high_scenario[-1])/2, '$170.1B\n10-year', ha='left', va='center',
        fontsize=7.5, color=GOLD, fontweight='bold')

# Formatting
ax.set_xlabel('Year', fontsize=10, fontweight='bold')
ax.set_ylabel('Annual Cost ($ Billions)', fontsize=10, fontweight='bold')
ax.set_xlim(2026.5, 2037.5)
ax.set_ylim(0, 26)
ax.set_xticks(range(2027, 2037))
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:.0f}B'))
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_color(DARK_GRAY)
ax.spines['left'].set_color(DARK_GRAY)
ax.grid(axis='y', alpha=0.15, color=WHITE, linestyle='-', linewidth=0.5)

fig.suptitle('Medicare BALANCE: 10-Year Budget Projection',
             fontsize=14, fontweight='bold', color=WHITE, y=0.97)
ax.set_title('Cost trajectories based on 13.2M eligible beneficiaries, enrollment ramp 5%-40%',
             fontsize=10, color=TEAL, pad=10)

ax.legend(loc='upper left', fontsize=8.5, framealpha=0.9, facecolor=LIGHT_NAVY, edgecolor=GOLD)

fig.text(0.12, 0.02, 'Source: CMS BALANCE documentation; Medicare obesity prevalence (CDC NHANES); author analysis',
         fontsize=5.5, color='#999', ha='left')
fig.text(0.88, 0.02, 'The American Healthcare Conundrum · Issue #7',
         fontsize=5.5, color='#999', ha='right')

plt.subplots_adjust(left=0.12, right=0.95, top=0.87, bottom=0.10)
fig.savefig(os.path.join(FIG_DIR, 'chart3_cost_projection.png'), dpi=150,
            facecolor=NAVY, edgecolor='none')
plt.close(fig)
print("  Saved chart3_cost_projection.png")

# ════════════════════════════════════════════════════════════════
# CHART 4: US vs International Pricing Structure
# ════════════════════════════════════════════════════════════════
print("\n--- Chart 4: Pricing Structure ---")

categories = ['Manufacturing\nCost', 'International\nPrice',
              'US Negotiated\n(IRA/BALANCE)', 'US Retail\nPrice']
values_base = [150, 280, 300, 1175]

fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
fig.patch.set_facecolor(NAVY)
ax.set_facecolor(NAVY)

x_pos = np.arange(len(categories))
bar_colors = [TEAL, LIGHT_TEAL, GOLD, RED]

bars = ax.bar(x_pos, values_base, color=bar_colors, edgecolor=NAVY, width=0.6)

# Add value labels above bars and markup annotations outside short bars
markups = [0, 87, 100, 683]
for i, (bar, val, markup) in enumerate(zip(bars, values_base, markups)):
    h = bar.get_height()
    # Value label above bar
    ax.text(bar.get_x() + bar.get_width()/2, h + 30, f'${val}',
            ha='center', va='bottom', fontsize=11, fontweight='bold', color=WHITE)
    if markup > 0:
        if h < 400:
            # Short bars: place markup annotation OUTSIDE, above the value label
            # Stagger vertically to avoid collision with the $value label
            label_y = h + 100
            ax.annotate(f'+{markup}% vs mfg cost',
                        xy=(bar.get_x() + bar.get_width()/2, h),
                        xytext=(bar.get_x() + bar.get_width()/2, label_y),
                        ha='center', va='bottom', fontsize=7.5, fontweight='bold', color=GOLD,
                        bbox=dict(boxstyle='round,pad=0.3', facecolor=NAVY, edgecolor=GOLD,
                                  linewidth=1, alpha=0.95),
                        arrowprops=dict(arrowstyle='-', color=GOLD, linewidth=0.8))
        else:
            # Tall bars (US Retail): label inside
            ax.text(bar.get_x() + bar.get_width()/2, h * 0.45, f'+{markup}%\nmarkup',
                    ha='center', va='center', fontsize=10, fontweight='bold', color=WHITE,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='#00000040', edgecolor='none'))

ax.set_ylabel('Price per 30-Day Supply ($)', fontsize=10, fontweight='bold')
ax.set_xticks(x_pos)
ax.set_xticklabels(categories, fontsize=10)
ax.set_ylim(0, 1500)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:.0f}'))
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_color(DARK_GRAY)
ax.spines['left'].set_color(DARK_GRAY)
ax.grid(axis='y', alpha=0.15, color=WHITE, linestyle='-', linewidth=0.5)

ax.axhline(y=150, color=TEAL, linestyle='--', linewidth=1.5, alpha=0.5, label='Manufacturing Cost')

fig.suptitle('From Factory to Patient: Where the GLP-1 Dollar Goes',
             fontsize=14, fontweight='bold', color=WHITE, y=0.97)
ax.set_title('Per-30-day-supply pricing for semaglutide (Ozempic/Wegovy)',
             fontsize=10, color=TEAL, pad=10)

ax.legend(loc='upper left', fontsize=9, framealpha=0.9, facecolor=LIGHT_NAVY, edgecolor=GOLD)

fig.text(0.12, 0.02, 'Sources: Compounded semaglutide cost estimates 2024-2025; Peterson-KFF; NHS Drug Tariff; CMS BALANCE',
         fontsize=5.5, color='#999', ha='left')
fig.text(0.88, 0.02, 'The American Healthcare Conundrum · Issue #7',
         fontsize=5.5, color='#999', ha='right')

plt.subplots_adjust(left=0.13, right=0.95, top=0.87, bottom=0.12)
fig.savefig(os.path.join(FIG_DIR, 'chart4_pricing_structure.png'), dpi=150,
            facecolor=NAVY, edgecolor='none')
plt.close(fig)
print("  Saved chart4_pricing_structure.png")

# ════════════════════════════════════════════════════════════════
# CHART 5: Savings Tracker (All 7 Issues)
# ════════════════════════════════════════════════════════════════
print("\n--- Chart 5: Savings Tracker ---")

issues = [
    ('Issue #1: OTC Overspend', 0.6),
    ('Issue #2: Drug Pricing', 25.0),
    ('Issue #3: Hospital Pricing', 73.0),
    ('Issue #4: PBM Reform', 30.0),
    ('Issue #5: Admin Waste', 200.0),
    ('Issue #6: Supply Waste', 28.0),
    ('Issue #7: GLP-1 Pricing', 40.0),
]

issue_names = [i[0] for i in issues]
issue_savings = [i[1] for i in issues]
cumulative = np.cumsum(issue_savings)
total_savings = cumulative[-1]

fig = plt.figure(figsize=(10, 6), dpi=100)
fig.patch.set_facecolor(NAVY)

# Create two subplots
gs = fig.add_gridspec(2, 1, height_ratios=[1, 1], hspace=0.4, top=0.86, bottom=0.12, left=0.12, right=0.95)
ax1 = fig.add_subplot(gs[0])
ax2 = fig.add_subplot(gs[1])

# ── Panel 1: Full $3T scale ──
ax1.set_facecolor(NAVY)
target = 3000
bar_width = 0.6
x_pos = np.array([0])

progress_pct = total_savings / target * 100
bar = ax1.barh(x_pos, total_savings, bar_width, color=TEAL, edgecolor=WHITE, linewidth=2, label='Identified Savings')
remaining = target - total_savings
ax1.barh(x_pos, remaining, bar_width, left=total_savings, color='#555555', alpha=0.3, edgecolor=WHITE, linewidth=2)

ax1.text(total_savings/2, x_pos[0], f'{total_savings:.1f}B identified ({progress_pct:.1f}% of 3T)',
         ha='center', va='center', fontsize=11, fontweight='bold', color=NAVY,
         bbox=dict(boxstyle='round,pad=0.4', facecolor=GOLD, alpha=0.9, edgecolor='none'))
ax1.text(total_savings + remaining/2, x_pos[0], f'{remaining:.1f}B gap',
         ha='center', va='center', fontsize=10, fontweight='bold', color=WHITE)

ax1.set_xlim(0, 3200)
ax1.set_ylim(-1, 1)
ax1.set_yticks([])
ax1.set_xlabel('Annual Savings ($ Billions)', fontsize=10, fontweight='bold', color=WHITE)
ax1.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:.0f}B'))
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.spines['left'].set_visible(False)
ax1.spines['bottom'].set_color(DARK_GRAY)
ax1.grid(axis='x', alpha=0.15, color=WHITE, linestyle='-', linewidth=0.5)
ax1.set_title('Full Scale: 396.6B of 3T US-Japan Healthcare Spending Gap',
              fontsize=10, color=WHITE, pad=10, fontweight='bold')

# ── Panel 2: $500B zoom window ──
ax2.set_facecolor(NAVY)
colors_by_issue = [TEAL] * len(issues)
colors_by_issue[-1] = RED

bar_height = 0.5
y_positions = np.arange(len(issues))
left_edge = np.zeros(len(issues))

for i, (name, savings, color) in enumerate(zip(issue_names, issue_savings, colors_by_issue)):
    ax2.barh(i, savings, bar_height, left=left_edge[i], color=color, edgecolor=NAVY,
             linewidth=1.5, alpha=0.85)
    if savings > 8:
        ax2.text(left_edge[i] + savings/2, i, f'{savings:.0f}B',
                ha='center', va='center', fontsize=8, fontweight='bold', color=WHITE)
    else:
        ax2.text(left_edge[i] + savings + 1, i, f'{savings:.0f}B',
                ha='left', va='center', fontsize=7.5, fontweight='bold', color=WHITE)
    left_edge[i] += savings

ax2.set_xlim(0, 520)
ax2.set_ylim(-0.5, len(issues) - 0.5)
ax2.set_yticks(y_positions)
ax2.set_yticklabels(issue_names, fontsize=9)
ax2.invert_yaxis()
ax2.set_xlabel('Annual Savings per Issue ($ Billions)', fontsize=10, fontweight='bold', color=WHITE)
ax2.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f'${x:.0f}B'))
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.spines['bottom'].set_color(DARK_GRAY)
ax2.spines['left'].set_color(DARK_GRAY)
ax2.grid(axis='x', alpha=0.15, color=WHITE, linestyle='-', linewidth=0.5)
ax2.set_title('Zoomed ($500B window): Per-Issue Breakdown',
              fontsize=10, color=WHITE, pad=10, fontweight='bold')

fig.suptitle('The American Healthcare Conundrum: Cumulative Savings Tracker',
             fontsize=14, fontweight='bold', color=WHITE, y=0.96)

fig.text(0.12, 0.02, 'Target: Close 3T US-Japan gap. Japan per-capita 5790 USD | US 14570 USD | Gap 8780 USD x 335M population',
         fontsize=5.5, color='#999', ha='left')
fig.text(0.88, 0.02, 'The American Healthcare Conundrum · Issues #1-7',
         fontsize=5.5, color='#999', ha='right')

fig.savefig(os.path.join(FIG_DIR, 'chart5_savings_tracker.png'), dpi=150,
            facecolor=NAVY, edgecolor='none')
plt.close(fig)
print("  Saved chart5_savings_tracker.png")

# ════════════════════════════════════════════════════════════════
# HERO IMAGE: Cover art for Substack
# ════════════════════════════════════════════════════════════════
print("\n--- Generating Hero Cover Image ---")

hero_width, hero_height = 1456, 1048

try:
    title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 120)
    subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 80)
    text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 60)
except:
    title_font = ImageFont.load_default()
    subtitle_font = ImageFont.load_default()
    text_font = ImageFont.load_default()

hero = Image.new('RGB', (hero_width, hero_height), color=(26, 31, 46))
draw = ImageDraw.Draw(hero)

teal_rgb = (14, 138, 114)
gold_rgb = (212, 175, 55)
white_rgb = (248, 248, 246)
red_rgb = (183, 24, 42)

# Series branding
brand_text = "THE AMERICAN HEALTHCARE CONUNDRUM"
draw.text((hero_width // 2, int(hero_height * 0.08)), brand_text,
          fill=red_rgb, font=title_font, anchor="mm")

# Issue number
issue_text = "Issue #7"
draw.text((hero_width // 2, int(hero_height * 0.18)), issue_text,
          fill=gold_rgb, font=subtitle_font, anchor="mm")

# Red divider line
divider_y = int(hero_height * 0.23)
draw.line([(int(hero_width * 0.35), divider_y), (int(hero_width * 0.65), divider_y)],
          fill=red_rgb, width=3)

# Main headline
headline = "$71.7B Market\n3-5× Overpriced"
draw.text((hero_width // 2, int(hero_height * 0.42)), headline,
          fill=white_rgb, font=subtitle_font, anchor="mm")

# Supporting comparison
comparison = "US: $1,175/month | International: $220-300/month"
draw.text((hero_width // 2, int(hero_height * 0.72)), comparison,
          fill=teal_rgb, font=text_font, anchor="mm")

# Stats bar
stats_text = "GLP-1 Gold Rush · BALANCE Impact · 10-Year Projection"
draw.text((hero_width // 2, int(hero_height * 0.88)), stats_text,
          fill=gold_rgb, font=text_font, anchor="mm")

hero.save(os.path.join(FIG_DIR, 'hero_cover.png'))
print(f"  Saved hero_cover.png ({hero_width}×{hero_height}px)")

print("\n✓ All charts generated successfully!")
print(f"\nChart Files:")
print(f"  1. chart1_market_growth.png")
print(f"  2. chart2_price_comparison.png")
print(f"  3. chart3_cost_projection.png")
print(f"  4. chart4_pricing_structure.png")
print(f"  5. chart5_savings_tracker.png")
print(f"  6. hero_cover.png")
