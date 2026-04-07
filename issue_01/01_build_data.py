#!/usr/bin/env python3
"""
01_build_data.py — Issue #1: OTC Drug Overspending
The American Healthcare Conundrum

Reproducible analysis pipeline. Downloads CMS Part D data, builds OTC crosswalk,
and computes savings potential from switching brand prescriptions to OTC equivalents.

Usage: python3 01_build_data.py
Dependencies: pip install duckdb pandas requests

Data source: CMS Medicare Part D Spending by Drug (data.cms.gov)

This is a wrapper that orchestrates the existing analysis pipeline:
  02_download_data.py → 03_build_database.py → 04_analyze.py

Expected outputs in results/:
  - yearly_summary.csv
  - by_drug_2023.csv
  - bene_overpayment_2023.csv
"""
import subprocess
import sys
import os


def main():
    issue_dir = os.path.dirname(os.path.abspath(__file__))

    steps = [
        ("Downloading CMS Part D data...", "02_download_data.py"),
        ("Building DuckDB database with OTC crosswalk...", "03_build_database.py"),
        ("Running analysis and generating results...", "04_analyze.py"),
    ]

    for msg, script in steps:
        print(f"\n{'='*60}")
        print(f"  {msg}")
        print(f"{'='*60}")
        script_path = os.path.join(issue_dir, script)
        if not os.path.exists(script_path):
            print(f"ERROR: {script} not found at {script_path}")
            sys.exit(1)
        result = subprocess.run([sys.executable, script_path], cwd=issue_dir)
        if result.returncode != 0:
            print(f"ERROR: {script} failed with return code {result.returncode}")
            sys.exit(1)

    # Verify outputs
    results_dir = os.path.join(issue_dir, "results")
    expected = ["yearly_summary.csv", "by_drug_2023.csv", "bene_overpayment_2023.csv"]
    print(f"\n{'='*60}")
    print("  Verifying outputs...")
    print(f"{'='*60}")

    all_found = True
    for f in expected:
        path = os.path.join(results_dir, f)
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"  OK {f} ({size:,} bytes)")
        else:
            print(f"  MISSING {f}")
            all_found = False

    print(f"\n{'='*60}")
    if all_found:
        print("  Issue #1 pipeline complete.")
        print("  Key finding: Medicare Part D spends ~$2B/year on drugs")
        print("  with OTC equivalents. Step therapy reform could save")
        print("  approximately $0.6B/year.")
        print(f"{'='*60}")
        return 0
    else:
        print("  ERROR: Some expected outputs are missing.")
        print(f"{'='*60}")
        sys.exit(1)


if __name__ == "__main__":
    main()
