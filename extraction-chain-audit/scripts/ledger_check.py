#!/usr/bin/env python3
"""Validate extraction-chain-audit ledgers and compute the stop-rule numbers.

Usage (<skill-dir> is the folder that holds SKILL.md):
  python3 <skill-dir>/scripts/ledger_check.py --selftest
  python3 <skill-dir>/scripts/ledger_check.py <dir> --mode audit|build|incident|quick|design|preflight
                                              [--k 2] [--require-stop] [--expensive-run]
  python3 <skill-dir>/scripts/ledger_check.py <dir> --digest    print instance_id and the seal digests
  python3 <skill-dir>/scripts/ledger_check.py <dir> --plant N   draw 3-5 seeds at random for the planter context

Run --selftest first. Without its PASS line, do not use this script's verdict: check the ledgers
by hand against references/templates.md.

Reads the files listed in references/templates.md section 0. A required file that is missing for the
mode is a violation; a missing optional file is NOT-CHECKED, never passing. Empty input is not a
pass: 0 seams in scope, missing preflight items, an INCIDENT without its finding, or an AUDIT with 0
guards and no NOT-CHECKED record are violations. Checks: fields and enums, tri-state results, the
severity scale, roots, instance identity (instance_id), guard verdicts and effectiveness, the HAZOP
grid with prune reasons, measured detection, run economics and first-error class recurrence (ST-06),
preflight items, the shift-left rule,
incident completeness, FM/ST coverage, seal and planting digests and the stop rule (audit), and
plausible-only findings (design).

Exit codes: 0 no violations; 1 violations; 2 usage error; 3 stop rule not met with --require-stop.
Standard library only.
"""
import argparse
import contextlib
import datetime
import hashlib
import io
import json
import pathlib
import random
import re
import shutil
import sys
import tempfile

FM_IDS = [f"FM-{i:02d}" for i in range(1, 32)]
ST_IDS = [f"ST-{i:02d}" for i in range(1, 16)]
UNIVERSAL = {"FM-04", "FM-05", "FM-15", "FM-23", "ST-03", "ST-07"}  # references/selection.md section 1
FM_NEW = re.compile(r"^FM-NEW-\d+$")
ROOTS = {"collection", "structure", "logic", "operations", "process"}
ESCAPES = {"absent", "vacuous", "narrow_scope", "warn_only", "wrong_instance", "not_run", "late_gate", "none"}
VERDICTS = {"confirmed", "plausible", "refuted", "not_checked"}
FOUND_BY = {"A", "B", "AB", "incident", "quick"}
VERIFIED_BY = {"fresh_session", "human", "same_context"}
PLANTED_BY = {"sub_agent", "human", "script", "self"}
FIX_LOCUS = {"platform", "stage", "spot"}
GATES = [f"G{i}" for i in range(9)]
LATE = {"G5", "G6", "G7", "G8", "user"}
DETECTED = set(GATES) | {"audit", "user"}
RESULTS = {"pass", "fail", "not_checked"}
COVERAGE = {"guarded", "finding", "not_applicable", "not_checked"}
TRIGGERS = {"pre-merge", "ci", "write", "preflight", "run", "promotion", "display", "periodic"}
GUARD_VERDICTS = {"unaudited", "phantom", "vacuous", "never_passes", "narrow", "warn_only", "effective"}
GUARD_STATUS = {"proposed", "registered", "retired"}
PRIORITIES = {"must_fix", "before_release", "backlog"}
UCA = {"not_provided", "harmful", "wrong_timing", "wrong_duration"}
PRUNE = {"not_carried", "feature_absent", "matrix_blank", "prevented_by_construction", "represented_by",
         "no_credible_cause", "not_examined"}
ONE_GUIDEWORD = {"no_credible_cause", "prevented_by_construction"}
CATCHABLE = {"G1", "G2", "G3", "G4", "runtime_only"}
RUN_STATUS = {"succeeded", "failed", "cancelled"}
P_CORE = ["P1", "P2", "P3", "P4", "P6", "P7"]  # P5 may be not_applicable (first run)
P_ALL = [f"P{i}" for i in range(1, 11)]
FAMILIES = {
    "record_conservation", "quantity_conservation", "partition_coverage", "round_trip", "metamorphic",
    "monotonicity_rank", "frame_consistency", "closed_vocabulary", "provenance_completeness",
    "tri_state_presence", "lineage_homogeneity", "tenant_isolation", "consumption",
    "promotion_monotonicity", "cross_field_identity", "uniqueness_identity", "scope_declaration",
    "oracle_separation", "answer_closure", "witness_independence",
}

# HAZOP applicability matrix; must equal the table in references/hazard-sweep.md 1.3 (selftest checks).
PARAMS = ["PRES", "VAL", "UNIT", "ID", "VOC", "SCOPE", "FRAME", "PROV", "VER", "SIG"]
GUIDEWORDS = ["NO", "MORE", "LESS", "AS WELL AS", "PART OF", "OTHER THAN", "REVERSE", "EARLY", "LATE",
              "STALE", "WRONG FRAME", "WRONG SCOPE"]
_ROWS = {  # one character per parameter in PARAMS order: X always, o feature-dependent, . blank
    "NO": "XXoXoooXoX", "MORE": "XXoXoX.ooo", "LESS": "XXoooXoX.o", "AS WELL AS": "Xo.XoX.XX.",
    "PART OF": "XXXo.XoX.o", "OTHER THAN": ".XXXXooXoX", "REVERSE": ".o.oo.X..o", "EARLY": "X....o..XX",
    "LATE": "o.......XX", "STALE": ".o...o.oXX", "WRONG FRAME": ".oXo.oX...", "WRONG SCOPE": ".X.o.X.ooo",
}
MATRIX = {(g, p): ("" if c == "." else c) for g, row in _ROWS.items() for p, c in zip(PARAMS, row)}
ALL_CELLS = {(g, p) for g in GUIDEWORDS for p in PARAMS}

REQUIRED = {
    "quick": ["instance.json"],
    "preflight": ["instance.json"],
    "build": ["instance.json", "seams.jsonl", "hazards.jsonl", "invariants.jsonl", "guards.jsonl"],
    "incident": ["instance.json", "invariants.jsonl", "guards.jsonl", "findings.jsonl"],
    "design": ["instance.json", "seams.jsonl", "hazards.jsonl", "guards.jsonl", "findings.jsonl"],
    "audit": ["instance.json", "seams.jsonl", "hazards.jsonl", "invariants.jsonl", "guards.jsonl",
              "findings.jsonl", "coverage.jsonl", "rounds.jsonl", "planted.jsonl"],
}
MARKDOWN = {"quick": ["quick-scan.md"], "preflight": [], "build": ["chain-map.md", "report.md"],
            "incident": ["report.md"], "design": ["chain-map.md", "report.md"], "audit": ["chain-map.md", "report.md"]}

# Generic seeds for --plant (references/guard-the-guards.md section 4, data mutants).
SEED_MENU = [
    ("NO", "PRES", "delete one input file, page or record"),
    ("MORE", "PRES", "duplicate one record or document under a new id"),
    ("MORE", "UNIT", "scale one value by 1000"),
    ("LESS", "PRES", "truncate one long input at 60%"),
    ("LESS", "PRES", "add one header line to one tenant's tabular file"),
    ("AS WELL AS", "SCOPE", "inject one record from another tenant"),
    ("AS WELL AS", "VER", "add a superseded revision of one source"),
    ("PART OF", "UNIT", "strip the unit from one value"),
    ("PART OF", "PROV", "strip provenance from one value"),
    ("REVERSE", "FRAME", "flip the sign or direction of one value"),
    ("OTHER THAN", "VOC", "put an unseen value in one closed-vocabulary field"),
    ("OTHER THAN", "VAL", "replace one value with a plausible value from another document"),
    ("STALE", "VER", "serve the previous version of one input"),
    ("WRONG FRAME", "ID", "rewrite one identifier in another notation"),
    ("WRONG FRAME", "VAL", "re-save one text source in another codepage"),
    ("WRONG SCOPE", "SCOPE", "replace one point value with its window aggregate"),
]


def label(s):
    if not isinstance(s, int) or not 1 <= s <= 10:
        return None
    return "critical" if s >= 9 else "high" if s >= 7 else "medium" if s >= 4 else "low"


class Report:
    def __init__(self):
        self.violations, self.notes = [], []

    def bad(self, where, msg):
        self.violations.append(f"{where}: {msg}")

    def note(self, msg):
        self.notes.append(msg)


def load_jsonl(d, name, rep, required):
    path = d / name
    if not path.exists():
        if required:
            rep.bad(name, "missing: required for this mode")
        else:
            rep.note(f"NOT-CHECKED {name}: file missing")
        return None
    rows = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            rows.append((f"{name}:{n}", json.loads(line)))
        except json.JSONDecodeError as exc:
            rep.bad(f"{name}:{n}", f"invalid JSON ({exc.msg})")
    return rows


def need(rep, where, row, fields):
    for f in fields:
        if row.get(f) in (None, "", []):
            rep.bad(where, f"missing {f}")


