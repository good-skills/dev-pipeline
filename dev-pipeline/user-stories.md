# User stories (business flows → durable SoT)

Read from `SKILL.md` when running `/dev-pipeline story` (aliases: `user-story`, `stories`, `us`).

**Purpose:** Let the user describe product behavior as **user stories**, or **extract** stories from already-implemented features on a mid-flight project. Persist each story as its own file under `docs/user-stories/`. Treat stories as **product-wide shared SoT** (business-logic peers to business rules) — they are **not** owned by a single surface, service, or phase. When emitting or selecting tasks, agents **must** cite related stories and verify whether each story’s **flows** are implemented, partial, or still open.

## Product-wide ownership (non-negotiable)

| Rule | Meaning |
|------|---------|
| Shared SoT | `docs/user-stories/` is indexed in `docs/dev-pipeline/SHARED.md` (category: User stories / flows) |
| Not surface-owned | Do **not** create `docs/frontend/user-stories/` or per-service story spines; all surfaces **consume** the same `US-*` files |
| Not phase-owned | Phases may **link** stories; they do not own a parallel tree under the phase folder |
| Consumers | SHARED consumers column for user-stories = **all** registered surfaces (or `all`) unless a story is explicitly non-applicable (rare — document why) |
| New services | Backend/worker/mobile **inherit** existing `US-*`; they must not redefine journeys for “just this service” |

## Brief vs story

| | `brief` | `story` |
|--|---------|---------|
| Scope | Phase-local capability claims | Product-wide user-facing flows (SHARED) |
| Primary artifacts | `briefs/BRIEF-*`, `CLAIMS.md` | `docs/user-stories/US-*.md`, `INDEX.md` |
| Dedup unit | Claim `CLM-*` | Story `US-*` + flow `US-*-F*` |
| Role | Intake → additive rules/backlog | Durable narrative + ordered flows agents must honor |

`brief` may **link** or suggest creating a story when a claim is clearly a user journey; it must not silently replace story files. Prefer an explicit `story` command for flow-level SoT.

## When to use

| Situation | Command |
|-----------|---------|
| Capture a user journey / business flow in durable form | `story <prose…>` |
| Add or refine flows on an existing story | `story US-XX …` or prose that matches INDEX |
| Mid-flight project: derive stories from **implemented** features/docs | `story extract` / `stories extract` |
| After `adopt`, fill SHARED story spine from Built vs open | `story extract` (or `adopt --extract-stories`) |
| See coverage (which flows still open) | `story status` / `stories status` |
| Dry classification only | `story --dry-run …` / `story extract --dry-run` |

Not a substitute for `/dev-pipeline backlog` epic shaping — stories bind **business behavior**; backlog binds **delivery units**. Link them.

## Activation forms

```text
/dev-pipeline story <user prose…>
/dev-pipeline story US-01 <refinement prose…>
/dev-pipeline story extract
/dev-pipeline stories extract
/dev-pipeline story harvest
/dev-pipeline user-story <…>
/dev-pipeline stories
/dev-pipeline stories status
/dev-pipeline us <…>
```

Flags:

| Flag | Meaning |
|------|---------|
| `--dry-run` | Classify / report planned writes; write nothing |
| `--story-only` | Persist story files + INDEX only; do **not** touch backlog, business-rules, or queues |
| `--phase PH-XX` | Tag story with phase **link** only (does not switch phase; does not make the story phase-owned) |
| `--force-new` | Treat near-duplicate narrative as a new story only if user insists (still never renumber IDs) |
| `--from-docs-only` | With `extract`: only use docs/ADOPTION evidence; do not infer from code paths |
| `--include-partial` | With `extract`: also harvest features marked `partial` (default: prefer `done` / Observed shipped) |

Natural language: «یوزر استوری», «user story», «داستان کاربری», «فلوی بیزنس», «استخراج استوری», «از فیچرهای پیاده‌شده استوری بساز».

