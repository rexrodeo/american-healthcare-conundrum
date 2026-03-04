# The American Healthcare Conundrum

An investigative data journalism newsletter. Each issue identifies one fixable, quantifiable problem in the US healthcare system, builds the data case from primary sources, and recommends a specific policy fix. All code and methodology are open-source — anyone can check the work.

**Substack:** [andrewrexroad.substack.com](https://andrewrexroad.substack.com)

---

## Published Issues

### Issue #1 — Medicare's OTC Drug Problem (~$0.6B/year)

Medicare Part D pays prescription prices for drugs available cheaply over-the-counter. Step therapy reform — requiring OTC equivalents before prescription coverage activates — would redirect roughly **$0.6 billion per year** in unnecessary spending.

**Read the full analysis →** [`issue_01/newsletter_issue_01_FINAL.md`](issue_01/newsletter_issue_01_FINAL.md)

#### Running the pipeline

```bash
cd issue_01

# One-time environment setup
chmod +x 01_setup.sh && ./01_setup.sh
source .venv/bin/activate

# Download CMS Part D data (~200 MB)
python 02_download_data.py

# Build local DuckDB database
python 03_build_database.py

# Run analysis
python 04_analyze.py

# Generate charts
python 05_visualize.py
```

#### Data sources

| Source | URL |
|--------|-----|
| CMS Part D Spending by Drug (2023) | https://data.cms.gov/summary-statistics-on-use-and-payments/medicare-medicaid-spending-by-drug/medicare-part-d-spending-by-drug |
| JAMA — OTC Equivalents Study (Socal 2023) | https://pmc.ncbi.nlm.nih.gov/articles/PMC10722384/ |
| MedPAC Part D Report (2024) | https://www.medpac.gov/wp-content/uploads/2024/03/Mar24_Ch11_MedPAC_Report_To_Congress_SEC.pdf |

#### Key methodology notes
- OTC unit prices sourced from current retail at major US pharmacies (March 2026)
- 30-unit-per-claim approximation; see `issue_01/VALIDATION_REPORT.md` for full methodology
- Savings figures are conservative — do not account for PBM rebates or dispensing fees

---

## Up Next

Issue #2 is in the works. Subscribe on Substack to get it when it drops.

---

## About This Project

The US spends roughly **2.5× per capita** what comparable nations spend on healthcare — while achieving worse aggregate outcomes on life expectancy and infant mortality. This newsletter maps the gap, issue by issue, using publicly available data.

All analysis uses primary sources. Code is reproducible. Caveats are named explicitly. The math is the argument.
