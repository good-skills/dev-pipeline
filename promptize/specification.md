# Promptize intermediate specification

Do **not** draft the final prompt prose first. Build an intermediate specification, lint it, then render.

Shared policies that inject into the spec: [policies.md](policies.md). Inspection evidence: [inspection.md](inspection.md).

## Three-stage pipeline

| Stage | Name | Input | Output |
|------:|------|-------|--------|
| 1 | **Extract** | short request + inspect slices | structured facts |
| 2 | **Specify** | facts | intermediate specification (schema below) |
| 3 | **Render** | lint-passed specification | compact or full prompt body |

```text
Inspect → Extract facts → Specify → Lint → Render → Persist → [Execute…]
```

Never skip Lint. If Lint fails with **BLOCKED** or unresolved **CONFLICT**, do not render a silent “best effort” prompt — surface the issue (prompt-only) or ask (`--execute`).

---

## Intermediate specification schema

Populate every field that applies. Use empty arrays / `null` when N/A — do not invent.

```json
{
  "schema_version": 2,
  "task_id": null,
  "objective": "",
  "authoritative_sources": [],
  "source_precedence": [],
  "routes": [],
  "inventories": [],
  "deliverables": [],
  "artifacts": [],
  "requirements": [],
  "constraints": [],
  "validation_checks": [],
  "acceptance_criteria": [],
  "evidence_policy": {},
  "naming": {},
  "ambiguities": [],
  "open_questions": [],
  "uncertainty": []
}
```

### Field contracts

| Field | Purpose |
|-------|---------|
| `task_id` | Pipeline/handoff ID when known (`TASK-…`); else `null` |
| `objective` | Single outcome sentence |
| `authoritative_sources` | Paths/roles used as evidence (with status) |
| `source_precedence` | Ordered list: which source wins per data kind |
| `routes` / `inventories` | Countable inventories (routes, entities, files, …) with `status: active\|inactive` |
| `deliverables` | Human-readable deliverable list derived from artifacts |
| `artifacts` | Machine-checkable artifact contracts (count, path, format) |
| `requirements` | Prioritized, preferably unique requirements |
| `constraints` | Hard limits / protected areas / deps |
| `validation_checks` | How to verify deliverables |
| `acceptance_criteria` | Observable MUST outcomes (must agree with artifacts) |
| `evidence_policy` | Labels + placement + Observed rules for this task |
| `naming` | Deterministic naming/normalization rules when filenames matter |
| `ambiguities` | Soft gaps that do not block a useful spec |
| `open_questions` | Questions for the user when needed |
| `uncertainty` | Typed uncertainty entries (`UNKNOWN` / `CONFLICT` / `BLOCKED`) |

---

## Requirements (type + obligation level)

Every instruction that will appear in the rendered prompt MUST be classified:

| `priority` | Meaning | Render language |
|------------|---------|-----------------|
| `MUST` | Binding; acceptance depends on it | Imperative, exact counts/paths |
| `SHOULD` | Strong preference; deviation needs justification | “SHOULD …” |
| `MAY` | Optional | “MAY …” / Optional |
| `GUIDANCE` | How to execute, not what to deliver | “Guidance:” |
| `CONTEXT` | Background only — not actionable | Context / Repository Context |
| `ACCEPTANCE` | Observable done-state | Acceptance criteria section |

```yaml
requirements:
  - id: REQ-001
    text: Create one HTML file per active route
    priority: MUST
    verifiable: true
  - id: REQ-002
    text: Prefer short filenames when the pattern allows
    priority: SHOULD
    verifiable: false
```

Rules:

- Do not repeat the same `MUST` in multiple sections with different wording.
- Render all `MUST` together (or under Requirements with a clear `MUST:` block).
- Never promote `GUIDANCE` / `CONTEXT` / `SHOULD` to sound like `MUST`.
- Soft phrases (`sensible`, `appropriate`, `as needed`, `or equivalent`) are **forbidden** on `MUST` / `ACCEPTANCE` unless bounded by an explicit rule in `naming` or `artifacts`.

---

## Source precedence

When the same fact appears in multiple places (task table, docs, runtime registration, handoff), emit an explicit precedence block in the specification **and** in the rendered prompt.