## Hard invariants (non-negotiable)

1. **Never renumber or reuse** `US-*` or flow IDs `US-{NN}-F{NN}`.
2. **Never delete** prior story files or intake sessions; supersede or cancel instead.
3. **Never change** status of tasks that are `in_progress`, `review`, `done`, or `rework_required` as a side effect of `story` / `story extract`.
4. **Never park/switch/activate** phases as a side effect of `story` / `story extract`.
5. **Duplicates do not rewrite** story bodies (INDEX “seen again” note only), unless classified as **refinement**.
6. **Contradictions** with absorbed stories, `SHARED.md`, or frozen contracts → **ask** before changing anything.
7. Stories are **business logic**: task prompts and implementers must not contradict active story flows without an explicit task that updates the story.
8. A story is **not** `implemented` until **all** of its flows are `done` (or explicitly `cancelled` / `superseded`).
9. Stories remain **product-wide SHARED** — never fork a surface-local or service-local user-story tree.
10. **Extract** must not invent journeys without evidence — tag Observed / Inferred / Unknown; `done` flows only with Observed (or strongly evidenced Inferred with citation).

## Docs layout (product-level)

```text
docs/
  user-stories/
    README.md              # how agents must treat stories (SHARED spine)
    INDEX.md               # durable story ledger (dedup + coverage)
    US-001.md              # one story per file
    US-002.md
    intake/                # raw sessions (user prose or extract sessions)
      STORY-001.md
      STORY-002.md
  business-rules/          # peer SoT; stories may cite / extend rules
  dev-pipeline/
    SHARED.md              # MUST list docs/user-stories/ for all surfaces
```

Create `docs/user-stories/` on first `story` / `story extract` (or on `init` as empty stubs). Prefer an existing user-stories / use-cases tree discovered by `adopt` — **extend** it; map IDs into `INDEX.md` without forking.

Index `docs/user-stories/` (or the discovered path) in `docs/dev-pipeline/SHARED.md` under Authoritative shared paths (category: User stories / Business flows) with consumers **all** surfaces.

## Story model

| Field | Meaning |
|-------|---------|
| `US-{NNN}` | Stable story ID (product-wide, never renumber) |
| `title` | Short human title |
| `status` | `draft` \| `active` \| `partial` \| `implemented` \| `superseded` \| `cancelled` |
| `origin` | `user` \| `extracted` \| `adopted-overlay` |
| `priority` | `P0`…`P3` when known |
| `actors` | Primary actors (user roles) |
| `narrative` | As a / I want / so that (or equivalent short narrative) |
| `business_logic` | Rules that govern the story (peer to `docs/business-rules/`) |
| `flows` | Ordered flow table + per-flow steps/AC |
| `links` | Feature / Task / CLAIMS / business-rule / SHARED paths; optional phase **links** (not ownership) |
| `surfaces` | Consuming surfaces (informational) — default all; **not** an owning surface |
| `evidence` | Paths + Observed/Inferred tags (required for `origin: extracted`) |
| `first_intake` | `STORY-{NNN}` when created via intake/extract session |

### Flow model

| Field | Meaning |
|-------|---------|
| `US-{NNN}-F{NN}` | Stable flow ID within the story |
| `name` | Short flow name (happy path, error, edge, …) |
| `status` | `todo` \| `partial` \| `done` \| `cancelled` \| `superseded` |
| `covered_by` | Task IDs that implement or partially implement this flow (may be empty for extracted legacy work) |
| `steps` | Ordered business steps (logic, not UI chrome) |
| `acceptance` | Observable checks for this flow |
| `evidence` | For extracted flows: path + tag supporting status |

### Classification on each new `story` session

Compare extracts to `INDEX.md` + existing `US-*.md`:

