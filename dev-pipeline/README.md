# Dev Pipeline — User Guide

> **Human-only** — for people learning the workflow. Agents must follow `SKILL.md` and [../shared/inspect.md](../shared/inspect.md); do not treat this file as agent procedure.

**Skill:** `dev-pipeline` · **Version:** 1.7.0 · **Activation:** `/dev-pipeline …`

This skill tracks product development as **token-efficient, ID-linked docs** so you (and multiple AI agents) can move through frontend, backend, and other services without losing business logic, contracts, user stories, or backlog integrity.

It **writes and maintains documentation + task handoff prompts**. It does **not** implement application code unless you separately ask for that.

**Companions**

| When… | Run… | Role |
|--------|------|------|
| You need product tracking (phases, briefs, stories, backlog, queue handoffs) | `/dev-pipeline …` | This skill |
| A queued task needs a **deep** repo-aware engineering spec | `/promptize` after `next`, or `next --promptize` | Promptize skill (companion) |
| Ad-hoc work **not** on the pipeline queue | `/promptize` (optionally `--execute`) | Promptize alone |
| An implementer finishes a task | `/commit` | Commit skill |
| A commit/push lands | `/review-task` | Review-task skill |

**Do not** use Promptize instead of `brief` / `story` / `backlog` / `adopt` — those update durable product docs. Promptize expands a **short engineering ask** (inspect repo → structured spec); the pipeline owns **what the product is and which task is next**.

---

## Table of contents

