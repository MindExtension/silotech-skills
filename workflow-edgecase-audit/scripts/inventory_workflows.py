#!/usr/bin/env python3
"""Inventory likely workflow entry points and risky transition vocabulary.

This is a deterministic discovery helper, not a vulnerability scanner. It reads
text files only, skips common generated directories, and prints paths plus line
numbers for manual audit routing.
"""

from __future__ import annotations

import argparse
from fnmatch import fnmatch
import json
from pathlib import Path
import re
import sys


SKIP_DIRS = {
    ".git", ".next", ".nuxt", ".output", ".turbo", ".venv", "build",
    "coverage", "dist", "node_modules", "target", "vendor",
}
TEXT_SUFFIXES = {
    ".cjs", ".go", ".graphql", ".js", ".jsx", ".json", ".md", ".mjs",
    ".py", ".rb", ".rs", ".sh", ".sql", ".swift", ".toml", ".ts",
    ".tsx", ".vue", ".yaml", ".yml",
}
SPECIAL_FILES = {"dockerfile", "procfile"}
MAX_FILE_BYTES = 5 * 1024 * 1024
ENTRY_PATH = re.compile(
    r"(?:^|/)(?:api|routes?|controllers?|handlers?|jobs?|cron|queues?|workers?|"
    r"migrations?|webhooks?|functions?|commands?|pages?|screens?|workflows?)(?:/|$)",
    re.IGNORECASE,
)
RISK_PATTERNS = {
    "auth": re.compile(r"\b(auth|authorize|permission|owner|tenant|session|token|rls)\b", re.I),
    "billing": re.compile(r"\b(payment|billing|checkout|processor|discount|refund|invoice)\b", re.I),
    "async": re.compile(r"\b(retry|timeout|queue|worker|lease|heartbeat|webhook|cron|job)\b", re.I),
    "state": re.compile(r"\b(status|state|pending|processing|failed|completed|expired|revoked)\b", re.I),
    "side_effect": re.compile(r"\b(email|notify|upload|download|storage|generate|deploy|publish)\b", re.I),
    "concurrency": re.compile(r"\b(idempoten|transaction|upsert|lock|unique|concurr|race)\w*\b", re.I),
}


def iter_files(root: Path, includes: list[str], excludes: list[str]):
    for path in root.rglob("*"):
        if path.is_symlink() or not path.is_file():
            continue
        try:
            rel = path.relative_to(root)
            path.resolve().relative_to(root)
        except (OSError, ValueError):
            continue
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        rel_text = rel.as_posix()
        if includes and not any(fnmatch(rel_text, pattern) for pattern in includes):
            continue
        if any(fnmatch(rel_text, pattern) for pattern in excludes):
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name.lower() not in SPECIAL_FILES:
            continue
        yield path


def is_test_path(rel: str) -> bool:
    path = Path(rel)
    parts = {part.lower() for part in path.parts[:-1]}
    name = path.name.lower()
    return (
        bool(parts & {"test", "tests", "__tests__"})
        or re.search(r"\.(?:test|spec)\.[^.]+$", name) is not None
        or re.match(r"test_.*\.py$", name) is not None
        or name.endswith("_test.go")
    )


def is_delivery_path(rel: str) -> bool:
    lower = rel.lower()
    name = Path(lower).name
    return (
        ".github/workflows/" in lower
        or name in SPECIAL_FILES
        or name.startswith("compose") and Path(name).suffix in {".yaml", ".yml"}
        or lower.endswith(("fly.toml", "render.yaml", "netlify.toml", "vercel.json"))
    )


