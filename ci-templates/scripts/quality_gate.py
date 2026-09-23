#!/usr/bin/env python3
"""Platform-owned quality gate. The repo only produces reports; this script decides.

Checks, in order:
  1. JUnit report(s) exist, contain > 0 tests, and 0 failures/errors.
  2. Overall line coverage >= --min-overall   (legacy repos start low, ratchet up).
  3. The coverage report's file paths resolve to files in the repo (else step 5 is blind).
  4. Every changed source file in the MR appears in the coverage report (else step 5 skips it).
  5. Coverage of NEW/CHANGED lines >= --min-new (default 80) vs --compare-branch.

Accepts Cobertura XML (Go, Python, .NET, TypeScript/Node.js/Next.js/Angular) or JaCoCo XML (Java).
"""
from __future__ import annotations

import argparse
import glob
import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from fnmatch import fnmatch
from pathlib import Path


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


def check_paths_resolve(path: str) -> None:
    """Fail if the coverage report's file paths don't point at files in this repo.

    Otherwise diff-cover finds "no lines with coverage information" and the
    new-code check passes silently (seen with ts-jest + TypeScript 6 + istanbul).
    """
    root = ET.parse(path).getroot()
    files: list[str] = []
    found = 0
    if root.tag == "coverage":  # Cobertura
        sources = [s.text or "" for s in root.iter("source")] or [""]
        for cls in root.iter("class"):
            fn = cls.get("filename", "")
            files.append(fn)
            if os.path.isfile(fn) or any(os.path.isfile(os.path.join(s, fn)) for s in sources):
                found += 1
    elif root.tag == "report":  # JaCoCo: <package name="com/x"><sourcefile name="A.java">
        for pkg in root.iter("package"):
            for sf in pkg.findall("sourcefile"):
                rel = f"{pkg.get('name')}/{sf.get('name')}"
                files.append(rel)
                if next(Path(".").glob(f"**/{rel}"), None):
                    found += 1
    if files and found == 0:
        fail(f"none of the {len(files)} files in {path} exist in this repo (e.g. '{files[0]}'). "
             "The coverage report paths are broken, so new-code coverage can't be measured.")
    print(f"coverage report maps to repo files: {found}/{len(files)}")


CODE_EXT = (".go", ".py", ".java", ".kt", ".cs", ".ts", ".tsx", ".js", ".jsx", ".mjs")
# Tests, generated/config files and app bootstrap files are not expected in coverage reports.
NOT_MEASURED = [
    "*_test.go", "*/test_*.py", "test_*.py", "*_test.py", "*/conftest.py", "*.spec.ts", "*.spec.tsx",
    "*.test.ts", "*.test.tsx", "*.test.js", "*.d.ts", "*/tests/*", "tests/*", "*/test/*", "test/*",
    "*/__tests__/*", "__tests__/*", "*/src/test/*", "src/test/*", "*.Tests/*", "*/*.Tests/*",
    "*.config.js", "*.config.ts", "*.config.mjs", "*.config.cjs", "src/main.ts", "*/app.config.ts",
    "*/Program.cs", "Program.cs", "tools/*", "scripts/*",
]


def measured_files(path: str) -> set[str]:
    """Repo-relative paths of every file that appears in the coverage report."""
    root = ET.parse(path).getroot()
    out: set[str] = set()
    if root.tag == "coverage":
        sources = [s.text or "" for s in root.iter("source")] or [""]
        for cls in root.iter("class"):
            fn = cls.get("filename", "")
            for cand in [fn] + [os.path.join(s, fn) for s in sources]:
                if os.path.isfile(cand):
                    out.add(os.path.relpath(os.path.realpath(cand), os.path.realpath(".")))
                    break
    elif root.tag == "report":
        for pkg in root.iter("package"):
            for sf in pkg.findall("sourcefile"):
                for hit in Path(".").glob(f"**/{pkg.get('name')}/{sf.get('name')}"):
                    out.add(str(hit))
    return out


def check_changed_files_measured(path: str, branch: str, extra_ignore: list[str]) -> None:
    """Fail if the MR changes source files that the coverage report doesn't contain at all.

    diff-cover silently skips such files ("no coverage information"), e.g. a new component
    that no test imports (Angular/Vite tree-shaking) or a path missing from collectCoverageFrom.
    """
    out = subprocess.run(["git", "diff", "--name-only", "--diff-filter=AM", f"{branch}...HEAD"],
                         capture_output=True, text=True, check=False).stdout.split()
    ignore = NOT_MEASURED + extra_ignore
    changed = [f for f in out if f.endswith(CODE_EXT) and not any(fnmatch(f, p) for p in ignore)]
    missing = sorted(set(changed) - measured_files(path))
    if missing:
        fail("changed source files are not in the coverage report at all (untested, or excluded by the "
             f"coverage config): {', '.join(missing)}")


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
    ap.add_argument("--not-measured", action="append", default=[],
                    help="extra glob of changed files allowed to be absent from the coverage report")
    a = ap.parse_args()

    check_junit(a.junit)

    try:
        rate = overall_line_rate(a.coverage)
    except FileNotFoundError:
        fail(f"{a.coverage} not found. Does `make coverage` write it?")
    print(f"overall line coverage: {rate:.1f}%  (floor {a.min_overall:.0f}%)")
    if rate < a.min_overall:
        fail(f"overall coverage {rate:.1f}% is below the floor {a.min_overall:.0f}%")

    check_paths_resolve(a.coverage)
    if a.compare_branch:
        check_changed_files_measured(a.coverage, a.compare_branch, a.not_measured)
        check_new_code(a.coverage, a.compare_branch, a.min_new)

    print("PASS: quality gate")


if __name__ == "__main__":
    main()
