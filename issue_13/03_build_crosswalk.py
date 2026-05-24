"""
03_build_crosswalk.py — Build EIN <-> CCN crosswalk for Issue #13.

HCRIS HOSP10 does not carry filer EIN. We must match Schedule H filer rows
(by EIN, with filer_name + filer_state) to HCRIS hospital rows (by CCN,
with hosp_name + state). For single-facility filers, exact-name + state
matching is the path. For multi-facility filers (Kaiser, Cleveland Clinic,
CommonSpirit, etc.), the consolidated 990 covers many HCRIS rows; we use
hospital_facilities_cnt + state to allocate.

OUTPUT:
    issue_13/results/ein_ccn_crosswalk.csv
"""
import csv
import json
import re
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
DATA_CACHE = HERE / "data_cache"
RESULTS.mkdir(exist_ok=True)


def normalize_name(name):
    """Normalize hospital/filer name for matching: uppercase, strip apostrophes,
    canonicalize spelling. Keep most words (the matcher uses Jaccard on tokens)."""
    if not name:
        return ""
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    s = s.upper()
    # Drop subsidiary/group markers
    s = re.sub(r"-\s*SUBORDINATES?\b", "", s)
    s = re.sub(r"GROUP RETURN", "", s)
    s = re.sub(r"\bINCORPORATED\b", "INC", s)
    s = re.sub(r"\bCORPORATION\b", "CORP", s)
    # Common abbreviations
    s = re.sub(r"\bCHILDREN'S\b", "CHILDRENS", s)
    s = re.sub(r"\bMOTHER'S\b", "MOTHERS", s)
    s = re.sub(r"\bST\.?\b", "SAINT", s)
    s = re.sub(r"\bMT\.?\b", "MOUNT", s)
    s = re.sub(r"\bN\.?\s+", "NORTH ", s)
    s = re.sub(r"\bS\.?\s+", "SOUTH ", s)
    s = re.sub(r"\bE\.?\s+", "EAST ", s)
    s = re.sub(r"\bW\.?\s+", "WEST ", s)
    # Remove apostrophes BEFORE token-splitting
    s = s.replace("'", "")
    # Punctuation
    s = re.sub(r"[^A-Z0-9 ]", " ", s)
    # Collapse whitespace
    s = " ".join(s.split())
    return s


# Stopwords that contribute little signal to filer-vs-hospital matching
STOPWORDS = {
    "THE", "OF", "AND", "INC", "LLC", "LP", "CORP", "COMPANY",
    "FOUNDATION", "GROUP", "RETURN", "A", "AN", "AT", "FOR",
    "MEDICAL", "HEALTH", "HOSPITAL", "HOSPITALS", "SYSTEM", "SYSTEMS",
    "HEALTHCARE", "CENTER", "CENTERS", "SERVICES", "SERVICE", "CARE",
}