def scan(
    root: Path,
    show_root: bool = False,
    includes: list[str] | None = None,
    excludes: list[str] | None = None,
    categories: set[str] | None = None,
) -> dict:
    entries: list[str] = []
    tests: list[str] = []
    workflows: list[str] = []
    skipped_large: list[str] = []

    includes = includes or []
    excludes = excludes or []
    categories = categories or set(RISK_PATTERNS)
    signals: dict[str, list[dict[str, object]]] = {key: [] for key in sorted(categories)}

    for path in iter_files(root, includes, excludes):
        rel = path.relative_to(root).as_posix()
        lower = rel.lower()
        if ENTRY_PATH.search(rel):
            entries.append(rel)
        if is_test_path(rel):
            tests.append(rel)
        if is_delivery_path(rel):
            workflows.append(rel)

        try:
            if path.stat().st_size > MAX_FILE_BYTES:
                skipped_large.append(rel)
                continue
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        for number, line in enumerate(lines, 1):
            if len(line) > 1200:
                continue
            for category in sorted(categories):
                if RISK_PATTERNS[category].search(line):
                    signals[category].append({"path": rel, "line": number})

    summarized_signals = {}
    for category in signals:
        seen = set()
        unique = []
        for item in signals[category]:
            key = (item["path"], item["line"])
            if key not in seen:
                unique.append(item)
                seen.add(key)
        unique.sort(key=lambda item: (str(item["path"]), int(item["line"])))
        summarized_signals[category] = {
            "total": len(unique),
            "returned": min(len(unique), 200),
            "truncated": len(unique) > 200,
            "items": unique[:200],
        }

    return {
        "root": str(root) if show_root else ".",
        "entry_points": sorted(set(entries)),
        "test_files": sorted(set(tests)),
        "delivery_workflows": sorted(set(workflows)),
        "skipped_large_files": sorted(set(skipped_large)),
        "risk_signals": summarized_signals,
        "note": "Discovery seed only; every candidate requires manual workflow tracing.",
        "sharing_warning": "Paths may contain private names. Generalize and scan output before sharing.",
    }


def markdown(data: dict, summary_only: bool = False) -> str:
    out = ["# Workflow inventory", "", data["note"], data["sharing_warning"], ""]
    for title, key in (
        ("Likely entry points", "entry_points"),
        ("Tests", "test_files"),
        ("Delivery workflows", "delivery_workflows"),
    ):
        out.extend([f"## {title}", ""])
        values = data[key]
        if summary_only:
            out.append(f"- Count: {len(values)}")
        else:
            out.extend(f"- `{value}`" for value in values[:300])
        if not values:
            out.append("- None detected")
        out.append("")
    out.extend(["## Risk signals", ""])
    for category, summary in data["risk_signals"].items():
        suffix = " (truncated)" if summary["truncated"] else ""
        out.append(f"### {category}: {summary['returned']} / {summary['total']}{suffix}")
        out.append("")
        if not summary_only:
            out.extend(f"- `{item['path']}:{item['line']}`" for item in summary["items"])
        if not summary["items"]:
            out.append("- None detected")
        out.append("")
    out.extend(["## Skipped large files", ""])
    if summary_only:
        out.append(f"- Count: {len(data['skipped_large_files'])}")
    else:
        out.extend(f"- `{value}`" for value in data["skipped_large_files"])
    if not data["skipped_large_files"]:
        out.append("- None")
    out.append("")
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    parser.add_argument("--show-root", action="store_true", help="include the absolute root path in output")
    parser.add_argument("--include", action="append", default=[], metavar="GLOB")
    parser.add_argument("--exclude", action="append", default=[], metavar="GLOB")
    parser.add_argument("--signals", help="comma-separated risk categories")
    parser.add_argument("--summary", action="store_true", help="print counts without repository paths")
    args = parser.parse_args()
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    categories = set(args.signals.split(",")) if args.signals else set(RISK_PATTERNS)
    unknown = categories - set(RISK_PATTERNS)
    if unknown:
        print(f"unknown signal categories: {', '.join(sorted(unknown))}", file=sys.stderr)
        return 2
    data = scan(root, args.show_root, args.include, args.exclude, categories)
    if args.summary:
        if args.format == "json":
            data = {
                "root": data["root"],
                "entry_points": len(data["entry_points"]),
                "test_files": len(data["test_files"]),
                "delivery_workflows": len(data["delivery_workflows"]),
                "skipped_large_files": len(data["skipped_large_files"]),
                "risk_signals": {
                    key: {k: value[k] for k in ("total", "returned", "truncated")}
                    for key, value in data["risk_signals"].items()
                },
                "note": data["note"],
                "sharing_warning": data["sharing_warning"],
            }
        else:
            print(markdown(data, summary_only=True))
            return 0
    print(json.dumps(data, indent=2) if args.format == "json" else markdown(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
