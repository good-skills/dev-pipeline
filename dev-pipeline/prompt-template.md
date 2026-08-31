# Task prompt template

Used by `/dev-pipeline next` and `/dev-pipeline task`, and by `/review-task` when emitting next/rework prompts.

## File naming

| Kind | Path |
|------|------|
| Normal | `agent-prompts/TASK-{FEATURE}-{NN}.md` |
| Rework | `agent-prompts/TASK-{FEATURE}-{NN}-R{N}.md` |

Confirm ignore: `git check-ignore -v <path>` when in a git repo.

## Prompt body (required sections)

Write **self-contained** prompts. No “as discussed above”.

```markdown
# {TASK-ID} — {short title}

**Task ID:** `{TASK-ID}`
**Feature ID:** `{FEATURE-ID}`
**Epic ID:** `{EPIC-ID}`
**Phase:** `{PH-ID}` ({phase slug})
**Surface(s):** `{SUR-ID}` ({slug}) — from `docs/dev-pipeline/SHARED.md`
**Priority:** `P0`|`P1`|`P2`|`P3`
**depends_on:** {ids or —}
**blocks:** {ids or —}
**Queue:** `docs/dev-pipeline/phases/{PH}/TASK-QUEUE.md`

## Product identity (do not violate)
{1–3 lines from docs/PRODUCT.md}

## Shared source of truth (do not fork)
- Index: `docs/dev-pipeline/SHARED.md`
- Follow contracts: `{paths from SHARED + phase freeze}`
- Consumers that must stay compatible: `{surfaces / modules}`
- Do **not** invent parallel API/DTO/entity docs for this surface

## Related user stories (required when user-facing)
- `{US-ID}` — `{docs/user-stories/US-….md}` — flows this task covers: `{US-…-F…}`; flows left open: `{… or —}`
- If none linked but behavior is user-facing: note **Unknown** / gap (prefer linking a story; do not invent story text)

### Flow coverage check
- Current status per cited flow: `{todo|partial|done}` (from story file)
- After this task, story remains incomplete unless all non-cancelled flows are `done`
- Do not contradict open or cancelled flows; do not claim the whole story done early

## Goal
{one paragraph}

## Current state (evidence)
- `{path}` — {what exists / gap}
- …

## Required changes
1. …
2. …

## Out of scope
- …

## Contracts & integrity
- Follow: `{api/dto/entity paths}` (must be SHARED-listed or explicit additive extension task)
- Business rules: `{docs/business-rules/… or CLAIMS links}`
- User stories: `{docs/user-stories/US-…}` — honor business logic + flow steps/AC
- Preserve: {invariants from phase CONTEXT.md + SHARED}
- Do not break: {consumers / modules / other surfaces}
- Respect absorbed claims: `briefs/CLAIMS.md` (do not contradict without an explicit task)

## Acceptance criteria
1. {observable — align with covered story flow AC when linked}
2. {observable}

## Definition of done
- AC met
- Linked story flows for this task reflected accurately (no false `implemented` on the story)
- No unrelated files modified
- No new dependency unless listed under Required changes
- Match existing repo patterns
- Ready for `/commit` then `/review-task {TASK-ID}`

## Validation
- Run only if defined in-repo: `{command}` …
- Manual: …

## Handoff
1. Implement only this task.
2. User runs `/commit` (commit skill) when ready — include `TASK-ID` or Feature-ID in commit subject when possible.
3. User runs `/review-task {TASK-ID}` — PASS → run `/dev-pipeline next`; FAIL/PARTIAL → rework prompt.

## Optional: deepen with Promptize
- When to use: task is complex, cross-cutting, high-risk, or AC/contracts are still fuzzy after this handoff.
- Command (prompt-only by default): `/promptize --save-to-file docs/promptize-prompts/{TASK-ID}.md {seed from Goal + US-* + contracts}`
- Or pipeline shortcut: `/dev-pipeline next --promptize` / `/dev-pipeline task {FEATURE-ID} --promptize`
- Deep spec path (if written): `docs/promptize-prompts/{TASK-ID}.md`
- Rules: Promptize inspects the **product repo**; must honor SHARED, linked `US-*` flows, and this Task/Feature ID — do not invent parallel backlog state.
```

## Rework prompt extras

Add after the title block:

```markdown
**Kind:** rework
**Previous prompt:** `agent-prompts/…`
**Review verdict:** FAIL | PARTIAL

## What failed
- …

## Required fixes (only these)
1. …

## Do not change
- …
```

Keep original Acceptance criteria that are still open; mark passed ones as already satisfied.

## Selection rules for `/dev-pipeline next`

1. Active phase queue only.
2. Status `ready` (or `todo` with all `depends_on` done).
3. Skip `blocked`, `in_progress` (unless user forces ID), `done`.
4. Prefer rework `*-R{N}` for the same feature before advancing to the next feature.
5. One prompt per invocation.
6. Resolve and cite related `US-*` per [user-stories.md](user-stories.md); include flow coverage (open vs covered). If user-facing work has no linked story, note the gap in the prompt — do not invent story text.
7. If `--promptize`: after writing this handoff, run the Promptize companion (prompt-only + `--save-to-file docs/promptize-prompts/{TASK-ID}.md` unless user asked `--execute`); link the saved path in **Optional: deepen with Promptize**. Pipeline handoff remains the ID/story/SHARED anchor.

## Size budget

Prefer prompts that stay scannable: short bullets, paths over pasted code, AC ≤ 7 items. Link epic sections instead of copying entire epics. Full Promptize bodies (when requested) live under `docs/promptize-prompts/` — do not paste the entire Promptize template into `agent-prompts/` by default.