# Known nonprofit hospital system brand-keyword maps. When a filer name contains
# the first set of keywords, treat its hospitals as those HCRIS hospitals
# whose names contain any of the second set of keywords (in the filer's state
# or any state for true multi-state systems).
SYSTEM_KEYWORDS = [
    # (filer_keywords, hcris_keywords, multi_state)
    ({"CLEVELAND", "CLINIC"}, {"CLEVELAND", "CLINIC"}, False),
    ({"MASS", "GENERAL", "BRIGHAM"}, {"MASS", "GENERAL", "BRIGHAM", "WOMEN", "MGH", "FAULKNER", "NEWTON", "WELLESLEY", "SALEM", "COOLEY", "DICKINSON", "MARTHAS", "VINEYARD", "NANTUCKET"}, False),
    ({"DIGNITY"}, {"DIGNITY", "MERCY", "MARYS", "BERNARDINE", "BARTON"}, True),
    ({"COMMONSPIRIT"}, {"COMMONSPIRIT", "CHI", "DIGNITY", "MARIAN", "SEQUOIA", "MERCY", "ST", "SAINT", "FRANCIS"}, True),
    ({"BON", "SECOURS", "MERCY"}, {"BON", "SECOURS", "MERCY"}, True),
    ({"IHC", "HEALTH"}, {"INTERMOUNTAIN", "IHC", "PRIMARY", "CHILDRENS", "VALLEY"}, True),
    ({"BJC"}, {"BARNES", "JEWISH", "CHILDRENS", "ALTON", "PARKLAND", "CHRISTIAN", "PROGRESS", "WEST"}, True),
    ({"PROVIDENCE"}, {"PROVIDENCE"}, True),
    ({"SUTTER"}, {"SUTTER"}, True),
    ({"INDIANA", "UNIVERSITY"}, {"INDIANA", "UNIVERSITY", "RILEY", "METHODIST"}, False),
    ({"KAISER"}, {"KAISER", "KFH", "PERMANENTE"}, True),
    ({"LONG", "ISLAND", "JEWISH"}, {"LONG", "ISLAND", "JEWISH", "LIJ", "NORTH", "SHORE"}, False),
    ({"OHIOHEALTH"}, {"OHIOHEALTH", "RIVERSIDE", "GRANT", "DUBLIN"}, False),
    ({"MAINEHEALTH"}, {"MAINE", "FRANKLIN", "MEMORIAL", "WALDO", "PEN", "BAY"}, False),
    ({"CHILDRENS", "BOSTON"}, {"BOSTON", "CHILDRENS"}, False),
    ({"HONORHEALTH"}, {"HONORHEALTH"}, False),
    ({"NORTON"}, {"NORTON"}, False),
    ({"RUSH"}, {"RUSH"}, False),
    ({"CHILDRENS", "COLORADO"}, {"CHILDRENS", "COLORADO"}, False),
    ({"CATHOLIC", "INITIATIVES"}, {"CATHOLIC", "ST", "SAINT", "MERCY"}, True),
    ({"UC", "HEALTHCARE"}, {"UC", "UNIVERSITY", "CINCINNATI"}, False),
    ({"ATRIUM"}, {"ATRIUM", "CAROLINAS", "WAKE"}, True),
    ({"ADVENTHEALTH"}, {"ADVENT", "FLORIDA", "ADVENTHEALTH"}, True),
    ({"ASCENSION"}, {"ASCENSION", "ST", "SAINT", "ALEXIAN"}, True),
    ({"BAPTIST"}, {"BAPTIST"}, True),
    ({"HCA"}, {"HCA"}, True),
    ({"TRINITY"}, {"TRINITY", "MERCY", "MARIAN"}, True),
    ({"INTERMOUNTAIN"}, {"INTERMOUNTAIN"}, True),
    ({"BAYLOR"}, {"BAYLOR"}, True),
    ({"NYU", "LANGONE"}, {"NYU", "LANGONE", "TISCH"}, False),
    ({"MOUNT", "SINAI"}, {"MOUNT", "SINAI", "BETH", "ISRAEL", "ROOSEVELT"}, False),
    ({"PRESBYTERIAN", "YORK", "NEW"}, {"PRESBYTERIAN", "YORK", "WEILL", "CORNELL"}, False),
    ({"INOVA"}, {"INOVA"}, False),
    ({"FRANCISCAN"}, {"FRANCISCAN"}, True),
    ({"SHANDS"}, {"SHANDS"}, False),
    ({"COOPER"}, {"COOPER"}, False),
    ({"PHILADELPHIA", "CHILDRENS"}, {"PHILADELPHIA", "CHILDRENS"}, False),
    ({"BENEFIS"}, {"BENEFIS"}, False),
    ({"NORTHWELL"}, {"NORTH", "SHORE", "LONG", "ISLAND", "NORTHWELL", "LENOX", "STATEN"}, False),
    ({"UNIVERSITY", "OHIO"}, {"UNIVERSITY"}, False),
    ({"UPMC"}, {"UPMC"}, True),
    ({"PENN"}, {"PENN", "PENNSYLVANIA"}, False),
    ({"BARNES", "JEWISH"}, {"BARNES", "JEWISH"}, False),
    ({"VANDERBILT"}, {"VANDERBILT"}, False),
    ({"NORTHWESTERN"}, {"NORTHWESTERN"}, False),
    ({"DUKE"}, {"DUKE"}, False),
    ({"JOHNS", "HOPKINS"}, {"JOHNS", "HOPKINS"}, False),
    ({"STANFORD"}, {"STANFORD"}, False),
    ({"UCLA"}, {"UCLA"}, False),
    ({"YALE"}, {"YALE"}, False),
]

