# Token efficiency (pipeline skills)

Rules for **dev-pipeline**, **promptize**, **review-task**, and **commit** so agents maximize work per token and avoid repeating inspect/read work.

Read this when any pipeline skill runs. Details: [context-cache.md](context-cache.md), [inspect.md](inspect.md).

## Golden rules

1. **One inspect per user intent** — pick slices from [inspect.md](inspect.md); do not re-run full repo inspect across skills in the same turn.
2. **Handoff is authoritative** — after `next` / `task`, Promptize and implementers start from `agent-prompts/TASK-*.md`; do not re-gather facts already in the handoff.
3. **Session cache** — before opening a path, check `docs/dev-pipeline/SESSION-CACHE.md` (if present). If listed and source file unchanged, **reuse carry-over**; read **delta only**.
4. **Conversation reuse** — same chat/session: do not re-read files you already loaded for the prior task unless the file changed or this task needs new sections.
5. **Delta `next`** — consecutive tasks in the same phase: reuse stable PRODUCT/SHARED summaries; read only new queue row, epic section, and new `US-*` / contract paths.
6. **Compact output** — Promptize default **compact**; pipeline handoffs stay within [prompt-template.md](../dev-pipeline/prompt-template.md) size budget.
7. **Skills are procedures, not content** — do not paste entire reference docs into replies; cite paths and tables.

## Orchestration (one pass per stage)

| Stage | Skill | Read / run | Do **not** |
|-------|-------|------------|------------|
| Queue handoff | `/dev-pipeline next` | cache → queue row → delta docs | Full docs tree; re-read PRODUCT if cached |
| Deep spec | `/promptize` | handoff → delta inspect only | Full inspect if handoff exists |
| Implement | implementer | handoff → paths in Required changes | Full SHARED unless contracts change |
| Commit | `/commit` | stat → scoped diff | Full `git diff`; re-read queue |
| Review | `/review-task` | task prompt → scoped change-set | Re-emit next prompt (`next` owns that) |

## When re-read is required

- User edited a cached path since last read (`git status` / explicit user change)
- New task links paths not in cache
- `adopt --refresh`, `shared refresh`, or `brief`/`story` changed domain docs
- Contradiction or blocking unknown — targeted re-read of one path only

## Skill reference loading

| Skill | Load on activation | Load only when subcommand needs |
|-------|-------------------|-------------------------------|
| dev-pipeline | `SKILL.md` | `schema.md`, `adopt.md`, `briefing.md`, `user-stories.md`, etc. — **one** file per branch |
| promptize | `SKILL.md` | `policies.md` when domain requires; compact tier default |
| review-task | `SKILL.md` | `checklist.md` when scoring |
| commit | `SKILL.md` only | — |

Do not read human-only `dev-pipeline/README.md` as agent procedure.

## Product repo artifacts (token tooling)

| File | Git | Role |
|------|-----|------|
| `docs/dev-pipeline/SESSION-CACHE.md` | gitignored | Paths already read + stable carry-over for delta `next` |
| `docs/dev-pipeline/ADOPTION.md` Inspect snapshot | committed | Repo-wide inspect index |
| `agent-prompts/TASK-*.md` | gitignored | Per-task handoff |
| `docs/promptize-prompts/{TASK-ID}.md` | usually committed | Deep spec anchor |

`init` and `adopt` create/update cache stubs; `next` / `task` update cache after each handoff.
