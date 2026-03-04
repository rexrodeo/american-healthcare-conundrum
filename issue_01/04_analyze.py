"""
Medicare OTC Drug Analysis
Step 4: Core analysis queries

Answers the key questions:
  1. How much does Medicare Part D spend on drugs with OTC equivalents?
  2. What would it cost if beneficiaries used the OTC version instead?
  3. What's the potential annual savings?
  4. Which drugs drive the most waste?
  5. Are beneficiaries paying MORE out-of-pocket than the OTC cash price?

Output: prints a rich report + saves results/summary.csv for the newsletter.
"""

import duckdb
import pandas as pd
from pathlib import Path

DB_PATH = "medicare_otc.duckdb"
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)


def run_analysis():
    print("\n🔍  Medicare OTC Drug Waste Analysis")
    print("=" * 60)

    con = duckdb.connect(DB_PATH, read_only=True)

    # ── 0. Sanity check ────────────────────────────────────────────────────────
    years = con.execute("SELECT DISTINCT year FROM part_d ORDER BY year").fetchdf()
    print(f"\nYears in database: {', '.join(str(y) for y in years['year'].tolist())}")

    # ── 1. Total Part D spending (universe) ────────────────────────────────────
    # CMS column: Tot_Spndng = total gross drug cost
    # Adjust column name below if your CSV has different naming.
    total_q = """
        SELECT
            year,
            COUNT(*)                           AS drug_count,
            SUM("Tot_Spndng")                  AS total_spending_usd,
            SUM("Tot_Clms")                    AS total_claims
        FROM part_d
        GROUP BY year
        ORDER BY year
    """
    try:
        total_df = con.execute(total_q).fetchdf()
        print("\n── Part D Universe ──────────────────────────────────────")
        print(total_df.to_string(index=False))
    except Exception as e:
        print(f"  ⚠️  Column name mismatch — check schema: {e}")
        print("  Run: duckdb medicare_otc.duckdb 'DESCRIBE part_d'")

    # ── 2. OTC-matched drugs spending ─────────────────────────────────────────
    otc_q = """
        SELECT
            year,
            otc_match_key,
            otc_brand,
            otc_unit_price,
            SUM("Tot_Spndng")                              AS medicare_spending_usd,
            SUM("Tot_Clms")                                AS total_claims,
            AVG("Avg_Spnd_Per_Dsg_Unt_Wghtd")             AS avg_medicare_unit_cost,
            otc_unit_price                                  AS avg_otc_unit_cost,
            -- Estimated OTC cost = OTC price × total doses
            -- (Using claims × avg days supply × avg daily doses as a proxy for units)
            SUM("Tot_Clms") * 30 * otc_unit_price          AS estimated_otc_spend,
            SUM("Tot_Spndng") - SUM("Tot_Clms") * 30 * otc_unit_price AS potential_savings_usd
        FROM otc_matched_spending
        GROUP BY year, otc_match_key, otc_brand, otc_unit_price
        ORDER BY year, medicare_spending_usd DESC
    """
    try:
        otc_df = con.execute(otc_q).fetchdf()
        print("\n── OTC-Matched Drug Spending ─────────────────────────────")
        display_cols = ["year", "otc_match_key", "medicare_spending_usd",
                        "total_claims", "avg_medicare_unit_cost", "avg_otc_unit_cost",
                        "potential_savings_usd"]
        print(otc_df[display_cols].to_string(index=False))

        otc_df.to_csv(RESULTS_DIR / "otc_matched_drugs.csv", index=False)
        print(f"\n  Saved: {RESULTS_DIR / 'otc_matched_drugs.csv'}")
    except Exception as e:
        print(f"  ⚠️  OTC analysis error: {e}")

    # ── 3. Aggregate savings summary ─────────────────────────────────────────
    agg_q = """
        SELECT
            year,
            COUNT(DISTINCT otc_match_key)                  AS drugs_identified,
            SUM("Tot_Clms")                                AS total_claims_otc_drugs,
            SUM("Tot_Spndng")                              AS medicare_spending_otc_drugs,
            SUM("Tot_Clms") * 30 * otc_unit_price          AS estimated_otc_cost,
            SUM("Tot_Spndng") -
              SUM("Tot_Clms") * 30 * otc_unit_price        AS potential_annual_savings,
            (SUM("Tot_Spndng") -
              SUM("Tot_Clms") * 30 * otc_unit_price)
              / SUM("Tot_Spndng") * 100                    AS pct_savings
        FROM otc_matched_spending
        GROUP BY year
        ORDER BY year
    """
    try:
        agg_df = con.execute(agg_q).fetchdf()
        print("\n── Aggregate Savings Potential ───────────────────────────")
        for _, row in agg_df.iterrows():
            print(f"\n  Year: {int(row['year'])}")
            print(f"  Drugs identified:          {int(row['drugs_identified'])}")
            print(f"  Total claims (OTC drugs):  {row['total_claims_otc_drugs']:,.0f}")
            print(f"  Medicare spent:            ${row['medicare_spending_otc_drugs']:,.0f}")
            print(f"  If OTC prices applied:     ${row['estimated_otc_cost']:,.0f}")
            print(f"  Potential savings:         ${row['potential_annual_savings']:,.0f}")
            print(f"  Savings %:                 {row['pct_savings']:.1f}%")

        agg_df.to_csv(RESULTS_DIR / "savings_summary.csv", index=False)
    except Exception as e:
        print(f"  ⚠️  Aggregate query error: {e}")

    # ── 4. Beneficiary overpayment check ──────────────────────────────────────
    # Are bene out-of-pocket costs > OTC retail price?
    bene_q = """
        SELECT
            year,
            otc_match_key,
            AVG("Avg_Bene_Oop_Cost")   AS avg_bene_oop,
            otc_unit_price * 30         AS est_monthly_otc_cost,
            AVG("Avg_Bene_Oop_Cost") - (otc_unit_price * 30)  AS bene_overpayment
        FROM otc_matched_spending
        GROUP BY year, otc_match_key, otc_unit_price
        HAVING avg_bene_oop > (otc_unit_price * 30)
        ORDER BY bene_overpayment DESC
    """
    try:
        bene_df = con.execute(bene_q).fetchdf()
        if not bene_df.empty:
            print("\n── Beneficiaries Overpaying vs OTC Cash Price ────────────")
            print(bene_df.to_string(index=False))
            bene_df.to_csv(RESULTS_DIR / "bene_overpayment.csv", index=False)
        else:
            print("\n  No beneficiary overpayment cases found (or column missing).")
    except Exception as e:
        print(f"  ⚠️  Beneficiary query: {e}")

    con.close()
    print(f"\n✅  Analysis complete. Results saved to: {RESULTS_DIR.resolve()}/")
    print("    Next step: python 05_visualize.py")


if __name__ == "__main__":
    run_analysis()
