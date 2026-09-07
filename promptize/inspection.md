# Promptize inspection

Run inspection **only after** reuse miss and ultra/micro miss. Shared layer: [../shared/inspect.md](../shared/inspect.md). Token rules: [specification.md](specification.md), [../shared/token-efficiency.md](../shared/token-efficiency.md). Cache reuse: [../shared/context-cache.md](../shared/context-cache.md).

## Gate order (after Parse / Understand)

```text
Promptize reuse → Ultra-gate → Micro direct-render → Fast path → Delta inspect
```

Never use ultra/micro/direct-render for security-sensitive, migration, new/modified public API, or `--full`.

### 1. Promptize reuse (exact/normalized)

1. Open `docs/dev-pipeline/SESSION-CACHE.md` if present (create stub later on Persist if missing).
2. Build `norm_key` per [context-cache.md](../shared/context-cache.md) (strip `/promptize` + flags; lowercase; collapse whitespace).
3. Compare current `git rev-parse HEAD` to row `git_head`.

**Hit:** matching `norm_key` + HEAD + reusable body (`saved_path` file or last inline body) → emit prior rendered prompt with header `Cache: REUSE_HIT`. Skip inspect, Extract, Specify, Lint. On `--execute`, still run execution revalidation.

**Miss:** continue to Ultra-gate. Rephrased requests are misses by design (no semantic matching).

### 2. Ultra-gate (direct render from handoff)

**Hit when all** are true:

- Valid handoff for resolved `TASK-ID` (paths exist; IDs + AC sketch present).
- Cache/handoff `git_head` matches current HEAD (or only unrelated dirty files).
- Short request deepens the **same** handoff goal (not a new feature surface).

**Action:** direct-render `minimal` from handoff fields (Goal → Objective, Required changes → MUST, Out of scope, AC). No intermediate spec. Header: `Cache: ULTRA`. No manifest/code/docs.

### 3. Micro direct-render

**Hit when all** are true:

- `estimated_tokens: ultra-low` — clearly a small fix/update/typo/comment/single-file tweak.
- No countable artifact inventory (no “N files / routes / diagrams” deliverable).
- Not security / migration / API / `--full`.

**Action:** direct-render `minimal` (skip Extract → Specify → Lint). Still include light MUST, AC, 3–4 OoS, Touch Set if known. Header: `Cache: ULTRA` (micro). Prefer opening only the named file if the user gave a path — not a 1-hop graph.

### 4. Fast path (skip manifest / code / docs)

When reuse/ultra/micro miss but:

- Carry-over or handoff already states stack + validation needed, **or** docs-only deepen with paths in handoff.
- Handoff (if any) valid and not stale.
- HEAD matches or divergence is non-material.
- No security / migration / auth semantics require fresh code evidence.

**Action:** Extract from handoff + Carry-over + user request only → Specify → Lint → Render. Header: `Cache: DELTA` is wrong here — use `Cache: ULTRA` only for direct-render; for this path use `Cache: DELTA` only if any slice ran, else omit or `Cache: FAST`. Prefer `Cache: FAST` when no code/docs/manifest read.

Still record baseline HEAD when `--execute` is likely.

### 5. Delta inspect

When all above miss: run **delta** slices only for uncovered facts — never a full-repo tour. Header: `Cache: DELTA`.

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

## Slice order (delta inspect only)

0. **SESSION-CACHE** — reuse Carry-over; skip Loaded; already checked Promptize reuse
1. **pipeline-handoff** — if handoff paths exist
2. **git (HEAD only)** — cheap match
3. **manifest** — unless handoff/cache lists stack + validation
4. **code** — affected areas only (delta); prefer aliases `basename` / `path#symbol`
5. **docs** — uncovered governing docs only
6. **git (full)** — when `--execute` or follow-up execute likely

## Slice contracts

| Slice | Entry | Max depth | Stop when | Escalate when |
|-------|-------|-----------|-----------|---------------|
| **manifest** | Root/touched package manifests, lockfiles, CI | Package roots only | PM, runtime, build/test/lint/typecheck found | Monorepo; no manifest for touched path |
| **code** | User path, handoff Required changes, symbol search | 1 hop imports/callers | Behavior + touch set clear | Multiple modules equally plausible |
| **docs** | Handoff links, architecture/epic/US cited | Linked sections only | Conventions known | Doc contradicts code |
| **git** | `status -sb`, branch, `HEAD` | Planned touch set | Baseline recorded | Dirty/staged/untracked on touch set |
| **pipeline-handoff** | `agent-prompts/TASK-*.md` → `docs/promptize-prompts/` → queue | Single task id | IDs, AC sketch, OoS loaded | Multiple candidates or stale |

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

1. **Current repository evidence** — wins on conflict when inspected.
2. Newest **valid** handoff for resolved `TASK-ID`.
3. Fresh inspection for gaps only.

**Resolve TASK-ID:** explicit user id → conversation path → queue `in_progress` → newest non-rework `agent-prompts/TASK-*.md`. Multiple matches → **ask** (blocking).

**Stale handoff** — reconcile when paths missing, HEAD/branch changed, manifest/validation differs, or planned files no longer match repo.

Handoff authoritative for: Task/Feature/Epic IDs, SHARED/US citations, AC sketch, Out of scope — **not** observed code state.

## Evidence in output

| Status | Meaning |
|--------|---------|
| **Observed** | Direct evidence — `[Observed: alias]` if map has ≥2 files; else short path |
| **Inferred** | Label required |
| **Assumption** | Label required; only when needed to proceed |
| **Unknown** | Not found after bounded/delta search |

Auto-build evidence aliases from mentioned paths. Emit **Evidence map** only if ≥2 files.

### Uncertainty typing

| Type | When |
|------|------|
| `UNKNOWN` | No establishing evidence after search |
| `CONFLICT` | Sources disagree |
| `BLOCKED` | Deliverable count/authority/format not specifiable |

Conflict/Blocked on inventories must not become “N or equivalent”. Prompt-only: do not print lint transcripts — surface only CONFLICT/BLOCKED that block counts. `--execute`: ask on BLOCKED.

## Persist → cache upsert

After successful Render (and Persist if saving): upsert **Promptize reuse** row (`norm_key`, HEAD, tier, task_id, saved_path or `inline:last`). Cap 5. See [context-cache.md](../shared/context-cache.md).

## Relevant files

Repo-relative path or alias + map; role; evidence. Never “the file above”.

## Git snapshot (execute)

Record baseline at generation; re-validate at execution. Protect unstaged, staged, and untracked (unless this task creates them). See [policies.md](policies.md).
