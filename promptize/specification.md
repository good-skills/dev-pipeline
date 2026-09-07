# Promptize intermediate specification

Do **not** draft final prompt prose first — **unless** reuse hit, ultra-gate, or micro direct-render ([inspection.md](inspection.md)). Otherwise: lean Specify → Lint → Render.

Shared policies: [policies.md](policies.md). Cache reuse: [../shared/context-cache.md](../shared/context-cache.md).

## Pipeline

| Path | Stages |
|------|--------|
| **Reuse hit** | Render prior body (`Cache: REUSE_HIT`) → upsert cache |
| **Ultra / micro** | Direct-render `minimal` (`Cache: ULTRA`) — no intermediate spec |
| **Fast / delta** | Extract → Specify → Lint → Render (`Cache: FAST` or `DELTA`) |

```text
Reuse → Ultra/Micro → [Inspect delta?] → Extract → Specify → Lint → Render → Persist + cache upsert → [Execute…]
```

Keep intermediate spec **internal**. Never dump full JSON to the user unless asked.

---

## Token efficiency (v2.1 Ultra Lean — binding)

Target: substantially fewer tokens than report-style prompts; reuse/ultra aim for the smallest viable engineering prompt while keeping MUST/artifact contracts when they apply.

| Rule | Do | Do not |
|------|----|--------|
| Reuse first | Exact/normalized `norm_key` + HEAD | Semantic / fuzzy match |
| Compress | Artifacts, inventories, aliases only | Long excerpts, architecture essays |
| Evidence | Map only if ≥2 files; else short path | Map for a single file |
| Lean spec | Omit empties; drop ambiguities/open_questions | Ceremonial null fields |
| Tier | `ultra-low` → minimal (4 sections); compact default; `--full` explicit | Auto-inflate to 20 sections |
| Decisions | **One sentence** when possible | Bullet essays |
| OoS | 3–4 hard excludes | Soft non-goal essays |
| Lint UI | Prompt-only: silent; surface only count-blocking CONFLICT/BLOCKED | Print WARN/ERROR transcripts |
| Validation | Inline under AC in compact/minimal | Require `validation_checks` array outside `--full` |

### Evidence aliases

```yaml
evidence:
  auth: src/auth.ts#loginHandler
  routes: src/routes.ts#GET_/login
```

```text
Evidence map: auth→src/auth.ts#loginHandler; routes→src/routes.ts#GET_/login
[Observed: auth]
```

One file → `auth.ts` (or short repo-relative path); skip the map.

### RECOMP-style compression

Keep: inventories + counts, artifacts, precedence, touch paths, validation commands, CONFLICT/BLOCKED.  
Drop: narrative stack already in Carry-over, unused policy sections, soft gaps.

---

## Intermediate specification schema

`schema_version: 3` · edition ultra-lean. Populate **only** fields that apply.

```yaml
schema_version: 3
task_id: null
objective: ""
render_tier: compact             # minimal | compact | full
estimated_tokens: low            # ultra-low | low | mid | high
evidence: {}                     # alias → path#symbol (≥2 files)
source_precedence: []            # only if multi-source
inventories: []
artifacts: []
requirements: []                 # id, text, priority, verifiable
constraints: []
out_of_scope: []                 # 3–4 hard excludes
acceptance_criteria: []
naming: {}                       # filenames as deliverables — one line in compact
evidence_policy: compact
uncertainty: []                  # UNKNOWN | CONFLICT | BLOCKED
# --full only:
# validation_checks: []
```

**Removed from schema:** `ambiguities`, `open_questions` — do not emit.

| Field | Purpose |
|-------|---------|
| `estimated_tokens` | `ultra-low` (micro fix) → minimal; `low` docs/single-file → minimal; `mid` multi-file → compact; `high` API/migration/security → prefer `--full` |
| `evidence` | Alias map when ≥2 cited files |
| `source_precedence` | Ordered authority when ≥2 sources for a data kind |
| `artifacts` / `inventories` | Exact integer counts or BLOCKED |
| `out_of_scope` | Aggressive excludes |
| `uncertainty` | Typed gaps only |

Evidence policy default (non-diagram): one line — Observed only with map/path; no upgrade Inferred/Unknown→Observed. Expand for diagram deliverables or `--full`. Async: [policies.md](policies.md) only if queues/workers apply.

---

## Requirements (obligation levels)

