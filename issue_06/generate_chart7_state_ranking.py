import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

# Brand colors from CLAUDE.md
NAVY = '#1A1F2E'
TEAL = '#0E8A72'
RED = '#B7182A'
GOLD = '#D4AF37'
WHITE = '#F8F8F6'

# Data: Top 10 states by addressable waste
states_data = [
    ('California', 5275, 381, 3.6),
    ('Texas', 2185, 395, 4.4),
    ('Florida', 2004, 245, 4.2),
    ('New York', 1715, 154, 3.0),
    ('North Carolina', 1468, 123, 3.2),
    ('Georgia', 1369, 152, 3.2),
    ('Washington', 1031, 101, 3.6),
    ('New Jersey', 1002, 92, 7.6),
    ('South Carolina', 989, 80, 6.2),
    ('Tennessee', 960, 128, 6.7),
]

# Reverse to have California at top when plotted
states_data = list(reversed(states_data))

states = [s[0] for s in states_data]
waste_millions = [s[1] for s in states_data]
hospital_counts = [s[2] for s in states_data]
ratios = [s[3] for s in states_data]

# Create figure with navy background
fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
fig.patch.set_facecolor(NAVY)
ax.set_facecolor(NAVY)

# Create horizontal bars
y_positions = np.arange(len(states))
bars = ax.barh(y_positions, waste_millions, color=TEAL, edgecolor=WHITE, linewidth=0.5)

# Set up axes
ax.set_yticks(y_positions)
ax.set_yticklabels(states, color=WHITE, fontsize=11, fontfamily='DejaVu Sans')
ax.set_xlabel('Addressable Waste ($M)', color=WHITE, fontsize=11, fontfamily='DejaVu Sans', labelpad=10)
ax.set_xlim(0, max(waste_millions) * 1.45)  # Extra space for right-side annotations

# Style the axes
ax.spines['bottom'].set_color(WHITE)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_color(WHITE)
ax.tick_params(colors=WHITE, labelsize=9)
ax.grid(axis='x', color=WHITE, alpha=0.15, linestyle='--', linewidth=0.5)

# Add value labels INSIDE each bar (left-aligned, centered vertically)
for i, (bar, waste, hospitals, ratio) in enumerate(zip(bars, waste_millions, hospital_counts, ratios)):
    # Format: $X.XB or $X.XXB
    if waste >= 1000:
        label_text = f'${waste/1000:.2f}B'
    else:
        label_text = f'${waste:.0f}M'
    
    # Place label inside bar, left-aligned with 8px padding from left edge
    ax.text(50, bar.get_y() + bar.get_height()/2, label_text,
            ha='left', va='center',
            fontsize=12, fontweight='bold', color=WHITE, fontfamily='DejaVu Sans')
    
    # Place annotations to the RIGHT of bar
    # Format: "N hospitals · P75/P25 = X.Xx"
    annotation = f'{hospitals} hosp. · {ratio:.1f}x'
    
    # Position to right of bar with offset
    x_pos = bar.get_width() + 150
    ax.text(x_pos, bar.get_y() + bar.get_height()/2, annotation,
            ha='left', va='center',
            fontsize=8, color=WHITE, fontfamily='DejaVu Sans', alpha=0.85)

# Title and subtitle
fig.suptitle('Where the Waste Is: Top 10 States by Addressable Supply Waste',
             fontsize=15, fontweight='bold', color=WHITE, fontfamily='DejaVu Sans',
             y=0.98, x=0.5, ha='center')

ax.text(0.5, 1.04, 'FY2023 HCRIS · Q4→P75 within bed-size peers · CMI-adjusted',
        transform=ax.transAxes, ha='center', va='top',
        fontsize=9.5, color=GOLD, fontfamily='DejaVu Sans', style='italic')

# Footnote at bottom left
footnote = ('Source: CMS HCRIS HOSP10-REPORTS FY2023. Addressable waste = excess spending by hospitals '
            'above 75th percentile, reduced to P75 within peer group.')
fig.text(0.12, 0.02, footnote,
         ha='left', va='bottom',
         fontsize=6, color=WHITE, fontfamily='DejaVu Sans', alpha=0.7, wrap=True)

# Tight layout with bottom space for footnote
plt.subplots_adjust(left=0.22, right=0.88, top=0.86, bottom=0.12)

# Ensure output directory exists
output_dir = Path('/sessions/friendly-lucid-thompson/mnt/healthcare/issue_06/figures')
output_dir.mkdir(parents=True, exist_ok=True)

# Save at 150dpi
output_path = output_dir / 'chart7_state_ranking.png'
plt.savefig(str(output_path), dpi=150, facecolor=NAVY, edgecolor='none', bbox_inches=None)
print(f'✓ Chart saved to {output_path}')
print(f'  Output dimensions: {int(10*150)}×{int(6*150)} pixels')

plt.close(fig)
print('✓ Figure closed and memory freed')
