---
name: dev-pipeline
description: >-
  Runs a phase-based product development tracking pipeline for AI-agent
  workflows: pre-prod docs, epics/features/tasks with stable IDs, phase
  switching without breaking changes, and self-contained task prompt handoffs.
  Use when the user starts with /dev-pipeline, asks to init a product backlog
  pipeline, create/switch phases, emit the next agent task prompt, or track
  epic/feature status across multi-agent development.
disable-model-invocation: true
version: 1.0.0
---

# Dev Pipeline

When the user message begins with `/dev-pipeline`, this skill is attached, or they explicitly ask to run the **dev-pipeline** / product tracking pipeline, activate this skill **immediately**.

**Purpose:** Persist product evolution as token-efficient, ID-linked docs so sequential or parallel agents can continue work without losing business-logic integrity or product identity. Emits self-contained task prompts for another agent; does **not** implement product code unless the user also asks.

**Companions:** `/commit` (commit skill) after implementation; `/review-task` (review-task skill) after a task lands.

## Design decisions

1. **Docs are source of truth** — code follows tracked epics/features/tasks; do not invent backlog state not reflected in files.
2. **Phases are switchable** — incomplete phases stay parked; switching must not rewrite IDs or break contracts.
3. **IDs are stable forever** — never renumber; mark superseded instead.
4. **Prompts are handoffs** — write under `agent-prompts/` (gitignored); do not commit prompt bodies unless the user explicitly requires it.
5. **Minimal tokens** — prefer tables, IDs, and short evidence pointers over prose dumps.
6. **Reuse existing docs** — if the repo already has `docs/epics/`, `ROADMAP.md`, etc., **extend** them; do not duplicate parallel trees without cause.

## Activation

| Form | Behavior |
|------|----------|
| `/dev-pipeline init [name]` | Bootstrap layout + product identity docs |
| `/dev-pipeline backlog` / `/dev-pipeline plan` | Inspect product → create/update backlog (epics/features) |
| `/dev-pipeline phase new <slug>` | Create a phase; optionally set active |
| `/dev-pipeline phase switch <PH-ID>` | Activate another phase without breaking prior work |
| `/dev-pipeline phase status` | Show active phase + epic/feature summary |
| `/dev-pipeline next` / `/dev-pipeline task` | Emit next ready task prompt under `agent-prompts/` |
| `/dev-pipeline task <FEATURE-ID>` | Emit prompt for a specific feature/task |
| `/dev-pipeline status` | Compact pipeline overview (phases, blockers, priorities) |
| Natural language: “dev pipeline”, «پایپلاین توسعه», «رهگیری فاز» | Same as matching subcommand intent |

Flags may appear anywhere after `/dev-pipeline`:

| Flag | Meaning |
|------|---------|
| `--set-active` | With `phase new`, mark the new phase active |
| `--suite <dir>` | Epic suite folder under `docs/` (default: discover) |
| `--dry-run` | Report planned file writes; do not write |

Do not treat ambient coding as this skill unless `/dev-pipeline` or an explicit pipeline ask is present.

## References

- Folder layout, IDs, statuses, templates: [schema.md](schema.md)
- Phase rules & switching: [phases.md](phases.md)
- Task prompt format: [prompt-template.md](prompt-template.md)

## Discover project conventions (do not invent)

Look for, in order:

1. `docs/dev-pipeline/PHASES.md` — canonical phase index (this skill)
2. Existing `docs/ROADMAP.md`, `docs/ARCHITECTURE.md`, `docs/epics/**`, suite folders like `docs/epics-*/`
3. `docs/**/TASK-QUEUE.md` or `**/BOLT-TASK-QUEUE.md`
4. `agent-prompts/` or legacy `bolt-prompts/`
5. Entity/API docs (`docs/**/Entities/`, `*api-contract*`, `*dto*`)

If both legacy and `docs/dev-pipeline/` exist, treat **legacy epic IDs as authoritative**; store phase/queue overlays under `docs/dev-pipeline/` and link out.

## Safety

- Never overwrite unrelated user edits; if a target file is dirty with unrelated changes, surface overlap before editing.
- Never delete epic/feature history; use status `cancelled` / `superseded`.
- Never invent stack, APIs, or architecture — tag Observed / Inferred / Unknown (same evidence rules as Promptize).
- Do not add dependencies. Do not implement product features in this skill unless the user also requested implementation in the same message.
- Destructive doc wipes require explicit confirmation.

## Workflow (sequential)

### 0. Parse

Extract subcommand, IDs, flags, and short request remainder.

### 1. Inspect (task-scoped)

1. Repo root + top-level layout.
2. Existing docs listed above.
3. Active phase from `docs/dev-pipeline/PHASES.md` (or ask if missing and command needs it).
4. `git status` when about to write files.

### 2. Branch by subcommand

#### `init`

1. Create layout per [schema.md](schema.md) (skip files that already exist with real content).
2. Write `docs/PRODUCT.md` (identity, surfaces: frontend/backend/other).
3. Write or link `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`.
4. Write `docs/dev-pipeline/PHASES.md` with no active phase or `PH-00` intake.
5. Ensure `.gitignore` contains `agent-prompts/` (and keep `bolt-prompts/` if already ignored).
6. Stop with paths created + next suggested command (`backlog` or `phase new`).

#### `backlog` / `plan`

1. Inspect product + code/docs evidence.
2. Produce/update epic suite README + epic files with stable IDs.
3. For each feature: status, priority, depends-on, co-req, blocks, acceptance sketch.
4. Record cross-links to entities, modules, API contracts, DTOs (paths only).
5. Do **not** emit an agent task prompt unless also `next`/`task` was requested.

#### `phase new` / `phase switch` / `phase status`

Follow [phases.md](phases.md). Switching must preserve all IDs and prior queues.

#### `next` / `task`

1. Resolve active phase + queue.
2. Pick highest-priority **ready** item (deps satisfied, not blocked).
3. Write one self-contained prompt via [prompt-template.md](prompt-template.md) to `agent-prompts/{TASK-ID}.md`.
4. Set queue row to `ready` or `in_progress` as appropriate.
5. Tell the user to hand that file to the implementing agent; mention `/commit` after work and `/review-task` after commit/push.

#### `status`

Emit a compact table: active phase, epic/feature counts by status, blockers, next ready IDs. No file writes unless fixing a broken index was requested.

### 3. Stop

Default: documentation + prompt handoff only. Implementation belongs to the other agent (or a separate user ask).

## Context loading order (for agents using the docs)

When reading pipeline docs, load **only** what the current task needs, in this order:

1. `docs/PRODUCT.md` (identity — short)
2. `docs/dev-pipeline/PHASES.md` → active phase README
3. Active `TASK-QUEUE.md` row for the task
4. Parent epic file section for the feature
5. Linked contract/entity paths cited by that feature
6. Skip unrelated suites

## Out of scope for this skill

- Implementing application code (unless user separately asks)
- `/commit` or `/review-task` workflows (delegate to those skills)
- Rewriting legacy epic IDs
- Opening PRs / force-push / destructive git
- Replacing Promptize for one-off engineering specs (use `/promptize` for that)