| Class | Meaning | Doc effect |
|-------|---------|------------|
| **new** | New story (or new flow on a matched story) | Create/extend `US-*.md`; update INDEX |
| **duplicate** | Same journey/flow meaning (rephrase OK) | INDEX “seen again” only — **no** body rewrite |
| **refinement** | Narrows/clarifies without contradicting | Additive steps/AC/rules on same `US-*` / flow |
| **contradiction** | Conflicts with active story, SHARED, or frozen contract | **Stop** that extract; ask user |

## Workflow — user prose (`story <prose>`)

### 0. Parse

Flags, optional `US-{NNN}` target, remainder = **raw user prose** (required unless `stories status` / `story extract` / empty rejected).

### 1. Inspect

1. Ensure or locate `docs/user-stories/` (or adopted equivalent path).
2. Read `INDEX.md` if present (empty ledger if first story).
3. Read `docs/dev-pipeline/SHARED.md`, active phase `CONTEXT.md` / `CLAIMS.md` as needed, linked business-rules.
4. If targeting `US-*`, read that file.
5. `git status` before writes.

### 2. Persist raw intake (unless `--dry-run`)

Allocate next `STORY-{NNN}` under `docs/user-stories/intake/`. Write:

```markdown
# STORY-001 — {ISO or local timestamp}

**Source:** user
**Phase tag:** `PH-01` | — (link only)

## Raw input
{verbatim user prose}

## Extracted (this session)
| Local | Class | Summary | Matches | Action |
|-------|-------|---------|---------|--------|
| 1 | new | … | — | create → US-004 |
| 2 | refinement | … | US-001 / F02 | extend flow |
| 3 | duplicate | … | US-002 | INDEX note only |
```

### 3. Apply only `new` / allowed `refinement`

Unless `--dry-run`:

**Story files**

- Create `US-{NNN}.md` for new stories (next ID; never reuse); set `origin: user`.
- For refinements: additive update to narrative/business_logic/flows; do not silently delete steps.
- New flows get next `F{NN}` within that story.
- Set story `status`: `draft`/`active` on create; `partial` if any flow `done`/`partial` but not all; `implemented` only when all non-cancelled flows are `done`.
- Do **not** set an owning surface; list consumers only if useful.

**INDEX.md**

- Append/update rows; never renumber.
- Update coverage columns (flow counts open vs done).

**Business rules** (unless `--story-only`)

- When the story states durable rules not already captured, **additively** extend `docs/business-rules/` (or adopted path); cite `US-*` / `STORY-*`.
- Do not silently overwrite contradicted rules — ask first.
- Add/refresh SHARED path row for user-stories + any new rule files (consumers: **all** surfaces).

**Backlog links** (unless `--story-only`)

- Map to existing Feature IDs when clearly the same capability (add Links → story/flows only; do not change Feature ID).
- Optionally add **new** `todo`/`ready` tasks at end of active (or `--phase`) queue that cite `US-*` / flows — never reorder existing IDs; never alter in-flight/done rows.
- Do not emit `agent-prompts/` during `story`.

### 4. Report

Compact table of extracts + paths touched + open-flow coverage for affected stories. Remind: IDs/phases/task statuses left intact unless additive queue rows were requested by mapping.

---

## Workflow — extract from implemented features (`story extract`)

**Purpose:** On a project **already in development**, reverse-map **shipped / implemented** (and optionally partial) capabilities into durable product-wide `US-*` stories so SHARED has a journey spine before new surfaces continue work.

### When to run

| Situation | Behavior |
|-----------|----------|
| Just finished `adopt` | Suggested next step; or `adopt --extract-stories` runs extract once at end |
| Pipeline exists; stories missing/thin | Standalone `story extract` |
| Greenfield empty product | Skip — nothing to extract; use `story <prose>` |

### 0. Parse

Flags: `--dry-run`, `--story-only`, `--from-docs-only`, `--include-partial`, `--force-new`.

### 1. Inspect (evidence sources, in order)

