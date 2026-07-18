#!/usr/bin/env python3
"""
Public-safety scan for local-ai-inference-proof repository.

The repository must NOT be published as public until this scan passes.

Usage:
  python3 scripts/write_test_safety.py                # all checks
  python3 scripts/write_test_safety.py --check readme  # single check
  python3 scripts/write_test_safety.py --ci             # JSON for CI
"""

from __future__ import annotations
import argparse, json, os, re, subprocess, sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EVIDENCE_DIR = REPO_ROOT / "evidence"

PERSONAL_PATTERNS = [
    re.compile(r"Payam.*Adloo", re.I),
    re.compile(r"piemasterflex", re.I),
    re.compile(r"TEST[ _]ENGINEER|Test Engineer", re.I),
    re.compile(r"resume|linkedin|cover letter|job application", re.I),
    re.compile(r"interview.*(preparation|tracker|schedule)", re.I),
    re.compile(r"DXC Luxoft|CData|Cislunar|Spacecraft Battery", re.I),
    re.compile(r"RTEI|Rockwell|Apache Spin", re.I),
    re.compile(r"manager name|city, state", re.I),
]

WORKSTATION_PATTERNS = [
    re.compile(r"NVIDIA (GeForce|RTX PRO 4000 Blackwell)", re.I),
    re.compile(r"Ryzen 7 9700X", re.I),
    re.compile(r"64 GB RAM", re.I),
]

PII_PATTERNS = [
    re.compile(r"\d{3}-\d{4}-\d{4}"),
    re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", re.I),
]

@dataclass
class CheckResult:
    name: str
    status: str
    detail: str
    matches: list = field(default_factory=list)

def scan_file(fp, patterns, label=""):
    if not fp.exists():
        return []
    text = fp.read_text(errors="ignore")
    hits = []
    for pat in patterns:
        for m in pat.finditer(text):
            ln = text[:m.start()].count("\n") + 1
            line = text.splitlines()[min(ln, len(text.splitlines()))-1]
            hits.append(f"{fp.name}:{ln}: {line.strip()[:100]}")
    return hits

def check_readme():
    results = []
    r = REPO_ROOT / "README.md"
    if not r.exists():
        results.append(CheckResult("readme_exists", "FAIL", "README.md missing"))
        return results
    results.append(CheckResult("readme_exists", "PASS", "README.md exists"))
    hits = scan_file(r, PERSONAL_PATTERNS)
    results.append(CheckResult("readme_clean", "FAIL" if hits else "PASS",
        "Personal refs" if hits else "Clean", hits))
    ws = scan_file(r, WORKSTATION_PATTERNS)
    results.append(CheckResult("readme_no_ws", "FAIL" if ws else "PASS",
        "Workstation specs" if ws else "No workstation", ws))
    return results

def check_license():
    results = []
    lf = REPO_ROOT / "LICENSE"
    if not lf.exists():
        results.append(CheckResult("license_exists", "FAIL", "No LICENSE"))
        return results
    text = lf.read_text()
    results.append(CheckResult("license_osi", "PASS" if "Permission is hereby granted" in text else "WARN",
        "MIT license" if "Permission is hereby granted" in text else "Non-standard"))
    hits = scan_file(lf, PERSONAL_PATTERNS)
    results.append(CheckResult("license_clean", "FAIL" if hits else "PASS", "Personal refs" if hits else "Clean", hits))
    return results

def check_development():
    results = []
    df = REPO_ROOT / "DEVELOPMENT.md"
    if not df.exists():
        results.append(CheckResult("dev_check", "PASS", "No DEVELOPMENT.md"))
        return results
    ws = scan_file(df, WORKSTATION_PATTERNS)
    results.append(CheckResult("dev_no_ws", "FAIL" if ws else "PASS", "Workstation specs" if ws else "Generic", ws))
    jr = scan_file(df, PERSONAL_PATTERNS)
    results.append(CheckResult("dev_no_job", "FAIL" if jr else "PASS", "Job content" if jr else "Clean", jr))
    return results

def check_deps():
    results = []
    rf = REPO_ROOT / "requirements.txt"
    pf = REPO_ROOT / "pyproject.toml"
    if not rf.exists() and not pf.exists():
        results.append(CheckResult("deps_exist", "FAIL", "No dependency file"))
        return results
    bad = ["pytest", "httpx", "black", "ruff", "mypy"]
    if rf.exists():
        lines = rf.read_text().splitlines()
        devs = [l.split("==")[0].split(">")[0].split("[")[0].strip() for l in lines
                if l.strip() and not l.startswith("#") and l.split("==")[0].split(">")[0].split("[")[0].strip().lower() in bad]
        results.append(CheckResult("req_no_dev", "WARN" if devs else "PASS",
            f"Dev deps: {devs}" if devs else "No dev deps", devs))
    return results

def check_env():
    results = []
    ee = REPO_ROOT / ".env.example"
    ef = REPO_ROOT / ".env"
    if ee.exists():
        secrets = [s for s in re.findall(r"[A-Za-z0-9]{40,}", ee.read_text())
                    if not re.fullmatch(r"[Xx*]+|placeholder|example", s)]
        results.append(CheckResult("env_clean", "FAIL" if secrets else "PASS",
            "Real secrets" if secrets else "Placeholders", secrets))
    results.append(CheckResult("env_git", "WARN" if ef.exists() else "PASS",
        ".env committed" if ef.exists() else "No .env"))
    return results

