# Token efficiency (pipeline skills)

Rules for **dev-pipeline**, **promptize**, **review-task**, and **commit** so agents maximize work per token and avoid repeating inspect/read work.

Read this when any pipeline skill runs. Details: [context-cache.md](context-cache.md), [inspect.md](inspect.md). Promptize Ultra Lean: [../promptize/specification.md](../promptize/specification.md).

## Golden rules

1. **One inspect per user intent** — pick slices from [inspect.md](inspect.md); do not re-run full repo inspect across skills in the same turn.
2. **Handoff is authoritative** — after `next` / `task`, Promptize and implementers start from `agent-prompts/TASK-*.md`; do not re-gather facts already in the handoff.
3. **Session cache** — before opening a path, check `docs/dev-pipeline/SESSION-CACHE.md` (if present). If listed and source file unchanged, **reuse carry-over**; read **delta only**.
4. **Conversation reuse** — same chat/session: do not re-read files you already loaded for the prior task unless the file changed or this task needs new sections.
5. **Delta `next`** — consecutive tasks in the same phase: reuse stable PRODUCT/SHARED summaries; read only new queue row, epic section, and new `US-*` / contract paths.
6. **Compact output** — Promptize default **compact**; auto-`minimal` for ultra-low; `--full` only when asked. Pipeline handoffs stay within [prompt-template.md](../dev-pipeline/prompt-template.md) size budget.
7. **Skills are procedures, not content** — do not paste entire reference docs into replies; cite paths and tables.
8. **Promptize reuse first** — check SESSION-CACHE **Promptize reuse** (`norm_key` + HEAD) before handoff/delta inspect ([context-cache.md](context-cache.md), [../promptize/inspection.md](../promptize/inspection.md)).
9. **Promptize ultra/micro** — on reuse miss, try ultra-gate / micro direct-render before delta inspect.

## Orchestration (one pass per stage)

| Stage | Skill | Read / run | Do **not** |
|-------|-------|------------|------------|
| Queue handoff | `/dev-pipeline next` | cache → queue row → delta docs | Full docs tree; re-read PRODUCT if cached |
| Deep spec | `/promptize` | reuse → ultra/micro → delta inspect | Full inspect on reuse/ultra hit; dump raw JSON; print lint transcripts |
| Implement | implementer | handoff → paths in Required changes | Full SHARED unless contracts change |
| Commit | `/commit` | stat → scoped diff | Full `git diff`; re-read queue |
| Review | `/review-task` | task prompt → scoped change-set | Re-emit next prompt (`next` owns that) |

## When re-read is required

- User edited a cached path since last read (`git status` / explicit user change)
- New task links paths not in cache
- `adopt --refresh`, `shared refresh`, or `brief`/`story` changed domain docs
- Contradiction or blocking unknown — targeted re-read of one path only
- Promptize reuse miss + ultra miss (HEAD drift, stale handoff, security/migration needs fresh code)

## Skill reference loading

| Skill | Load on activation | Load only when subcommand needs |
|-------|-------------------|-------------------------------|
| dev-pipeline | `SKILL.md` | `schema.md`, `adopt.md`, `briefing.md`, `user-stories.md`, etc. — **one** file per branch |
| promptize | `SKILL.md` + `specification.md` | `inspection.md` on reuse/ultra miss; `policies.md` for security/DB/API/UI/async |
| review-task | `SKILL.md` | `checklist.md` when scoring |
| commit | `SKILL.md` only | — |

Do not read human-only `dev-pipeline/README.md` as agent procedure.

## Product repo artifacts (token tooling)

| File | Git | Role |
|------|-----|------|
| `docs/dev-pipeline/SESSION-CACHE.md` | gitignored | Carry-over + Loaded + **Promptize reuse** |
| `docs/dev-pipeline/ADOPTION.md` Inspect snapshot | committed | Repo-wide inspect index |
| `agent-prompts/TASK-*.md` | gitignored | Per-task handoff |
| `docs/promptize-prompts/{TASK-ID}.md` | usually committed | Deep spec anchor / reuse body |

`init` and `adopt` create/update cache stubs; `next` / `task` update cache after each handoff; `/promptize` upserts Promptize reuse.

## Promptize output density (v2.1 Ultra Lean)

- Evidence map only if ≥2 files; else short path.
- Engineering Decisions: **one sentence** when possible.
- Out of Scope: 3–4 hard excludes (`❌` / Do not:).
- Minimal = **4 sections**; omit empty; no `N/A` walls outside `--full`.
- Intermediate spec internal — render only (skipped on reuse / ultra / micro direct-render).
- Prompt-only: never print WARN/ERROR lists; surface only real CONFLICT/BLOCKED that block counts.
- Header may include `Cache: REUSE_HIT | ULTRA | DELTA` — never invent “tokens saved” numbers.