Default data-kind templates (adapt to the task; do not invent sources that were not inspected):

```text
Source precedence (<data-kind>):
1. <highest-authority source>
2. <secondary>
3. <tertiary>

If sources disagree:
- do not silently choose one;
- record uncertainty type CONFLICT (or BLOCKED if deliverables cannot be counted);
- do not implement affected output until resolved.
```

Examples of data kinds: `routes`, `entities`, `validation_commands`, `stack`, `contracts`.

When the task table (or user request) is explicitly the deliverable authority:

```text
The route table in this task is authoritative for deliverable count.
index.js and api.md are verification sources.
```

This decision lives in the skill defaults + task facts — not left for the prompt author to invent per task.

**Handoff vs repo:** current repository evidence still wins on conflict with handoff for *implementation state*; handoff remains authoritative for Task IDs, SHARED/US citations, and stated Out of scope ([inspection.md](inspection.md)).

---

## Artifact contracts

For each deliverable, specify a checkable contract:

```yaml
artifacts:
  - id: sequence-diagram
    count: 11                    # exact integer, or null if BLOCKED
    path: docs/onboarding/sequences/
    filename_pattern: "{method}-{normalized-path}.html"
    format: standalone-html
    embedded_assets: true
    external_dependencies: false
    one_to_one_with: active_routes
    prior_state: absent          # absent | partial | exists
    validation:
      - file_count_equals_inventory
      - each_file_contains_inline_svg
```

Rendered form (example):

```text
Artifact contract:
- Create exactly 11 files under docs/onboarding/sequences/.
- Each file must be standalone HTML.
- Each file must contain an inline SVG.
- No Mermaid-only output.
- No external JavaScript, CSS, fonts, or image assets.
- There must be a one-to-one mapping between ACTIVE_ROUTES and output files.
```

Rules:

- `count` must be computable from an authoritative inventory, or set `uncertainty: BLOCKED`.
- Ban unbounded phrasing: `N files or equivalent`, `about N`, `as many as needed`.
- `external_dependencies: false` means no external JS/CSS/fonts/images unless the contract says otherwise.

---

## Filename normalization

When artifacts need filenames, define a deterministic function in `naming` — never “sensible filenames” alone.

Default rule set (use unless the repo already has a stronger convention — then Observed convention wins):

```text
Filename normalization:
- lowercase
- HTTP method first (when method applies)
- replace `/` with `-`
- replace `:param` with `param` (or `{param}` only if the path pattern requires braces)
- use `root` for `/`
- no spaces
- collapse repeated `-`
```

Examples:

```text
GET /                    → get-root.html
GET /sites/:site_id/links → get-sites-site-id-links.html
POST /sites/:site_id/requeue → post-sites-site-id-requeue.html
```

If a shorter pattern is required, state **one** deterministic mapping and examples that match it. Do not give a general pattern **and** conflicting short examples.

---

## Evidence policy (schema)

`Tag evidence Observed/Inferred/Unknown` alone is insufficient. Put a concrete policy in the specification:

```yaml
evidence_policy:
  labels:
    - Observed
    - Inferred
    - Assumption
    - Unknown
  observed_requires:
    - source_file
    - source_reference   # symbol, line range, or section when available
  placement:
    - every_interaction   # when diagrams / sequence docs
    - diagram_legend
  upgrade_forbidden: true   # never promote Inferred/Unknown → Observed
```

Preferred render tags:

```text
[Observed: path/to/file]
[Inferred]
[Assumption]
[Unknown]
```

Rendered rules block (inject when the task produces diagrams, inventories, or behavior claims):

```text
Evidence rules:
- Label every interaction as [Observed], [Inferred], [Assumption], or [Unknown].
- Use [Observed] only when supported directly by code or documentation; cite path.
- Use [Inferred] for behavior logically implied but not directly shown.
- Use [Assumption] for unverified premises required to proceed.
- Use [Unknown] when the repository does not establish the behavior.
- Add a legend when diagrams are deliverables.
- Do not upgrade Inferred, Assumption, or Unknown to Observed.
```

---

## Async evidence policy (reusable)

Inject when the task touches queues, workers, jobs, webhooks, or “fire-and-forget” side effects:

