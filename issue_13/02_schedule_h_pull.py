"""
02_schedule_h_pull.py — Issue #13 Stage 2 v2

Pulls per-filer IRS Form 990 Schedule H Part I data for the universe of
~9,000 hospital filers identified in the ProPublica NTEE=E index. The XML
is streamed from the IRS bulk XML batches (~30 ZIP files totaling ~7GB,
hosted at apps.irs.gov/pub/epostcard/990/xml/{YEAR}/{BATCH}.zip). Each
batch is downloaded, scanned for target object_ids, the matching XMLs are
extracted to per-EIN cache, the batch ZIP is deleted to free disk, and
Schedule H Part I lines 7a-7k are parsed into a per-filer panel.

This is the v2 fix for Stage 2 v1's broken broad-subset path
(charity x 2.5 uniform sector uplift). The new path replaces the uniform
uplift with per-filer Schedule H Part I line items.

OUTPUT:
    issue_13/data_cache/schedule_h_xml/{ein}_{tax_period_end}.xml
    issue_13/results/per_filer_schedule_h.csv

USAGE:
    python3 02_schedule_h_pull.py [--dry-run] [--max-batches=N]
"""

import csv
import io
import json
import os
import re
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from collections import defaultdict
from pathlib import Path


# =============================================================================
# PATHS
# =============================================================================
HERE = Path(__file__).resolve().parent
DATA_CACHE = HERE / "data_cache"
RESULTS = HERE / "results"
XML_CACHE = DATA_CACHE / "schedule_h_xml"
XML_CACHE.mkdir(parents=True, exist_ok=True)
RESULTS.mkdir(exist_ok=True)

# Scratch dir for temporary batch ZIP downloads (must be unlink-able;
# Cowork mounts disallow rm on /sessions/.../mnt/, so we use /sessions root)
SCRATCH = Path("/sessions/peaceful-determined-lovelace/_scratch_issue_13") \
    if Path("/sessions/peaceful-determined-lovelace").exists() else Path("/tmp/_scratch_issue_13")
SCRATCH.mkdir(parents=True, exist_ok=True)

INDEX_FILES = [
    (2024, DATA_CACHE / "index_2024.csv"),
    (2025, DATA_CACHE / "index_2025.csv"),
    (2026, DATA_CACHE / "index_2026.csv"),
]
PROPUBLICA_PATH = DATA_CACHE / "propublica_hospitals.json"
OUT_CSV = RESULTS / "per_filer_schedule_h.csv"
COVERAGE_LOG = RESULTS / "schedule_h_pull_coverage.json"


# =============================================================================
# SCHEDULE H PARSER
# =============================================================================
NS = {"ef": "http://www.irs.gov/efile"}

# Schedule H Part I Line 7 components
# Tag names from IRS 2023v5.0 / 2023v5.1 schema
GROUPS = [
    ("line_7a", "FinancialAssistanceAtCostTyp"),     # Financial assistance (charity care) at cost
    ("line_7b", "UnreimbursedMedicaidGrp"),          # Medicaid shortfall
    ("line_7c", "UnreimbursedCostsGrp"),             # Other means-tested govt programs (CHIP, etc.)
    ("line_7d", "TotalFinancialAssistanceTyp"),      # Subtotal financial assistance + means-tested
    ("line_7e", "CommunityHealthServicesGrp"),       # Community health improvement & operations
    ("line_7f", "HealthProfessionsEducationGrp"),    # Health professions education
    ("line_7g", "SubsidizedHealthServicesGrp"),      # Subsidized health services
    ("line_7h", "ResearchGrp"),                      # Research
    ("line_7i", "CashAndInKindContributionsGrp"),    # Cash and in-kind contributions
    ("line_7j", "TotalOtherBenefitsGrp"),            # Subtotal "other benefits"
    ("line_7k", "TotalCommunityBenefitsGrp"),        # Total community benefits (7d + 7j)
]


def _get_int(elem, tag):
    if elem is None:
        return 0
    e = elem.find(f"ef:{tag}", NS)
    if e is None or e.text is None:
        return 0
    try:
        return int(e.text)
    except Exception:
        return 0


def _get_float(elem, tag):
    if elem is None:
        return 0.0
    e = elem.find(f"ef:{tag}", NS)
    if e is None or e.text is None:
        return 0.0
    try:
        return float(e.text)
    except Exception:
        return 0.0