1. `docs/dev-pipeline/ADOPTION.md` — **Built vs open** table (prefer `done` / shipped rows).
2. Epic/feature docs with status `done` (and `partial` if `--include-partial`).
3. Existing use-case / user-story / journey docs (map/overlay — do not wipe).
4. PRODUCT / ROADMAP / CHANGELOG capability lists (Observed citations).
5. Unless `--from-docs-only`: high-signal code/module paths cited by features (Inferred only with path citation — never invent UX).
6. Existing `INDEX.md` / `US-*.md` for dedup.
7. `SHARED.md` surfaces list (for consumers column — stories still not owned by any one surface).

### 2. Persist extract session

Allocate `STORY-{NNN}` intake with **Source:** `extract`:

```markdown
# STORY-00N — {timestamp}

**Source:** extract
**Mode:** from implemented features

## Evidence scanned
| Source | Path | Notes |
|--------|------|-------|
| ADOPTION Built vs open | `docs/dev-pipeline/ADOPTION.md` | … |
| Feature | `docs/epics/…` | status done |

## Candidates
| Local | Class | Summary | Feature links | Flow status guess | Evidence |
|-------|-------|---------|---------------|-------------------|----------|
| 1 | new | … | ASK-01 | F01 done | Observed from … |
```

### 3. Create / refine stories

For each **new** candidate (after dedup):

1. Allocate `US-{NNN}`; `origin: extracted` (or `adopted-overlay` when wrapping pre-existing journey docs).
2. Write narrative + business logic **only** from evidenced behavior; mark gaps Unknown — do not invent alternate flows.
3. Flows:
   - Status `done` only with Observed completion evidence (docs AC met, changelog shipped, feature `done` with citation).
   - Status `partial` when feature/docs say partial or some steps missing.
   - Status `todo` for related but unimplemented edges discovered as open (do not mark story `implemented`).
4. `covered_by`: link Feature IDs; Task IDs if known — else `—` with note “pre-pipeline implementation”.
5. **Surfaces:** informational consumers = all SHARED surfaces; never create per-service copies.
6. Update INDEX + SHARED user-stories row (consumers: all).
7. Link Feature **Links** → `US-*` (additive) unless `--story-only`.

**Never** during extract:

- Mark flows `done` without evidence
- Renumber features/tasks or change in-flight task status
- Create surface-local story folders
- Emit `agent-prompts/`
- Silently overwrite existing `US-*` bodies on duplicate (INDEX note only)

### 4. Report

| Story | Class | Flows done/total | Features | Evidence |
|-------|-------|------------------|----------|----------|
| … | … | … | … | … |

List Unknowns (journeys suspected but undocumented). Suggest `stories status` and `shared` to confirm spine.

## `story status`

Read-only (create stub INDEX only if missing and user asked to init layout):

1. List stories from INDEX with status + open flow counts + origin.
2. Highlight `active`/`partial` stories with `todo`/`partial` flows (implementation gaps).
3. Optionally note Features/Tasks linked vs unlinked gaps (Unknown if not linked — do not invent).
4. Confirm SHARED lists `docs/user-stories/` for all surfaces.

## `US-*.md` template

```markdown
# US-001 — {short title}

**Story ID:** `US-001`
**Status:** active
**Origin:** user | extracted | adopted-overlay
**Priority:** P1
**Actors:** End user
**Surfaces (consumers):** all  # not an owning surface — product-wide SHARED
**Phases (links):** PH-01
**Features:** ASK-01
**Business rules:** `docs/business-rules/…`
**Claims:** CLM-001
**First intake:** STORY-001
**Evidence:** Observed from `docs/…` | Inferred from `…`

## Narrative
As a … I want … so that …

## Business logic
- … (cite rule paths when present)

## Flows

| Flow ID | Name | Status | Covered by | Notes |
|---------|------|--------|------------|-------|
| US-001-F01 | Happy path | todo | — | |
| US-001-F02 | Validation error | todo | — | |

### US-001-F01 — Happy path

**Status:** todo

**Steps**
1. …
2. …

**Acceptance**
- …

### US-001-F02 — Validation error

**Status:** todo

**Steps**
1. …

**Acceptance**
- …

## Non-goals
- …

## Changed by

| Event | Note |
|-------|------|
| STORY-001 | created |
```