1. [What this skill is for](#1-what-this-skill-is-for)
2. [Core concepts](#2-core-concepts)
3. [Quick start](#3-quick-start)
4. [Command reference](#4-command-reference)
5. [Flags](#5-flags)
6. [Use cases (walkthroughs)](#6-use-cases-walkthroughs)
7. [Document layout in your repo](#7-document-layout-in-your-repo)
8. [IDs, statuses, and priorities](#8-ids-statuses-and-priorities)
9. [Multi-agent workflow](#9-multi-agent-workflow)
10. [Safety rules](#10-safety-rules)
11. [What this skill will not do](#11-what-this-skill-will-not-do)
12. [Reference docs (for agents)](#12-reference-docs-for-agents)

---

## 1. What this skill is for

Use **dev-pipeline** when you need a durable product tracker across sessions and agents:

- Bootstrap or attach a backlog for a product (greenfield or mid-flight)
- Describe phase capabilities in natural language and turn them into docs/backlog **without duplicate churn**
- Capture **user stories** as durable **product-wide SHARED** business-flow docs (not owned by one service); every task must cite related stories and check which flows are still open
- On mid-flight projects, **extract** user stories from already-implemented features into that shared spine
- Switch between frontend / backend / integration **phases** without breaking IDs or contracts
- Keep one **shared source of truth** for APIs, DTOs, entities, business rules, and user stories across all services
- Emit a **self-contained task prompt** for another agent to implement

Trigger it with `/dev-pipeline …` or clear natural language (e.g. «پایپلاین توسعه», «adopt از روی docs», «brief فاز», «یوزر استوری», «استخراج استوری», «شروع بک‌اند»).

---

## 2. Core concepts

### Docs are the source of truth

Code follows tracked epics, features, and tasks. Do not invent backlog state that is not reflected in files.

### Phases are responsibility windows

A phase is not a git branch. Examples: `frontend-mvp`, `backend-api`, `integrations`. You can **park** an incomplete phase, activate another, and resume later — IDs and contracts stay stable.

Lifecycle: `intake → active → parked ⇄ active → done`  
**Invariant:** at most one **active** phase.

### Shared source of truth (SHARED)

`docs/dev-pipeline/SHARED.md` is the **product-wide contract spine**:

- Surfaces (`SUR-*`): frontend, backend, worker, mobile, BFF, …
- Authoritative paths: entities, API/DTO, business rules, **user stories / flows**, architecture, ADRs

When you add a backend during or after frontend (or any new service), **phases + SHARED** are the whole source of truth. New services **inherit** that spine — they must not invent a parallel API/DTO tree.

### Briefs with claim deduplication

You describe what a phase should deliver in prose. The skill stores the brief, classifies claims (`new` / `duplicate` / `refinement` / `contradiction`), and only applies **new** (and allowed refinement) deltas to business rules and backlog. Repeats do not rewrite docs.

### User stories (business flows)

You describe user journeys in prose, **or** extract them from already-shipped features on a mid-flight project. The skill stores each story as its own file under `docs/user-stories/` (`US-*`), with ordered **flows** (`US-*-F*`) treated as **business logic** on the **SHARED** spine — **not** owned by frontend, backend, or any single service. All surfaces consume the same `US-*` files.

When `/dev-pipeline next` emits a task, the prompt **must** cite related stories and state which flows this task covers vs leaves open — a story is not complete until all non-cancelled flows are done.

**Brief vs story**

| | `brief` | `story` |
|--|---------|---------|
| Scope | Phase-local capability claims | Product-wide user-facing flows (SHARED) |
| Artifacts | `briefs/BRIEF-*`, `CLAIMS.md` | `docs/user-stories/US-*.md`, `INDEX.md` |
| Dedup unit | Claim `CLM-*` | Story `US-*` + flow `US-*-F*` |
| Role | Intake → additive rules/backlog | Durable narrative + flows agents must honor |

`brief` may suggest creating a story when a claim is clearly a user journey. Prefer an explicit `story` (or `story extract` after `adopt`) for flow-level SoT. Full rules: [user-stories.md](user-stories.md).

### Task prompts are handoffs

`/dev-pipeline next` writes `agent-prompts/{TASK-ID}.md` (gitignored). Hand that file to an implementing agent. After work: `/commit`, then `/review-task`.

### Promptize (companion skill)

**Where it fits:** after a pipeline handoff (or for work outside the queue) — **not** inside `brief` / `story` / `backlog` / phase ops.

| Situation | What to run |
|-----------|-------------|
| Normal backlog task | `/dev-pipeline next` → implement from `agent-prompts/` |
| Task is complex / cross-cutting / fuzzy AC | `/dev-pipeline next --promptize` **or** `next` then `/promptize --save-to-file docs/promptize-prompts/{TASK-ID}.md …` |
| Spike / bugfix not tracked as a Feature/Task | `/promptize …` (optionally `--execute`) — no pipeline write |
| Capture product journeys or phase claims | `/dev-pipeline story` / `brief` — **not** Promptize |

Pipeline handoffs stay the ID / SHARED / `US-*` anchor. Promptize adds a **deeper engineering spec** (repo inspection, impact, edge cases). Saved deep specs default to `docs/promptize-prompts/{TASK-ID}.md`.

---

## 3. Quick start

### A. Brand-new product (greenfield)

```text
/dev-pipeline init MyProduct
/dev-pipeline backlog
/dev-pipeline phase new frontend-mvp --set-active
/dev-pipeline brief Users can sign up, log in, and reset password. …
/dev-pipeline story As a new user I want to sign up with email so that I can access my account. …
/dev-pipeline next
```

`init` also stubs `docs/user-stories/` (`README.md`, `INDEX.md`, empty `intake/`) and indexes that path in SHARED.

### B. Existing project that already has docs (mid-flight)

```text
/dev-pipeline adopt
/dev-pipeline status
/dev-pipeline story extract          # harvest US-* from shipped features → SHARED
/dev-pipeline backlog
/dev-pipeline phase new frontend-mvp --set-active
/dev-pipeline next
```

Prefer **`adopt`** over **`init`** when a real docs tree already exists. If use-case docs already exist, `adopt` maps them into SHARED; use `story extract` (or `adopt --extract-stories`) to allocate `US-*` overlays without rewriting bodies. Stories stay product-wide — not owned by the intake phase or one service.

### C. Frontend underway — starting backend (same product spine)

```text
/dev-pipeline shared refresh
/dev-pipeline surface new backend --kind backend --phase-slug backend-api --set-active
/dev-pipeline brief Backend must expose the auth and profile APIs already frozen for the frontend. …
/dev-pipeline stories status   # confirm which US-* flows still open across surfaces
/dev-pipeline next
```

---

## 4. Command reference

| Command | What it does | Typical next step |
|---------|--------------|-------------------|
| `init [name]` | Bootstrap `docs/`, `PHASES.md`, stub `SHARED.md`, stub `user-stories/`, product identity | `backlog` or `phase new` |
| `adopt` (`import`, `from-docs`) | Attach pipeline to existing docs; write `ADOPTION.md`; create-if-missing overlays | `story extract`, `backlog`, `shared`, `phase new` |
| `backlog` / `plan` | Create/update epics & features with stable IDs | `phase new`, `story`, or `next` |
| `phase new <slug>` | Create a phase folder + queue; optional first brief from trailing prose | `brief`, `story`, or `next` |
| `phase switch <PH-ID>` | Park current active; activate another; refresh CONTEXT from SHARED | `next` or `status` |
| `phase status` | Active phase + epic/feature summary | — |
| `brief [PH-ID] …` | Ingest user prose → claims → additive docs/backlog | `story` / `next` or resolve contradictions |
| `story …` | Create/refine product-wide `US-*` stories + flows from prose | `next` or link features |
| `story extract` / `stories extract` | Harvest `US-*` from implemented/shipped features into SHARED | `stories status` / `next` |
| `stories` / `story status` | Coverage report: open vs done flows (read-mostly) | `story` or `next` |
| `shared` / `shared status` | Show SHARED surfaces + authoritative paths | `surface new` or `next` |
| `shared refresh` | Additive rebuild of SHARED index from docs/phases | `surface new` or `phase switch` |
| `surface new <slug>` | Register a new surface/service on SHARED; optional phase | `brief` / `story` / `next` |
| `next` / `task` | Emit next ready task prompt under `agent-prompts/` (cites related `US-*` + flow coverage) | Implement → `/commit` → `/review-task` |
| `next --promptize` / `task … --promptize` | Same handoff **plus** deepen via Promptize → `docs/promptize-prompts/{TASK-ID}.md` | Implement (prefer deep spec + honor pipeline IDs) |
| `task <FEATURE-ID>` | Emit prompt for a specific feature/task | Same handoff |
| `status` | Compact overview: phase, surfaces, blockers, next ready IDs | — |

Aliases for brief: `tell`, `phase brief`, `intake-notes`.  
Aliases for story: `user-story`, `stories`, `us`.  
Aliases for extract: `stories extract`, `story harvest`.

---

## 5. Flags

Flags may appear anywhere after `/dev-pipeline`.

| Flag | Used with | Meaning |
|------|-----------|---------|
| `--set-active` | `phase new`, `adopt`, `surface new` | Mark new/intake phase (and surface) active |
| `--suite <dir>` | backlog / adopt | Epic suite folder under `docs/` |
| `--docs <dir>` | `adopt` | Docs root to scan |
| `--refresh` | `adopt` | Rebuild adoption snapshot + CONTEXT/SHARED links only |
| `--extract-stories` | `adopt` | After adopt, run one `story extract` pass |
| `--phase PH-XX` | `brief`, `story` | Target phase (else Active phase); for `story` tags links only (does not switch phase) |
| `--brief-only` | `brief` | Record claims only; skip backlog/business-rule writes |
| `--story-only` | `story` | Persist story files + INDEX only; skip backlog/rule/queue writes |
| `--from-docs-only` | `story extract` | Docs/ADOPTION only; no code-path inference |
| `--include-partial` | `story extract` | Also harvest `partial` features |
| `--force-new` | `brief`, `story` | Treat near-duplicates as new only if you insist (still never renumber IDs) |
| `--kind <kind>` | `surface new` | `frontend` \| `backend` \| `worker` \| `mobile` \| `bff` \| `shared-lib` \| `other` |
| `--phase-slug <slug>` | `surface new` | Also create a phase for that surface |
| `--promptize` | `next`, `task` | Also run Promptize deepen; save under `docs/promptize-prompts/{TASK-ID}.md` (prompt-only unless you separately ask execute) |
| `--dry-run` | most writers | Report planned writes; write nothing |

---

## 6. Use cases (walkthroughs)

### Use case 1 — Greenfield product from scratch

**Goal:** Empty or nearly empty repo; establish identity, backlog, first phase, stories, first task.

```text
/dev-pipeline init AcmeBoard
/dev-pipeline backlog
/dev-pipeline phase new frontend-mvp --set-active Users can create boards, lists, and cards.
/dev-pipeline story As a board owner I want to create a board so that I can organize work.
/dev-pipeline status
/dev-pipeline next
```

**What you get**

- `docs/PRODUCT.md`, architecture/roadmap stubs or links
- `docs/dev-pipeline/PHASES.md`, `SHARED.md` (includes user-stories path when seeded)
- Stub `docs/user-stories/` (`README.md`, `INDEX.md`, `intake/`)
- Phase folder with `TASK-QUEUE.md`, `CONTEXT.md`, optional first `BRIEF-001`
- `US-*` story file(s) when you ran `story`
- One prompt under `agent-prompts/` (with related stories + flow coverage when user-facing)

---

### Use case 2 — Adopt a mid-flight documented project

**Goal:** Development already started; docs exist; attach the tracker without wiping anything.

```text
/dev-pipeline adopt
# or: /dev-pipeline adopt --docs documentation/
# or: /dev-pipeline adopt --extract-stories   # also harvest US-* in the same turn
/dev-pipeline adopt --refresh   # later, to refresh the source map only
```

**What you get**

- `docs/dev-pipeline/ADOPTION.md` (source map, built vs open, authoritative paths, unknowns)
- Create-if-missing only: PRODUCT / ARCHITECTURE / ROADMAP links, `PH-00-intake`, seeded `SHARED.md` (user-stories path for **all** surfaces)
- Existing use-case / user-story trees noted in ADOPTION + SHARED (bodies not rewritten)
- With `--extract-stories` (or a follow-up `story extract`): product-wide `US-*` from shipped features
- **No** invented APIs; **no** task prompts yet

Then confirm stories + backlog and leave intake:

```text
/dev-pipeline story extract   # if you did not pass --extract-stories
/dev-pipeline backlog
/dev-pipeline phase new frontend-mvp --set-active
```

---

### Use case 3 — Brief a phase (natural-language product input)

**Goal:** Tell the agent what this phase must deliver; update rules/backlog only for **new** claims.

```text
/dev-pipeline brief PH-01
Auth: email/password login, JWT sessions, password reset via email.
Boards are private to the owner unless shared by link.
```

Or after creating a phase, put prose on the same line as `phase new` (becomes `BRIEF-001`).

**Behavior**

| Claim class | Effect |
|-------------|--------|
| `new` | May update business-rules + additive backlog; may extend SHARED paths |
| `duplicate` | Ledger note only — no doc churn |
| `refinement` | Narrow additive update when allowed |
| `contradiction` | **Stops**; asks you; leaves IDs alone |

Use `--brief-only` to record claims without touching backlog yet. Use `--dry-run` to preview.

When a claim is clearly a user journey, follow with `/dev-pipeline story …` (or accept the agent’s suggestion). Default `brief` alone does **not** create `US-*` files.

---

### Use case 4 — Create user stories (business flows)

**Goal:** Persist user journeys as durable business-logic docs with ordered flows; keep coverage visible.

```text
/dev-pipeline story
As a board owner I want to invite a collaborator by email so that we can edit the same board.
If the invitee already has an account, attach them; otherwise send a signup invite link.
```

Refine an existing story:

```text
/dev-pipeline story US-001
Also: expired invite links must show a clear resend action.
```

**What you get**

- `docs/user-stories/intake/STORY-….md` (verbatim + classification)
- `docs/user-stories/US-….md` (narrative, business logic, flows `US-…-F…`)
- Updated `INDEX.md` (coverage: flows done/total)
- Optional links into business-rules / features / queue (unless `--story-only`)
- SHARED path row for user-stories when missing

**Classification** (same idea as briefs): `new` → write story/flows; `duplicate` → INDEX note only; `refinement` → additive; `contradiction` → ask first.

Check gaps anytime:

```text
/dev-pipeline stories status
# aliases: /dev-pipeline story status
```

When you later run `next`, the task prompt cites related `US-*` and lists which flows this task covers vs leaves open. A story stays incomplete while any non-cancelled flow is not `done`.

---

### Use case 4b — Extract stories from implemented features (mid-flight)

**Goal:** Project already developing; reverse-map shipped capabilities into the SHARED user-story spine so every surface shares the same journeys.

```text
/dev-pipeline story extract
# options:
/dev-pipeline story extract --from-docs-only
/dev-pipeline story extract --include-partial
/dev-pipeline stories extract --dry-run
```

**Sources (evidence-ordered):** ADOPTION Built vs open → done features → existing journey docs → PRODUCT/ROADMAP/CHANGELOG → optional code paths (unless `--from-docs-only`).

**Rules**

- `origin: extracted`; flows marked `done` only with Observed evidence
- Stories indexed in SHARED with consumers **all** — never `docs/backend/user-stories/` forks
- Dedup against INDEX; duplicates do not rewrite bodies
- Does not emit `agent-prompts/` or change in-flight task statuses

---

### Use case 5 — Shape or refresh the backlog

**Goal:** Epics/features with stable IDs, deps, priorities, links to contracts and user stories.

```text
/dev-pipeline backlog
# alias: /dev-pipeline plan
```

Does **not** emit an implementer prompt unless you also ask for `next` / `task`. Prefer feature **Links** that cite `docs/user-stories/US-….md` (and flow IDs) when the feature is user-facing.

---

### Use case 6 — Switch phases without breaking work

**Goal:** Pause frontend; start (or resume) backend; keep IDs and contract spine.

```text
/dev-pipeline phase switch PH-02
/dev-pipeline status
/dev-pipeline stories status
/dev-pipeline next
```

On switch the skill:

1. Writes switch notes on the previous phase (done / remains / blockers / freeze)
2. Parks previous; activates target
3. Refreshes target `CONTEXT.md` from **SHARED** (additive)
4. Does **not** renumber IDs or rewrite completed acceptance criteria

Phases **link** stories; they do not own a parallel story tree. Resume frontend later with `phase switch PH-01` again.

---

### Use case 7 — Add backend (or any new service) after/during frontend

**Goal:** New surface shares the same SoT as existing phases.

```text
/dev-pipeline shared                    # inspect spine
/dev-pipeline shared refresh            # optional: re-index paths from docs/phases
/dev-pipeline surface new backend \
  --kind backend \
  --phase-slug backend-api \
  --set-active
/dev-pipeline brief Backend implements the frozen auth and board APIs; additive pagination on list endpoints.
/dev-pipeline stories status            # which US-* flows still need backend work
/dev-pipeline next
```

**Rules**

- One contract spine in `SHARED.md` (including user-stories path)
- Phase freezes **point into** SHARED — no private fork
- Task prompts include a **Shared source of truth** section and **Related user stories** when user-facing
- Breaking changes need an explicit task + dual-surface note

Same pattern for `worker`, `mobile`, `bff`, etc. (`--kind`).

---

### Use case 8 — Emit the next implementer task

**Goal:** One ready queue item → one self-contained prompt file.

```text
/dev-pipeline next
# or force a feature:
/dev-pipeline task ASK-01
```

**Then**

1. Open `agent-prompts/TASK-….md` (or hand it to another agent/chat)
2. Implement only that task (honor cited `US-*` business logic + flow steps/AC)
3. `/commit`
4. `/review-task {TASK-ID}` → PASS (next) or FAIL (rework prompt)

Selection prefers: active phase → ready deps → priority → rework before next feature.

The emitted prompt includes **Related user stories** + a **flow coverage check** when the work is user-facing (see [user-stories.md](user-stories.md) and [prompt-template.md](prompt-template.md)):

- Which `US-*` / flows this task covers
- Which flows stay open (and whether a follow-up task exists)
- Do not claim the whole story `implemented` early

**Deepen with Promptize (optional)** when the task is complex or AC/contracts are still fuzzy:

```text
/dev-pipeline next --promptize
# or after a normal next:
/promptize --save-to-file docs/promptize-prompts/TASK-ASK-01-01.md \
  Implement TASK-ASK-01-01 per agent-prompts handoff; honor US-001 flows F01–F02 and SHARED contracts.
```

The pipeline file under `agent-prompts/` remains the tracking anchor; the Promptize file is the deep engineering spec.

---

### Use case 9 — Multi-agent split (planner / implementer / reviewer)

| Role | Who | Action |
|------|-----|--------|
| Planner / tracker | You + `/dev-pipeline` | init/adopt, brief, story, backlog, phase, shared, next |
| Spec deepener (optional) | You + `/promptize` | After `next`, or `next --promptize`; ad-hoc work off-queue |
| Implementer | Separate agent/session | Reads `agent-prompts/*.md` (+ optional `docs/promptize-prompts/{TASK-ID}.md`) and linked `US-*` |
| Reviewer | `/review-task` | PASS → user runs `/dev-pipeline next`; FAIL → rework prompt |

Agents do not need shared chat history: **SHARED + phase CONTEXT + user stories + prompt** (+ optional Promptize deep spec) carry the product identity.

**Context load order** (for implementers reading docs): PRODUCT → SHARED → ADOPTION (if any) → active phase → CLAIMS → user-stories INDEX / linked `US-*` → queue row → epic feature → cited contracts / business rules → optional `docs/promptize-prompts/{TASK-ID}.md`.

---

### Use case 10 — Promptize with (or without) the pipeline

**Goal:** Know exactly where Promptize belongs relative to this skill.

**A. Queued product work (recommended path)**

```text
/dev-pipeline next                 # compact handoff → agent-prompts/TASK-….md
/dev-pipeline next --promptize     # same + deep spec → docs/promptize-prompts/TASK-….md
```

Implementer follows the handoff IDs/stories/SHARED; uses the Promptize file for detailed approach/AC/impact when present.

**B. Ad-hoc engineering (no backlog row)**

```text
/promptize fix pagination off-by-one on board list
/promptize --execute …
```

No `TASK-*` required. If you later want it tracked, add a backlog/queue item via `/dev-pipeline backlog` / `story`, then use `next`.

**C. Never substitute Promptize for**

| Instead of… | Use… |
|-------------|------|
| Phase capability intake | `brief` |
| User journeys / flows | `story` |
| Epic/feature shaping | `backlog` |
| Mid-flight attach | `adopt` |
| Phase create/switch | `phase …` |

---

### Use case 11 — Status check / unblock planning

```text
/dev-pipeline status
/dev-pipeline phase status
/dev-pipeline shared status
/dev-pipeline stories status
```

Use when you need a compact picture of active phase, surfaces, blockers, next ready IDs, and **open story flows** without writing files.

---

### Use case 12 — Dry-run before writing

```text
/dev-pipeline adopt --dry-run
/dev-pipeline brief --dry-run Password reset must use 6-digit OTP instead of email link.
/dev-pipeline story --dry-run As a user I want to cancel an order before shipment.
/dev-pipeline shared refresh --dry-run
```

Reports planned reads/writes; does not mutate docs (except optional preview behavior defined by the command).

---

### Use case 13 — Persian / natural-language activation

Examples of intents that map to the same commands:

| You say | Maps to |
|---------|---------|
| «پایپلاین توسعه را init کن» | `init` |
| «از روی مستندات وصل کن» / adopt | `adopt` |
| «درباره این فاز بگو» / brief فاز | `brief` |
| «یوزر استوری» / user story / داستان کاربری / فلوی بیزنس | `story` |
| «استخراج استوری» / از فیچرهای پیاده‌شده استوری بساز | `story extract` |
| «پوشش استوری» / وضعیت فلوی استوری | `stories status` |
| «سرویس جدید بک‌اند» / شروع بک‌اند | `surface new` (+ phase) |
| «وضعیت پایپلاین» | `status` |
| «تسک بعدی» | `next` |
| «این تسک را عمیق‌تر مشخص کن» / promptize این task | `next --promptize` or `/promptize` on the task |
| «یک اسکیپ مهندسی جدا» (off-queue) | `/promptize` alone |

---

## 7. Document layout in your repo

Created or linked as needed (existing trees are **extended**, not duplicated):

```text
docs/
  PRODUCT.md
  ARCHITECTURE.md          # or link
  ROADMAP.md               # or link
  business-rules/          # optional; from briefs / stories
  user-stories/            # product-wide SHARED business flows (not surface-owned)
    README.md
    INDEX.md
    intake/
    US-001.md
  epics/                   # or docs/<suite>/
  dev-pipeline/
    PHASES.md
    SHARED.md              # surfaces + contracts + user-stories path (consumers: all)
    ADOPTION.md
    phases/
      PH-01-frontend-mvp/
        README.md
        CONTEXT.md
        TASK-QUEUE.md
        briefs/
          CLAIMS.md
          BRIEF-001.md

agent-prompts/             # gitignored handoff prompts
docs/promptize-prompts/    # optional deep specs from Promptize companion
```

If the repo already has `docs/epics/` or `docs/backend/epics/`, those paths stay authoritative for epic IDs; phase overlays live under `docs/dev-pipeline/`.  
If the repo already has use-case / user-story docs, **extend** them and map into `INDEX.md` / SHARED — do **not** fork a second tree per service.

---

## 8. IDs, statuses, and priorities

| Kind | Pattern | Example |
|------|---------|---------|
| Phase | `PH-{NN}` | `PH-01` |
| Surface | `SUR-{NN}` | `SUR-02` |
| Epic | `EPIC-{SUFFIX}` | `EPIC-ASK` |
| Feature | `{SUFFIX}-{NN}` | `ASK-01` |
| Task | `TASK-{FEATURE}-{NN}` | `TASK-ASK-01-01` |
| Rework | `{TASK-ID}-R{N}` | `TASK-ASK-01-01-R1` |
| Brief / claim | `BRIEF-{NNN}` / `CLM-{NNN}` | per phase |
| User story / flow / intake | `US-{NNN}` / `US-{NNN}-F{NN}` / `STORY-{NNN}` | product-wide |

**Never renumber or reuse IDs.** Cancel or supersede instead.

**Statuses (features/tasks):** `todo` · `ready` · `in_progress` · `blocked` · `partial` · `done` · `cancelled` · `superseded`

**Statuses (stories):** `draft` · `active` · `partial` · `implemented` · `superseded` · `cancelled`  
**Statuses (flows):** `todo` · `partial` · `done` · `cancelled` · `superseded` — a story is `implemented` only when all non-cancelled flows are `done`.

**Priorities:** `P0` (blocking) → `P3` (later)

**Deps:** `depends_on`, `co_req` (same-window contract coordination), `blocks`, optional `blocked_by`

---

## 9. Multi-agent workflow

```text
┌─────────────────┐     agent-prompts/*.md      ┌──────────────┐
│  /dev-pipeline  │ ──────────────────────────► │ Implementer  │
│  (planner)      │     optional:               └──────┬───────┘
└────────▲────────┘     docs/promptize-prompts/        │
         │              via /promptize                 │
         │              /commit                        │
         │              /review-task                   ▼
         │         ┌──────────────┐             code + commit
         └─────────┤   Reviewer   │◄────────────────────
                   └──────────────┘
```

SHARED + user stories keep frontend and backend agents aligned when phases are parked or parallelized. Promptize deepens a single task without replacing the pipeline spine.

---

## 10. Safety rules

- Do not overwrite unrelated dirty working-tree edits; surface overlaps first
- Do not delete epic/feature/story history — use `cancelled` / `superseded`
- Do not invent stack, APIs, or architecture — tag **Observed / Inferred / Unknown**
- Do not add npm/pip dependencies via this skill
- Do not implement product features unless you also asked for implementation
- Destructive doc wipes require explicit confirmation
- Briefs must never renumber IDs or disturb `in_progress` / `done` / `review` tasks
- User stories must never renumber `US-*` / flow IDs; duplicates must not rewrite story bodies; do not mark a story `implemented` while flows remain open; do not fork surface-local story trees
- Do not fork a second contract spine for a new surface — extend `SHARED.md`

---

## 11. What this skill will not do

- Replace `/promptize` for one-off engineering specs — **or** pretend Promptize replaces `brief` / `story` / `backlog`
- Open PRs, force-push, or run destructive git
- Rewrite legacy epic IDs
- Invent a full backlog from thin air during `adopt` (use `backlog` with confirmation)
- Reshuffle/renumber the backlog via `brief`
- Auto-create `US-*` files from every `brief` (use `story` / `story extract` for journeys)
- Delete or renumber user stories/flows, or mark stories complete with open flows
- Treat user stories as owned by one frontend/backend/service (they are SHARED)
- Own `/commit` or `/review-task` flows (use those skills)
- Use the full Promptize template as the default `agent-prompts/` body (deep specs are optional under `docs/promptize-prompts/`)

---

## 12. Reference docs (for agents)

Authoritative mechanics live next to this README:

| File | Topic |
|------|--------|
| [SKILL.md](SKILL.md) | Activation, workflow, safety (agent entrypoint) |
| [schema.md](schema.md) | Folder layout, IDs, templates |
| [phases.md](phases.md) | Phase lifecycle, switch, contract freeze |
| [shared.md](shared.md) | SHARED.md, surfaces, multi-service SoT |
| [briefing.md](briefing.md) | Brief ingestion + claim dedup |
| [user-stories.md](user-stories.md) | User stories + flow coverage |
| [adopt.md](adopt.md) | Mid-flight attach from existing docs |
| [prompt-template.md](prompt-template.md) | Task / rework prompt format |

---

## Cheat sheet

```text
# Greenfield
/dev-pipeline init MyApp
/dev-pipeline backlog
/dev-pipeline phase new frontend-mvp --set-active …
/dev-pipeline story …
/dev-pipeline next

# Mid-flight
/dev-pipeline adopt
/dev-pipeline story extract       # or: adopt --extract-stories
/dev-pipeline backlog

# Describe capabilities (phase claims)
/dev-pipeline brief …

# Durable user stories + flow coverage
/dev-pipeline story …
/dev-pipeline story US-001 …   # refine
/dev-pipeline stories status

# Backend after/during FE
/dev-pipeline shared refresh
/dev-pipeline surface new backend --kind backend --phase-slug backend-api --set-active

# Ship work
/dev-pipeline next
/dev-pipeline next --promptize    # optional deep engineering spec
# → implement → /commit → /review-task TASK-…

# Ad-hoc (off-queue)
/promptize …

# Orient
/dev-pipeline status
/dev-pipeline stories status
```
