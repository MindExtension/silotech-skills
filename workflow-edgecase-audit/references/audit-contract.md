# Audit contract

## Truth seed template

```text
Revision:
Dirty state / isolated worktree:
Product contract:
Supported workflows and tiers:
Canonical providers:
Expected terminal states:
Known fixed issues to suppress:
Accepted risks:
Requires deployed proof:
Forbidden actions / paths:
```

Do not send agents a narrative dump. Give them this compact, shared seed so findings are comparable.

## Coverage matrix

Freeze user/system triggers as the coverage denominator. Count downstream helpers, migrations, schemas, and tests as traced nodes, not extra entry points. Report `owned triggers / inventoried triggers`, the traced-node count, and explicit exclusions.

For every workflow record:

| Field | Question |
|---|---|
| Trigger | What starts it: UI, API, webhook, cron, queue, migration? |
| Identity | Who may start, read, resume, retry, or revoke it? |
| Durable state | Which rows, files, objects, or events prove progress? |
| Invariant | What must remain true across every transition? |
| Side effects | Payment, email, LLM call, storage, analytics, deployment? |
| Recovery | What happens after timeout, crash, retry, reorder, or partial success? |
| Terminal proof | How do we know it completed exactly once? |
| Existing tests | Which exact assertions cover the risky transitions? |

An endpoint list is not a workflow map. Follow data and side effects across boundaries.

## Finding schema

```text
ID:
Title:
Severity: CRITICAL | HIGH | MEDIUM | LOW
Confidence: CONFIRMED | HIGH | MODERATE
Workflow:
Trigger sequence:
Violated invariant:
Impact:
Evidence: stable path:line when available; otherwise a relocatable symbol, route, migration, event ID, command output, or runtime observation
Verification: test, direct probe, static trace, runtime, deployed
Regression test needed:
Evidence still missing:
```

Reject a finding that cannot name both a reachable trigger and a violated invariant. If reachability depends on unknown deployment configuration, move the candidate to `Evidence gaps` as `UNCONFIRMED`; do not count it as a finding.

## Severity calibration

- `CRITICAL`: credible broad compromise, irreversible widespread corruption, or a systemic failure that blocks most core transactions with no practical recovery.
- `HIGH`: payment/access boundary failure, cross-tenant exposure, duplicate costly effects, or a primary workflow can become permanently stuck.
- `MEDIUM`: meaningful integrity, reliability, cost, or UX failure with narrower reach or a practical workaround.
- `LOW`: localized defect with limited impact; do not use LOW for style or hypothetical hardening.

Severity is impact times realistic reachability, not code smell intensity.

## Ten-zone fallback team

Derive zones from the frozen executable workflow inventory first. This is a SaaS-oriented fallback, not a required taxonomy. Merge empty zones, split overloaded zones, and record substitutions before delegation.

1. Intake, input validation, autocomplete, and client request races.
2. Authentication, authorization, ownership, sessions, and tokens.
3. Billing, discounts, payment-provider webhook order, refunds, and idempotency.
4. Async pipeline, LLM/provider behavior, retries, leases, and recovery.
5. Documents, storage, versioning, signed URLs, and downloads.
6. Notifications, recipient lifecycle, reminders, completion, and issued artifacts.
7. Database constraints, RLS, migrations, and concurrent writes.
8. Privacy, consent, analytics, email safety, and legal claims in behavior.
9. Frontend state machines, routing, debounce, cancellation, and accessibility.
10. CI/CD, environment contracts, smoke tests, observability, and deployed truth.

Use waves when fewer than ten slots are available. A wave is complete only after every assigned agent returns or is explicitly marked unavailable.

## Adversarial validation protocol

The validator receives the candidate and its evidence, but not the first auditor's conclusion. Ask:

1. Is the trigger reachable under the pinned product contract?
2. Is there a guard elsewhere in the call chain?
3. Does a database or provider guarantee invalidate the race?
4. Does framework behavior change event ordering or retry semantics?
5. Does an existing test assert this exact invariant, not merely the route status?
6. Can a minimal direct probe reproduce the boundary without external mutation?
7. Is this one root cause already reported under another symptom?

Outcomes: `KEEP`, `DOWNGRADE`, `MERGE`, `EVIDENCE_GAP`, or `REJECT`, each with one evidence-backed reason.

If no peer reviewer is available, perform the validation as a separate sequential pass with a different falsification probe and disclose that it was not peer-independent.

## Final response contract

```text
Verdict: GO | GO WITH FIXES | NO-GO | INCOMPLETE EVIDENCE

Critical / high findings
Medium findings
Coverage and verification
Known issues suppressed
Evidence gaps
```

## Narrow-scope template

```text
Included triggers:
Excluded triggers and reason:
Owned / inventoried triggers:
Downstream nodes traced:
Permitted probes:
Required evidence level:
```

## Sequential validation worksheet

Use this only when no peer-independent reviewer is available:

```text
Candidate hidden from first-pass conclusion: yes/no
Trigger retraced from entry point:
Downstream guard or constraint checked:
Different falsification probe:
Outcome: KEEP | DOWNGRADE | MERGE | EVIDENCE_GAP | REJECT
Disclosure: sequential, not peer-independent
```

Do not turn missing production credentials, inaccessible dashboards, or absent external access into product bugs. Report them as evidence gaps unless the configuration itself is the audited failure.
