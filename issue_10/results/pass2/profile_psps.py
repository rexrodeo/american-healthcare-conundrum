"""Profile PSPS Schwartz subset: modifier and POS distribution per HCPCS.
Quick exploratory analysis to inform Pass 2 measure-by-measure resolution."""
import pandas as pd
from pathlib import Path

ROOT = Path("/sessions/eloquent-sweet-pasteur/mnt/healthcare/issue_10")
PSPS = ROOT / "raw" / "psps_cy2023" / "psps_2023_schwartz_subset.csv"
LONG = ROOT / "results" / "schwartz_hcpcs_long.csv"
OUT = ROOT / "results" / "pass2"
OUT.mkdir(parents=True, exist_ok=True)

print("Loading PSPS subset...")
df = pd.read_csv(PSPS, dtype=str, low_memory=False)
print(f"  rows: {len(df):,}, unique HCPCS: {df['HCPCS_CD'].nunique()}")

for col in ["PSPS_SUBMITTED_SERVICE_CNT", "PSPS_ALLOWED_CHARGE_AMT",
            "PSPS_NCH_PAYMENT_AMT", "PSPS_DENIED_SERVICES_CNT",
            "PSPS_DENIED_CHARGE_AMT"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

def classify_mod(m):
    if pd.isna(m) or m == "" or m is None:
        return "GLOBAL"
    return str(m).strip()

df["mod1"] = df["HCPCS_INITIAL_MODIFIER_CD"].apply(classify_mod)
df["mod2"] = df["HCPCS_SECOND_MODIFIER_CD"].apply(classify_mod)

POS_GROUP = {
    "11": "office", "12": "home", "13": "alf", "14": "group_home",
    "21": "inpatient", "22": "hopd_on_campus", "23": "er",
    "24": "asc", "31": "snf", "32": "nf", "33": "custodial",
    "41": "ambulance_land", "49": "indep_clinic",
    "50": "fqhc", "51": "inp_psy", "52": "psy_partial", "53": "cmhc",
    "61": "rehab_inp", "62": "rehab_outp", "65": "esrd",
    "71": "phl_state", "72": "rural_hc", "81": "indep_lab",
    "99": "other",
}
df["pos_group"] = df["PLACE_OF_SERVICE_CD"].map(POS_GROUP).fillna("other")

print("\nAggregating per HCPCS...")
total_per_hcpcs = df.groupby("HCPCS_CD").agg(
    paid=("PSPS_NCH_PAYMENT_AMT", "sum"),
    allowed=("PSPS_ALLOWED_CHARGE_AMT", "sum"),
    services=("PSPS_SUBMITTED_SERVICE_CNT", "sum"),
).reset_index()
total_per_hcpcs.to_csv(OUT / "psps_total_per_hcpcs.csv", index=False)
print(f"  unique Schwartz HCPCS in PSPS: {len(total_per_hcpcs)}")

mod_dist = df.groupby(["HCPCS_CD", "mod1"]).agg(
    paid=("PSPS_NCH_PAYMENT_AMT", "sum"),
    services=("PSPS_SUBMITTED_SERVICE_CNT", "sum"),
).reset_index()
mod_dist = mod_dist.merge(
    total_per_hcpcs[["HCPCS_CD", "paid"]].rename(columns={"paid": "hcpcs_total_paid"}),
    on="HCPCS_CD", how="left"
)
mod_dist["paid_share"] = mod_dist["paid"] / mod_dist["hcpcs_total_paid"].replace(0, pd.NA)
mod_dist.to_csv(OUT / "psps_modifier_dist.csv", index=False)

pos_dist = df.groupby(["HCPCS_CD", "pos_group"]).agg(
    paid=("PSPS_NCH_PAYMENT_AMT", "sum"),
    services=("PSPS_SUBMITTED_SERVICE_CNT", "sum"),
).reset_index()
pos_dist = pos_dist.merge(
    total_per_hcpcs[["HCPCS_CD", "paid"]].rename(columns={"paid": "hcpcs_total_paid"}),
    on="HCPCS_CD", how="left"
)
pos_dist["paid_share"] = pos_dist["paid"] / pos_dist["hcpcs_total_paid"].replace(0, pd.NA)
pos_dist.to_csv(OUT / "psps_pos_dist.csv", index=False)

long = pd.read_csv(LONG, dtype=str)
long["hcpcs_cd"] = long["hcpcs_cd"].astype(str)

mod_dist["_join"] = mod_dist["HCPCS_CD"].astype(str)
joined = long.merge(mod_dist, left_on="hcpcs_cd", right_on="_join", how="left")
m_per_measure_mod = (
    joined.groupby(["measure_key", "measure_name", "mod1"])["paid"]
    .sum().reset_index()
)
m_per_measure_total = (
    joined.groupby(["measure_key", "measure_name"])["paid"]
    .sum().reset_index().rename(columns={"paid": "measure_total_paid"})
)
m_per_measure_mod = m_per_measure_mod.merge(
    m_per_measure_total, on=["measure_key", "measure_name"]
)
m_per_measure_mod["share"] = (
    m_per_measure_mod["paid"] / m_per_measure_mod["measure_total_paid"].replace(0, pd.NA)
)
m_per_measure_mod = m_per_measure_mod.sort_values(
    ["measure_key", "share"], ascending=[True, False]
)
m_per_measure_mod.to_csv(OUT / "measure_modifier_dist.csv", index=False)

pos_dist["_join"] = pos_dist["HCPCS_CD"].astype(str)
joined_pos = long.merge(pos_dist, left_on="hcpcs_cd", right_on="_join", how="left")
m_per_measure_pos = (
    joined_pos.groupby(["measure_key", "measure_name", "pos_group"])["paid"]
    .sum().reset_index()
)
m_per_measure_pos = m_per_measure_pos.merge(
    m_per_measure_total, on=["measure_key", "measure_name"]
)
m_per_measure_pos["share"] = (
    m_per_measure_pos["paid"] / m_per_measure_pos["measure_total_paid"].replace(0, pd.NA)
)
m_per_measure_pos = m_per_measure_pos.sort_values(
    ["measure_key", "share"], ascending=[True, False]
)
m_per_measure_pos.to_csv(OUT / "measure_pos_dist.csv", index=False)

print("\n=== TOP MODIFIERS PER MEASURE ===\n")
for measure in m_per_measure_mod["measure_key"].unique():
    sub = m_per_measure_mod[m_per_measure_mod["measure_key"] == measure].head(4)
    if len(sub) == 0 or sub["measure_total_paid"].iloc[0] == 0:
        continue
    name = sub["measure_name"].iloc[0]
    total = sub["measure_total_paid"].iloc[0]
    print(f"  {measure:10s} ({name[:35]}) total=${total/1e6:.2f}M")
    for _, r in sub.iterrows():
        print(f"      mod={r['mod1']:6s} share={r['share']:.1%}  paid=${r['paid']/1e6:.2f}M")

print("\n=== POS DISTRIBUTION (TOP 3) PER MEASURE ===\n")
for measure in m_per_measure_pos["measure_key"].unique():
    sub = m_per_measure_pos[m_per_measure_pos["measure_key"] == measure].head(3)
    if len(sub) == 0 or sub["measure_total_paid"].iloc[0] == 0:
        continue
    name = sub["measure_name"].iloc[0]
    print(f"  {measure:10s} ({name[:30]})")
    for _, r in sub.iterrows():
        print(f"      pos={r['pos_group']:18s} share={r['share']:.1%}")

print("\nProfiling complete.")
