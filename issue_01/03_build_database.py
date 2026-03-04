"""
Medicare OTC Drug Analysis
Step 3: Build DuckDB database + OTC crosswalk

Loads all downloaded Parquet files into a persistent DuckDB database,
then creates the OTC crosswalk table mapping generic drug names to their
OTC equivalents and typical OTC retail prices.

DuckDB on Apple Silicon (M4) is extremely fast — expect sub-second queries
even on the full multi-year dataset.
"""

import duckdb
from pathlib import Path

DB_PATH = "medicare_otc.duckdb"
DATA_DIR = Path("data/raw")

# ── OTC Crosswalk ──────────────────────────────────────────────────────────────
# Each entry: (generic_name_fragment, brand_rx_name, otc_brand, otc_price_per_unit_usd, notes)
# OTC prices sourced from GoodRx OTC tracker and JAMA 2023 (Socal et al.)
OTC_CROSSWALK = [
    # Generic name (lower, partial match)   RX brand       OTC brand       OTC $/unit  Notes
    ("omeprazole",           "Prilosec Rx", "Prilosec OTC", 0.33,  "20mg, 42ct ~$14 at Walmart"),
    ("esomeprazole",         "Nexium Rx",   "Nexium 24HR",  0.50,  "20mg, 42ct ~$21 at CVS"),
    ("lansoprazole",         "Prevacid Rx", "Prevacid 24HR",0.48,  "15mg, 42ct ~$20 at Walgreens"),
    ("famotidine",           "Pepcid Rx",   "Pepcid AC",    0.18,  "20mg, 100ct ~$18 at Costco"),
    ("loratadine",           "Claritin Rx", "Claritin OTC", 0.10,  "10mg, 365ct ~$37 at Costco"),
    ("cetirizine",           "Zyrtec Rx",   "Zyrtec OTC",   0.12,  "10mg, 365ct ~$44 at Costco"),
    ("fexofenadine",         "Allegra Rx",  "Allegra OTC",  0.22,  "180mg, 90ct ~$20 at Target"),
    ("fluticasone propionate","Flonase Rx", "Flonase",      0.25,  "120 sprays ~$30 at Walgreens"),
    ("triamcinolone acetonide","Nasacort Rx","Nasacort",    0.23,  "120 sprays ~$28 at CVS"),
    ("mometasone furoate",   "Nasonex Rx",  "Nasonex OTC",  0.35,  "120 sprays ~$42 at Walgreens"),
    ("azelastine",           "Astelin Rx",  "Astepro OTC",  0.30,  "200 sprays ~$60 at CVS"),
    ("ketotifen",            "Zaditor Rx",  "Zaditor OTC",  0.45,  "5ml drops"),
    ("minoxidil",            "Rogaine Rx",  "Rogaine OTC",  0.20,  "Topical solution"),
    ("naproxen sodium",      "Anaprox Rx",  "Aleve OTC",    0.07,  "220mg, 320ct ~$22 at Costco"),
    ("ibuprofen",            "Motrin Rx",   "Advil/Motrin", 0.03,  "200mg, 500ct ~$15 at Costco"),
    ("diphenhydramine",      "Benadryl Rx", "Benadryl OTC", 0.05,  "25mg, 365ct ~$18 at CVS"),
    ("dextromethorphan",     "Delsym Rx",   "Delsym OTC",   0.08,  "Cough syrup"),
    ("guaifenesin",          "Mucinex Rx",  "Mucinex OTC",  0.10,  "600mg, 200ct ~$20"),
    ("loperamide",           "Imodium Rx",  "Imodium OTC",  0.15,  "2mg, 72ct ~$11 at Target"),
]


def build_database():
    print(f"\n🦆  Building DuckDB database: {DB_PATH}")
    print("=" * 55)

    con = duckdb.connect(DB_PATH)

    # 1. Load all Parquet files into a unified part_d table
    parquet_files = sorted(DATA_DIR.glob("*.parquet"))
    if not parquet_files:
        print("  ❌  No Parquet files found. Run 02_download_data.py first.")
        return

    print(f"  Loading {len(parquet_files)} year(s) of data...")
    con.execute("""
        CREATE OR REPLACE TABLE part_d AS
        SELECT * FROM read_parquet('data/raw/part_d_spending_*.parquet')
    """)
    count = con.execute("SELECT COUNT(*) FROM part_d").fetchone()[0]
    print(f"  ✅ part_d table: {count:,} rows")

    # 2. Show actual column names so we can adapt queries
    cols = con.execute("DESCRIBE part_d").fetchdf()
    print("\n  Columns in dataset:")
    for _, row in cols.iterrows():
        print(f"    {row['column_name']:45s} {row['column_type']}")

    # 3. Create OTC crosswalk table
    print("\n  Building OTC crosswalk table...")
    con.execute("DROP TABLE IF EXISTS otc_crosswalk")
    con.execute("""
        CREATE TABLE otc_crosswalk (
            generic_name_fragment  VARCHAR,
            rx_brand_name          VARCHAR,
            otc_brand_name         VARCHAR,
            otc_price_per_unit_usd DOUBLE,
            notes                  VARCHAR
        )
    """)
    con.executemany(
        "INSERT INTO otc_crosswalk VALUES (?, ?, ?, ?, ?)",
        OTC_CROSSWALK
    )
    print(f"  ✅ otc_crosswalk table: {len(OTC_CROSSWALK)} drugs")

    # 4. Create analysis view joining Part D + crosswalk
    # NOTE: Column names may differ by CMS year. This handles the most common schema.
    #       Run `python 03_build_database.py` first to see your actual column names,
    #       then adjust the view below if needed.
    print("\n  Creating analysis view...")
    con.execute("""
        CREATE OR REPLACE VIEW otc_matched_spending AS
        SELECT
            p.*,
            c.generic_name_fragment  AS otc_match_key,
            c.rx_brand_name          AS rx_brand,
            c.otc_brand_name         AS otc_brand,
            c.otc_price_per_unit_usd AS otc_unit_price,
            c.notes                  AS otc_notes
        FROM part_d p
        JOIN otc_crosswalk c
          ON lower(p."Gnrc_Name") LIKE '%' || c.generic_name_fragment || '%'
    """)
    print("  ✅ otc_matched_spending view created")

    con.close()
    print(f"\n✅  Database ready: {DB_PATH}")
    print("    Next step: python 04_analyze.py")


if __name__ == "__main__":
    build_database()
