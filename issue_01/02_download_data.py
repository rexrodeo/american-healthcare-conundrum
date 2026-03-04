"""
Medicare OTC Drug Analysis
Step 2: Download CMS Part D Spending by Drug data

Data source:
  CMS Medicare Part D Spending by Drug
  https://data.cms.gov/summary-statistics-on-use-and-payments/
          medicare-medicaid-spending-by-drug/medicare-part-d-spending-by-drug

The public API returns paginated JSON. This script pulls all available years
and saves them locally as Parquet files for fast DuckDB querying.

Mac Mini M4 note: 16 GB RAM is ample — the full dataset is ~200 MB uncompressed.
"""

import os
import json
import time
import requests
import pandas as pd
from pathlib import Path
from tqdm import tqdm

# ── Config ─────────────────────────────────────────────────────────────────────
DATA_DIR = Path("data/raw")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# CMS data.gov API — dataset ID for Part D Spending by Drug
DATASET_ID = "8c2b6c56-b256-4c85-a9b8-d39e8b55e18b"
BASE_URL = f"https://data.cms.gov/data-api/v1/dataset/{DATASET_ID}/data"

# Direct CSV download links per year (verified March 2026).
# NOTE: The 2023 file uses a new CMS naming convention (hash-based path).
#       If a URL returns 404, check data.cms.gov for the updated path.
CSV_URLS = {
    "2023": "https://data.cms.gov/sites/default/files/2025-05/56d95a8b-138c-4b60-84a5-613fbab7197f/DSD_PTD_RY25_P04_V10_DY23_BGM.csv",
    "2022": "https://data.cms.gov/sites/default/files/2024-01/Medicare_Part_D_Spending_by_Drug_2022.csv",
    "2021": "https://data.cms.gov/sites/default/files/2023-02/Medicare_Part_D_Spending_by_Drug_2021.csv",
    "2020": "https://data.cms.gov/sites/default/files/2022-03/Medicare_Part_D_Spending_by_Drug_2020.csv",
    "2019": "https://data.cms.gov/sites/default/files/2021-11/Medicare_Part_D_Spending_by_Drug_2019.csv",
    "2018": "https://data.cms.gov/sites/default/files/2021-11/Medicare_Part_D_Spending_by_Drug_2018.csv",
}

# ── Helpers ────────────────────────────────────────────────────────────────────

def download_csv_year(year: str, url: str) -> Path:
    """Download one year's CSV and save locally."""
    out_path = DATA_DIR / f"part_d_spending_{year}.csv"
    if out_path.exists():
        print(f"  [skip] {year} already downloaded.")
        return out_path

    print(f"  Downloading {year}...")
    r = requests.get(url, stream=True, timeout=120)
    r.raise_for_status()

    total = int(r.headers.get("content-length", 0))
    with open(out_path, "wb") as f, tqdm(
        total=total, unit="B", unit_scale=True, desc=f"  {year}"
    ) as bar:
        for chunk in r.iter_content(chunk_size=65536):
            f.write(chunk)
            bar.update(len(chunk))

    return out_path


def csv_to_parquet(csv_path: Path, year: str) -> Path:
    """Convert CSV to Parquet for fast DuckDB access."""
    parquet_path = DATA_DIR / f"part_d_spending_{year}.parquet"
    if parquet_path.exists():
        print(f"  [skip] {year} Parquet already exists.")
        return parquet_path

    print(f"  Converting {year} to Parquet...")
    df = pd.read_csv(csv_path, low_memory=False)
    df["year"] = int(year)
    df.to_parquet(parquet_path, index=False)
    print(f"  Saved: {parquet_path}  ({len(df):,} rows)")
    return parquet_path


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("\n📥  CMS Part D Spending by Drug — Data Download")
    print("=" * 55)

    for year, url in CSV_URLS.items():
        try:
            csv_path = download_csv_year(year, url)
            csv_to_parquet(csv_path, year)
        except Exception as e:
            print(f"  ⚠️  Error for {year}: {e}")
        time.sleep(0.5)  # be polite to CMS servers

    print("\n✅  All downloads complete. Files are in:", DATA_DIR.resolve())
    print("    Next step: python 03_build_database.py")


if __name__ == "__main__":
    main()
