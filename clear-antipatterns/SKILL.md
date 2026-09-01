---
name: clear-antipatterns
description: >-
  Production-grade conservative TS anti-pattern remediation.
  /clear-antipatterns [scope] [pattern]. Candidates require contextual confirmation.
disable-model-invocation: true
version: 2.2.0
---

# Clear Anti-Patterns

`/clear-antipatterns` → activate. Detection: [detection.md](detection.md) (**load at Scan**). Tokens: [../shared/token-efficiency.md](../shared/token-efficiency.md).

**Principle:** Regex/grep/awk/find/hashes are **discovery only** — they MUST NOT alone justify a code change. Optimize for **justified, minimal, behavior-preserving** improvements. Modify code only when anti-pattern is **confirmed** and remediation has clear engineering benefit.

## Args

| Form | Behavior |
|------|----------|
| `[scope] [pattern]` | Path (dir or `.ts`/`.tsx`) + optional pattern (`1`–`10`, name) |
| `[pattern]` only | Auto scope when arg is not a path |
| (none) | Auto scope; all 10 patterns **sequentially** (see Pattern-by-pattern) |

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
| `candidate` | Detection output only; unproven |
| `inspected` | Context read; remediation decision not final |
| `confirmed` | Anti-pattern verified |
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

## Risk (after Inspect + Confirm only)

When uncertain between two levels → **choose higher**.

| Risk | Criteria | Execution |
|------|----------|-----------|
| **low** | Mechanical, local, behavior-preserving highly likely | Auto-fix when confirmed |
| **medium** | Contextual refactor; limited coupling; internal types with contained blast radius; local abstraction swap; needs stronger test/type validation | Execute only when evidence + targeted validation make behavior preservation reasonably demonstrable |
| **high** | Public contract, security, behavior-sensitive, large blast radius | **MUST NOT execute autonomously** — document, propose minimal fix, **stop**, wait for explicit user approval |

**High-risk rule:** inspect → explain risk → propose fix → **stop before code change** → wait for approval. Never assume confirmation.

Confirmed but low-benefit → `accepted` with justification.

## Workflow

1. **Resolve** — scope, pattern, tsconfig, package boundaries.
2. **Scan** — load detection.md; discovery → **candidates only**.
3. **Classify** — dedupe; assign pattern (no risk yet).
4. **Inspect** — bounded context; confirm/reject; assess risk; judge benefit.
5. **Plan** — minimal fix; remediation file if tracking threshold met (see below).
6. **Protect** — git baseline.
7. **Execute** — per risk policy; confirmed + justified only.
8. **Verify** — narrowest repo-defined validation (see Validation failure).
9. **Re-scan** — **required** — re-run detection for changed scope/patterns; verify fixes, accepted still intentional, no new unrelated issues; repair incomplete fixes before report.
10. **Review** — scoped diff + semantic impact (below).
11. **Report** — structured format (below).

### Pattern-by-pattern

When all 10 patterns active: process **sequentially** per pattern:

`scan → confirm → fix → verify → re-scan`

Do not parallelize dependent remediations. Finish one pattern before the next to avoid ambiguous cross-pattern effects.

### Remediation file threshold

`>15 confirmed` OR `>10 files` → create tracking file **when repo permits** (`docs/antipattern-remediation.md` default). Threshold is for **tracking**, not permission for broad refactoring.

## Git baseline (before Execute)

Record: `HEAD`, branch, `status -sb`, unstaged/staged `--stat`, scoped diff per touch path, planned touch set.

Protect staged, unstaged, pre-existing untracked. Never reset/revert/discard/overwrite user changes. Dirty path → scoped diff before edit.

## Change budget

- Touch set = minimal paths for confirmed findings only.
- Never broad mechanical remediation across many files without batching + re-validation.
- If changes grow unexpectedly → **stop**, reassess, split safe vs risky.
- No opportunistic refactors.

## Validation

Narrowest **existing** repo command covering touch set; escalate per monorepo/shared-lib boundaries. **No invented scripts.**

If no repo-defined validation: use available static checks only; report **validation limited**.

### Validation failure

1. Determine if failure caused by remediation.
2. Never revert/overwrite pre-existing user changes.
3. Never fix unrelated failures.
4. Caused by remediation → small safe repair, else mark `blocked`.
5. Pre-existing → preserve change; report as pre-existing.

## Behavior-sensitive & TSX

Usually medium/high. Before TSX extraction/refactor verify: hook order, closure capture, state ownership, ref identity, effect dependencies, context/provider boundaries, memo boundaries, forwarded refs, lifecycle semantics. Mechanical JSX extraction **forbidden**. Escalate risk if extraction may affect these.

## Diff & semantic review (required)

```bash
git status -sb
git diff --stat
git diff -- <touch-set paths>
git diff --cached -- <touch-set paths>
```

Compare to baseline. Full diff only on ambiguity.

**Semantic review** (behavior-sensitive changes): call sites, exports/imports, public API, type relationships, async/control-flow, closure/state ownership.

## Definition of Done

Done only when:

- Every confirmed finding is `fixed`, `accepted`, or `blocked`
- Every `fixed` has verification evidence
- Every `accepted`/`blocked` has justification/blocker
- Validation performed where available (or reported limited)
- Post-fix **re-scan** completed
- No unrelated files modified; user changes preserved
- Final diff reviewed

## Report format

```markdown
## Fixed
## Accepted
## Rejected
## Blocked
## Validation
## Re-scan
## Notes / Assumptions
```

Per finding: pattern + file + short reason. No secret values.

## Rules

- `disable-model-invocation: true`; no new deps; preserve behavior.
- **#2 Golden Hammer, #5 Premature Opt:** manual review only — no auto-fix; evidence required to remove optimizations.
- Prefer existing repo AST/tsc/ESLint/unused-export tooling over grep. Details: [detection.md](detection.md).

## Protected areas

Single source of truth: [detection.md](detection.md) `$F` exclusions. Also protect authoritative fixtures/reference data per repo conventions.

## Out of Scope

Non-TS/TSX, unrelated features, new tools, ESLint config (unless asked), mechanical `any→unknown`, splitting coherent large modules by line count alone.
