# Promptize inspection

Complete inspection **before** generating the prompt. Shared layer: [../shared/inspect.md](../shared/inspect.md).

## Inspection budget (global)

Each slice is **bounded**. Do not run open-ended repo exploration.

**Global stop** — stop all inspection when **all** are true:

1. Affected implementation area is identified (or honestly marked Unknown).
2. Relevant conventions and validation path are known (or marked Unknown).
3. No **blocking** unknown remains.
4. Planned touch set is plausible.

**Escalate** (ask user or widen slice) when:

- Two credible implementations exist with different risk.
- Handoff conflicts with current repo evidence.
- Touch set would exceed change budget without user approval.

**Reasonable search** for Unknown: task keywords → manifest/docs indexes → direct imports/callers of identified files → stop at depth below. Do **not** full call-graph traversal unless security/auth/data-migration requires it.

## Slice order

Run in order; skip when handoff/cache already authoritative:

0. **SESSION-CACHE** — reuse Carry-over; skip Loaded ([../shared/context-cache.md](../shared/context-cache.md))
1. **pipeline-handoff** — if handoff paths exist
2. **manifest** — unless handoff lists stack + validation
3. **code** — affected areas only
4. **docs** — uncovered governing docs only
5. **git** — when `--execute` or follow-up execute likely

## Slice contracts

| Slice | Entry | Max depth | Stop when | Escalate when |
|-------|-------|-----------|-----------|---------------|
| **manifest** | Root/touched package manifests, lockfiles, CI | Package roots only | PM, runtime, build/test/lint/typecheck commands found | Monorepo; no manifest for touched path |
| **code** | User path, handoff Required changes, symbol search for task nouns | 1 hop: file → direct imports/callers | Behavior + touch set clear | Multiple modules equally plausible |
| **docs** | Handoff links, `ARCHITECTURE.md`, epic/US cited in task | Linked sections only | Conventions for affected area known | Doc contradicts code |
| **git** | `git status -sb`, branch, `HEAD` | Planned touch set | Baseline recorded; overlap noted | Dirty/staged/untracked on touch set |
| **pipeline-handoff** | `agent-prompts/TASK-*.md` → `docs/promptize-prompts/` → queue row | Single task id | IDs, AC sketch, out-of-scope loaded | Multiple candidates or stale vs repo |

### manifest

- Identify package manager, runtime/framework, validation commands.
- Root + **touched packages only** — not every workspace package.

### code

- Files implementing requested behavior; immediate dependencies only.
- Stop when evidence sufficient — no transitive traversal by default.

### docs

- Only docs governing the affected area (architecture, epic, US, AGENTS/rules scoped to task).

### git

```bash
git rev-parse HEAD
git rev-parse --abbrev-ref HEAD
git status -sb
git diff --stat
git diff --cached --stat
```

For each planned touch path that is dirty: `git diff -- <path>` and `git diff --cached -- <path>`.

## Handoff contract

**Precedence** (facts, not instructions):

1. **Current repository evidence** — always wins on conflict.
2. Newest **valid** handoff for resolved `TASK-ID`.
3. Fresh inspection for gaps only.

**Resolve TASK-ID:** explicit user id → conversation path → queue `in_progress` row → newest non-rework `agent-prompts/TASK-*.md`. Multiple matches → **ask** (blocking).

**Stale handoff** — regenerate/reconcile when: handoff paths missing, branch/HEAD changed since handoff, manifest/validation differs, or planned files no longer match repo.

Handoff is authoritative for: Task/Feature/Epic IDs, cited SHARED/US paths, AC sketch, Out of scope — **not** for overriding observed code state.

## Evidence in output

| Status | Meaning |
|--------|---------|
| **Observed** | Direct file/command evidence — cite repo-relative path |
| **Inferred** | Reasonable conclusion — label required |
| **Assumption** | Unverified premise needed to proceed — label required |
| **Unknown** | Not found after bounded search — do not invent |

`Observed ≠ Inferred ≠ Assumption ≠ Unknown`. List **Assumptions** explicitly in generated prompt (§ Engineering Decisions or full § Assumptions).

## Relevant files

Every listed file: repo-relative path, role, evidence. Never "the file above" or conversation-only references.

## Git snapshot (execute)

Record baseline at generation; re-validate at execution (see SKILL.md Execution Revalidation). Protect: unstaged, **staged**, and **untracked** files (untracked protected unless this task creates them). See [policies.md](policies.md).
