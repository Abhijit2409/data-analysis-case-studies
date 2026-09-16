"""
Run every automated check for the SYNTHETIC case-study prototype and write evidence/test-results.md.
Exits with status 1 if any step fails.

Usage:
  python build/run_tests.py            # full suite
  python build/run_tests.py --skip-ui  # without the headless-Edge rendered-page tests

Steps:
  0. Reproducibility: regenerate the CSV with the fixed seed and confirm it is byte-identical
  1. 32 structural and seeded-pattern checks (build/validate_and_analyze.py), which also rebuild the analysis outputs
  2. Calculation regression tests (tests/test_calculations.py)
  3. Dashboard logic and Python-JavaScript reconciliation tests (tests/test_dashboard_logic.js)
  4. Build dashboard-mockup.html and confirm it embeds the current template, logic and data
  5. Rendered-page regression tests in headless Microsoft Edge (tests/ui_regression.js)
"""
import datetime
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
PY = sys.executable
OUT = os.path.join(ROOT, "evidence", "test-results.md")
ENV = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONWARNINGS="ignore")


def sha(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def run(cmd):
    t = time.time()
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV)
    return p.returncode, (p.stdout or "") + (p.stderr or ""), time.time() - t


def version(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=30).stdout.strip() or "unknown"
    except Exception:  # noqa: BLE001
        return "unknown"


def main():
    skip_ui = "--skip-ui" in sys.argv
    results = []

    # 0. reproducibility
    csv = os.path.join(ROOT, "data", "synthetic_store_weekly.csv")
    before = sha(csv)
    code, out, dur = run([PY, "build/generate_synthetic.py"])
    same = code == 0 and sha(csv) == before
    results.append(("Reproducibility: regenerated CSV is byte-identical (seed 20260913)", "python build/generate_synthetic.py", same, "SHA-256 unchanged" if same else "CSV changed or generator failed", dur, out))

    # 1. structural and seeded-pattern checks
    code, out, dur = run([PY, "build/validate_and_analyze.py"])
    m = re.search(r"Checks passed: (\d+)/(\d+)", out)
    results.append(("Structural and seeded-pattern checks", "python build/validate_and_analyze.py", code == 0, m.group(0) if m else "no summary", dur, out))

    # 2. Python calculation tests
    code, out, dur = run([PY, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"])
    m = re.search(r"Ran (\d+) tests?", out)
    fails = re.search(r"FAILED \((.*?)\)", out)
    results.append(("Calculation regression tests (Python)", "python -m unittest discover -s tests -p \"test_*.py\"", code == 0,
                    (m.group(0) if m else "no summary") + (f"; FAILED {fails.group(1)}" if fails else "; all OK"), dur, out))

    # 3. Node logic tests
    code, out, dur = run(["node", "--test", "tests/test_dashboard_logic.js"])
    p_, f_ = re.search(r"ℹ pass (\d+)", out), re.search(r"ℹ fail (\d+)", out)
    results.append(("Dashboard logic and reconciliation tests (Node)", "node --test tests/test_dashboard_logic.js", code == 0,
                    f"pass {p_.group(1) if p_ else '?'}, fail {f_.group(1) if f_ else '?'}", dur, out))

    # 4. build and consistency of generated page
    code, out, dur = run([PY, "build/build_mockup.py"])
    consistent = False
    if code == 0:
        page = open(os.path.join(ROOT, "dashboard-mockup.html"), encoding="utf-8").read()
        data = json.dumps(json.load(open(os.path.join(ROOT, "data", "analysis_summary.json"), encoding="utf-8")), separators=(",", ":"), allow_nan=False).replace("</", "<\\/")
        logic = open(os.path.join(ROOT, "build", "dashboard_logic.js"), encoding="utf-8").read().replace("</script", "<\\/script")
        tpl = open(os.path.join(ROOT, "build", "mockup_template.html"), encoding="utf-8").read()
        head = tpl.split("/*__LOGIC__*/")[0]
        consistent = data in page and logic in page and page.startswith(head) and "/*__DATA__*/" not in page
    results.append(("Build dashboard; generated page embeds the current template, logic and data", "python build/build_mockup.py", consistent,
                    "consistent" if consistent else "generated page does not match sources", dur, out))

    # 5. UI tests
    if skip_ui:
        results.append(("Rendered-page regression tests (headless Edge)", "node tests/ui_regression.js", None, "SKIPPED (--skip-ui)", 0, ""))
    else:
        code, out, dur = run(["node", "tests/ui_regression.js"])
        m = re.search(r"UI checks passed: (\d+)/(\d+)", out)
        results.append(("Rendered-page regression tests (headless Edge)", "node tests/ui_regression.js", code == 0, m.group(0) if m else "no summary", dur, out))

    # 6. document and deck consistency (reads the built deck; run node build/build_deck.js first after changes)
    code, out, dur = run([PY, "build/consistency_scan.py"])
    m = re.search(r"Document checks passed: (\d+/\d+)", out)
    results.append(("Document and deck consistency checks", "python build/consistency_scan.py", code == 0, m.group(0) if m else "no summary", dur, out))

    ok = all(r[2] is not False for r in results)
    try:
        import numpy
        import pandas
        pv = f"pandas {pandas.__version__}, numpy {numpy.__version__}"
    except Exception:  # noqa: BLE001
        pv = "pandas/numpy unavailable"
    edge = version(["powershell", "-NoProfile", "-Command", "(Get-Item 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe').VersionInfo.ProductVersion"]) if platform.system() == "Windows" else "n/a"

    L = ["# Automated Test Results (generated)\n",
         f"**Run:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')} · **Overall:** {'PASS' if ok else 'FAIL'} · **Command:** `python build/run_tests.py{' --skip-ui' if skip_ui else ''}`\n",
         f"**Environment:** Python {platform.python_version()} ({pv}); Node {version(['node', '--version'])}; Microsoft Edge {edge}; {platform.system()} {platform.release()}\n",
         "> Synthetic data only. These are automated prototype checks. They are not Power BI tests, not user acceptance testing and not an accessibility audit. See `evidence/test-report.md` for scope and manual checks.\n",
         "| # | Step | Command | Result | Summary | Seconds |", "|---|---|---|---|---|---|"]
    for i, (name, cmd, passed, summary, dur, _) in enumerate(results):
        L.append(f"| {i} | {name} | `{cmd}` | {'SKIPPED' if passed is None else 'PASS' if passed else '**FAIL**'} | {summary} | {dur:.1f} |")

    def section(title, out, pattern):
        lines = [ln.strip() for ln in out.splitlines() if re.search(pattern, ln)]
        return [f"\n## {title}\n", "```", *lines, "```"] if lines else []

    L += section("Calculation regression tests (Python)", results[2][5], r"\.\.\. (ok|FAIL|ERROR)$")
    L += section("Dashboard logic tests (Node)", results[3][5], r"^[✔✖] ")
    if not skip_ui:
        L += section("Rendered-page tests (headless Edge)", results[5][5], r"^(PASS|FAIL|INFO) ")
    failed_out = [r for r in results if r[2] is False]
    for name, _, _, _, _, out in failed_out:
        L += [f"\n## Output of failed step: {name}\n", "```", out[-4000:], "```"]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")

    for name, _, passed, summary, dur, _ in results:
        print(f"{'SKIP' if passed is None else 'PASS' if passed else 'FAIL'}  {name}: {summary} ({dur:.1f}s)")
    print(f"\nOverall: {'PASS' if ok else 'FAIL'} · wrote {os.path.relpath(OUT, ROOT)}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
