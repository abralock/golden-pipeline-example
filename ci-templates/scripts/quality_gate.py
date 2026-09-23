#!/usr/bin/env python3
"""Platform-owned quality gate. The repo only produces reports; this script decides.

Checks, in order:
  1. JUnit report(s) exist, contain > 0 tests, and 0 failures/errors.
  2. Overall line coverage >= --min-overall   (legacy repos start low, ratchet up).
  3. Coverage of NEW/CHANGED lines >= --min-new (default 80) vs --compare-branch.

Accepts Cobertura XML (Python, .NET/coverlet, JS/Jest, Go) or JaCoCo XML (Java).
"""
from __future__ import annotations

import argparse
import glob
import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET


def fail(msg: str) -> None:
    # Rollout phase 1: QG_MODE=warn reports but never blocks.
    if os.environ.get("QG_MODE", "enforce") == "warn":
        print(f"WARN (not blocking, QG_MODE=warn): {msg}")
        sys.exit(0)
    print(f"FAIL: {msg}")
    sys.exit(1)


def check_junit(pattern: str) -> None:
    files = sorted(glob.glob(pattern))
    if not files:
        fail(f"no JUnit report matched '{pattern}'. Does `make coverage` write reports/junit.xml?")
    tests = failures = 0
    for f in files:
        root = ET.parse(f).getroot()
        suites = [root] if root.tag == "testsuite" else root.iter("testsuite")
        for s in suites:
            tests += int(s.get("tests", 0))
            failures += int(s.get("failures", 0)) + int(s.get("errors", 0))
    print(f"tests: {tests} run, {failures} failed  ({len(files)} report file(s))")
    if tests == 0:
        fail("0 tests executed. An empty test target is not allowed.")
    if failures:
        fail(f"{failures} test(s) failed.")


def overall_line_rate(path: str) -> float:
    root = ET.parse(path).getroot()
    if root.tag == "coverage":  # Cobertura
        return float(root.get("line-rate", 0)) * 100
    if root.tag == "report":  # JaCoCo: report-level LINE counter
        for c in root.findall("counter"):
            if c.get("type") == "LINE":
                missed, covered = int(c.get("missed")), int(c.get("covered"))
                return 100.0 * covered / max(missed + covered, 1)
    fail(f"unrecognised coverage format in {path} (need Cobertura or JaCoCo XML)")
    return 0.0


def check_new_code(path: str, branch: str, minimum: float) -> None:
    if not shutil.which("diff-cover"):
        fail("diff-cover not installed in the toolbox image")
    print(f"new-code coverage vs {branch} (min {minimum:.0f}%):")
    rc = subprocess.run(
        ["diff-cover", path, f"--compare-branch={branch}",
         f"--fail-under={minimum}", "--format", "markdown:reports/new-code-coverage.md"],
        check=False,
    ).returncode
    if rc != 0:
        fail(f"new/changed lines are below {minimum:.0f}% coverage. See reports/new-code-coverage.md")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--junit", default="reports/junit*.xml")
    ap.add_argument("--coverage", default="reports/coverage.xml")
    ap.add_argument("--min-overall", type=float, default=0)
    ap.add_argument("--min-new", type=float, default=80)
    ap.add_argument("--compare-branch", default="",
                    help="e.g. origin/main. Empty = skip new-code check (main branch builds)")
    a = ap.parse_args()

    check_junit(a.junit)

    try:
        rate = overall_line_rate(a.coverage)
    except FileNotFoundError:
        fail(f"{a.coverage} not found. Does `make coverage` write it?")
    print(f"overall line coverage: {rate:.1f}%  (floor {a.min_overall:.0f}%)")
    if rate < a.min_overall:
        fail(f"overall coverage {rate:.1f}% is below the floor {a.min_overall:.0f}%")

    if a.compare_branch:
        check_new_code(a.coverage, a.compare_branch, a.min_new)

    print("PASS: quality gate")


if __name__ == "__main__":
    main()