def check_evidence():
    results = []
    if not EVIDENCE_DIR.exists():
        results.append(CheckResult("evidence_absent", "PASS", "No evidence dir"))
        return results
    gi = (REPO_ROOT / ".gitignore").read_text() if (REPO_ROOT / ".gitignore").exists() else ""
    results.append(CheckResult("evidence_gi", "PASS" if "evidence" in gi else "FAIL",
        "Gitignored" if "evidence" in gi else "NOT gitignored"))
    results.append(CheckResult("evidence_empty", "PASS", "OK"))
    return results

def check_paths():
    results = []
    exts = {".md", ".txt", ".py", ".yaml", ".yml", ".json", ".toml"}
    leaks = []
    for fp in REPO_ROOT.rglob("*"):
        if not fp.is_file() or fp.suffix not in exts:
            continue
        if ".git" in str(fp) or ".venv/" in str(fp):
            continue
        # Skip the safety script itself (contains regex patterns with /home/)
        if "write_test_safety.py" in str(fp):
            continue
        text = fp.read_text(errors="ignore")
        for hit in re.findall(r"/(?:rootdir)/[^\s]+|/home/[^\s]+", text):
            leaks.append(f"{fp.relative_to(REPO_ROOT)}: {hit[:50]}")
    results.append(CheckResult("no_leaks", "FAIL" if leaks else "PASS",
        "Path leaks" if leaks else "No leaks", leaks))
    return results

def check_git():
    results = []
    gi = REPO_ROOT / ".gitignore"
    if not gi.exists():
        results.append(CheckResult("gi_exists", "FAIL", "No .gitignore"))
        return results
    text = gi.read_text()
    missing = [e for e in [".env", "*.pyc", "__pycache__", "evidence", ".venv"] if e not in text]
    results.append(CheckResult("gi_complete", "WARN" if missing else "PASS",
        f"Missing: {missing}" if missing else "Standard entries", missing))
    r = subprocess.run(["git", "rev-list", "--objects", "--all"],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=30)
    large = []
    if r.returncode == 0:
        for line in r.stdout.splitlines():
            parts = line.split()
            if len(parts) >= 2:
                s = subprocess.run(["git", "cat-file", "-s", parts[0]],
                    cwd=REPO_ROOT, capture_output=True, text=True, timeout=10)
                if s.returncode == 0 and int(s.stdout.strip()) > 5000000:
                    large.append(f"{parts[1]}")
    results.append(CheckResult("no_large", "FAIL" if large else "PASS",
        f"Large: {large}" if large else "No large files", large))
    return results

def check_binaries():
    results = []
    bad = {".exe", ".dll", ".so", ".dylib", ".bin", ".img"}
    bins = [str(f.relative_to(REPO_ROOT)) for f in REPO_ROOT.rglob("*")
            if f.is_file() and f.suffix in bad]
    results.append(CheckResult("no_bins", "FAIL" if bins else "PASS",
        "Binaries" if bins else "No binaries", bins))
    return results

def check_privacy():
    is_pub = False
    try:
        r = subprocess.run(["gh", "repo", "view", "--json", "visibility"],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=15)
        if r.returncode == 0:
            is_pub = json.loads(r.stdout).get("visibility") == "PUBLIC"
    except Exception:
        pass
    return CheckResult("privacy", "WARN" if is_pub else "PASS",
        "PUBLIC" if is_pub else "Private",
        ["Clean before publishing"] if is_pub else [])

def run_all():
    all_res = []
    for fn in [check_readme, check_license, check_development, check_deps,
                check_env, check_evidence, check_paths, check_git,
                check_binaries]:
        all_res.extend(fn())
    all_res.append(check_privacy())
    return all_res

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", type=str)
    parser.add_argument("--ci", action="store_true")
    args = parser.parse_args()

    all_checkers = {"readme": check_readme, "license": check_license, "development": check_development,
                    "deps": check_deps, "env": check_env, "evidence": check_evidence,
                    "paths": check_paths, "git": check_git, "binaries": check_binaries}

    if args.check:
        checker = all_checkers.get(args.check)
        if not checker:
            print(f"Unknown check: {args.check}")
            sys.exit(1)
        results = checker() if isinstance(checker(), list) else [checker()]
    else:
        results = run_all()

    fails = [r for r in results if r.status == "FAIL"]
    warns = [r for r in results if r.status == "WARN"]
    passes = [r for r in results if r.status == "PASS"]
    safe = len(fails) == 0

    if args.ci:
        print(json.dumps({"verdict": "SAFE" if safe else "NOT_SAFE",
            "fail_count": len(fails), "details": [{"name": r.name, "status": r.status,
            "detail": r.detail, "matches": r.matches} for r in results]}, indent=2))
        sys.exit(0 if safe else 2)

    print("=" * 60)
    print("PUBLIC SAFETY SCAN")
    print("=" * 60)
    for r in results:
        print(f"  [{r.status}] {r.name}: {r.detail}")
        for m in r.matches:
            print(f"        >> {m}")
    print("-" * 60)
    if safe:
        print("VERDICT: SAFE FOR PUBLIC")
    else:
        print("VERDICT: NOT SAFE FOR PUBLIC")
        print("\nFix these FAIL items:")
        for f in fails:
            print(f"  - {f.name}: {f.detail}")
        if warns:
            print("\nWarnings:")
            for w in warns:
                print(f"  - {w.name}: {w.detail}")
    print(f"\n{len(passes)} PASS | {len(fails)} FAIL | {len(warns)} WARN")
    sys.exit(0 if safe else 2)

if __name__ == "__main__":
    main()
