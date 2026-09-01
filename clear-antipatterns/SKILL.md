---
name: clear-antipatterns
description: >-
  Production-grade conservative TS anti-pattern remediation.
  /clear-antipatterns [scope] [pattern]. Candidates require contextual confirmation.
disable-model-invocation: true
version: 2.2.1
---

# Clear Anti-Patterns

`/clear-antipatterns` → activate. Detection: [detection.md](detection.md) (**load at Scan**). Tokens: [../shared/token-efficiency.md](../shared/token-efficiency.md).

**Principle:** Regex/grep/awk/find/hashes are **discovery only** — they MUST NOT alone justify a code change. Optimize for **justified, minimal, behavior-preserving** improvements. Modify code only when anti-pattern is **confirmed** and remediation has clear engineering benefit.

## Args

| Form | Behavior |
|------|----------|
| `[scope] [pattern]` | Path (dir or `.ts`/`.tsx`) + optional pattern (`1`–`10`, name) |
| `[pattern]` only | Auto scope when arg is not a path |
| (none) | Auto scope; patterns **1–10 sequentially** — skip auto-scan for #2, #5 (manual-only) |

**Path** = `/`, `.ts`/`.tsx`, or `.` / `..`. Else → pattern.

## Resolve — scope & package boundaries

**tsconfig selection** (conservative; note ambiguity in report):

1. Scope inside a package → nearest package/project `tsconfig.json`
2. Honor `references` / project boundaries when present
3. Root `tsconfig` only when no package-specific config applies
4. Do not use `tsconfig.build.json` or tooling-only configs as source scope without evidence