# v3 PATCH: System keywords known to operate genuinely cross-state. Used as a
# gating list — cross-state matches in Phase 2 (multi_facility_jaccard) require
# the filer name to contain one of these substrings. This prevents one bad EIN
# (e.g., "University Hospitals Health System Inc", Cleveland OH) from being
# allocated to academic medical centers in other states (Vanderbilt, Duke,
# Cooper, etc.) via low-jaccard token overlap.
CROSS_STATE_SYSTEM_SUBSTRINGS = {
    "ASCENSION", "ADVENTHEALTH", "ADVENT", "BAYLOR", "BON SECOURS",
    "COMMONSPIRIT", "CATHOLIC HEALTH INITIATIVES", "DIGNITY",
    "INTERMOUNTAIN", "HCA", "KAISER", "PROVIDENCE", "SUTTER",
    "TRINITY HEALTH", "TENET", "UPMC", "BJC", "NORTHWELL",
    "FRANCISCAN ALLIANCE", "MERCY HEALTH", "TRINITY",
    "MOUNT SINAI", "ADVOCATE", "ATRIUM",
    "BANNER", "CHRISTUS",
}


def tokens(name):
    raw = set(normalize_name(name).split())
    return raw - STOPWORDS


def system_keyword_match(filer_tokens, candidates):
    """Try matching against known system brand-keyword maps. Returns a list of
    HCRIS candidates whose names contain any of the system's hcris_keywords."""
    for filer_kw_set, hcris_kw_set, multi_state in SYSTEM_KEYWORDS:
        if filer_kw_set.issubset(filer_tokens):
            # Match HCRIS candidates whose tokens intersect hcris_kw_set
            matched = []
            for c in candidates:
                if c["tokens"] & hcris_kw_set:
                    matched.append(c)
            if matched:
                return matched, filer_kw_set, hcris_kw_set, multi_state
    return None, None, None, None