## `INDEX.md` template

```markdown
# User story index

**Root:** `docs/user-stories/`
**SHARED:** product-wide — see `docs/dev-pipeline/SHARED.md` (not surface-owned)

| Story ID | Title | Status | Origin | Priority | Flows (done/total) | Features | Path |
|----------|-------|--------|--------|----------|--------------------|----------|------|
| US-001 | … | active | extracted | P1 | 2/2 | ASK-01 | [US-001.md](./US-001.md) |
```

## `docs/user-stories/README.md` (minimum)

- User stories are **product-wide SHARED business-logic SoT** for user-facing flows (peer to business-rules).
- They do **not** belong to a single frontend/backend/service — all surfaces consume the same `US-*` files.
- One file per `US-*`; never renumber; supersede instead of delete.
- Agents implementing tasks **must** open linked stories and honor flow steps/AC.
- A story is incomplete while any non-cancelled flow is not `done`.
- Dedup via `INDEX.md`; duplicates must not rewrite story bodies.
- Mid-flight: use `/dev-pipeline story extract` to harvest journeys from implemented features.

## Task emission rules (`next` / `task`)

When writing an agent prompt ([prompt-template.md](prompt-template.md)):

1. Resolve related `US-*` from: feature Links, INDEX, queue notes, or explicit user ID (stories are SHARED — available to every surface).
2. If the feature/task clearly implements user-facing behavior and **no** story is linked: mark **Unknown** in the prompt and prefer linking/creating/extracting a story before claiming business completeness — do not invent story text.
3. Include a **Related user stories** section listing each `US-*` path + which flows this task covers vs leaves open.
4. **Flow coverage check (mandatory):**
   - State current status of each cited flow (`todo` / `partial` / `done`).
   - If this task only covers a subset, list remaining flows and whether a follow-up task already exists; if not, note the gap (do not silently mark the story `implemented`).
   - Acceptance criteria in the prompt must not contradict open/cancelled flows.
5. After review PASS (when pipeline docs are updated elsewhere), story flow `covered_by` / status updates are expected via explicit doc updates — `story` refinement or tracker follow-up — never renumber IDs.

## Interaction with `brief`

- Briefs absorb phase claims; stories capture durable journeys/flows on the SHARED spine.
- If a new claim is clearly a user journey and no `US-*` exists, the agent may **suggest** `/dev-pipeline story …` or, when the user combined intents, run `story` once after brief — but default `brief` alone does not require creating stories.
- Cross-link: CLAIMS `links` may include `docs/user-stories/US-*.md`; story `Claims:` may list `CLM-*`.

## Interaction with `init` / `adopt`

- **`init`:** create empty `docs/user-stories/README.md` + `INDEX.md` (+ empty `intake/`) when bootstrapping layout; index in SHARED for all surfaces.
- **`adopt`:** if use-case / user-story docs exist, record path in `ADOPTION.md` + SHARED; do not rewrite bodies.
  - Always suggest `/dev-pipeline story extract` when Built vs open has shipped user-facing items and INDEX is empty/thin.
  - With `--extract-stories`: after adopt writes, run **one** `story extract` pass (same turn).
  - Extracted stories remain product-wide SHARED — not tied to the intake phase as owner.

## Safety & evidence

- Store **verbatim** raw input in `intake/STORY-*.md` for user prose (Observed). Tag normalized narratives Inferred when fuzzy.
- For extract sessions, store the evidence table (Observed/Inferred) in the intake file.
- Do not invent APIs/stack from a story unless evidenced — mark Unknown otherwise.
- `--dry-run` writes nothing.
