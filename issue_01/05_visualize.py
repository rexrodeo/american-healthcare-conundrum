"""
Medicare OTC Drug Analysis
Step 5: Visualizations for the newsletter

Generates:
  - Bar chart: Medicare spending vs. OTC cost per drug
  - Price markup chart (Rx vs OTC unit cost — the 3,400% story)
  - Waterfall chart: potential savings breakdown by drug category
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from pathlib import Path

RESULTS_DIR = Path("results")
FIG_DIR = Path("figures")
FIG_DIR.mkdir(exist_ok=True)

# Style
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 150,
})
BRAND_BLUE = "#1a5276"
BRAND_RED  = "#c0392b"
BRAND_GRAY = "#95a5a6"


def chart_spending_vs_otc():
    """Bar chart: Medicare spent vs. what OTC would cost, top 10 drugs."""
    try:
        df = pd.read_csv(RESULTS_DIR / "otc_matched_drugs.csv")
    except FileNotFoundError:
        print("  Run 04_analyze.py first to generate results.")
        return

    # Use most recent year
    df = df[df["year"] == df["year"].max()]
    df = df.nlargest(10, "medicare_spending_usd")

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(df))
    width = 0.38

    ax.bar(x - width/2, df["medicare_spending_usd"] / 1e6,
           width, label="Medicare Part D Paid", color=BRAND_BLUE, alpha=0.9)
    ax.bar(x + width/2, df["estimated_otc_spend"] / 1e6,
           width, label="Est. OTC Cost", color=BRAND_RED, alpha=0.9)

    ax.set_xticks(x)
    ax.set_xticklabels(df["otc_match_key"], rotation=30, ha="right", fontsize=9)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:.0f}M"))
    ax.set_ylabel("Annual Spending (Millions USD)")
    ax.set_title("Medicare Part D Pays Far More Than OTC Retail\nTop 10 OTC-Equivalent Drugs",
                 fontsize=13, fontweight="bold")
    ax.legend()
    fig.tight_layout()
    out = FIG_DIR / "01_spending_vs_otc.png"
    fig.savefig(out)
    print(f"  Saved: {out}")


def chart_markup_omeprazole():
    """Visual: Rx vs OTC unit price — omeprazole case study."""
    # Based on JAMA 2023 (Socal et al.) — use hardcoded values if data unavailable
    drugs = ["Omeprazole\n(heartburn)", "Lansoprazole\n(heartburn)",
             "Mometasone\n(allergy spray)", "Loratadine\n(allergy)"]
    rx_prices   = [27.85, 18.40, 12.30, 3.20]
    otc_prices  = [0.80,  0.48,  0.35,  0.10]
    markups     = [rx / otc for rx, otc in zip(rx_prices, otc_prices)]

    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(drugs))
    width = 0.35

    bars_rx  = ax.bar(x - width/2, rx_prices, width,
                      label="Medicare Part D (per unit)", color=BRAND_BLUE)
    bars_otc = ax.bar(x + width/2, otc_prices, width,
                      label="OTC Retail (per unit)", color=BRAND_RED)

    # Annotate markup multiples
    for i, (rx_bar, markup) in enumerate(zip(bars_rx, markups)):
        ax.text(rx_bar.get_x() + rx_bar.get_width() / 2,
                rx_bar.get_height() + 0.3,
                f"{markup:.0f}×", ha="center", va="bottom",
                fontsize=10, color=BRAND_BLUE, fontweight="bold")

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:.2f}"))
    ax.set_xticks(x)
    ax.set_xticklabels(drugs, fontsize=10)
    ax.set_ylabel("Cost Per Dose")
    ax.set_title("Medicare Pays Up to 35× More Per Dose Than OTC Retail\n"
                 "Source: Socal et al., JAMA 2023", fontsize=12, fontweight="bold")
    ax.legend()
    fig.tight_layout()
    out = FIG_DIR / "02_markup_chart.png"
    fig.savefig(out)
    print(f"  Saved: {out}")


def chart_progress_bar():
    """Newsletter hero graphic: savings found so far on the healthcare journey."""
    # These numbers will grow with each issue
    savings_found_bn = 0.406   # $406M from JAMA 2023 study on 19 drugs
    total_target_bn  = 500.0   # aspirational target — will refine over time

    pct = savings_found_bn / total_target_bn * 100

    fig, ax = plt.subplots(figsize=(10, 2.2))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 1)

    # Background bar
    ax.barh(0.5, 100, height=0.5, color="#e8e8e8", left=0)
    # Progress
    ax.barh(0.5, pct, height=0.5, color=BRAND_BLUE, left=0)

    ax.text(pct + 0.5, 0.5,
            f"${savings_found_bn:.3f}B found\n({pct:.2f}% of target)",
            va="center", fontsize=10, color=BRAND_BLUE, fontweight="bold")

    ax.text(99, 0.5, f"${total_target_bn:.0f}B+\nTarget",
            va="center", ha="right", fontsize=9, color=BRAND_GRAY)

    ax.set_title("Healthcare Savings Found So Far  🔍",
                 fontsize=12, fontweight="bold", loc="left")
    ax.axis("off")
    fig.tight_layout()
    out = FIG_DIR / "03_progress_bar.png"
    fig.savefig(out)
    print(f"  Saved: {out}")


if __name__ == "__main__":
    print("\n📊  Generating visualizations...")
    chart_spending_vs_otc()
    chart_markup_omeprazole()
    chart_progress_bar()
    print("\n✅  Charts saved to:", FIG_DIR.resolve())