def main():
    print("Building EIN <-> CCN crosswalk")
    print("=" * 60)

    # Load Schedule H per-filer panel
    sh_rows = []
    with open(RESULTS / "per_filer_schedule_h.csv") as f:
        r = csv.DictReader(f)
        for row in r:
            sh_rows.append({
                "ein": row["ein"],
                "filer_name": row["filer_name"],
                "filer_state": row["filer_state"],
                "hospital_facilities_cnt": int(row.get("hospital_facilities_cnt") or 0) or 1,
                "form990_total_expenses": int(row.get("form990_total_expenses") or 0),
            })
    print(f"Schedule H filers: {len(sh_rows)}")

    # Load HCRIS nonprofit hospitals
    with open(DATA_CACHE / "hcris_hospitals.json") as f:
        hcris = json.load(f)
    # Also load financials so we can use total_costs for allocation
    with open(DATA_CACHE / "hcris_financials.json") as f:
        fin = json.load(f)
    # Merge financials
    for rid, h in hcris.items():
        h.update(fin.get(rid, {}))

    # Filter to nonprofits (ctrl_type 1, 2)
    HCRIS_NONPROFIT = ("1", "2")
    np_hospitals = {rid: h for rid, h in hcris.items() if h.get("ctrl_type") in HCRIS_NONPROFIT}
    print(f"HCRIS nonprofit hospitals: {len(np_hospitals)}")

    # Build name tokens per hospital, grouped by state
    by_state = {}
    for rid, h in np_hospitals.items():
        state = (h.get("state") or "").strip().upper()
        hosp_name = (h.get("hosp_name") or "").strip()
        if not state or not hosp_name:
            continue
        by_state.setdefault(state, []).append({
            "rpt_rec_num": rid,
            "ccn": h.get("ccn", ""),
            "hosp_name": hosp_name,
            "norm_name": normalize_name(hosp_name),
            "tokens": tokens(hosp_name),
            "state": state,
            "total_costs": h.get("total_costs") or 0,
            "beds_available": h.get("beds_available") or 0,
        })

    # Score helpers
    def jaccard(s1, s2):
        if not s1 or not s2:
            return 0.0
        inter = len(s1 & s2)
        union = len(s1 | s2)
        return inter / union if union else 0.0

    all_candidates = []
    for state, lst in by_state.items():
        all_candidates.extend(lst)

    # Match each filer
    matches = []
    unmatched_filers = []
    matched_ccns = set()  # CCN can be matched at most once per pipeline run

    # v3 PATCH: Two-pass ordering. Within each phase the pipeline still uses
    # the all-filers loop, but we run it TWICE:
    #   Pass A: single-facility filers first (n_facilities == 1). These are
    #           almost always exact-name same-state matches, and giving them
    #           first claim prevents multi-facility cross-state matches from
    #           consuming their CCNs greedily.
    #   Pass B: multi-facility filers (n_facilities > 1). Phase 1 (system
    #           keyword) and Phase 2 (jaccard) then operate against the
    #           remaining unclaimed CCN pool.
    # Within each pass, sort by facility count descending so the largest
    # systems claim before smaller ones in the same tier.
    sh_singles = [s for s in sh_rows if s["hospital_facilities_cnt"] == 1]
    sh_multis = sorted(
        [s for s in sh_rows if s["hospital_facilities_cnt"] > 1],
        key=lambda x: -x["hospital_facilities_cnt"],
    )
    sh_sorted = sh_singles + sh_multis

    for sh in sh_sorted:
        state = sh["filer_state"]
        n_facilities = sh["hospital_facilities_cnt"]
        filer_tokens = tokens(sh["filer_name"])
        if not filer_tokens:
            unmatched_filers.append({**sh, "reason": "no_tokens"})
            continue

        # Phase 1: try system-keyword matching for known systems
        sys_candidates = None
        if n_facilities > 1:
            search_pool = all_candidates  # multi-state
            sys_matched, fkw, hkw, multi = system_keyword_match(filer_tokens, search_pool)
            if sys_matched is not None:
                # Filter to unclaimed CCNs and (if not multi_state) same-state
                if not multi:
                    sys_matched = [c for c in sys_matched if c["state"] == state]
                sys_matched = [c for c in sys_matched if c["ccn"] not in matched_ccns]
                if sys_matched:
                    # Cap at the filer's reported facility count to avoid grabbing
                    # hospitals that belong to a competitor system with overlapping keywords
                    cap = min(len(sys_matched), n_facilities)
                    top = sys_matched[:cap]
                    total_costs_matched = sum(c["total_costs"] or 0 for c in top) or 1
                    for c in top:
                        matched_ccns.add(c["ccn"])
                        share = (c["total_costs"] or 0) / total_costs_matched
                        matches.append({
                            "ein": sh["ein"],
                            "filer_name": sh["filer_name"],
                            "filer_state": state,
                            "ccn": c["ccn"],
                            "rpt_rec_num": c["rpt_rec_num"],
                            "hcris_name": c["hosp_name"],
                            "hcris_state": c["state"],
                            "jaccard": 1.0,
                            "hospital_facilities_cnt": n_facilities,
                            "match_type": "system_keyword",
                            "match_scope": "multi_state" if multi else "same_state",
                            "allocation_share": round(share, 4),
                            "total_costs": c["total_costs"],
                        })
                    continue

        # Phase 2 (v3): jaccard-based matching with same-state enforcement.
        #
        # v3 PATCH (Stage 5.5 red-team fix):
        #   - Same-state matches require jaccard >= 0.7 (was 0.3 in v2).
        #   - Cross-state matches are only attempted when:
        #       (a) the filer name contains an explicit cross-state system
        #           substring (CROSS_STATE_SYSTEM_SUBSTRINGS), AND
        #       (b) no same-state candidate with jaccard >= 0.7 exists for the
        #           competing CCN, AND
        #       (c) jaccard on the cross-state pair >= 0.85.
        #   - Cross-state scoring is no longer discounted by 0.85; the higher
        #     threshold replaces the discount.
        #
        # This eliminates the v2 bug where one Cleveland-OH EIN was allocated to
        # academic medical centers in 10 other states via low-jaccard token
        # overlap on {COUNTY, MEMORIAL} type pairs.

        SAME_STATE_THRESHOLD = 0.70
        CROSS_STATE_THRESHOLD = 0.85

        same_state = [c for c in by_state.get(state, []) if c["ccn"] not in matched_ccns]
        scored_same = [(jaccard(filer_tokens, c["tokens"]), c, "same_state") for c in same_state]
        scored_same = [(j, c, scope) for j, c, scope in scored_same if j >= SAME_STATE_THRESHOLD]

        # Cross-state: only if filer name is on the explicit cross-state systems
        # whitelist. (Multi-state Phase 1 system_keyword matches already covered
        # genuine national systems via SYSTEM_KEYWORDS multi_state=True.)
        filer_name_upper = normalize_name(sh["filer_name"])
        is_cross_state_eligible = any(sub in filer_name_upper for sub in CROSS_STATE_SYSTEM_SUBSTRINGS)

        scored_cross = []
        if n_facilities > 1 and is_cross_state_eligible:
            for c in all_candidates:
                if c["state"] == state or c["ccn"] in matched_ccns:
                    continue
                j = jaccard(filer_tokens, c["tokens"])
                if j >= CROSS_STATE_THRESHOLD:
                    scored_cross.append((j, c, "cross_state"))

        # Sanity: for any cross-state candidate, reject if a higher-or-equal
        # same-state candidate exists for the same CCN. (Same-state candidates
        # are by definition for *this* filer's state, not the candidate's
        # state, so this check is the symmetric one: ensure no same-state
        # candidate exists with higher score. The greedy outer loop also
        # ensures lower-priority filers see only unclaimed CCNs.)
        if scored_same and scored_cross:
            best_same = max(scored_same, key=lambda x: x[0])
            scored_cross = [(j, c, sc) for j, c, sc in scored_cross if j > best_same[0]]

        scored = scored_same + scored_cross
        scored.sort(key=lambda x: -x[0])

        good = scored  # already threshold-filtered

        if not good:
            unmatched_filers.append({
                **sh,
                "reason": "no_match_above_threshold",
                "best_jaccard": scored[0][0] if scored else 0,
                "best_candidate": scored[0][1]["hosp_name"] if scored else "",
            })
            continue

        if n_facilities == 1:
            j, c, scope = good[0]
            matched_ccns.add(c["ccn"])
            matches.append({
                "ein": sh["ein"],
                "filer_name": sh["filer_name"],
                "filer_state": state,
                "ccn": c["ccn"],
                "rpt_rec_num": c["rpt_rec_num"],
                "hcris_name": c["hosp_name"],
                "hcris_state": c["state"],
                "jaccard": round(j, 3),
                "hospital_facilities_cnt": n_facilities,
                "match_type": "single_facility_jaccard",
                "match_scope": scope,
                "allocation_share": 1.0,
                "total_costs": c["total_costs"],
            })
        else:
            top_n = good[:n_facilities]
            total_costs_matched = sum(c["total_costs"] or 0 for j, c, scope in top_n) or 1
            for j, c, scope in top_n:
                matched_ccns.add(c["ccn"])
                share = (c["total_costs"] or 0) / total_costs_matched
                matches.append({
                    "ein": sh["ein"],
                    "filer_name": sh["filer_name"],
                    "filer_state": state,
                    "ccn": c["ccn"],
                    "rpt_rec_num": c["rpt_rec_num"],
                    "hcris_name": c["hosp_name"],
                    "hcris_state": c["state"],
                    "jaccard": round(j, 3),
                    "hospital_facilities_cnt": n_facilities,
                    "match_type": "multi_facility_jaccard",
                    "match_scope": scope,
                    "allocation_share": round(share, 4),
                    "total_costs": c["total_costs"],
                })

    print(f"\nMatches: {len(matches)}")
    print(f"  Unique EINs matched: {len(set(m['ein'] for m in matches))}")
    print(f"  Unique CCNs matched: {len(set(m['ccn'] for m in matches))}")
    print(f"  Unmatched filers: {len(unmatched_filers)}")
    print()

    # Match type distribution
    by_type = {}
    for m in matches:
        by_type.setdefault(m["match_type"], 0)
        by_type[m["match_type"]] += 1
    print(f"  By match type: {by_type}")

    # Unmatched reasons
    by_reason = {}
    for u in unmatched_filers:
        by_reason.setdefault(u["reason"], 0)
        by_reason[u["reason"]] += 1
    print(f"  Unmatched reasons: {by_reason}")

    # Write crosswalk
    if matches:
        keys = list(matches[0].keys())
        with open(RESULTS / "ein_ccn_crosswalk.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            for m in matches:
                w.writerow(m)
        print(f"\nWrote {len(matches)} matches to ein_ccn_crosswalk.csv")

    if unmatched_filers:
        keys = sorted({k for u in unmatched_filers for k in u})
        with open(RESULTS / "ein_ccn_unmatched.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            for u in unmatched_filers:
                w.writerow(u)
        print(f"Wrote {len(unmatched_filers)} unmatched filers to ein_ccn_unmatched.csv")

    return 0


if __name__ == "__main__":
    sys.exit(main())
