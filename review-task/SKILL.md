---
name: review-task
description: >-
  Reviews the latest git changes against a tracked pipeline task prompt
  (agent-prompts/ or bolt-prompts/), scores acceptance criteria, updates the
  phase task queue, and writes rework prompts on FAIL/PARTIAL. On PASS, tells
  the user to run /dev-pipeline next (does not emit the next task prompt).
  Use when the user starts with /review-task, attaches this skill, or asks to
  review the latest task changes for a TASK-ID after agent implementation.
disable-model-invocation: true
version: 1.1.0
---

# Review Task

When the user message begins with `/review-task`, this skill is attached, or they ask to **review the latest task changes** for a pipeline `TASK-ID`, run this workflow **immediately**.

**Purpose:** Verify an implementer agent’s diff against the **exact task prompt** that was assigned, report PASS/FAIL/PARTIAL, update queue status, and on failure emit a rework prompt under `agent-prompts/` (gitignored). On PASS, **do not** write the next task prompt — delegate to `/dev-pipeline next`.

**Companions:** Task prompts from `/dev-pipeline`; commits via `/commit`. Inspect: [../shared/inspect.md](../shared/inspect.md). Token rules: [../shared/token-efficiency.md](../shared/token-efficiency.md).

## Activation

| Form | Behavior |
|------|----------|
| `/review-task` | Review resolved task → verdict (+ rework prompt if FAIL/PARTIAL) |
| `/review-task TASK-…` | Force review against that task id |
| `/review-task --pull` | `git pull --ff-only` first (default: **no** pull) |
| `/review-task --no-pull` | Explicit skip pull (default behavior) |
| Natural language: “review task”, «ریویو تسک», «بررسی آخرین تغییرات تسک» | Same as `/review-task` |

### Flag parsing

| Flag | Meaning |
|------|---------|
| `--pull` | Pull current branch ff-only before reviewing |
| `--no-pull` | Do not pull (default) |
| `TASK-…` | Explicit task under review |

Do not treat generic code-review asks as this skill unless a pipeline/bolt task prompt handoff is clearly intended.

## Discover conventions

Look for, in order:

1. `agent-prompts/TASK-*.md` (preferred)
2. `bolt-prompts/TASK-*.md` (legacy)
3. `docs/dev-pipeline/phases/*/TASK-QUEUE.md` or `**/BOLT-TASK-QUEUE.md` / `**/TASK-QUEUE.md`
4. Epic docs linked from the queue
5. Conversation: last prompt path / task id written

If `agent-prompts/` is missing, create it and ensure `.gitignore` contains `agent-prompts/` before writing **rework** prompts only.

## Safety

- **NEVER** update git config
- **NEVER** `push --force`, hard reset, or discard user changes
- **NEVER** skip hooks unless the user explicitly asks
- **NEVER** use interactive git (`-i`)
- Before `--pull`: if working tree is **dirty**, stop and ask (stash / commit / proceed). Do not discard dirty files.
- Prefer `git pull --ff-only`. If it fails, report and ask — do not rebase/merge without confirmation.
- Do not commit or push unless the user explicitly asks in the same turn.
- Never put prompt bodies into git-tracked paths; confirm with `git check-ignore -v <path>`.

## Workflow

### 1. Resolve task under review

Determine `TASK_ID` and prompt path — use **one** match; if multiple candidates conflict, **ask** (blocking):

1. Explicit `TASK-…` in the user message (strip rework suffix `-R{N}` for base task when reviewing rework)
2. `TASK_ID` in recent commit subjects (`git log -15 --oneline`) matching `TASK-…` or conventional scope `feat(ASK-01):` / `fix(TASK-ASK-01-01):`
3. Queue row with status `in_progress` whose Task ID matches an existing `agent-prompts/TASK-*.md`
4. Path cited in the current conversation (last handoff)
5. Newest `agent-prompts/TASK-*.md` without `-R` suffix **only** if steps 1–4 yield nothing
6. Legacy `bolt-prompts/`, else ask (blocking)

Read the full prompt. Extract: Goal, Required changes, Out of scope, Acceptance criteria, Definition of done, Contracts.

Do **not** re-read PRODUCT/SHARED/epic files if the task prompt already contains inherited context or cites paths as satisfied — verify only the change-set.

### 2. Collect the change set

```bash
git rev-parse --abbrev-ref HEAD
git rev-parse HEAD
git status -sb
git log -15 --oneline
```

If `--pull`: save `BEFORE_SHA`, pull ff-only, then review `BEFORE_SHA..HEAD`.

Otherwise prefer, in order:

1. Commits whose subject/body contains `TASK_ID` (or base feature id from `TASK_ID`)
2. Range since queue row was marked `in_progress` if that timestamp/note exists
3. Unpushed commits on the branch clearly for this task (single logical deliverable)
4. `git diff` working tree + staged if uncommitted work is the deliverable
5. **Ask** which SHA range to use (blocking) — do not guess across unrelated commits

Note unrelated dirty files as **protected** — do not revert them.

### 3. Review against the task prompt

Score each acceptance criterion: **pass** / **fail** / **unclear**.

Also check:

| Check | Fail if |
|-------|---------|
| Scope | Files/behavior outside Out of scope / drive-by refactors |
| Dependencies | New packages unless the prompt allowed them |
| Contracts | Breaking API/DTO/entity changes not required by the task |
| Patterns | Ignores repo conventions called out in the prompt |
| Secrets | Credentials or `.env` committed |
| Identity | Violates Product identity / phase invariants in the prompt |

Run **only** validation commands that exist in-repo and are relevant. Do not invent a harness.

Details: [checklist.md](checklist.md).

### 4. Verdict

- **PASS** — all AC pass; scope clean; relevant validation OK
- **FAIL** — required criterion fails, out-of-scope damage, or build broken by the change
- **PARTIAL** — core behavior works but blocking gaps remain → treat like FAIL for queue advance unless user overrides

### 5. Update queue + prompts

**On PASS:**

1. Set this task to `done` in the phase `TASK-QUEUE.md` (if present).
2. Update parent feature status in the epic file when all its tasks are done (or set `partial` if only part shipped).
3. **Do not** write the next task prompt — `/dev-pipeline next` owns selection rules and handoff format.
4. Tell the user: run `/dev-pipeline next` (or `/dev-pipeline task <FEATURE-ID>`) for the next implementer handoff.

**On FAIL or PARTIAL:**

1. Leave task `in_progress` or mark rework needed.
2. Write `agent-prompts/{TASK-ID}-R{N}.md` with failures, required fixes only, open AC (see [checklist.md](checklist.md)).
3. Do **not** advance to the next feature task.

### 6. Stop

Do not implement the next task unless the user also asked to implement. This skill reviews and emits **rework** prompts only.

## Out of scope

- Writing the **next** normal task prompt on PASS (use `/dev-pipeline next`)
- Implementing the feature instead of reviewing (unless user separately asks)
- Opening PRs / pushing
- Treating unrelated dirty local edits as the task deliverable
- Advancing `blocked` tasks
- Replacing `/review-bolt-changes` when the user explicitly wants the bolt pull-centric flow