| `priority` | Render |
|------------|--------|
| `MUST` | Imperative; exact counts/paths |
| `SHOULD` | “SHOULD …” |
| `MAY` | Optional |
| `GUIDANCE` | Omit in minimal unless safety |
| `CONTEXT` | Context only |
| `ACCEPTANCE` | AC (folded under Requirements in minimal) |

Forbidden on MUST/ACCEPTANCE: `sensible`, `or equivalent`, `as needed`, `appropriate` unless bounded by `naming`/`artifacts`.

---

## Source precedence

Only when ≥2 sources:

```text
Precedence (routes): 1) index.js 2) task table 3) api.md — conflict → CONFLICT, do not guess.
```

---

## Artifact contracts

```yaml
artifacts:
  - id: sequence-diagram
    count: 11
    path: docs/onboarding/sequences/
    filename_pattern: "{method}-{normalized-path}.html"
    format: standalone-html
    external_dependencies: false
    one_to_one_with: active_routes
```

Render tight: exact count, path, format, deps, 1:1 map. `count` computable or BLOCKED.

---

## Filename normalization

One line when needed:

```text
Naming: lower; method-first; /→-; :param→param; /→root; no spaces
```

---

## Uncertainty

| Type | Prompt-only | `--execute` |
|------|-------------|-------------|
| `UNKNOWN` | Tag if needed; continue | Continue if non-blocking |
| `CONFLICT` | One-line if blocks counts | Do not implement affected outputs |
| `BLOCKED` | State blocker; no fake counts | **Ask** before coding |

---

## Smart lint (Zero-overhead)

### Always (fix silently; do not print transcript)

MUST uniqueness; AC ↔ artifact counts; computable `count`; no soft MUST words; Unknown≠Blocked; no active/inactive mix; multi-source count needs precedence.

### Prompt-only

- **Do not** show WARN/ERROR lists in the body.
- Surface **only** CONFLICT/BLOCKED that block deliverable counts/authority.
- Soft WARNs: fix if cheap or omit.

### `--execute` / `--full`

- Ask user **only** on BLOCKED.
- Treat format/safety WARNs as must-fix before coding; still no long lint dump.

---

## Tier selection

| Tier | Trigger | Shape |
|------|---------|-------|
| **minimal** | `--minimal`, or `ultra-low`/`low` without artifact inventory | **4 sections** |
| **compact** | default / `mid` | 8 sections, pruned |
| **full** | `--full` only (or user asks complete template) | 20 sections |

Never auto-`full` for docs-only or single-file bugfix. Honor `--minimal` over auto-escalate.

---

## Render mapping

| Spec | minimal (4) | compact | full |
|------|-------------|---------|------|
| objective | 1 Objective | 1 | Objective |
| decisions + context + evidence | 2 Context/Decisions (1 sentence + paths) | 2 + 3 | Decisions + Context |
| behavior | 3 Behavior (current→desired) | 4 + 5 | Current + Desired |
| requirements + artifact + OoS + AC + touch | 4 Requirements (fold tails) | 6–8 | Functional…Plan |

Header:

```text
Promptize specification version: 3
Output tier: minimal | compact | full
Cache: REUSE_HIT | ULTRA | FAST | DELTA
```

Omit `Cache:` only if unknown; never invent token-saved counts.

### Minimal density (4 sections)

1. **Objective** — one sentence.
2. **Context & decisions** — one-sentence decision; stack/paths; evidence map if ≥2 files; precedence if needed.
3. **Behavior** — current → desired (short combined block).
4. **Requirements** — MUST first; artifact/naming if any; Touch Set (≤3 lines); OoS 3–4 with `❌` or “Do not:”; AC ≤5; repo validation commands inline if known. No separate Constraints section.

### Compact density

1. Objective — one sentence.
2. Engineering Decisions — one sentence when possible (≤2 max).
3. Repository Context — stack one line; files/aliases; precedence if needed.
4–5. Current / Desired — ≤5 bullets each.
6. Requirements — MUST block; artifact one paragraph; naming one line.
7. Constraints & OoS — Touch Set ≤3 lines; OoS 3–4 excludes.
8. AC + validation (+ plan ≤4 steps). Skip empty subsections. No `N/A` walls.

### Save metadata (ultra-light)

```yaml
---
promptize:
  schema_version: 3
  skill_version: <frontmatter>
  generated_at: <timestamp>
  tier: minimal | compact | full
  mode: prompt-only | execute
---
```

Do **not** put `source_request` or `git_head` in frontmatter — HEAD lives on the Promptize reuse row in SESSION-CACHE.