def parse_schedule_h_from_xml(xml_bytes):
    """Parse Schedule H Part I from raw XML bytes. Returns None if no Schedule H."""
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return None

    # EIN
    ein_e = root.find(".//ef:Filer/ef:EIN", NS)
    ein = ein_e.text if ein_e is not None else None

    # Filer name
    name_e = root.find(".//ef:Filer/ef:BusinessName/ef:BusinessNameLine1Txt", NS)
    filer_name = name_e.text if name_e is not None else ""

    # State (from filer address)
    state_e = root.find(".//ef:Filer/ef:USAddress/ef:StateAbbreviationCd", NS)
    filer_state = state_e.text if state_e is not None else ""

    # Tax period
    tpe_e = root.find(".//ef:ReturnHeader/ef:TaxPeriodEndDt", NS)
    tax_period_end = tpe_e.text if tpe_e is not None else None

    # Schedule H presence
    sch_h = root.find(".//ef:IRS990ScheduleH", NS)
    if sch_h is None:
        return None  # No Schedule H = not a hospital filer

    # Get Form 990 expenses for cross-check
    form_990 = root.find(".//ef:IRS990", NS)
    total_func_expns = _get_int(form_990, "TotalFunctionalExpensesGrp/TotalAmt") if form_990 is not None else 0
    # Alt path direct
    if total_func_expns == 0 and form_990 is not None:
        e = form_990.find("ef:CYTotalExpensesAmt", NS)
        if e is not None and e.text:
            try:
                total_func_expns = int(e.text)
            except Exception:
                pass

    out = {
        "ein": ein,
        "filer_name": filer_name,
        "filer_state": filer_state,
        "tax_period_end": tax_period_end,
        "form990_total_expenses": total_func_expns,
        "schedule_h_present": True,
        "hospital_facilities_cnt": _get_int(sch_h, "HospitalFacilitiesCnt"),
        "bad_debt_expense_amt": _get_int(sch_h, "BadDebtExpenseAmt"),
        "bad_debt_attributable_amt": _get_int(sch_h, "BadDebtExpenseAttributableAmt"),
        "medicare_revenue_amt": _get_int(sch_h, "ReimbursedByMedicareAmt"),
        "medicare_cost_amt": _get_int(sch_h, "CostOfCareReimbursedByMedcrAmt"),
        "medicare_surplus_shortfall_amt": _get_int(sch_h, "MedicareSurplusOrShortfallAmt"),
    }

    # Line 7 components (gross, offsetting revenue, NET, % of expense)
    for label, tag in GROUPS:
        grp = sch_h.find(f"ef:{tag}", NS)
        out[f"{label}_gross_expense"] = _get_int(grp, "TotalCommunityBenefitExpnsAmt")
        out[f"{label}_offsetting_revenue"] = _get_int(grp, "DirectOffsettingRevenueAmt")
        out[f"{label}_net_benefit"] = _get_int(grp, "NetCommunityBenefitExpnsAmt")
        out[f"{label}_pct_expense"] = _get_float(grp, "TotalExpensePct")

    # Conservative Bai/Anderson subset = 7a + 7b + 7c + 7e + 7g + 7i (NET)
    out["bai_conservative_subset_net"] = (
        out["line_7a_net_benefit"]
        + out["line_7b_net_benefit"]
        + out["line_7c_net_benefit"]
        + out["line_7e_net_benefit"]
        + out["line_7g_net_benefit"]
        + out["line_7i_net_benefit"]
    )
    out["full_schedule_h_total_net"] = out["line_7k_net_benefit"]

    return out


# =============================================================================
# BATCH DOWNLOAD / STREAM
# =============================================================================
def http_get(url, timeout=180):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (AHC research; vonrexroad@gmail.com)"})
    return urllib.request.urlopen(req, timeout=timeout)


