import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

NAVY = '#1A1F2E'
TEAL = '#0E8A72'
RED = '#B7182A'
GOLD = '#D4AF37'
WHITE = '#F8F8F6'

# Hero: 1456x1048 at 150dpi -> figsize at 100dpi = 14.56x10.48 -> too big
# Use figsize=(9.7, 7.0) at 100dpi, save at 150dpi -> 1455x1050
fig, ax = plt.subplots(1, 1, figsize=(9.7, 7.0), dpi=100)
fig.patch.set_facecolor(NAVY)
ax.set_facecolor(NAVY)
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')

# Subtle grid
for x in range(0, 11):
    ax.axvline(x, color='#252a3a', linewidth=0.3, alpha=0.5)
for y in range(0, 11):
    ax.axhline(y, color='#252a3a', linewidth=0.3, alpha=0.5)

# Series branding (top center, inside safe zone)
ax.text(5, 8.8, 'THE AMERICAN HEALTHCARE CONUNDRUM', ha='center', va='center',
        color=RED, fontsize=13, fontweight='bold', fontfamily='sans-serif')
ax.text(5, 8.2, 'ISSUE #6', ha='center', va='center',
        color=GOLD, fontsize=18, fontweight='bold')

# Red divider line
ax.plot([2.5, 7.5], [7.8, 7.8], color=RED, linewidth=2)

# Main hook number
ax.text(5, 6.6, '$170.9 BILLION', ha='center', va='center',
        color=WHITE, fontsize=36, fontweight='bold')
ax.text(5, 5.8, 'Annual Hospital Supply Costs', ha='center', va='center',
        color=TEAL, fontsize=14)

# Supporting stats
ax.text(5, 4.8, '5,480 Hospitals  •  142 Million Discharges', ha='center', va='center',
        color=WHITE, fontsize=11, alpha=0.9)
ax.text(5, 4.2, 'Up to 7.7× Variance in Supply Costs Per Discharge', ha='center', va='center',
        color=GOLD, fontsize=12, fontweight='bold')

# Bottom stats bar
ax.text(5, 3.0, '$28 Billion in Addressable Savings Identified', ha='center', va='center',
        color=WHITE, fontsize=13, fontweight='bold',
        bbox=dict(boxstyle='round,pad=0.4', facecolor=TEAL, alpha=0.85, edgecolor='none'))

# Thin red line at bottom of safe zone
ax.plot([2.5, 7.5], [2.2, 2.2], color=RED, linewidth=1, alpha=0.5)

# Bottom subtitle
ax.text(5, 1.6, 'Original analysis: CMS HCRIS FY2023', ha='center', va='center',
        color=WHITE, fontsize=8, alpha=0.5)

plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
plt.savefig('/sessions/blissful-optimistic-allen/mnt/healthcare/issue_06/figures/hero_cover.png',
            dpi=150, facecolor=NAVY, bbox_inches='tight', pad_inches=0.1)
plt.close(fig)
print("Hero image regenerated.")