def check_severity(rep, where, row):
    s, lab = row.get("S"), row.get("severity")
    if label(s) is None:
        rep.bad(where, f"S {s!r} is not an integer 1-10")
    elif lab != label(s):
        rep.bad(where, f"severity {lab!r} does not match S={s} (expected {label(s)!r})")


def as_list(v, universe):
    if v == "*":
        return list(universe)
    return v if isinstance(v, list) else [v]


def digest(rows):
    blob = json.dumps(sorted(rows), ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def instance_id(inst):
    core = {k: inst.get(k) for k in ("code_rev", "env", "data_versions")}
    return hashlib.sha256(json.dumps(core, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()[:12]


def path_a_digest(findings):
    """Round-1 path-A rows (found_by A or AB): id and title must not change after sealing."""
    return digest([[str(f.get("id") or ""), str(f.get("title") or "")] for _, f in findings
                   if f.get("found_by") in ("A", "AB") and f.get("round") == 1])


def planted_digest(planted):
    return digest([[str(p.get("id") or ""), str(p.get("seed") or ""), str(p.get("location") or "")]
                   for _, p in planted])


def parse_ts(s):
    try:
        t = datetime.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        return None
    return t if t.tzinfo else t.replace(tzinfo=datetime.timezone.utc)


def same_instance(rep, where, value, iid):
    if iid is None:
        return
    if not value:
        rep.bad(where, "missing instance_id")
    elif value != iid:
        rep.bad(where, f"wrong_instance: instance_id {value} is not the pinned {iid}")


def load_instance(d, rep):
    p = d / "instance.json"
    if not p.exists():
        rep.bad("instance.json", "missing: no claim can name its instance")
        return None
    try:
        inst = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        rep.bad("instance.json", "invalid JSON")
        return None
    need(rep, "instance.json", inst, ["code_rev", "env", "data_versions"])
    iid = instance_id(inst)
    rep.note(f"instance_id={iid}")
    return iid


def effective_problems(g, iid):
    """Return the effective-guard criteria this row fails (empty list = mechanically effective)."""
    sf, lr, base = g.get("seeded_fault") or {}, g.get("last_run") or {}, g.get("baseline") or {}
    probs = []
    if not g.get("runner"):
        probs.append("no runner")
    if sf.get("killed") is not True:
        probs.append("seeded fault not killed")
    if not (lr.get("executed_count") or 0) > 0:
        probs.append("last executed_count is 0")
    if iid and lr.get("instance_id") != iid:
        probs.append("last run not on the pinned instance")
    if g.get("mode") != "block":
        if (g.get("S") or 0) >= 7:
            probs.append("warn-only on S >= 7")
        elif not (g.get("owner") and g.get("expires") and g.get("ceiling") is not None):
            probs.append("warn guard without owner, ceiling and expiry")
    if base.get("source") not in (None, "none") and base.get("can_be_empty") is not False:
        probs.append("baseline may be empty")
    return probs


def check_guards(d, mode, rep, iid):
    rows = load_jsonl(d, "guards.jsonl", rep, "guards.jsonl" in REQUIRED[mode]) or []
    guards = {}
    for where, g in rows:
        need(rep, where, g, ["id", "protects", "gate", "trigger", "mode", "scope", "blind_spots", "status", "verdict"])
        check_severity(rep, where, g)
        if g.get("gate") not in GATES:
            rep.bad(where, f"gate {g.get('gate')!r} not in G0..G8")
        if g.get("trigger") not in TRIGGERS:
            rep.bad(where, f"trigger {g.get('trigger')!r} invalid")
        if g.get("mode") not in ("block", "warn"):
            rep.bad(where, f"mode {g.get('mode')!r} invalid")
        if g.get("status") not in GUARD_STATUS:
            rep.bad(where, f"status {g.get('status')!r} invalid")
        v, pv = g.get("verdict"), g.get("predicted_verdict")
        if v not in GUARD_VERDICTS:
            rep.bad(where, f"verdict {v!r} invalid")
        if pv is not None and pv not in GUARD_VERDICTS:
            rep.bad(where, f"predicted_verdict {pv!r} invalid")
        if mode == "design" and (v != "unaudited" or pv is None):
            rep.bad(where, "DESIGN REVIEW: verdict stays unaudited, with a predicted_verdict and its reason")
        probs = effective_problems(g, iid)
        if v == "effective" and probs:
            rep.bad(where, f"verdict effective contradicts the registry fields: {', '.join(probs)}")
        if not g.get("runner") and v not in ("phantom", "unaudited"):
            rep.bad(where, f"no runner but verdict {v!r}: a guard without a runner is phantom (FM-23)")
        if (v and v not in ("effective", "unaudited") or pv) and not g.get("verdict_reason"):
            rep.bad(where, f"verdict {pv or v} without verdict_reason")
        guards[g.get("id")] = g
    eff = {gid for gid, g in guards.items() if g.get("verdict") == "effective" and not effective_problems(g, iid)}
    if guards:
        by = {}
        for g in guards.values():
            by[g.get("verdict")] = by.get(g.get("verdict"), 0) + 1
        rep.note(f"guards: {len(eff)} effective of {len(guards)}; by verdict {dict(sorted(by.items(), key=str))}")
    return guards, eff


def check_findings(d, mode, rep, planted_ids, guards, iid, a_sealed):
    rows = load_jsonl(d, "findings.jsonl", rep, "findings.jsonl" in REQUIRED[mode]) or []
    ids = {f.get("id") for _, f in rows}
    for where, f in rows:
        need(rep, where, f, ["id", "title", "cause_root", "escape_root", "instance_id", "verdict", "found_by"])
        if not (f.get("found_by") == "A" and not a_sealed) and not (f.get("fm") or f.get("st")):
            rep.bad(where, "missing fm and st: name at least one mode id (path A rows may wait until sealing)")
        check_severity(rep, where, f)
        for key, allowed in (("cause_root", ROOTS), ("escape_root", ESCAPES), ("verdict", VERDICTS),
                             ("found_by", FOUND_BY)):
            if f.get(key) not in allowed:
                rep.bad(where, f"{key} {f.get(key)!r} invalid")
        if f.get("fix_locus") is not None and f.get("fix_locus") not in FIX_LOCUS:
            rep.bad(where, f"fix_locus {f.get('fix_locus')!r} invalid")
        if f.get("detected_gate") is not None and f.get("detected_gate") not in DETECTED:
            rep.bad(where, f"detected_gate {f.get('detected_gate')!r} invalid")
        for x in f.get("fm") or []:
            if x not in FM_IDS and not FM_NEW.match(str(x)):
                rep.bad(where, f"unknown mode id {x!r}")
        for x in f.get("st") or []:
            if x not in ST_IDS:
                rep.bad(where, f"unknown stall id {x!r}")
        same_instance(rep, where, f.get("instance_id"), iid)
        if mode == "audit" and not (isinstance(f.get("round"), int) and f.get("round") >= 1):
            rep.bad(where, "missing integer round >= 1: a dry round is never assumed")
        if f.get("planted") and planted_ids is not None and f.get("planted") not in planted_ids:
            rep.bad(where, f"planted {f.get('planted')!r} not in planted.jsonl")
        if f.get("planted") and not f.get("copy"):
            rep.bad(where, "planted-defect finding without copy (the scratch copy it reproduces on)")
        for gid in f.get("guards") or []:
            if gid not in guards:
                rep.bad(where, f"guard {gid!r} not in guards.jsonl")
        v = f.get("verdict")
        if mode == "design" and v == "confirmed":
            rep.bad(where, "DESIGN REVIEW findings are plausible at most: there is no instance to reproduce on")
        if v == "confirmed":
            if not (f.get("evidence") or {}).get("repro"):
                rep.bad(where, "confirmed without a reproduction")
            if f.get("found_by") != "quick":
                if not f.get("class_predicate"):
                    rep.bad(where, "confirmed without a class predicate")
                if f.get("intentional_state_checked") is not True:
                    rep.bad(where, "confirmed before checking the intentional-state registry")
            if f.get("cause_root") in ("collection", "structure") and f.get("fix_locus") != "platform":
                rep.bad(where, "collection/structure root must be fixed platform-wide (fix_locus platform)")
            if f.get("detected_gate") in LATE and not (f.get("cause_root") == "process" and f.get("escape_root") == "late_gate"):
                linked = any(g.get("cause_root") == "process" and g.get("escape_root") == "late_gate"
                             and f.get("id") in (g.get("related") or []) for _, g in rows)
                if not linked:
                    rep.bad(where, f"shift-left rule: caught at {f.get('detected_gate')} but no Process finding with escape_root late_gate lists it in related")
            if f.get("found_by") == "incident":
                sig = f.get("signature") or {}
                if not all(sig.get(k) for k in ("seam_type", "parameter", "guideword", "carrier")):
                    rep.bad(where, "incident finding without a full class signature (seam_type, parameter, guideword, carrier)")
                if not isinstance(f.get("siblings"), int):
                    rep.bad(where, "incident finding without an integer siblings count")
                elif f.get("siblings") == 0 and not f.get("positive_control"):
                    rep.bad(where, "zero siblings without a positive_control")
                if (f.get("earliest_detector") or {}).get("gate") not in GATES:
                    rep.bad(where, "incident finding without earliest_detector.gate")
            if mode == "audit" and not f.get("planted"):
                ver = f.get("verification") or {}
                if ver.get("by") not in VERIFIED_BY:
                    rep.bad(where, "confirmed without verification.by (fresh_session | human | same_context)")
                elif ver.get("by") == "same_context" or ver.get("saw_candidate") is not False:
                    rep.bad(where, "confirmed by a same_context verifier or one that saw the candidate: cap at plausible (solo protocol)")
        elif v in ("refuted", "not_checked", "plausible") and not f.get("verdict_reason"):
            rep.bad(where, f"{v} without verdict_reason")
        for r in f.get("related") or []:
            if r not in ids:
                rep.bad(where, f"related id {r!r} not in findings")
        if f.get("duplicate_of") and f.get("duplicate_of") not in ids:
            rep.bad(where, f"duplicate_of {f.get('duplicate_of')!r} not in findings")
    if mode == "quick" and len(rows) > 3:
        rep.bad("findings.jsonl", f"QUICK SCAN reports at most 3 findings, found {len(rows)}")
    if mode == "incident" and not any(f.get("found_by") == "incident" for _, f in rows):
        rep.bad("findings.jsonl", "no finding with found_by incident: the incident itself is not recorded")
    return rows


def check_invariants(d, mode, rep, guards, iid):
    for where, v in load_jsonl(d, "invariants.jsonl", rep, "invariants.jsonl" in REQUIRED[mode]) or []:
        need(rep, where, v, ["id", "family", "statement", "gate", "result"])
        if v.get("family") not in FAMILIES:
            rep.bad(where, f"family {v.get('family')!r} invalid")
        if v.get("gate") not in GATES:
            rep.bad(where, f"gate {v.get('gate')!r} not in G0..G8")
        if v.get("result") not in RESULTS:
            rep.bad(where, f"result {v.get('result')!r} not tri-state")
        if v.get("result") == "pass" and not (v.get("executed_count") or 0) > 0:
            rep.bad(where, "pass with executed_count 0: empty is not a measurement")
        if v.get("result") in ("fail", "not_checked") and not v.get("reason"):
            rep.bad(where, f"{v.get('result')} without reason")
        if v.get("guard") and v.get("guard") not in guards:
            rep.bad(where, f"guard {v.get('guard')} not in registry")
        same_instance(rep, where, v.get("instance_id"), iid)


def hazop_grid(d, mode, rep, eff):
    """Seams and the HAZOP cells covered per seam. represented_by rows are returned for a second pass."""
    seams = {}
    for where, s in load_jsonl(d, "seams.jsonl", rep, mode in ("build", "audit", "design")) or []:
        need(rep, where, s, ["id", "type", "producer", "consumer", "intent", "carries"])
        for p in s.get("carries") or []:
            if p not in PARAMS:
                rep.bad(where, f"carries unknown parameter {p!r}")
        seams[s.get("id")] = s
    rows = load_jsonl(d, "hazards.jsonl", rep, "hazards.jsonl" in REQUIRED[mode]) or []
    covered, unexamined, deferred = {}, {}, []
    for where, h in rows:
        if h.get("source") != "hazop":
            continue
        need(rep, where, h, ["seam", "status", "parameter", "guideword"])
        seam = seams.get(h.get("seam"))
        if seams and seam is None:
            rep.bad(where, f"seam {h.get('seam')!r} not in seams.jsonl")
        params, gws = as_list(h.get("parameter"), PARAMS), as_list(h.get("guideword"), GUIDEWORDS)
        bad = [x for x in params if x not in PARAMS] + [x for x in gws if x not in GUIDEWORDS]
        if bad:
            rep.bad(where, f"unknown parameter or guideword {bad}")
        cells = [(g, p) for g in gws for p in params if g in GUIDEWORDS and p in PARAMS]
        status = h.get("status")
        if status not in ("hazard", "pruned"):
            rep.bad(where, f"status {status!r} must be hazard or pruned")
            continue
        if status == "hazard":
            covered.setdefault(h.get("seam"), set()).update(cells)
            continue
        reason, ok = h.get("prune_reason"), True
        if reason not in PRUNE:
            rep.bad(where, f"pruned without a valid prune_reason ({reason!r})")
            ok = False
        if not h.get("prune_detail"):
            rep.bad(where, "pruned without prune_detail: a pruned cell must say why")
            ok = False
        if reason in ONE_GUIDEWORD:
            if h.get("guideword") == "*" or len(gws) != 1:
                rep.bad(where, f"{reason} takes exactly one guideword per row: each guideword is its own question")
                ok = False
            if not (isinstance(h.get("examined"), list) and h.get("examined")):
                rep.bad(where, f"{reason} without an examined list (code paths, contract fields, record ids)")
                ok = False
        if reason == "prevented_by_construction" and h.get("guard") not in eff:
            rep.bad(where, f"prevented_by_construction needs an effective guard that proves it (guard {h.get('guard')!r})")
            ok = False
        if reason == "represented_by":
            deferred.append((where, h, cells))
            continue
        carries = (seam or {}).get("carries") or []
        misfit = []
        for g, p in cells:
            if reason == "feature_absent" and MATRIX[(g, p)] != "o":
                misfit.append(f"{g}/{p}")
            if reason == "matrix_blank" and MATRIX[(g, p)] != "":
                misfit.append(f"{g}/{p}")
            if reason == "not_carried" and p in carries:
                misfit.append(f"{g}/{p}")
        if misfit:
            rep.bad(where, f"prune_reason {reason} does not fit {len(misfit)} cells, e.g. {misfit[:3]}")
            ok = False
        if ok:
            covered.setdefault(h.get("seam"), set()).update(cells)
            if reason == "not_examined":
                unexamined.setdefault(h.get("seam"), set()).update(cells)
    return seams, rows, covered, unexamined, deferred


def resolve_representative(d, ref, seams, covered):
    """Return (seam row, covered cells) for 'SM-x' in this ledger or 'SM-x@<dir>' in a prior ledger."""
    if "@" not in str(ref):
        return seams.get(ref), covered.get(ref, set())
    sid, other = str(ref).split("@", 1)
    od = pathlib.Path(other) if pathlib.Path(other).is_absolute() else d / other
    if not od.is_dir():
        return None, set()
    scratch = Report()
    _, eff2 = check_guards(od, "audit", scratch, None)
    seams2, _, cov2, _, _ = hazop_grid(od, "audit", scratch, eff2)
    return seams2.get(sid), cov2.get(sid, set())


def check_hazards(d, mode, rep, eff, guards):
    seams, rows, covered, unexamined, deferred = hazop_grid(d, mode, rep, eff)
    direct = {k: set(v) for k, v in covered.items()}
    for where, h, cells in deferred:
        ref = h.get("represented_by")
        rep_seam, rep_cells = resolve_representative(d, ref, seams, direct)
        own = seams.get(h.get("seam")) or {}
        if rep_seam is None:
            rep.bad(where, f"represented_by {ref!r} names no existing seam")
        elif rep_seam.get("type") != own.get("type"):
            rep.bad(where, f"represented_by {ref!r} has type {rep_seam.get('type')!r}, not {own.get('type')!r}")
        elif rep_cells != ALL_CELLS:
            rep.bad(where, f"represented_by {ref!r}: the representative's own grid is not fully covered ({len(rep_cells)} of {len(ALL_CELLS)})")
        else:
            covered.setdefault(h.get("seam"), set()).update(cells)
    for where, h in rows:
        need(rep, where, h, ["id", "source"])
        if h.get("source") == "hazop" and h.get("status") != "hazard":
            continue
        if h.get("source") == "stpa":
            need(rep, where, h, ["control_action"])
            if h.get("uca_type") not in UCA:
                rep.bad(where, f"uca_type {h.get('uca_type')!r} invalid")
        need(rep, where, h, ["consequence", "O", "D", "priority"])
        check_severity(rep, where, h)
        if h.get("priority") not in PRIORITIES:
            rep.bad(where, f"priority {h.get('priority')!r} invalid")
        s, dd = h.get("S") or 0, h.get("D")
        for sg in h.get("safeguards") or []:
            if sg not in eff:
                rep.bad(where, f"safeguard {sg} is not an effective guard; list it as none")
        gates = [int(str(guards[g].get("gate"))[1:]) for g in h.get("safeguards") or []
                 if g in eff and str(guards[g].get("gate")) in GATES]
        ev = str(h.get("detection_evidence") or "")
        if not isinstance(dd, int) or not 1 <= dd <= 10:
            rep.bad(where, f"D {dd!r} is not an integer 1-10")
        elif dd <= 3 and not any(x <= 3 for x in gates):
            rep.bad(where, "D 1-3 needs an effective safeguard at G0-G3 that killed its seed (measured, not believed)")
        elif 4 <= dd <= 6 and not any(x <= 6 for x in gates):
            rep.bad(where, "D 4-6 needs an effective safeguard at G0-G6")
        elif dd in (7, 8) and not gates and not re.search(r"(?i)\b(human|review|G8)\b", ev):
            rep.bad(where, "D 7-8 needs detection_evidence naming a human review or G8 step; otherwise D >= 9")
        dd = dd if isinstance(dd, int) else 10
        if s >= 7 and dd >= 7 and h.get("priority") != "must_fix":
            rep.bad(where, "S >= 7 and D >= 7 must be must_fix")
        if s >= 7 and h.get("priority") == "backlog":
            rep.bad(where, "S >= 7 cannot be backlog")
    in_scope = [sid for sid, s in seams.items() if mode != "build" or s.get("changed") is True]
    if mode in ("build", "audit", "design") and not in_scope:
        rep.bad("seams.jsonl", "0 seams in scope: HAZOP grid not executed (executed_count 0)"
                + ("; mark the changed seams with changed: true" if mode == "build" else ""))
    for sid in in_scope:
        gap = [f"{g}/{p}" for g in GUIDEWORDS for p in PARAMS if (g, p) not in covered.get(sid, set())]
        if gap:
            rep.bad(f"hazards.jsonl[{sid}]", f"{len(gap)} of {len(ALL_CELLS)} cells neither swept nor pruned, e.g. {gap[:4]}")
    n_unexamined = sum(len(unexamined.get(sid, ())) for sid in in_scope)
    if in_scope:
        rep.note(f"HAZOP grid: {len(in_scope)} seams in scope, {len(ALL_CELLS)} cells each; "
                 f"{n_unexamined} cells not_examined (NOT-CHECKED, never swept)")
    return n_unexamined


def check_runs(d, mode, rep, findings):
    rows = load_jsonl(d, "runs.jsonl", rep, False)
    if rows is None:
        return set()
    has_st02 = any("ST-02" in (f.get("st") or []) for _, f in findings)
    has_st06 = any("ST-06" in (f.get("st") or []) for _, f in findings)
    seen, p_items, all_min, fail_min, catch_min, n_fail = set(), set(), 0.0, 0.0, 0.0, 0
    n_unknown, class_count = 0, {}
    for where, r in rows:
        need(rep, where, r, ["run_id", "status"])
        if r.get("status") not in RUN_STATUS:
            rep.bad(where, f"status {r.get('status')!r} invalid")
        if r.get("minutes") is None:
            n_unknown += 1
        minutes = float(r.get("minutes") or 0)
        all_min += minutes
        if r.get("status") != "failed":
            continue
        n_fail += 1
        fail_min += minutes
        fp, cat = r.get("fingerprint"), r.get("catchable")
        if not fp:
            rep.bad(where, "failed run without fingerprint")
        if cat not in CATCHABLE:
            rep.bad(where, f"failed run: catchable {cat!r} must be one of G1..G4 or runtime_only")
        elif cat != "runtime_only":
            catch_min += minutes
            if not r.get("catching_check"):
                rep.bad(where, "catchable run without catching_check")
            if not r.get("p_item"):
                rep.bad(where, "catchable fingerprint without a proposed P-item (p_item)")
            elif cat == "G4":
                p_items.add(str(r.get("p_item")))
        if fp and fp in seen:
            change = r.get("change_since_last_same_fingerprint")
            if change is None:
                rep.bad(where, f"repeated fingerprint {fp} without change_since_last_same_fingerprint")
            elif change is False and not has_st02:
                rep.bad(where, f"fingerprint {fp} repeated with no change: needs an ST-02 finding")
        if fp:
            seen.add(fp)
        fe = r.get("first_error") if isinstance(r.get("first_error"), dict) else {}
        cls = (fe.get("node"), fe.get("error_class"))
        if all(cls):
            class_count[cls] = class_count.get(cls, 0) + 1
        else:
            rep.bad(where, "failed run without first_error.node and first_error.error_class (class recurrence)")
    for cls, n in class_count.items():
        if n >= 3 and not has_st06:
            rep.bad("runs.jsonl", f"class {cls[0]}|{cls[1]} failed in {n} runs: needs an ST-06 finding and INCIDENT on the class")
    if rows and n_unknown:
        rep.note(f"run economics: failed {n_fail} of {len(rows)} runs; compute shares NOT-CHECKED "
                 f"({n_unknown} runs without minutes)")
    elif rows:
        share = (100 * catch_min / fail_min) if fail_min else 0.0
        rep.note(f"run economics: failed {n_fail} of {len(rows)} runs; failed compute "
                 f"{(100 * fail_min / all_min) if all_min else 0:.0f}% of all; catchable at G1-G4 {share:.0f}% of failed compute")
    return p_items


def check_preflight(d, rep, required, iid, p_items):
    p = d / "preflight.json"
    if not p.exists():
        if required:
            rep.bad("preflight.json", "missing: required before an expensive run")
        else:
            rep.note("NOT-CHECKED preflight.json: file missing")
        return
    try:
        pf = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        rep.bad("preflight.json", "invalid JSON")
        return
    same_instance(rep, "preflight.json", pf.get("instance_id"), iid)
    items = {str(it.get("id")): it for it in pf.get("items") or []}
    blocking = [f"{i} (missing: NOT-CHECKED)" for i in P_ALL + sorted(p_items) if i not in items]
    for iid_, it in items.items():
        res = it.get("result")
        if res not in RESULTS | {"not_applicable"}:
            rep.bad("preflight.json", f"{iid_} result {res!r} not tri-state or not_applicable")
            continue
        if res == "not_applicable":
            if iid_ in P_CORE or "+" in iid_:
                rep.bad("preflight.json", f"{iid_} cannot be not_applicable: P1-P4, P6, P7 and fingerprint items always apply")
            elif not it.get("reason"):
                rep.bad("preflight.json", f"{iid_} not_applicable without reason (cite the chain-map feature answer)")
            continue
        if res == "pass" and not (it.get("executed_count") or 0) > 0:
            rep.bad("preflight.json", f"{iid_} pass with executed_count 0")
        if res != "pass":
            blocking.append(iid_)
    if pf.get("verdict") not in ("go", "no_go"):
        rep.bad("preflight.json", f"verdict {pf.get('verdict')!r} must be go or no_go")
    if pf.get("verdict") == "go" and blocking:
        rep.bad("preflight.json", f"verdict go with items not pass: {blocking}")
    if required and pf.get("verdict") != "go":
        rep.bad("preflight.json", "verdict is not go: the expensive run stays blocked")


def check_coverage(d, rep, eff, guards, fmap):
    rows = load_jsonl(d, "coverage.jsonl", rep, True)
    seen = {}
    for where, c in rows or []:
        cid, st = c.get("id"), c.get("status")
        seen[cid] = c
        if st not in COVERAGE:
            rep.bad(where, f"status {st!r} invalid")
        if st == "not_applicable" and cid in UNIVERSAL:
            rep.bad(where, f"{cid} is universal (selection.md section 1): never not_applicable")
        if st == "guarded":
            if str(cid).startswith("ST-"):
                if not c.get("evidence"):
                    rep.bad(where, f"{cid} guarded needs evidence that its ST Check line passed")
            elif not [g for g in c.get("guards") or [] if g in eff and cid in (guards[g].get("protects") or [])]:
                rep.bad(where, f"{cid} guarded without an effective guard whose protects lists it")
        if st == "finding":
            hits = [x for x in c.get("findings") or [] if x in fmap
                    and cid in (fmap[x].get("fm") or []) + (fmap[x].get("st") or [])]
            if not hits:
                rep.bad(where, f"{cid} finding status without a finding whose fm or st lists it")
        if st == "not_applicable" and not c.get("feature"):
            rep.bad(where, f"{cid} not_applicable must cite the chain-map feature answer (feature)")
        if st in ("not_applicable", "not_checked") and not c.get("reason"):
            rep.bad(where, f"{cid} {st} without reason")
    missing = [i for i in FM_IDS + ST_IDS if i not in seen]
    if missing:
        rep.bad("coverage.jsonl", f"no status for {len(missing)} ids: {', '.join(missing[:8])}{' ...' if len(missing) > 8 else ''}")
    return seen, missing


def check_seals(rep, findings, rounds, planted):
    r1 = [r for _, r in rounds if r.get("round") == 1]
    for r in r1:
        if r.get("completed") and parse_ts(r.get("started_at")) is None:
            rep.bad("rounds.jsonl", f"round 1 path {r.get('path')} without a valid started_at")
        if r.get("sealed") is True and r.get("path") in ("A", "both"):
            if r.get("sealed_digest") != path_a_digest(findings):
                rep.bad("rounds.jsonl", "path A sealed_digest missing or not equal to the recomputed digest: "
                        "the path A list changed after sealing (run --digest at seal time)")
    r0 = [r for _, r in rounds if r.get("round") == 0]
    if not r0:
        rep.bad("rounds.jsonl", "no round 0 row: planted defects were not sealed before hunting")
    else:
        if r0[0].get("planted_by") not in PLANTED_BY:
            rep.bad("rounds.jsonl", f"round 0 planted_by {r0[0].get('planted_by')!r} invalid")
        if planted is not None and r0[0].get("planted_digest") != planted_digest(planted):
            rep.bad("rounds.jsonl", "planted_digest missing or not equal to the recomputed digest: planted.jsonl changed after sealing")
    starts = [t for t in (parse_ts(r.get("started_at")) for r in r1) if t]
    first = min(starts) if starts else None
    for where, p in planted or []:
        if p.get("sealed") is not True:
            rep.bad(where, "planted defect not sealed")
        t = parse_ts(p.get("planted_at"))
        if t is None:
            rep.bad(where, "missing or invalid planted_at")
        elif first and t >= first:
            rep.bad(where, "planted_at is not before round 1: planting after the hunt proves nothing")
    if planted is not None and len(planted) < 3:
        rep.bad("planted.jsonl", f"{len(planted)} planted defects: plant 3-5 before round 1")


def stop_rule(rep, findings, rounds, k, coverage_missing, planted, unexamined):
    planted_ids = {p.get("id") for _, p in planted or []}
    found_planted = {f.get("planted") for _, f in findings if f.get("verdict") == "confirmed" and f.get("planted")}
    recall = (len(found_planted & planted_ids) / len(planted_ids)) if planted_ids else None
    r1 = [r for _, r in rounds if r.get("round") == 1 and r.get("completed")]
    paths_done = {r.get("path") for r in r1}
    sealed_paths = {r.get("path") for r in r1 if r.get("sealed") is True}
    solo = "both" in paths_done
    both_done = solo or {"A", "B"} <= paths_done
    sealed = "both" in sealed_paths or {"A", "B"} <= sealed_paths
    groups = {}
    for _, f in findings:
        if f.get("verdict") != "confirmed" or (f.get("S") or 0) < 4 or f.get("planted") or f.get("duplicate_of"):
            continue
        fb = f.get("found_by") or ""
        if fb not in ("A", "B", "AB") or not isinstance(f.get("round"), int):
            continue
        key = (tuple(sorted(f.get("fm") or [])), tuple(sorted(f.get("st") or [])), f.get("cause_root"), f.get("class_predicate"))
        g = groups.setdefault(key, {"paths": set(), "first_round": 10 ** 9})
        if fb == "AB" and not sealed:
            g["paths"].add("A")
        else:
            g["paths"].update(p for p in ("A", "B") if p in fb)
        g["first_round"] = min(g["first_round"], f.get("round"))
    n1 = sum(1 for g in groups.values() if "A" in g["paths"])
    n2 = sum(1 for g in groups.values() if "B" in g["paths"])
    m = sum(1 for g in groups.values() if {"A", "B"} <= g["paths"])
    found = n1 + n2 - m
    est = (n1 + 1) * (n2 + 1) / (m + 1) - 1
    resid = est - found
    done = sorted({r.get("round") for _, r in rounds if r.get("completed") and isinstance(r.get("round"), int) and r.get("round") >= 1})
    dry = 0
    for r in reversed(done):
        if r == 1 or any(g["first_round"] == r for g in groups.values()):
            break
        dry += 1
    branch = "standard" if (m >= 3 and found >= 6 and not solo) else "low-count"
    rep.note(f"capture-recapture: n1={n1} n2={n2} m={m} sealed={sealed} Chapman N={est:.1f} found={found} "
             f"residual={resid:.1f} (lower bound{'; solo: information only' if solo else ''}); branch={branch}; "
             f"dry rounds={dry}; planted recall={'n/a' if recall is None else f'{recall:.2f} of {len(planted_ids)}'}")
    reasons = []
    if not both_done:
        reasons.append("paths A and B not both completed in round 1")
    if not sealed:
        reasons.append("round 1 paths not sealed: AB rows counted for path A only")
    if branch == "standard" and resid > max(2, 0.1 * found):
        reasons.append(f"residual {resid:.1f} > max(2, 10% of {found})")
    if len(planted_ids) < 3:
        reasons.append(f"needs >= 3 planted defects, have {len(planted_ids)}")
    elif recall < 0.8:
        reasons.append(f"planted recall {recall:.2f} < 0.8")
    if dry < k:
        reasons.append(f"dry rounds {dry} < K={k}")
    r0 = [r for _, r in rounds if r.get("round") == 0]
    if r0 and r0[0].get("planted_by") == "self":
        reasons.append("planted by the finder: recall not blind")
    if coverage_missing:
        reasons.append("coverage incomplete")
    if unexamined:
        reasons.append(f"{unexamined} HAZOP cells not_examined")
    return not reasons, reasons


def check(directory, mode="audit", k=2, expensive_run=False):
    d, rep = pathlib.Path(directory), Report()
    rep.note(f"mode={mode}")
    iid = load_instance(d, rep)
    for md in MARKDOWN[mode]:
        if not (d / md).exists():
            rep.note(f"NOT-CHECKED {md}: file missing")
    rounds = None
    if mode == "audit" or (d / "rounds.jsonl").exists():
        rounds = load_jsonl(d, "rounds.jsonl", rep, "rounds.jsonl" in REQUIRED[mode]) or []
    a_sealed = any(r.get("round") == 1 and r.get("path") in ("A", "both") and r.get("sealed") is True
                   for _, r in rounds or [])
    planted = None
    if mode == "audit" or (d / "planted.jsonl").exists():
        planted = load_jsonl(d, "planted.jsonl", rep, "planted.jsonl" in REQUIRED[mode])
    planted_ids = {p.get("id") for _, p in planted} if planted is not None else None
    guards, eff = check_guards(d, mode, rep, iid)
    findings = check_findings(d, mode, rep, planted_ids, guards, iid, a_sealed)
    check_invariants(d, mode, rep, guards, iid)
    unexamined = 0
    if mode in ("build", "audit", "design") or (d / "hazards.jsonl").exists():
        unexamined = check_hazards(d, mode, rep, eff, guards)
    p_items = check_runs(d, mode, rep, findings)
    if mode in ("build", "preflight") or expensive_run or (d / "preflight.json").exists():
        check_preflight(d, rep, mode == "preflight" or expensive_run, iid, p_items)
    stop_met = None
    if mode == "audit":
        fmap = {f.get("id"): f for _, f in findings}
        for gid, g in guards.items():
            if (g.get("S") or 0) >= 7 and g.get("status") == "registered" and gid not in eff:
                if not any("FM-23" in (f.get("fm") or []) and gid in (f.get("guards") or []) for _, f in findings):
                    rep.bad(f"guards.jsonl[{gid}]", "S >= 7 guard not effective and no FM-23 finding lists it in guards")
        seen, missing = check_coverage(d, rep, eff, guards, fmap)
        if not guards and (seen.get("FM-23") or {}).get("status") != "not_checked":
            rep.bad("guards.jsonl", "0 guard rows: register the existing guards, or mark FM-23 not_checked with the reason")
        check_seals(rep, findings, rounds, planted)
        stop_met, reasons = stop_rule(rep, findings, rounds, k, missing, planted, unexamined)
        if rep.violations:
            stop_met = False
            rep.note(f"STOP RULE: NOT EVALUATED ({len(rep.violations)} violations)")
        else:
            rep.note("STOP RULE: MET" if stop_met else "STOP RULE: NOT MET: " + "; ".join(reasons))
    return rep, stop_met


def digests(directory):
    d, rep = pathlib.Path(directory), Report()
    iid = load_instance(d, rep)
    findings = load_jsonl(d, "findings.jsonl", rep, False) or []
    planted = load_jsonl(d, "planted.jsonl", rep, False) or []
    print(f"instance_id={iid}")
    print(f"sealed_digest={path_a_digest(findings)}  (round-1 rows with found_by A or AB: write on the path A round 1 row)")
    print(f"planted_digest={planted_digest(planted)}  (write on the round 0 row)")
    return 0


def plant(directory, n):
    d = pathlib.Path(directory)
    out = d / "planted.jsonl"
    if not 3 <= n <= 5:
        print("plant 3-5 seeds")
        return 2
    if out.exists():
        print("planted.jsonl exists: refusing to overwrite sealed seeds")
        return 2
    now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    rng = random.SystemRandom()
    rows = []
    for i, (gw, param, seed) in enumerate(rng.sample(SEED_MENU, min(n, len(SEED_MENU))), 1):
        rows.append({"id": f"PL-{i}", "seed": seed, "guideword": gw, "parameter": param,
                     "target_rank": rng.randint(1, 1000), "location": "", "sealed": True, "planted_at": now})
    _write(d, "planted.jsonl", rows)
    print(f"wrote {len(rows)} seeds to {out}: hand this file to a planter context (fresh sub-agent or human); "
          "the finder must not read it before the reveal. The planter applies each seed to the scratch copy at "
          "item target_rank (modulo the item count, in key order), fills location, then runs --digest and writes "
          "the round 0 row (planted_by: script) before round 1; a finder that applies its own seeds writes "
          "planted_by: self, which cannot certify the stop rule")
    return 0


# ---------------------------------------------------------------- selftest

def _write(d, name, rows):
    (d / name).write_text("\n".join(json.dumps(r) for r in rows) + ("\n" if rows else ""), encoding="utf-8")


def _read(d, name):
    return [json.loads(x) for x in (d / name).read_text(encoding="utf-8").splitlines() if x.strip()]


def _matrix_from_reference():
    ref = pathlib.Path(__file__).resolve().parent.parent / "references" / "hazard-sweep.md"
    if not ref.exists():
        return None
    got = {}
    for line in ref.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 11 and cells[0] in GUIDEWORDS:
            for p, c in zip(PARAMS, cells[1:]):
                got[(cells[0], p)] = c
    return got


def _fixture(tmp):
    inst = {"code_rev": "abc", "env": "prod", "data_versions": {"t1": "v1"}}
    (tmp / "instance.json").write_text(json.dumps(inst), encoding="utf-8")
    iid = instance_id(inst)
    for md in ("chain-map.md", "report.md", "quick-scan.md"):
        (tmp / md).write_text("x\n", encoding="utf-8")
    _write(tmp, "guards.jsonl", [{
        "id": "GR-1", "protects": ["FM-03"], "gate": "G1", "runner": "pytest x", "trigger": "pre-merge",
        "mode": "block", "S": 8, "severity": "high", "scope": "code", "blind_spots": "runtime strings",
        "status": "registered", "verdict": "effective", "baseline": {"source": "none"},
        "seeded_fault": {"id": "SF-1", "killed": True},
        "last_run": {"executed_count": 5, "result": "pass", "instance_id": iid}}])
    carries = [p for p in PARAMS if p != "FRAME"]
    _write(tmp, "seams.jsonl", [{"id": "SM-1", "type": "extractor->normalizer", "producer": "S1", "consumer": "S2",
                                 "intent": "i", "carries": carries, "changed": True}])
    hz = [{"id": "HZ-1", "source": "hazop", "seam": "SM-1", "status": "hazard", "parameter": ["ID"],
           "guideword": ["OTHER THAN"], "consequence": "c", "S": 9, "severity": "critical", "O": 3, "D": 2,
           "detection_evidence": "SF-1", "safeguards": ["GR-1"], "priority": "before_release"},
          {"id": "HZ-2", "source": "hazop", "seam": "SM-1", "status": "pruned", "parameter": ["FRAME"],
           "guideword": "*", "prune_reason": "not_carried", "prune_detail": "no frame on this seam"}]
    for n, g in enumerate(GUIDEWORDS):
        live = [p for p in carries if MATRIX[(g, p)]]
        blank = [p for p in carries if not MATRIX[(g, p)]]
        hz.append({"id": f"HZ-N{n}", "source": "hazop", "seam": "SM-1", "status": "pruned", "parameter": live,
                   "guideword": [g], "prune_reason": "no_credible_cause", "prune_detail": "no cause on this path",
                   "examined": ["normalize()", "records r1-r20"]})
        if blank:
            hz.append({"id": f"HZ-B{n}", "source": "hazop", "seam": "SM-1", "status": "pruned", "parameter": blank,
                       "guideword": [g], "prune_reason": "matrix_blank", "prune_detail": "ordinary seam"})
    _write(tmp, "hazards.jsonl", hz)
    fi = {"title": "t", "cause_root": "logic", "escape_root": "absent", "verdict": "confirmed", "S": 7,
          "severity": "high", "instance_id": iid, "evidence": {"repro": "cmd"}, "intentional_state_checked": True,
          "fix_locus": "stage", "verification": {"by": "fresh_session", "saw_candidate": False}}
    main = [dict(fi, id=f"F-{i}", title=f"t{i}", fm=[FM_IDS[i]], class_predicate=f"p{i}", found_by="AB", round=1)
            for i in range(6)]
    hits = [dict(fi, id=f"F-P{i}", fm=["FM-14"], class_predicate=f"pp{i}", found_by="B", round=1, planted=f"PL-{i}",
                 copy="scratch-1") for i in range(3)]
    _write(tmp, "findings.jsonl", main + hits)
    planted = [{"id": f"PL-{i}", "seed": "s", "location": f"scratch/r{i}", "sealed": True,
                "planted_at": "2026-10-14T08:00:00Z"} for i in range(3)]
    _write(tmp, "planted.jsonl", planted)
    _write(tmp, "invariants.jsonl", [{"id": "INV-1", "family": "closed_vocabulary", "statement": "s", "gate": "G1",
                                      "result": "pass", "executed_count": 5, "guard": "GR-1", "instance_id": iid}])
    cov = []
    for i in FM_IDS + ST_IDS:
        if i == "FM-03":
            cov.append({"id": i, "status": "guarded", "guards": ["GR-1"]})
        elif i in [f"FM-{j:02d}" for j in range(1, 7)]:
            cov.append({"id": i, "status": "finding", "findings": [f"F-{int(i[3:]) - 1}"]})
        elif i in UNIVERSAL:
            cov.append({"id": i, "status": "not_checked", "reason": "r"})
        else:
            cov.append({"id": i, "status": "not_applicable", "reason": "r", "feature": "no model stage"})
    _write(tmp, "coverage.jsonl", cov)
    rows_f = [(None, r) for r in main + hits]
    _write(tmp, "rounds.jsonl", [
        {"round": 0, "planted_by": "script", "planted_digest": planted_digest([(None, p) for p in planted]), "completed": True},
        {"round": 1, "path": "A", "completed": True, "sealed": True, "sealed_digest": path_a_digest(rows_f),
         "started_at": "2026-10-14T09:00:00Z"},
        {"round": 1, "path": "B", "completed": True, "sealed": True, "started_at": "2026-10-14T09:00:00Z"},
        {"round": 2, "path": "A", "completed": True},
        {"round": 3, "path": "B", "completed": True}])
    _write(tmp, "runs.jsonl", [
        {"run_id": "r1", "status": "succeeded", "minutes": 30},
        {"run_id": "r2", "status": "failed", "minutes": 60, "fingerprint": "f1", "catchable": "G4",
         "first_error": {"node": "normalize", "error_class": "schema_enum"},
         "catching_check": "P3", "p_item": "P11+f1", "change_since_last_same_fingerprint": None}])
    return fi, iid


def _preflight(iid, verdict="go", drop=(), extra=None):
    items = [{"id": i, "result": "pass", "executed_count": 1} for i in P_ALL + ["P11+f1"] if i not in drop]
    return {"instance_id": iid, "items": items + (extra or []), "verdict": verdict}


def selftest():
    """Build a valid audit dir, assert it passes, then seed faults and assert each is caught."""
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="eca-selftest-"))
    caught = 0
    try:
        ref = _matrix_from_reference()
        if ref is None:
            print("NOTE NOT-CHECKED matrix parity: references/hazard-sweep.md not found next to scripts/")
        else:
            diff = [c for c in MATRIX if ref.get(c, "?") != MATRIX[c]]
            assert not diff, f"MATRIX differs from hazard-sweep.md 1.3 at {diff[:5]}"
            caught += 1
        fi, iid = _fixture(tmp)
        rep, stop = check(tmp, "audit")
        assert not rep.violations, rep.violations
        assert stop, rep.notes
        assert any("branch=standard" in n for n in rep.notes), rep.notes

        def first(r, **kw):
            return [dict(r[0], **kw)] + r[1:]

        hz_base = _read(tmp, "hazards.jsonl")
        seeds = [
            ("findings.jsonl", lambda r: first(r, evidence={}), "confirmed without a reproduction"),
            ("findings.jsonl", lambda r: first(r, cause_root="structure"), "platform-wide"),
            ("findings.jsonl", lambda r: first(r, S=9, severity="medium"), "does not match S"),
            ("findings.jsonl", lambda r: r + [dict(fi, id="F-9", fm=["FM-14"], class_predicate="q", found_by="B",
                                                   round=1, detected_gate="G6")], "shift-left rule"),
            ("findings.jsonl", lambda r: first(r, instance_id="OLD999"), "wrong_instance"),
            ("findings.jsonl", lambda r: [{k: v for k, v in r[0].items() if k != "round"}] + r[1:], "integer round"),
            ("findings.jsonl", lambda r: first(r, verification={"by": "same_context", "saw_candidate": False}), "same_context"),
            ("findings.jsonl", lambda r: first(r, verification={"by": "fresh_session", "saw_candidate": True}), "saw the candidate"),
            ("findings.jsonl", lambda r: first(r, title="edited after sealing"), "changed after sealing"),
            ("findings.jsonl", lambda r: first(r, fm=[], st=[]), "missing fm and st"),
            ("guards.jsonl", lambda r: first(r, seeded_fault={"killed": False}), "contradicts"),
            ("guards.jsonl", lambda r: first(r, verdict="bogus"), "verdict 'bogus' invalid"),
            ("guards.jsonl", lambda r: first(r, verdict="vacuous", verdict_reason="seed survived"), "no FM-23 finding"),
            ("guards.jsonl", lambda r: first(r, last_run={"executed_count": 5, "instance_id": "OLD999"}), "pinned instance"),
            ("guards.jsonl", lambda r: first(r, mode="warn", S=5, severity="medium", owner="o", expires="2027-01-01"), "ceiling"),
            ("invariants.jsonl", lambda r: first(r, executed_count=0), "empty is not a measurement"),
            ("invariants.jsonl", lambda r: first(r, instance_id="OLD999"), "wrong_instance"),
            ("coverage.jsonl", lambda r: r[1:], "no status for"),
            ("coverage.jsonl", lambda r: [dict(c, status="not_applicable", feature="f") if c["id"] == "FM-04" else c for c in r], "universal"),
            ("coverage.jsonl", lambda r: [dict(c, guards=["GR-1"], status="guarded") if c["id"] == "FM-14" else c for c in r], "protects lists it"),
            ("coverage.jsonl", lambda r: [{k: v for k, v in c.items() if k != "feature"} for c in r], "feature"),
            ("coverage.jsonl", lambda r: [dict(c, findings=["F-0"]) if c["id"] == "FM-02" else c for c in r], "whose fm or st lists it"),
            ("hazards.jsonl", lambda r: first(r, D=8, detection_evidence="none", safeguards=[]), "D 7-8"),
            ("hazards.jsonl", lambda r: first(r, D=2, detection_evidence="we think tests cover it", safeguards=[]), "D 1-3"),
            ("hazards.jsonl", lambda r: first(r, D=9, detection_evidence="none", safeguards=[], priority="before_release"), "must be must_fix"),
            ("hazards.jsonl", lambda r: r[:2], "neither swept nor pruned"),
            ("hazards.jsonl", lambda r: r[:2] + [{k: v for k, v in r[2].items() if k != "prune_reason"}] + r[3:], "valid prune_reason"),
            ("hazards.jsonl", lambda r: r[:2] + [dict(r[2], prune_detail="")] + r[3:], "without prune_detail"),
            ("hazards.jsonl", lambda r: [r[0], dict(r[1], prune_reason="matrix_blank")] + r[2:], "does not fit"),
            ("hazards.jsonl", lambda r: r[:1] + [dict(r[1], parameter="*")], "does not fit"),
            ("hazards.jsonl", lambda r: r[:2] + [dict(r[2], guideword="*")] + r[3:], "exactly one guideword"),
            ("hazards.jsonl", lambda r: r[:2] + [{k: v for k, v in r[2].items() if k != "examined"}] + r[3:], "examined list"),
            ("hazards.jsonl", lambda r: r[:2] + [dict(r[2], prune_reason="prevented_by_construction", guard="GR-404")] + r[3:], "effective guard that proves it"),
            ("hazards.jsonl", lambda r: r[:2] + [dict(r[2], prune_reason="represented_by", represented_by="SM-999")] + r[3:], "names no existing seam"),
            ("seams.jsonl", lambda r: first(r, carries=[]), "missing carries"),
            ("seams.jsonl", lambda r: [], "0 seams in scope"),
            ("rounds.jsonl", lambda r: r[1:], "no round 0 row"),
            ("rounds.jsonl", lambda r: [dict(r[0], planted_digest="0")] + r[1:], "planted_digest"),
            ("planted.jsonl", lambda r: first(r, planted_at="2026-10-14T10:00:00Z"), "not before round 1"),
            ("planted.jsonl", lambda r: r[:2], "plant 3-5"),
            ("runs.jsonl", lambda r: [r[0], {k: v for k, v in r[1].items() if k != "catchable"}], "catchable"),
            ("runs.jsonl", lambda r: [r[0], {k: v for k, v in r[1].items() if k != "p_item"}], "P-item"),
            ("runs.jsonl", lambda r: r + [dict(r[1], run_id="r3", change_since_last_same_fingerprint=False)], "ST-02"),
            ("runs.jsonl", lambda r: [r[0], {k: v for k, v in r[1].items() if k != "first_error"}], "first_error.node"),
            ("runs.jsonl", lambda r: r + [dict(r[1], run_id=f"r{n}", fingerprint=f"f{n}") for n in (3, 4)], "needs an ST-06 finding"),
            ("findings.jsonl", lambda r: r[:6] + [{k: v for k, v in r[6].items() if k != "copy"}] + r[7:], "without copy"),
        ]
        for name, mutate, expect in seeds:
            original = (tmp / name).read_text(encoding="utf-8")
            _write(tmp, name, mutate(_read(tmp, name)))
            rep, met = check(tmp, "audit")
            assert any(expect in v for v in rep.violations), (name, expect, rep.violations)
            assert not met and any("NOT EVALUATED" in n for n in rep.notes), ("stop rule shown as met with violations", name)
            (tmp / name).write_text(original, encoding="utf-8")
            caught += 1
        saved_planted = (tmp / "planted.jsonl").read_text(encoding="utf-8")
        (tmp / "planted.jsonl").unlink()
        rep, _ = check(tmp, "audit")
        assert any("planted.jsonl: missing" in v for v in rep.violations), rep.violations
        (tmp / "planted.jsonl").write_text(saved_planted, encoding="utf-8")
        caught += 1

        def stop_of(mutations):
            saved = {n: (tmp / n).read_text(encoding="utf-8") if (tmp / n).exists() else None for n in mutations}
            for n, rows in mutations.items():
                _write(tmp, n, rows)
            rep, met = check(tmp, "audit")
            for n, text in saved.items():
                if text is None:
                    (tmp / n).unlink(missing_ok=True)
                else:
                    (tmp / n).write_text(text, encoding="utf-8")
            return rep, met

        rounds, findings = _read(tmp, "rounds.jsonl"), _read(tmp, "findings.jsonl")
        rep, met = stop_of({"rounds.jsonl": rounds[:3]})
        assert not met and not rep.violations, ("stop met without dry rounds", rep.violations)
        unsealed = [dict(r, sealed=False) for r in rounds]
        rep, met = stop_of({"rounds.jsonl": unsealed})
        assert not met and any("m=0" in n for n in rep.notes), ("unsealed AB rows counted as overlap", rep.notes)
        many = [dict(fi, id=f"F-{i}", title=f"t{i}", fm=[FM_IDS[i]], class_predicate=f"p{i}", round=1,
                     found_by="AB" if i < 3 else ("A" if i < 10 else "B")) for i in range(17)] + findings[6:]
        sealed = [dict(r, sealed_digest=path_a_digest([(None, f) for f in many])) if r.get("path") == "A" else r for r in rounds]
        rep, met = stop_of({"findings.jsonl": many, "rounds.jsonl": sealed})
        assert not met and not rep.violations and any("residual" in n for n in rep.notes), ("high residual accepted", rep.violations, rep.notes)
        few = findings[:1] + [dict(findings[1], found_by="B")] + findings[6:]
        sealed = [dict(r, sealed_digest=path_a_digest([(None, f) for f in few])) if r.get("path") == "A" else r for r in rounds]
        cov_few = [dict(id=c["id"], status="not_checked", reason="r") if c["status"] == "finding" else c
                   for c in _read(tmp, "coverage.jsonl")]
        rep, met = stop_of({"findings.jsonl": few, "rounds.jsonl": sealed, "coverage.jsonl": cov_few})
        assert met and any("branch=low-count" in n for n in rep.notes), ("low-count branch deadlocked", rep.notes, rep.violations)
        rep, met = stop_of({"findings.jsonl": few[:-1], "rounds.jsonl": sealed, "coverage.jsonl": cov_few})
        assert not met and not rep.violations, ("low-count branch met with planted recall 0.67", rep.violations)
        solo = [r for r in rounds if not (r.get("round") == 1 and r.get("path") == "B")]
        solo = [dict(r, path="both") if r.get("round") == 1 else r for r in solo]
        rep, met = stop_of({"rounds.jsonl": solo})
        assert met and any("branch=low-count" in n and "solo" in n for n in rep.notes), ("solo audit used Chapman", rep.notes, rep.violations)
        stall = [dict(findings[0], id="F-S", fm=[], st=["ST-02"], found_by="B", class_predicate="ps")] + findings
        rep, met = stop_of({"findings.jsonl": stall})
        assert not rep.violations, ("stall-only finding rejected", rep.violations)
        link = [dict(findings[0], id="F-G", fm=["FM-23"], found_by="B", class_predicate="pg", guards=["GR-1"])] + findings
        bad_guard = [dict(_read(tmp, "guards.jsonl")[0], verdict="vacuous", verdict_reason="seed survived")]
        rep, met = stop_of({"findings.jsonl": link, "guards.jsonl": bad_guard})
        assert not any("no FM-23 finding" in v for v in rep.violations), ("FM-23 link via guards not accepted", rep.violations)
        cov23 = [dict(c, status="finding", findings=["F-0"]) if c["id"] == "FM-23" else c for c in _read(tmp, "coverage.jsonl")]
        rep, met = stop_of({"guards.jsonl": [], "coverage.jsonl": cov23})
        assert any("0 guard rows" in v for v in rep.violations), ("empty guard registry accepted", rep.violations)
        unex = [dict(h, prune_reason="not_examined", examined=[]) if h["id"] == "HZ-N0" else h for h in hz_base]
        rep, met = stop_of({"hazards.jsonl": unex})
        assert not met and not rep.violations and any("NOT MET" in n and "cells not_examined" in n for n in rep.notes), \
            ("not_examined cells counted as swept", rep.violations, rep.notes)
        caught += 12
        same_ctx = findings[:6] + [dict(f, verification={"by": "same_context", "saw_candidate": True}) for f in findings[6:]]
        rep, met = stop_of({"findings.jsonl": same_ctx})
        assert met and not rep.violations, ("planted finding rejected for its verifier: the reveal is its oracle", rep.violations)
        self_planted = [dict(rounds[0], planted_by="self")] + rounds[1:]
        rep, met = stop_of({"rounds.jsonl": self_planted})
        assert not met and not rep.violations and any("not blind" in n for n in rep.notes), \
            ("self-planted seeds certified the stop rule", rep.violations, rep.notes)
        runs = _read(tmp, "runs.jsonl")
        rep, met = stop_of({"runs.jsonl": [{k: v for k, v in runs[0].items() if k != "minutes"}] + runs[1:]})
        assert not rep.violations and any("compute shares NOT-CHECKED" in n for n in rep.notes), \
            ("missing minutes counted as 0", rep.violations, rep.notes)
        cls3 = runs + [dict(runs[1], run_id=f"r{n}", fingerprint=f"f{n}") for n in (3, 4)]
        st06 = [dict(findings[0], id="F-S6", fm=[], st=["ST-06"], found_by="B", class_predicate="p6")] + findings
        rep, met = stop_of({"runs.jsonl": cls3, "findings.jsonl": st06})
        assert not rep.violations, ("class recurrence with an ST-06 finding rejected", rep.violations)
        for n_seeds in (0, 2, 6):
            with contextlib.redirect_stdout(io.StringIO()):
                assert plant(tmp, n_seeds) == 2, f"--plant {n_seeds} accepted"
        caught += 7

        prior = tmp / "prior"
        prior.mkdir()
        for n in ("instance.json", "guards.jsonl", "seams.jsonl", "hazards.jsonl"):
            shutil.copy(tmp / n, prior / n)
        rep_row = {"id": "HZ-R", "source": "hazop", "seam": "SM-1", "status": "pruned", "parameter": "*",
                   "guideword": "*", "prune_reason": "represented_by", "represented_by": "SM-1@prior", "prune_detail": "one new field only"}
        rep, met = stop_of({"hazards.jsonl": hz_base[:1] + [rep_row]})
        assert not rep.violations, ("represented_by a fully swept prior ledger rejected", rep.violations)
        _write(prior, "hazards.jsonl", hz_base[:2])
        rep, met = stop_of({"hazards.jsonl": hz_base[:1] + [rep_row]})
        assert any("not fully covered" in v for v in rep.violations), rep.violations
        shutil.rmtree(prior)
        caught += 2

        inc = pathlib.Path(tempfile.mkdtemp(prefix="eca-incident-", dir=tmp))
        for n in ("instance.json", "report.md", "guards.jsonl", "invariants.jsonl"):
            shutil.copy(tmp / n, inc / n)
        good = dict(fi, id="F-1", fm=["FM-08"], class_predicate="p", found_by="incident", round=1,
                    signature={"seam_type": "parser->extractor", "parameter": "PRES", "guideword": "PART OF", "carrier": "c"},
                    siblings=0, positive_control="finds the original case", earliest_detector={"gate": "G4"})
        _write(inc, "findings.jsonl", [good])
        rep, _ = check(inc, "incident")
        assert not rep.violations, ("incident fixture", rep.violations)
        rep, _ = check(inc, "audit")
        assert any("coverage.jsonl" in v for v in rep.violations), "audit mode must require coverage"
        _write(inc, "findings.jsonl", [{k: v for k, v in good.items() if k != "positive_control"}])
        rep, _ = check(inc, "incident")
        assert any("positive_control" in v for v in rep.violations), rep.violations
        _write(inc, "findings.jsonl", [])
        rep, _ = check(inc, "incident")
        assert any("found_by incident" in v for v in rep.violations), rep.violations
        quick = dict(good, found_by="quick")
        quick.pop("class_predicate")
        _write(inc, "findings.jsonl", [quick])
        rep, _ = check(inc, "quick")
        assert not rep.violations, ("quick finding needs only a repro", rep.violations)
        _write(inc, "findings.jsonl", [dict(good, id=f"F-{i}", found_by="quick") for i in range(4)])
        rep, _ = check(inc, "quick")
        assert any("at most 3" in v for v in rep.violations), rep.violations
        caught += 5

        pre = pathlib.Path(tempfile.mkdtemp(prefix="eca-preflight-", dir=tmp))
        for n in ("instance.json", "runs.jsonl"):
            shutil.copy(tmp / n, pre / n)
        rep, _ = check(pre, "preflight")
        assert any("required before an expensive run" in v for v in rep.violations), rep.violations
        for pf, expect in ((_preflight(iid), None),
                           ({"instance_id": iid, "items": [], "verdict": "go"}, "verdict go"),
                           (_preflight(iid, drop=P_ALL[1:]), "verdict go"),
                           (_preflight(iid, drop=["P9"], extra=[{"id": "P9", "result": "not_applicable", "reason": "no model stage"}]), None),
                           (_preflight(iid, drop=["P3"], extra=[{"id": "P3", "result": "not_applicable", "reason": "x"}]), "always apply"),
                           (_preflight(iid, drop=["P5"], extra=[{"id": "P5", "result": "not_applicable", "reason": "first run of this tenant"}]), None),
                           (_preflight(iid, drop=["P11+f1"]), "P11+f1"),
                           (_preflight(iid, verdict="no_go"), "stays blocked"),
                           (dict(_preflight(iid), instance_id="OLD999"), "wrong_instance")):
            (pre / "preflight.json").write_text(json.dumps(pf), encoding="utf-8")
            rep, _ = check(pre, "preflight")
            if expect is None:
                assert not rep.violations, ("valid preflight rejected", rep.violations)
            else:
                assert any(expect in v for v in rep.violations), (expect, rep.violations)
        caught += 9

        des = pathlib.Path(tempfile.mkdtemp(prefix="eca-design-", dir=tmp))
        for n in ("instance.json", "chain-map.md", "report.md", "seams.jsonl"):
            shutil.copy(tmp / n, des / n)
        _write(des, "hazards.jsonl", [dict(h, prune_reason="not_examined") if h.get("prune_reason") == "no_credible_cause"
                                      else h for h in hz_base[1:]] + [dict(hz_base[0], D=9, safeguards=[], priority="must_fix")])
        _write(des, "guards.jsonl", [{"id": "GR-D", "protects": ["FM-13"], "gate": "G6", "trigger": "promotion",
                                      "mode": "warn", "S": 8, "severity": "high", "scope": "totals", "blind_spots": "items",
                                      "status": "registered", "verdict": "unaudited", "predicted_verdict": "narrow",
                                      "verdict_reason": "anti-pattern 31: total-only tolerance"}])
        dfind = dict(fi, id="F-D", fm=["FM-13"], found_by="A", class_predicate="p", verdict="plausible",
                     verdict_reason="described, not reproduced")
        _write(des, "findings.jsonl", [dfind])
        rep, _ = check(des, "design")
        assert not rep.violations, ("design fixture", rep.violations)
        _write(des, "findings.jsonl", [dict(dfind, verdict="confirmed")])
        rep, _ = check(des, "design")
        assert any("plausible at most" in v for v in rep.violations), rep.violations
        caught += 2
        print(f"selftest: PASS (clean fixtures pass; {caught} seeded faults and parity checks caught)")
        return 0
    except AssertionError as exc:
        print(f"selftest: FAIL {exc}")
        return 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("audit_dir", nargs="?")
    ap.add_argument("--mode", choices=sorted(REQUIRED), default="audit")
    ap.add_argument("--k", type=int, default=2, help="dry rounds required by the stop rule")
    ap.add_argument("--require-stop", action="store_true", help="exit 3 when the stop rule is not met (audit)")
    ap.add_argument("--expensive-run", action="store_true", help="preflight.json must exist with verdict go")
    ap.add_argument("--digest", action="store_true", help="print instance_id, sealed_digest and planted_digest")
    ap.add_argument("--plant", type=int, metavar="N", help="draw N seeds at random into planted.jsonl")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.audit_dir or not pathlib.Path(a.audit_dir).is_dir():
        ap.print_usage()
        return 2
    if a.digest:
        return digests(a.audit_dir)
    if a.plant is not None:
        return plant(a.audit_dir, a.plant)
    rep, stop = check(a.audit_dir, a.mode, a.k, a.expensive_run)
    for n in rep.notes:
        print("NOTE", n)
    for v in rep.violations:
        print("VIOLATION", v)
    print(f"{len(rep.violations)} violations")
    if rep.violations:
        return 1
    return 3 if (a.require_stop and a.mode == "audit" and not stop) else 0


if __name__ == "__main__":
    sys.exit(main())