def stream_batch(year, batch_id, target_object_ids, parsed_records, fallback_target_eins=None):
    """Download a single IRS XML batch and extract matching filings. Stream zip
    to disk first (memory-bounded), open as zipfile, extract matched XMLs only.
    Parse Schedule H Part I and append to parsed_records dict keyed by object_id.
    """
    # IRS canonical URLs are uppercase batch IDs
    bid_uc = batch_id.upper()
    url = f"https://apps.irs.gov/pub/epostcard/990/xml/{year}/{bid_uc}.zip"
    target_set = set(target_object_ids)

    # Stream to a temp file in scratch (must be in an unlink-able location)
    tmp_zip = SCRATCH / f"_batch_{year}_{bid_uc}.zip"

    t0 = time.time()
    try:
        with http_get(url, timeout=600) as r:
            content_length = int(r.headers.get("Content-Length", 0))
            with open(tmp_zip, "wb") as out_f:
                # Stream in 8MB chunks
                while True:
                    chunk = r.read(8 * 1024 * 1024)
                    if not chunk:
                        break
                    out_f.write(chunk)
    except urllib.error.HTTPError as e:
        alt_url = f"https://apps.irs.gov/pub/epostcard/990/xml/{year}/{batch_id}.zip"
        if alt_url != url:
            try:
                with http_get(alt_url, timeout=600) as r:
                    with open(tmp_zip, "wb") as out_f:
                        while True:
                            chunk = r.read(8 * 1024 * 1024)
                            if not chunk:
                                break
                            out_f.write(chunk)
            except Exception as e2:
                print(f"    [FAIL] HTTP error for {url} and {alt_url}: {e} / {e2}")
                if tmp_zip.exists():
                    tmp_zip.unlink()
                return 0, 0
        else:
            print(f"    [FAIL] HTTP {e.code} {url}")
            if tmp_zip.exists():
                tmp_zip.unlink()
            return 0, 0
    except Exception as e:
        print(f"    [FAIL] {url}: {e}")
        if tmp_zip.exists():
            tmp_zip.unlink()
        return 0, 0

    dl_secs = time.time() - t0
    zip_size = tmp_zip.stat().st_size
    n_matched = 0
    n_with_h = 0

    # Detect compression method to decide between Python zipfile and external unzip
    needs_unzip_fallback = False
    target_filenames = {}  # obj_id -> filename within zip
    try:
        with zipfile.ZipFile(tmp_zip) as z:
            for info in z.infolist():
                name = info.filename
                if not name.endswith("_public.xml"):
                    continue
                m = re.search(r"(\d{17,18})_public\.xml$", name)
                if not m:
                    continue
                obj_id = m.group(1)
                if obj_id not in target_set:
                    continue
                target_filenames[obj_id] = name
                # compress_type 9 = deflate64 (not supported by Python zipfile pre-3.11.4)
                if info.compress_type not in (0, 8):
                    needs_unzip_fallback = True
    except zipfile.BadZipFile:
        print(f"    [FAIL] bad zip for {url} (size {zip_size/1e6:.0f}MB)")
        if tmp_zip.exists():
            tmp_zip.unlink()
        return 0, 0

    try:
        if needs_unzip_fallback:
            # Bulk extract with unzip — single subprocess call with all matched filenames
            import subprocess
            # Pass all target filenames as args. unzip handles many files in one invocation.
            if target_filenames:
                # Use -j (junk paths) so files extract flat, output to a tempdir
                # Then read each file.
                extract_dir = tmp_zip.parent / f"_xz_{tmp_zip.stem}"
                extract_dir.mkdir(exist_ok=True)
                # Build the list of filenames to extract
                filenames_to_extract = list(target_filenames.values())
                # unzip accepts multiple filenames after the zip arg
                # Use -o to overwrite, -d for output dir, -j to strip paths
                # Chunk if too many args
                CHUNK_SIZE = 200
                for i in range(0, len(filenames_to_extract), CHUNK_SIZE):
                    chunk = filenames_to_extract[i:i+CHUNK_SIZE]
                    cmd = ["unzip", "-o", "-q", "-j", "-d", str(extract_dir), str(tmp_zip)] + chunk
                    subprocess.run(cmd, capture_output=True, timeout=60)
                # Now process each extracted file
                for obj_id, name in target_filenames.items():
                    bare = name.split("/")[-1]
                    xml_path_extracted = extract_dir / bare
                    if not xml_path_extracted.exists():
                        parsed_records[obj_id] = {"object_id": obj_id, "schedule_h_present": False, "_extract_error": True}
                        continue
                    xml_bytes = xml_path_extracted.read_bytes()
                    n_matched += 1
                    record = parse_schedule_h_from_xml(xml_bytes)
                    if record is None:
                        parsed_records[obj_id] = {"object_id": obj_id, "schedule_h_present": False}
                        continue
                    record["object_id"] = obj_id
                    parsed_records[obj_id] = record
                    ein = record.get("ein") or "unknown"
                    tpe = (record.get("tax_period_end") or "unknown").replace("-", "")
                    xml_save_path = XML_CACHE / f"{ein}_{tpe}_{obj_id}.xml"
                    if not xml_save_path.exists():
                        xml_save_path.write_bytes(xml_bytes)
                    if record.get("schedule_h_present"):
                        n_with_h += 1
                # Clean up extract dir
                import shutil
                shutil.rmtree(extract_dir, ignore_errors=True)
        else:
            # Keep zipfile open once and iterate
            with zipfile.ZipFile(tmp_zip) as z:
                for obj_id, name in target_filenames.items():
                    try:
                        with z.open(name) as f:
                            xml_bytes = f.read()
                    except Exception:
                        parsed_records[obj_id] = {"object_id": obj_id, "schedule_h_present": False, "_extract_error": True}
                        continue
                    n_matched += 1
                    record = parse_schedule_h_from_xml(xml_bytes)
                    if record is None:
                        parsed_records[obj_id] = {"object_id": obj_id, "schedule_h_present": False}
                        continue
                    record["object_id"] = obj_id
                    parsed_records[obj_id] = record
                    ein = record.get("ein") or "unknown"
                    tpe = (record.get("tax_period_end") or "unknown").replace("-", "")
                    xml_save_path = XML_CACHE / f"{ein}_{tpe}_{obj_id}.xml"
                    if not xml_save_path.exists():
                        xml_save_path.write_bytes(xml_bytes)
                    if record.get("schedule_h_present"):
                        n_with_h += 1
        # Mark any targeted obj_ids NOT found in this zip as "not in batch"
        not_found = target_set - set(target_filenames.keys())
        for obj_id in not_found:
            if obj_id not in parsed_records:
                parsed_records[obj_id] = {"object_id": obj_id, "schedule_h_present": False, "_not_in_batch": True}
    finally:
        if tmp_zip.exists():
            tmp_zip.unlink()

    proc_secs = time.time() - t0 - dl_secs
    print(f"    [OK] {year}/{bid_uc}: {zip_size/1e6:.0f}MB in {dl_secs:.0f}s, extracted {n_matched} matches ({n_with_h} w/SchedH) in {proc_secs:.0f}s",
          flush=True)
    return n_matched, n_with_h


