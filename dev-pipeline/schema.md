# Dev Pipeline Schema

Read from `SKILL.md` when creating or updating pipeline docs.

## Default layout

Create only what is missing. Prefer linking existing docs over duplication.

```text
docs/
  PRODUCT.md                 # product identity, surfaces, non-goals
  ARCHITECTURE.md            # modules, boundaries (or link if exists)
  ROADMAP.md                 # coarse completed vs remaining
  dev-pipeline/
    PHASES.md                # phase index + active pointer
    ADOPTION.md              # mid-flight adopt/refresh snapshot (optional until adopt)
    phases/
      PH-00-intake/          # optional intake after adopt/init
        README.md
        TASK-QUEUE.md
        CONTEXT.md
      PH-01-<slug>/
        README.md            # goals, status, switch notes, contract freeze
        TASK-QUEUE.md        # ordered tasks for this phase
        CONTEXT.md           # compact map: entities ↔ modules ↔ APIs/DTOs
  epics/                     # or docs/<suite>/ — epic index + epic files
  # optional domain trees already in repo:
  # backend/Entities/, api-contract-and-dtos.md, etc.

agent-prompts/               # gitignored handoff prompts (required)
```

If the repo already uses `docs/epics/`, `docs/backend/epics/`, or `docs/epics-*/`, **keep those paths**. Put only phase/queue overlays under `docs/dev-pipeline/`.

### Greenfield vs mid-flight

| Command | Use when |
|---------|----------|
| `init` | Little/no product docs; bootstrap empty layout |
| `adopt` | Project already developing; docs tree exists — read it, map state, overlay pipeline |

`adopt` details: [adopt.md](adopt.md). Do not duplicate existing doc bodies; link and cite paths with Observed / Inferred / Unknown.

## ID scheme (stable, token-cheap)

| Kind | Pattern | Example |
|------|---------|---------|
| Phase | `PH-{NN}` | `PH-01` |
| Epic | `EPIC-{SUFFIX}` | `EPIC-ASK` |
| Feature | `{SUFFIX}-{NN}` | `ASK-01` |
| Task | `TASK-{FEATURE}-{NN}` | `TASK-ASK-01-01` |
| Rework | `{TASK-ID}-R{N}` | `TASK-ASK-01-01-R1` |

Rules:

- `{SUFFIX}` = short uppercase token (2–8 chars), unique across the product.
- Never reuse or renumber IDs. Cancel or supersede instead.
- Feature IDs appear in queues, commits messages (optional), and prompts — keep them scannable.
- One **task** = one agent session of work (small enough for clear AC).

## Status legend

| Status | Meaning |
|--------|---------|
| `todo` | Not started |
| `ready` | Deps met; can be prompted |
| `in_progress` | Prompt issued / work underway |
| `blocked` | Waiting on dependency or decision |
| `partial` | Usable but incomplete |
| `done` | AC + DoD met (after review PASS) |
| `cancelled` | Will not do |
| `superseded` | Replaced by another ID (link it) |

## Priority

Use `P0` (blocking product), `P1` (high), `P2` (normal), `P3` (later).  
Queue order = active phase → `P0`…`P3` → explicit `order` column → Feature ID.

## Dependency fields (required on features/tasks)

| Field | Meaning |
|-------|---------|
| `depends_on` | Must be `done` (or accepted `partial`) before start |
| `co_req` | Should ship in the same phase window; coordinate contracts |
| `blocks` | IDs that cannot proceed until this is done |
| `blocked_by` | Inverse view (optional; can be derived) |

## `PHASES.md` template

```markdown
# Phases

**Active:** `PH-01`

| Phase ID | Slug | Status | Goal (one line) | Queue |
|----------|------|--------|-----------------|-------|
| PH-01 | frontend-mvp | active | … | [TASK-QUEUE](./phases/PH-01-frontend-mvp/TASK-QUEUE.md) |
| PH-02 | backend-api | parked | … | [TASK-QUEUE](./phases/PH-02-backend-api/TASK-QUEUE.md) |
```

## Phase `README.md` (minimum)

- Goal, in-scope surfaces (frontend / backend / …)
- Status: `active` | `parked` | `done`
- Contract freeze: which API/DTO/entity docs are authoritative for this phase
- Switch notes: why parked / what remains
- Links to epic suite(s)

## Phase `CONTEXT.md` (minimum)

Compact tables only:

```markdown
# PH-01 context

## Entities ↔ modules
| Entity | Module / path | Notes |
|--------|---------------|-------|

## API / DTO contracts
| Contract | Path | Consumers |
|----------|------|-----------|

## Invariants (do not break across phases)
- …

## Changed by
| Task / event | Note |
|--------------|------|
| adopt | Initial seed from docs root `…` (if applicable) |
```

After `adopt`, seed tables from `ADOPTION.md` authoritative paths (paths + short notes only).

## `TASK-QUEUE.md` template

```markdown
# TASK-QUEUE — PH-01

| Order | Task ID | Feature | Title | Priority | Status | depends_on | blocks | Prompt |
|------:|---------|---------|-------|----------|--------|------------|--------|--------|
| 1 | TASK-ASK-01-01 | ASK-01 | Accept answer API+UI | P0 | ready | — | ASK-02 | |
```

Update the Prompt column to `agent-prompts/TASK-….md` when emitted.

## Epic file (minimum feature table)

```markdown
# EPIC-ASK — …

**Epic ID:** `EPIC-ASK`

| Feature ID | Feature | Status | Priority | depends_on | co_req | blocks |
|------------|---------|--------|----------|------------|--------|--------|
| ASK-01 | … | todo | P0 | — | — | ASK-02 |

## ASK-01 — title

**Status:** todo

### Acceptance
- …

### Links
- Entity: `docs/…`
- Contract: `docs/…`
```

## PRODUCT.md (minimum)

- Name + one-sentence identity
- Surfaces in scope (e.g. frontend only / frontend+backend)
- Non-goals
- Link to architecture + active phase

When created by `adopt`, prefer linking Observed identity sources over rewriting them. Point to `docs/dev-pipeline/ADOPTION.md`.

## `ADOPTION.md` (mid-flight)

Written by `adopt` / `adopt --refresh`. Holds:

- Docs root + discovery rule
- Source map (category → path → evidence)
- Built vs open table
- Authoritative contract/entity/decision paths
- Unknowns / blockers
- Next suggested commands

Full template: [adopt.md](adopt.md).

## Gitignore

Ensure:

```gitignore
agent-prompts/
```

Keep existing `bolt-prompts/` ignore entries if present.