```text
Async evidence policy:
- HTTP request → enqueue call: Observed if directly present in route/helper code.
- Queue name and payload: Observed only if defined in source.
- Worker consumption: Observed only if the consumer and linkage are traceable.
- Background processing after the request: do not imply temporal ordering unless documented.
- Completion callback, retry, refresh, or persistence: mark Unknown unless directly evidenced.
```

Do not imply that enqueue proves worker success.

---

## Uncertainty: Unknown vs Conflict vs Blocked

| Type | Meaning | May render useful prompt? | May implement affected output? |
|------|---------|---------------------------|--------------------------------|
| `UNKNOWN` | Behavior/fact not established after bounded search | Yes — document with `[Unknown]` | Yes, if deliverables remain well-defined |
| `CONFLICT` | Sources disagree; precedence not yet resolving | Yes — surface conflict + precedence | No for affected outputs until resolved |
| `BLOCKED` | Essential facts missing/contradictory; correct delivery impossible | Prompt-only: state blocker; `--execute`: stop and ask | No |

```yaml
uncertainty:
  - type: UNKNOWN
    subject: worker completion after enqueue
  - type: CONFLICT
    subject: active route count
    sources: [task table, index.js]
  - type: BLOCKED
    subject: deliverable file count
    reason: authoritative inventory not computable
```

Laws:

- `Unknown` behavior may be documented; it does **not** by itself block documentation tasks.
- `Conflict` / `Blocked` on count, authority, or format **do** block affected implementation.
- Never mix inactive inventory items into active deliverable counts.

---

## Prompt lint (before Render)

Run all checks. Fix the specification when possible; otherwise emit WARN/ERROR and follow the table.

| Check | Severity if fail |
|-------|------------------|
| Every `MUST` requirement is unique (no duplicate meaning) | ERROR |
| Acceptance criteria agree with artifact contracts / deliverable counts | ERROR |
| Every artifact `count` is an exact integer computable from an authoritative inventory | ERROR |
| Source precedence defined for every multi-source data kind | ERROR |
| Referenced paths exist **or** are explicitly `Unknown` / proposed-new | WARN / ERROR if claimed Observed |
| Soft unbounded words on MUST/ACCEPTANCE: `or equivalent`, `sensible`, `as needed`, `appropriate`, `about N` | ERROR |
| Active and inactive inventory items not mixed into one count | ERROR |
| Optional / SHOULD / MAY clearly marked (not sounding like MUST) | WARN |
| Evidence tag syntax and placement defined when claims/diagrams exist | WARN |
| Async/worker observation criteria defined when async paths exist | WARN |
| Self-contained / standalone deliverables have dependency contract (`external_dependencies`) | WARN |
| `Unknown` vs `Blocked` not conflated | ERROR |

Example warnings for a bad draft:

```text
WARN: "11 files or equivalent" is non-deterministic.
WARN: Route authority is not explicitly ordered.
WARN: Evidence tag syntax is undefined.
WARN: Worker observation criteria are ambiguous.
WARN: "self-contained HTML/SVG" lacks a dependency contract.
```

**ERROR** → fix spec or mark `BLOCKED` before render.  
**WARN** → fix when cheap; otherwise include an explicit Ambiguities / Uncertainty note in the rendered prompt.

---

## Render mapping

| Spec field | Compact section | Full section |
|------------|-----------------|--------------|
| `objective` | 1. Objective | Objective |
| engineering choices + labeled assumptions | 2. Engineering Decisions | Engineering Decisions + Assumptions |
| sources, stack, files, precedence | 3. Repository Context | Repository Context |
| today state | 4. Current Behavior | Current Behavior |
| target state | 5. Desired Behavior | Desired Behavior |
| `requirements` (MUST/SHOULD/…) + artifacts | 6. Requirements | Functional + Technical Requirements |
| `constraints` + out of scope + touch set | 7. Constraints & Out of Scope | Constraints + Out of Scope |
| `acceptance_criteria` + `validation_checks` + plan | 8. Acceptance, Validation & Plan | AC + DoD + Testing + Plan |

Always start rendered body with:

```text
Promptize specification version: 2
Output tier: compact | full
```

When `--save-to-file`, metadata `schema_version: 2`.
