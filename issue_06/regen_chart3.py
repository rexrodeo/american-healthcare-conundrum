import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Colors
NAVY = '#1A1F2E'
TEAL = '#0E8A72'
RED = '#B7182A'
GOLD = '#D4AF37'
WHITE = '#F8F8F6'

# Data
issues = ['#1\nOTC', '#2\nDrug\nPricing', '#3\nHospital\nPricing', '#4\nPBMs', '#5\nAdmin\nWaste', '#6\nSupply\nWaste']
savings = [0.6, 25.0, 73.0, 30.0, 200.0, 28.0]
colors = [TEAL, TEAL, RED, GOLD, RED, TEAL]
cumulative = np.cumsum(savings)
total = 356.6
target = 3000

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), dpi=100,
                                 gridspec_kw={'height_ratios': [2, 1], 'hspace': 0.45})
fig.patch.set_facecolor(NAVY)

# Top panel: individual issue bars
bars = ax1.bar(range(len(issues)), savings, color=colors, edgecolor='white', linewidth=0.5, width=0.7)
ax1.set_facecolor(NAVY)
ax1.set_xticks(range(len(issues)))
ax1.set_xticklabels(issues, color=WHITE, fontsize=8, ha='center')
ax1.set_ylabel('Savings ($ Billions)', color=WHITE, fontsize=9)
ax1.tick_params(colors=WHITE, labelsize=8)
ax1.spines['bottom'].set_color(WHITE)
ax1.spines['left'].set_color(WHITE)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.set_title('Addressable Savings by Issue', color=WHITE, fontsize=11, pad=10)

# Labels on bars
for i, (bar, val) in enumerate(zip(bars, savings)):
    if val >= 10:
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height()/2,
                f'${val:.0f}B', ha='center', va='center', color='white', fontsize=10, fontweight='bold')
    else:
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3,
                f'${val:.1f}B', ha='center', va='bottom', color=WHITE, fontsize=8)

ax1.set_ylim(0, 230)

# Bottom panel: progress bar toward $3T
bar_height = 0.4
# Full target bar (background)
ax2.barh(0, target, height=bar_height, color='#2a2f3e', edgecolor=WHITE, linewidth=0.5)
# Filled portion
ax2.barh(0, total, height=bar_height, color=TEAL, edgecolor=WHITE, linewidth=0.5)

ax2.set_facecolor(NAVY)
ax2.set_xlim(0, target * 1.05)
ax2.set_yticks([])
ax2.set_xlabel('Cumulative Savings ($ Billions)', color=WHITE, fontsize=9)
ax2.tick_params(colors=WHITE, labelsize=8)
ax2.spines['bottom'].set_color(WHITE)
ax2.spines['left'].set_visible(False)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.set_title(f'Progress Toward $3 Trillion Target: ${total}B (11.9%)', color=WHITE, fontsize=11, pad=10)

# Annotation on progress bar
ax2.text(total + 30, 0, f'${total}B', va='center', ha='left', color=GOLD, fontsize=11, fontweight='bold')
ax2.text(target - 30, 0, '$3,000B\nTarget', va='center', ha='right', color=WHITE, fontsize=8, alpha=0.7)

fig.suptitle('The American Healthcare Conundrum: Savings Tracker',
             color=WHITE, fontsize=14, fontweight='bold', y=0.98)

fig.text(0.12, 0.01, 'Data: CMS NHE 2023, CMS Part D PUF, CMS HCRIS FY2023. All savings booked at conservative estimates.',
         color=WHITE, fontsize=5.5, alpha=0.6, ha='left')

plt.savefig('/sessions/blissful-optimistic-allen/mnt/healthcare/issue_06/figures/chart3_savings_tracker.png',
            dpi=150, facecolor=NAVY, bbox_inches='tight')
plt.close(fig)

# Also save as global tracker
plt.close('all')
fig2, (ax1b, ax2b) = plt.subplots(2, 1, figsize=(10, 6), dpi=100,
                                    gridspec_kw={'height_ratios': [2, 1], 'hspace': 0.45})
fig2.patch.set_facecolor(NAVY)

bars2 = ax1b.bar(range(len(issues)), savings, color=colors, edgecolor='white', linewidth=0.5, width=0.7)
ax1b.set_facecolor(NAVY)
ax1b.set_xticks(range(len(issues)))
ax1b.set_xticklabels(issues, color=WHITE, fontsize=8, ha='center')
ax1b.set_ylabel('Savings ($ Billions)', color=WHITE, fontsize=9)
ax1b.tick_params(colors=WHITE, labelsize=8)
ax1b.spines['bottom'].set_color(WHITE)
ax1b.spines['left'].set_color(WHITE)
ax1b.spines['top'].set_visible(False)
ax1b.spines['right'].set_visible(False)
ax1b.set_title('Addressable Savings by Issue', color=WHITE, fontsize=11, pad=10)
for i, (bar, val) in enumerate(zip(bars2, savings)):
    if val >= 10:
        ax1b.text(bar.get_x() + bar.get_width()/2, bar.get_height()/2,
                f'${val:.0f}B', ha='center', va='center', color='white', fontsize=10, fontweight='bold')
    else:
        ax1b.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3,
                f'${val:.1f}B', ha='center', va='bottom', color=WHITE, fontsize=8)
ax1b.set_ylim(0, 230)

ax2b.barh(0, target, height=bar_height, color='#2a2f3e', edgecolor=WHITE, linewidth=0.5)
ax2b.barh(0, total, height=bar_height, color=TEAL, edgecolor=WHITE, linewidth=0.5)
ax2b.set_facecolor(NAVY)
ax2b.set_xlim(0, target * 1.05)
ax2b.set_yticks([])
ax2b.set_xlabel('Cumulative Savings ($ Billions)', color=WHITE, fontsize=9)
ax2b.tick_params(colors=WHITE, labelsize=8)
ax2b.spines['bottom'].set_color(WHITE)
ax2b.spines['left'].set_visible(False)
ax2b.spines['top'].set_visible(False)
ax2b.spines['right'].set_visible(False)
ax2b.set_title(f'Progress Toward $3 Trillion Target: ${total}B (11.9%)', color=WHITE, fontsize=11, pad=10)
ax2b.text(total + 30, 0, f'${total}B', va='center', ha='left', color=GOLD, fontsize=11, fontweight='bold')
ax2b.text(target - 30, 0, '$3,000B\nTarget', va='center', ha='right', color=WHITE, fontsize=8, alpha=0.7)
fig2.suptitle('The American Healthcare Conundrum: Savings Tracker',
             color=WHITE, fontsize=14, fontweight='bold', y=0.98)
fig2.text(0.12, 0.01, 'Data: CMS NHE 2023, CMS Part D PUF, CMS HCRIS FY2023. All savings booked at conservative estimates.',
         color=WHITE, fontsize=5.5, alpha=0.6, ha='left')
plt.savefig('/sessions/blissful-optimistic-allen/mnt/healthcare/figures/savings_tracker.png',
            dpi=150, facecolor=NAVY, bbox_inches='tight')
plt.close(fig2)

print("Chart 3 and global savings tracker regenerated.")
