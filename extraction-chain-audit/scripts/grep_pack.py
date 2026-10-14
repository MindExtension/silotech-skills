#!/usr/bin/env python3
"""Run the grep pack (references/grep-pack.tsv) with a positive control for every pattern.

Usage (<skill-dir> is the folder that holds SKILL.md):
  python3 <skill-dir>/scripts/grep_pack.py --selftest
  python3 <skill-dir>/scripts/grep_pack.py [paths ...] [--only GP-2,GP-9] [--exclude 'test*,fixtures']

Each pattern first runs on its own sample; a pattern that misses its sample is NOT-CHECKED and the
exit code is 1. Hits print as "GP-n path:line: text" and are candidates, not findings: open each one
and check the intentional-state registry. The summary gives hits per id and files scanned; a zero
counts only with files scanned > 0 and no file skipped for that id. Binary or unreadable files are
skipped for every id, and files over 2 MB for multi-line and absent patterns (line patterns stream
them); each prints as "SKIPPED <reason> <path>", makes the affected ids NOT-CHECKED and sets exit
code 1. --exclude takes globs matched against each path component below the given root (and each
component of a file argument); excluded files are counted, not skipped. An unknown --only id exits 2.
Files that are not valid UTF-8 are listed under GP-11 and scanned as Latin-1 for the other patterns.
Standard library only (Python regex syntax).
"""
import argparse
import fnmatch
import os
import pathlib
import re
import shutil
import sys
import tempfile

PACK = pathlib.Path(__file__).resolve().parent.parent / "references" / "grep-pack.tsv"
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build", ".next",
             ".mypy_cache", ".pytest_cache", ".ruff_cache"}
LARGE = 2_000_000


def load():
    pats = []
    for n, line in enumerate(PACK.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) != 5 or parts[1] not in ("line", "multi", "absent"):
            raise SystemExit(f"grep-pack.tsv:{n}: expected id, kind, glob, sample, regex (tab-separated)")
        gid, kind, glob, sample, pat = parts
        pats.append({"id": gid, "kind": kind, "glob": glob, "sample": sample.replace("\\n", "\n"),
                     "re": re.compile(pat, re.M), "row": n})
    return pats


def select(pats, only):
    """Return (patterns kept, unknown ids) for a comma-separated --only value."""
    if not only:
        return pats, set()
    want = {x.strip() for x in only.split(",") if x.strip()}
    return [p for p in pats if p["id"] in want], want - {p["id"] for p in pats}


def excluded(parts, exclude):
    return any(fnmatch.fnmatch(part, e) for part in parts for e in exclude)


def walk(paths, exclude):
    """Yield (path, is_excluded) for every file under the given paths."""
    for root in paths:
        root = pathlib.Path(root)
        if root.is_file():
            yield root, excluded(root.parts, exclude)
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = sorted(x for x in dirnames if x not in SKIP_DIRS)
            for fn in sorted(filenames):
                fp = pathlib.Path(dirpath) / fn
                yield fp, excluded(fp.relative_to(root).parts, exclude)


def classify(fp):
    try:
        size = fp.stat().st_size
        with fp.open("rb") as fh:
            head = fh.read(8192)
    except OSError:
        return "unreadable"
    if b"\0" in head:
        return "binary"
    return "large" if size > LARGE else "text"


def decode(raw):
    try:
        return raw.decode("utf-8"), True
    except UnicodeDecodeError:
        return raw.decode("latin-1"), False


def scan(paths, exclude, pats, out=print):
    """Scan files; return (hits per id, files scanned, skipped per id, skipped rows, excluded count)."""
    hits = {p["id"]: 0 for p in pats}
    skipped_by_id = {p["id"]: 0 for p in pats}
    skipped, n_excluded, scanned = [], 0, 0
    for fp, is_excluded in walk(paths, exclude):
        if is_excluded:
            n_excluded += 1
            continue
        kind = classify(fp)
        applicable = [p for p in pats if fnmatch.fnmatch(fp.name, p["glob"])]
        if kind in ("binary", "unreadable"):
            skipped.append((kind, fp))
            for gid in {p["id"] for p in applicable}:
                skipped_by_id[gid] += 1
            out(f"SKIPPED {kind} {fp}")
            continue
        scanned += 1
        if kind == "large":
            whole = [p for p in applicable if p["kind"] != "line"]
            if whole:
                skipped.append(("large", fp))
                for gid in {p["id"] for p in whole}:
                    skipped_by_id[gid] += 1
                out(f"SKIPPED large {fp} (over 2 MB: multi-line and absent patterns not run; line patterns streamed)")
            utf8_all = True
            with fp.open("rb") as fh:
                for ln, raw in enumerate(fh, 1):
                    line, utf8 = decode(raw)
                    utf8_all = utf8_all and utf8
                    for p in applicable:
                        if p["kind"] == "line" and p["re"].search(line):
                            hits[p["id"]] += 1
                            out(f"{p['id']} {fp}:{ln}: {line.strip()[:200]}")
            if not utf8_all and "GP-11" in hits:
                hits["GP-11"] += 1
                out(f"GP-11 {fp}: not valid UTF-8")
            continue
        text, utf8 = decode(fp.read_bytes())
        lines = text.splitlines()
        if not utf8 and "GP-11" in hits:
            hits["GP-11"] += 1
            out(f"GP-11 {fp}: not valid UTF-8")
        for p in applicable:
            if p["kind"] == "absent":
                if not p["re"].search(text):
                    hits[p["id"]] += 1
                    out(f"{p['id']} {fp}: lacks /{p['re'].pattern}/")
            elif p["kind"] == "multi":
                for m in p["re"].finditer(text):
                    ln = text.count("\n", 0, m.start()) + 1
                    hits[p["id"]] += 1
                    out(f"{p['id']} {fp}:{ln}: {lines[ln - 1].strip()[:200]}")
            else:
                for ln, line in enumerate(lines, 1):
                    if p["re"].search(line):
                        hits[p["id"]] += 1
                        out(f"{p['id']} {fp}:{ln}: {line.strip()[:200]}")
    return hits, scanned, skipped_by_id, skipped, n_excluded


