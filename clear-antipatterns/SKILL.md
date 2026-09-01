---
name: clear-antipatterns
description: >-
  Conservative TS anti-pattern remediation in any path/file.
  /clear-antipatterns [scope] [pattern]. Grep finds candidates; context confirms.
disable-model-invocation: true
version: 2.1.0
---

# Clear Anti-Patterns

`/clear-antipatterns` → activate. Heuristics: [detection.md](detection.md) (**load at Scan**). Tokens: [../shared/token-efficiency.md](../shared/token-efficiency.md).

**Principle:** Detection identifies **candidates**; contextual evidence determines whether remediation is justified. Optimize for **justified, minimal, behavior-preserving** improvements. Do not modify code unless the anti-pattern is **confirmed** and remediation has clear engineering benefit.

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

On conflict: prefer repo evidence → preserve behavior → reassess or escalate.

**Secrets:** never echo, `cat`, print, or include raw secret values in terminal output, reports, remediation files, summaries, patches, or comments.

## Risk (after Inspect + Confirm only)

Assess risk **after** contextual confirmation — not at scan time.

| Risk | Execution policy |
|------|------------------|
| **low** | Auto-fix when confirmed and behavior-preserving |
| **medium** | Execute only when contextual evidence + targeted validation make behavior preservation reasonably demonstrable |
| **high** | Explicit user confirmation required (public contract, security, behavior-sensitive) |

Confirmed but low-benefit → mark `accepted` with justification; do not fix opportunistically.

## Workflow

1. **Resolve** — scope, pattern, package boundaries.
2. **Scan** — load detection.md; grep-first → **candidates only**.
3. **Classify** — dedupe; assign pattern (no risk yet).
4. **Inspect** — bounded context; confirm or reject; assess **risk**; judge engineering benefit.
5. **Plan** — minimal fix; remediation file if >15 confirmed or >10 files (when repo permits).
6. **Protect** — record git baseline (below).
7. **Execute** — per risk policy; confirmed + justified only.
8. **Verify** — narrowest repo-defined validation for touch set.
9. **Review** — scoped diff attribution (below).
10. **Report** — fixes, accepted retains, validation, blockers.

`grep`/`awk`/`find`/hashes = discovery only. Prefer repo AST/lint/unused-export tooling when present; no new deps.

## Git baseline (before Execute)

Record for attribution:

```text
HEAD, branch, status -sb
unstaged diff --stat (+ scoped diff per touch path)
staged diff --stat (+ scoped diff --cached per touch path)
planned touch set
```

- Protect staged, unstaged, and pre-existing untracked (untracked ≠ disposable).
- Never reset/revert/discard/overwrite user changes.
- Dirty existing path → scoped diff before edit; preserve intent.

## Change budget

Touch set = minimal paths for confirmed findings. Reassess if it grows unexpectedly. No opportunistic refactors.

## Behavior-sensitive (usually medium/high)

Closures/state extraction; cross-module moves; export deletion; public types; async/control-flow; memo/cache removal; config loading; security code. **TSX:** hook order, closures, state, context, memo — no mechanical JSX extraction.

## Validation

Narrowest existing command covering touch set. Escalate per monorepo/shared-lib boundaries. No invented commands.

## Diff review (required, scoped)

```bash
git status -sb
git diff --stat
git diff -- <touch-set paths>
git diff --cached -- <touch-set paths>   # if staged
```

Compare to baseline for attribution. Full `git diff` only on ambiguity. Check: unrelated files, user changes preserved, no vendor/generated edits, debug/TODO churn, no unjustified deps, each change maps to a confirmed finding.

## Remediation file

When >15 confirmed or >10 files **and** repo conventions permit task-generated docs — default `docs/antipattern-remediation.md` unless conventions conflict. Format in detection.md. Never store secrets.

## Rules

- No new deps; preserve behavior; match project conventions.
- **#2, #5:** manual review only — no auto-fix.
- False positives / low-benefit retains → `accepted` with justification.

## Protected areas

Skip: `node_modules`, `dist`, `build`, `coverage`, `.next`, `.turbo`, repo-specific generated/vendor paths from conventions. Protect authoritative fixtures/reference datasets when conventions indicate source-of-truth. Edit source files, not generated output.

## Out of Scope

Non-TS/TSX, unrelated features, new tools, ESLint config (unless asked), mechanical `any→unknown`, splitting coherent large modules by line count alone.
