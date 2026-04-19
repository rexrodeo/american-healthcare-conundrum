"""
Issue #8 chart regeneration entry-point.

Wipes issue_08/figures/*.png (preserves hero_cover.png if present)
then regenerates every chart referenced by newsletter_issue_08.md.

Runs each chart script as a subprocess so a failure in one chart
does not block the others, and so each script's own saving code
(relative paths via Path(__file__)) works correctly.

Usage:  python3 issue_08/generate_all_charts.py
"""

from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
FIGURES = HERE / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

# Charts to regenerate, in newsletter order.
# Filenames MUST correspond 1:1 with *[Chart N: ...]* placeholders in
# newsletter_issue_08.md (see CLAUDE.md Chart Creation Rule #9).
CHART_SCRIPTS = [
    "chart1_denial_variance.py",       # Chart 1: 36x denial variance
    "chart2_appeal_gap.py",            # Chart 2: Appeal gap UHC vs Humana
    "chart3_savings_components.py",    # Chart 3: $32B stacked bar (Path C, Component D dropped)
    "chart4_savings_tracker.py",       # Chart 4: Running total $428.6B
]

# Files preserved across wipes (not regenerated here).
PRESERVE = {"hero_cover.png"}


def wipe_figures():
    removed = []
    for png in FIGURES.glob("*.png"):
        if png.name in PRESERVE:
            continue
        png.unlink()
        removed.append(png.name)
    return removed


def run_script(script_name: str) -> tuple[str, bool, str]:
    script_path = HERE / script_name
    if not script_path.exists():
        return (script_name, False, f"ERROR: script not found at {script_path}")
    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True, text=True,
    )
    ok = result.returncode == 0
    output = (result.stdout + result.stderr).strip()
    return (script_name, ok, output)


def main() -> int:
    print(f"Regenerating charts in {FIGURES}")
    removed = wipe_figures()
    if removed:
        print(f"  wiped: {', '.join(removed)}")
    else:
        print("  nothing to wipe")

    failures = []
    for script in CHART_SCRIPTS:
        name, ok, output = run_script(script)
        status = "OK " if ok else "FAIL"
        print(f"  [{status}] {name}")
        if not ok:
            print(f"        {output}")
            failures.append(name)
        elif output:
            # Chart scripts print their save path; echo it for traceability.
            for line in output.splitlines():
                print(f"        {line}")

    # Final inventory check: PNG count should equal len(CHART_SCRIPTS) + preserved.
    final_pngs = sorted(p.name for p in FIGURES.glob("*.png"))
    expected = set(s.replace(".py", ".png") for s in CHART_SCRIPTS) | {
        p for p in PRESERVE if (FIGURES / p).exists()
    }
    orphans = [p for p in final_pngs if p not in expected]
    missing = [p for p in expected if p not in final_pngs]

    print()
    print(f"Final figures/ inventory: {len(final_pngs)} PNGs")
    for p in final_pngs:
        print(f"  {p}")
    if orphans:
        print(f"WARNING: orphan PNGs not in CHART_SCRIPTS: {orphans}")
    if missing:
        print(f"WARNING: expected PNGs missing: {missing}")
    if failures:
        print(f"FAILURES: {failures}")
        return 1
    if orphans or missing:
        return 2
    print("All charts regenerated successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
