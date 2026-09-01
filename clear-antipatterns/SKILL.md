---
name: clear-antipatterns
description: >-
  Conservative TS anti-pattern remediation in any path/file.
  /clear-antipatterns [scope] [pattern]. Grep finds candidates; context confirms.
disable-model-invocation: true
version: 2.0.0
---

# Clear Anti-Patterns

`/clear-antipatterns` → activate. Heuristics: [detection.md](detection.md) (**load at Scan**). Tokens: [../shared/token-efficiency.md](../shared/token-efficiency.md).

**Principle:** Detection identifies **candidates**; contextual evidence determines whether remediation is justified. Optimize for **low-risk, behavior-preserving** fixes — not removal count.

## Args

| Form | Behavior |
|------|----------|
| `[scope] [pattern]` | Path (dir or `.ts`/`.tsx`) + optional pattern (`9`, `any`) |
| `[pattern]` only | Auto scope when arg is not a path |
| (none) | Auto scope; all 10 patterns |

**Path** = `/`, `.ts`/`.tsx`, or `.` / `..`. Else → pattern.

**Scope:** user path; else nearest `tsconfig.json` → `.`, else `src/`/`lib/`/`app/`/`packages/*/src`, else repo root. File scope = that file. Dir = recurse; skip generated/vendor dirs (see Protected areas).

## Evidence

| Status | Use |
|--------|-----|
| **Observed** | Direct code/manifest evidence |
| **Inferred** | Reasonable — label required |
| **Assumption** | Unverified premise — label required |
| **Unknown** | Not established — do not fabricate |

On conflict: prefer repo evidence → preserve behavior → reassess or escalate. Never print secret values.

## Risk (confirmed findings only)

| Risk | Fix when |
|------|----------|
| **low** | Mechanical, behavior-preserving change highly likely |
| **medium** | Contextual refactor; minimal change; stronger validation |
| **high** | Public contract, security, behavior-sensitive — **confirm before execute** |

## Workflow

1. **Resolve** — scope, pattern, package boundaries.
2. **Scan** — load detection.md; grep-first → **candidates only** (not proof).
3. **Classify** — dedupe; assign pattern; estimate risk.
4. **Inspect** — read containing fn/class/module, imports/exports, usages, tests, conventions; confirm or reject. Stop when sufficient.
5. **Plan** — minimal fix; split safe vs risky; remediation file if >15 confirmed or >10 files.
6. **Protect** — git baseline (below); detect dirty overlap.
7. **Execute** — confirmed findings only; preserve behavior; no opportunistic refactors.
8. **Verify** — narrowest repo-defined validation covering changed files; escalate per monorepo boundaries.
9. **Review** — mandatory diff review (below).
10. **Report** — fixes, accepted retains, validation, blockers.

`grep`/`awk`/`find`/hashes = discovery tools, not semantic proof. Prefer existing repo AST/lint tooling when present; no new deps for detection.

## Git protection (before Execute)

```bash
git rev-parse --abbrev-ref HEAD
git status -sb
git diff --stat
git diff --cached --stat
```

- Protect all pre-existing **staged**, **unstaged**, and **untracked** changes (untracked ≠ disposable).
- Never reset/revert/discard/overwrite user changes.
- Dirty touch path → `git diff -- <path>` + `git diff --cached -- <path>`; preserve intent; avoid same lines unless necessary; surface overlap if unsafe.

## Change budget

- Only files required for **confirmed** findings.
- Smallest coherent change; no unrelated cleanup or architecture shifts.
- Reassess if touch set grows unexpectedly.

## Behavior-sensitive (extra validation)

Extracting fns with closures/state; cross-module moves; deleting exports; public type changes; async/control-flow changes; removing memo/cache; config loading; security-sensitive code. **TSX:** preserve hook order, closure/state ownership, context, memo boundaries — no mechanical JSX extraction.

## Validation

Narrowest existing command covering changed files (`package.json` scripts, per-package `tsc`/test). Walk up for monorepo/shared-lib boundaries. **No invented commands.**

## Diff review (required)

```bash
git status -sb
git diff --stat
git diff
```

Check: unrelated files, user changes preserved, no vendor/generated edits, no debug/TODO churn, no unjustified deps, no unintended API changes, each change maps to a confirmed finding.

## Remediation file

Large jobs → `docs/antipattern-remediation.md` (format in detection.md). Status: `pending` | `fixed` | `accepted` | `blocked`. Never store secrets.

## Rules

- No new deps; preserve behavior; match project conventions.
- **#2 Golden Hammer, #5 Premature Opt:** manual review only — no auto-fix; require evidence before removing optimizations.
- False positives / intentional retains → mark `accepted` with justification.

## Protected areas

Always skip: `node_modules`, `dist`, `build`, `coverage`, `.next`, `.turbo`. Also skip repo-specific generated/vendor paths (`generated/`, `vendor/`, `.codegen/`, `prisma/generated/`, etc.) from manifest/conventions. Edit source-of-truth, not generated output.

## Out of Scope

Non-TS/TSX, application features unrelated to confirmed anti-patterns, new tools/frameworks, ESLint config (unless asked), mechanical `any→unknown`, splitting coherent large modules by line count alone.