# =============================================================================
# MAIN
# =============================================================================
def load_propublica_eins():
    with open(PROPUBLICA_PATH) as f:
        pp = json.load(f)
    return {str(h["ein"]).lstrip("0") for h in pp}, pp


def select_filings(pp_eins, prefer_tax_periods=("2023",), fallback_tax_periods=("2024", "2022")):
    """Choose one filing per EIN: prefer 2023 tax period, fallback 2024 or 2022.
    Returns dict {ein: (tax_period, object_id, batch_id, submission_yr)}.
    """
    by_ein = defaultdict(list)
    for yr, path in INDEX_FILES:
        with open(path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                ein = row["EIN"].lstrip("0")
                if ein not in pp_eins:
                    continue
                if row["RETURN_TYPE"] != "990":  # exclude 990-EZ, 990-PF, 990-N
                    continue
                tp = row["TAX_PERIOD"]
                tp_year = tp[:4]
                if tp_year not in set(prefer_tax_periods + fallback_tax_periods):
                    continue
                by_ein[ein].append({
                    "tax_period": tp,
                    "tax_period_year": tp_year,
                    "object_id": row["OBJECT_ID"],
                    "batch_id": row["XML_BATCH_ID"],
                    "submission_yr": yr,
                    "sub_date": row["SUB_DATE"],
                })

    chosen = {}
    for ein, rows in by_ein.items():
        pref = [r for r in rows if r["tax_period_year"] in prefer_tax_periods]
        if pref:
            pref.sort(key=lambda r: (r["submission_yr"], r["sub_date"]), reverse=True)
            chosen[ein] = pref[0]
            continue
        # Fallback - prefer the most recent fallback period
        # For Issue #13, FY2024 returns are sparsely filed (most are not yet due);
        # FY2022 returns are stale. Prefer FY2024 if available (still sparse).
        for fpy in fallback_tax_periods:
            cand = [r for r in rows if r["tax_period_year"] == fpy]
            if cand:
                cand.sort(key=lambda r: (r["submission_yr"], r["sub_date"]), reverse=True)
                chosen[ein] = cand[0]
                break
    return chosen


def write_csv(records, out_path):
    if not records:
        print("No records to write.")
        return
    # Collect all keys
    all_keys = set()
    for r in records.values():
        all_keys.update(r.keys())
    # Stable order: anchor columns first
    anchor = [
        "object_id", "ein", "filer_name", "filer_state", "tax_period_end",
        "schedule_h_present", "hospital_facilities_cnt",
        "form990_total_expenses",
        "line_7a_net_benefit", "line_7b_net_benefit", "line_7c_net_benefit",
        "line_7d_net_benefit", "line_7e_net_benefit", "line_7f_net_benefit",
        "line_7g_net_benefit", "line_7h_net_benefit", "line_7i_net_benefit",
        "line_7j_net_benefit", "line_7k_net_benefit",
        "bai_conservative_subset_net",
        "full_schedule_h_total_net",
        "bad_debt_expense_amt",
        "medicare_surplus_shortfall_amt",
    ]
    rest = sorted(all_keys - set(anchor))
    header = anchor + rest

    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header, extrasaction="ignore")
        writer.writeheader()
        for r in records.values():
            writer.writerow(r)
    print(f"Wrote {len(records)} rows to {out_path}")


