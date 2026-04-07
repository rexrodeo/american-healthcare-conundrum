#!/usr/bin/env python3
"""
01_build_data.py — Issue #2: The Same Pill, A Different Price
The American Healthcare Conundrum

Reproducible analysis pipeline. Builds international drug price reference tables
comparing Medicare Part D prices against NHS (UK), OECD averages, and IRA negotiated prices.

Usage: python3 01_build_data.py
Dependencies: pip install pandas

Data sources:
  - CMS Medicare Part D Spending by Drug, 2023 (data.cms.gov)
  - NHS Drug Tariff Part VIIIA, March 2026 (nhsbsa.nhs.uk)
  - RAND RRA788-3, Feb 2024
  - Peterson-KFF Health System Tracker, Dec 2024

This wraps 01_build_reference_data.py which contains the core analysis.

Expected outputs in results/:
  - kff_drug_comparison.csv
  - nhs_vs_medicare.csv
  - rand_country_ratios.csv
"""
import subprocess
import sys
import os


def main():
    issue_dir = os.path.dirname(os.path.abspath(__file__))

    print("=" * 60)
    print("  Building international drug price reference tables...")
    print("=" * 60)

    script_path = os.path.join(issue_dir, "01_build_reference_data.py")
    if not os.path.exists(script_path):
        print(f"ERROR: 01_build_reference_data.py not found at {script_path}")
        sys.exit(1)

    result = subprocess.run([sys.executable, script_path], cwd=issue_dir)
    if result.returncode != 0:
        print(f"ERROR: 01_build_reference_data.py failed with return code {result.returncode}")
        sys.exit(1)

    # Verify outputs
    results_dir = os.path.join(issue_dir, "results")
    expected = [
        "kff_drug_comparison.csv",
        "nhs_vs_medicare.csv",
        "rand_country_ratios.csv",
    ]
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
        print("  Issue #2 pipeline complete.")
        print("  Key finding: 9 top-spend Medicare brand drugs cost")
        print("  7-581x more than international peers.")
        print("  Savings: ~$25.0B/year (net of 49% rebate adjustment).")
        print(f"{'='*60}")
        return 0
    else:
        print("  ERROR: Some expected outputs are missing.")
        print(f"{'='*60}")
        sys.exit(1)


if __name__ == "__main__":
    main()