**Monorepo:** identify root vs package `tsconfig`, references, workspace deps. For exports, unused code, public types, shared utils, cross-package imports — check usage **outside** current package. In-package non-reference ≠ dead code (especially #3 Lava Flow).

**Scope fallback:** user path → package `tsconfig` dir → `src/`/`lib/`/`app/`/`packages/*/src` → repo root. File scope = that file only.

## Finding lifecycle

```text
candidate → inspected → confirmed ──→ rejected
                          ↓
                    fixed | accepted | blocked
```

| Status | Meaning |
|--------|---------|
| `candidate` | Detection output only; unproven — **no risk classification** |
| `inspected` | Context read; remediation decision not final |
| `confirmed` | Anti-pattern verified — risk assigned here |
| `rejected` | False positive or intentional code |
| `fixed` | Remediated and verified |
| `accepted` | Intentionally retained — **reason required** |
| `blocked` | Cannot safely execute — **blocker/evidence required** |

**Confirmed finding metadata (required):** Pattern, File, Location, Evidence, Risk, Decision, Action, Verification.

## Evidence

| Status | Use |
|--------|-----|
| **Observed** | Direct code/manifest evidence |
| **Inferred** | Label required |
| **Assumption** | Label required |
| **Unknown** | Do not fabricate |

On conflict: repo evidence → preserve behavior → reassess/escalate.

## Secrets & redaction

Never echo/`cat`/print literal credentials, tokens, passwords, API keys, or secrets in findings, plans, remediation files, summaries, patches, logs, or examples. Represent as `<REDACTED>` even when present in source.

## Risk (confirmed findings only)

**Candidates have no risk.** Risk is assigned only after contextual inspection confirms the finding.

When uncertain between two levels → **choose higher**.

| Risk | Criteria | Execution |
|------|----------|-----------|
| **low** | Mechanical, local, behavior-preserving highly likely | Auto-fix when confirmed |
| **medium** | Contextual refactor; limited coupling; internal types with contained blast radius; local abstraction swap; needs stronger test/type validation | Execute only when evidence + targeted validation make behavior preservation reasonably demonstrable |
| **high** | Public contract, security, behavior-sensitive, large blast radius | **MUST NOT execute autonomously** — document, propose minimal fix, **stop**, wait for explicit user approval |

**High-risk rule:** inspect → explain risk → propose fix → **stop before code change** → wait for approval. Never assume confirmation.

**Low-benefit confirmed → `accepted`** when benefit does not justify change. Assess benefit only against: duplication reduction, clarity, correctness, maintainability, consistency with project conventions, risk reduction. Do not accept solely because the agent avoids touching code.

## Workflow

1. **Resolve** — scope, pattern, tsconfig, package boundaries.
2. **Scan** — load detection.md; discovery → **candidates only** (#2, #5: not auto-scanned).
3. **Classify** — dedupe; assign pattern (no risk).
4. **Inspect** — bounded context; confirm/reject; assign risk; judge benefit.
5. **Plan** — minimal fix; remediation file if tracking threshold met.
6. **Protect** — git baseline (pre-execution snapshot).
7. **Execute** — per risk policy; confirmed + justified only.
8. **Verify** — narrowest repo-defined validation (see Validation failure).
9. **Re-scan** — **required** — affected pattern(s) + touch set first; expand only if remediation changed exports, shared types, package boundaries, or generated artifacts.
10. **Review** — scoped diff + semantic impact + untracked files.
11. **Report** — structured format (below).

### Pattern-by-pattern

When all patterns active: process **sequentially** per pattern (`scan → confirm → fix → verify → re-scan`). Skip auto-scan for **#2 Golden Hammer** and **#5 Premature Opt** — manual review only; never autonomous remediation or fake regex detection.

### Remediation file

`>15 confirmed` OR `>10 files` → tracking file when repo permits (`docs/antipattern-remediation.md`). Threshold = **tracking**, not broad-refactor permission. Remediation file is **metadata** — do not analyze or modify it as a finding target.

## Git baseline (before Execute)

Record **pre-execution baseline** (not just `HEAD`):

```text
HEAD, branch, status -sb
unstaged/staged --stat + scoped diff per touch path
planned touch set
```

Protect staged, unstaged, pre-existing untracked. Never reset/revert/discard/overwrite user changes. Dirty path → scoped diff before edit.

**Diff attribution:** compare post-change state against **pre-execution baseline**, not only `HEAD` (baseline includes user dirty state).

## Change budget

Touch set = minimal paths for confirmed findings. Stop and reassess if scope grows. No opportunistic refactors.

## Validation

Narrowest **existing** repo command covering touch set. **Only tooling already in the repository/toolchain** — do not install or invoke globally unavailable tools. No invented scripts. Report **validation limited** when no repo command exists.

### Validation failure

1. Caused by remediation? → small safe repair, else `blocked`.
2. Never revert/overwrite pre-existing user changes or fix unrelated failures.
3. Pre-existing → preserve; report as pre-existing.

## Behavior-sensitive & TSX

Usually medium/high. Before TSX extraction: hook order, closures, state, refs, effects, context, memo, forwarded refs, lifecycle. Mechanical JSX extraction **forbidden**.

## Diff & semantic review (required)

```bash
git status -sb
git diff --stat
git diff -- <touch-set paths>
git diff --cached -- <touch-set paths>
git ls-files --others --exclude-standard   # review new untracked explicitly
```

Compare to **pre-execution baseline**. Full diff only on ambiguity. Review newly created untracked files (e.g. remediation metadata) explicitly — `git diff` does not show them.

**Semantic review** (behavior-sensitive): call sites, exports/imports, public API, types, async/control-flow, closure/state.

## Definition of Done

- All confirmed → `fixed`, `accepted`, or `blocked` (with evidence/reason)
- Validation + re-scan completed
- No unrelated files modified; user changes preserved
- Final diff reviewed against baseline

## Report format

`## Fixed` · `## Accepted` · `## Rejected` · `## Blocked` · `## Validation` · `## Re-scan` · `## Notes / Assumptions` — pattern + file + reason; no secrets.

## Rules

- `disable-model-invocation: true`; no new deps; preserve behavior.
- **#2, #5:** manual-only — not auto-scanned; no autonomous remediation.
- Prefer repo tooling **already available** over grep ([detection.md](detection.md)).

## Protected areas

```text
Protected = standard exclusions + observed repo-specific exclusions.
```

[detection.md](detection.md) is the **canonical execution rule** for file discovery; repo conventions (tsconfig exclude, `.gitignore`, package layout) determine repo-specific additions. Protect authoritative fixtures/reference data when conventions indicate source-of-truth.

## Out of Scope

Non-TS/TSX, unrelated features, new tools, ESLint config (unless asked), mechanical `any→unknown`, splitting coherent large modules by line count alone.
