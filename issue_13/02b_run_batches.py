"""
02b_run_batches.py — Resume-aware single-call batch runner.

Processes one (or several) batches per invocation. Designed to be called
repeatedly under a 45-second per-call timeout. Caches incremental progress
in scratch/parsed_records.json. Sorts batches by ascending size so quick
wins land first; the giant 1GB+ batches process one-per-call.

Args:
    --max-secs N    Time budget per call (default 38s, conservative for 45s timeout)
    --max-batches N  Max number of batches per call (default unlimited)
    --finalize       Write final per_filer_schedule_h.csv from parsed cache
"""
import json
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

# Import from sibling module
sys.path.insert(0, str(Path(__file__).resolve().parent))
import importlib.util
spec = importlib.util.spec_from_file_location("schpull", str(Path(__file__).resolve().parent / "02_schedule_h_pull.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def main():
    args = sys.argv[1:]
    max_secs = 38.0
    max_batches = None
    finalize = False
    for a in args:
        if a.startswith("--max-secs="):
            max_secs = float(a.split("=")[1])
        elif a.startswith("--max-batches="):
            max_batches = int(a.split("=")[1])
        elif a == "--finalize":
            finalize = True

    # Load context
    pp_eins, pp = mod.load_propublica_eins()
    chosen = mod.select_filings(pp_eins)

    batch_to_objs = defaultdict(set)
    for ein, r in chosen.items():
        batch_to_objs[(r["submission_yr"], r["batch_id"])].add(r["object_id"])

    # Resume cache
    parsed_cache = mod.SCRATCH / "parsed_records.json"
    parsed_records = {}
    if parsed_cache.exists():
        with open(parsed_cache) as f:
            parsed_records = json.load(f)

    print(f"[runner] chosen filings: {len(chosen)}, batches: {len(batch_to_objs)}")
    print(f"[runner] already cached: {len(parsed_records)} records")
    n_with_h = sum(1 for r in parsed_records.values() if r.get("schedule_h_present"))
    print(f"[runner] cached with schedule_h: {n_with_h}")

    if finalize:
        # Write final CSV
        final_records = {k: v for k, v in parsed_records.items() if v.get("schedule_h_present")}
        mod.write_csv(final_records, mod.OUT_CSV)
        coverage = {
            "propublica_universe": len(pp_eins),
            "filings_indexed": len(chosen),
            "filings_extracted": len(parsed_records),
            "filings_with_schedule_h": n_with_h,
            "batches_total": len(batch_to_objs),
            "batches_complete": sum(
                1 for k, objs in batch_to_objs.items()
                if all(o in parsed_records for o in objs)
            ),
        }
        with open(mod.COVERAGE_LOG, "w") as f:
            json.dump(coverage, f, indent=2)
        print(f"[runner] FINALIZED: {coverage}")
        return 0

    # Pick batches to process: smallest-first to maximize completion under timeout
    # Already-complete batches are skipped
    pending = []
    for (yr, bid), objs in batch_to_objs.items():
        remaining = objs - set(parsed_records.keys())
        if remaining:
            pending.append((yr, bid, remaining, len(objs)))

    # Sort by ascending count (smallest first)
    pending.sort(key=lambda x: len(x[2]))

    print(f"[runner] pending batches: {len(pending)}")
    if not pending:
        print("[runner] All batches complete. Run with --finalize to write CSV.")
        return 0

    t0 = time.time()
    n_done = 0
    for (yr, bid, remaining, total) in pending:
        if time.time() - t0 > max_secs:
            print(f"[runner] time budget exceeded ({time.time()-t0:.0f}s), stopping")
            break
        if max_batches is not None and n_done >= max_batches:
            print(f"[runner] batch limit reached")
            break
        print(f"[runner] batch ({yr}/{bid}): {len(remaining)} of {total} remaining...")
        try:
            mod.stream_batch(yr, bid, remaining, parsed_records)
        except Exception as e:
            print(f"[runner] ERROR on batch {yr}/{bid}: {e}")
        # Persist after each batch
        with open(parsed_cache, "w") as f:
            json.dump(parsed_records, f)
        n_done += 1

    elapsed = time.time() - t0
    print(f"[runner] completed {n_done} batches in {elapsed:.0f}s")
    print(f"[runner] total cached records: {len(parsed_records)}")
    print(f"[runner] cached with schedule_h: {sum(1 for r in parsed_records.values() if r.get('schedule_h_present'))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