def selftest(pats, failed):
    """Pattern samples, then the scan controls: large-file streaming, binary skip, component exclude, unknown id."""
    problems = [f"{p['id']} misses its sample" for p in failed]
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="grep-pack-selftest-"))
    try:
        (tmp / "latest").mkdir()
        (tmp / "latest" / "keep.py").write_text('x = row.get("qty", 0)\n', encoding="utf-8")
        (tmp / "test_x.py").write_text('x = row.get("qty", 0)\n', encoding="utf-8")
        (tmp / "blob.bin").write_bytes(b"\0\1\2" * 100)
        with (tmp / "big.txt").open("w", encoding="utf-8") as fh:
            fh.write("ok\n" * (LARGE // 3 + 10))
            fh.write('label = "Stra\\U+00DFe"\n')
        hits, scanned, skipped_by_id, skipped, n_excluded = scan([tmp], ["test*"], pats, out=lambda _m: None)
        checks = [
            (n_excluded == 1, "--exclude 'test*' must drop test_x.py only"),
            (hits.get("GP-1", 0) == 1, "latest/keep.py must be scanned (substring exclude would drop it)"),
            (hits.get("GP-11", 0) >= 1, "a hit in a file over 2 MB must be found by streaming"),
            (("binary", tmp / "blob.bin") in skipped, "a binary file must be reported as skipped"),
            (all(skipped_by_id[g] > 0 for g in skipped_by_id), "every id must be NOT-CHECKED after a skip"),
            (scanned == 2, f"expected 2 files scanned, got {scanned}"),
            (select(pats, "GP-1,GP-99")[1] == {"GP-99"}, "an unknown --only id must be reported"),
        ]
        problems += [msg for ok, msg in checks if not ok]
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    n_ok = len(pats) - len(failed)
    if problems:
        print("selftest: FAIL " + "; ".join(problems))
        return 1
    print(f"selftest: PASS ({n_ok} of {len(pats)} patterns match their samples; scan controls: large-file "
          "streaming, binary skip, component exclude, unknown id)")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--only", default="", help="comma-separated GP ids")
    ap.add_argument("--exclude", default="", help="comma-separated globs matched against each path component")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    pats = load()
    if a.selftest:
        return selftest(pats, [p for p in pats if not p["re"].search(p["sample"])])
    pats, unknown = select(pats, a.only)
    if unknown or not pats:
        print(f"unknown GP ids: {sorted(unknown)}")
        return 2
    failed = [p for p in pats if not p["re"].search(p["sample"])]
    for p in failed:
        print(f"{p['id']} NOT-CHECKED: the pattern on grep-pack.tsv row {p['row']} misses its own sample")
    live = [p for p in pats if p not in failed]
    hits, scanned, skipped_by_id, skipped, n_excluded = scan(
        a.paths or ["."], [x.strip() for x in a.exclude.split(",") if x.strip()], live)
    bad_ids = {p["id"] for p in failed}
    for gid in sorted({p["id"] for p in pats}, key=lambda x: int(x.split("-")[1])):
        if gid in bad_ids:
            state = "NOT-CHECKED (control failed)"
        elif not scanned:
            state = "NOT-CHECKED (0 files scanned)"
        elif skipped_by_id.get(gid):
            state = f"NOT-CHECKED ({skipped_by_id[gid]} files skipped)"
        else:
            state = ""
        print(f"{gid}: {hits.get(gid, 0)} hits, {scanned} files scanned {state}".rstrip())
    by = {r: sum(1 for k, _ in skipped if k == r) for r in ("large", "binary", "unreadable")}
    print(f"skipped: {by['large']} over 2 MB, {by['binary']} binary, {by['unreadable']} unreadable; "
          f"excluded: {n_excluded} files")
    return 1 if failed or not scanned or skipped else 0


if __name__ == "__main__":
    sys.exit(main())