def main():
    print("=" * 75)
    print("Issue #13 Stage 2 v2 — Schedule H Per-Filer Pull")
    print("=" * 75)

    # Step 1: identify target filings
    pp_eins, pp = load_propublica_eins()
    print(f"ProPublica universe: {len(pp_eins)} EINs")

    chosen = select_filings(pp_eins)
    print(f"Chosen filings (one per EIN, prefer FY2023): {len(chosen)}")
    tp_dist = defaultdict(int)
    for ein, r in chosen.items():
        tp_dist[r["tax_period_year"]] += 1
    print(f"  by tax period year: {dict(tp_dist)}")

    # Group by batch
    batch_to_objs = defaultdict(set)
    obj_to_ein = {}
    for ein, r in chosen.items():
        batch_to_objs[(r["submission_yr"], r["batch_id"])].add(r["object_id"])
        obj_to_ein[r["object_id"]] = ein
    print(f"Unique XML batches needed: {len(batch_to_objs)}")
    print(f"Total filings to extract: {sum(len(v) for v in batch_to_objs.values())}")

    # Step 2: download batches and extract
    parsed_records = {}
    # Resume cache: load any prior pull (kept in scratch so we can refresh it)
    parsed_cache = SCRATCH / "parsed_records.json"
    if parsed_cache.exists():
        with open(parsed_cache) as f:
            parsed_records = json.load(f)
        print(f"Resumed: {len(parsed_records)} records already extracted")

    # Sort batches by descending size for parallel-friendly ordering
    sorted_batches = sorted(
        batch_to_objs.items(),
        key=lambda x: -len(x[1]),
    )

    for i, ((year, batch_id), obj_ids) in enumerate(sorted_batches):
        # Skip if all target ids in this batch are already parsed
        remaining = obj_ids - set(parsed_records.keys())
        if not remaining:
            print(f"  ({i+1}/{len(sorted_batches)}) {year}/{batch_id}: all {len(obj_ids)} already cached, skipping")
            continue
        print(f"  ({i+1}/{len(sorted_batches)}) {year}/{batch_id}: pulling {len(remaining)} of {len(obj_ids)}...")
        n_matched, n_with_h = stream_batch(year, batch_id, remaining, parsed_records)

        # Persist cache after each batch
        with open(parsed_cache, "w") as f:
            json.dump(parsed_records, f)

    print(f"\nExtraction complete: {len(parsed_records)} parsed records")
    n_with_h = sum(1 for r in parsed_records.values() if r.get("schedule_h_present"))
    print(f"  Filings with Schedule H attached: {n_with_h}")

    # Step 3: emit per-filer CSV
    # Filter to records with Schedule H
    final_records = {k: v for k, v in parsed_records.items() if v.get("schedule_h_present")}
    write_csv(final_records, OUT_CSV)

    # Coverage log
    coverage = {
        "propublica_universe": len(pp_eins),
        "filings_indexed": len(chosen),
        "filings_extracted": len(parsed_records),
        "filings_with_schedule_h": n_with_h,
        "tax_period_distribution": dict(tp_dist),
        "batches_processed": len(sorted_batches),
        "out_csv": str(OUT_CSV),
    }
    with open(COVERAGE_LOG, "w") as f:
        json.dump(coverage, f, indent=2)

    print(f"\nCoverage log: {COVERAGE_LOG}")
    print(f"Per-filer Schedule H CSV: {OUT_CSV}")
    print("=" * 75)
    return 0


if __name__ == "__main__":
    sys.exit(main())
