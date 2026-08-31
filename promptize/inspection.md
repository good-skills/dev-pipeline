# Promptize inspection

Read [../shared/inspect.md](../shared/inspect.md) for the unified inspect layer. Complete inspection **before** generating the prompt.

## Promptize slices (task-scoped)

Run in order; stop when the task is sufficiently specified:

1. **pipeline-handoff** — if `agent-prompts/TASK-*.md`, `docs/promptize-prompts/TASK-*.md`, or queue row exists
2. **manifest** — unless handoff already lists stack and validation commands
3. **code** — affected implementation areas only
4. **docs** — only paths not already covered by handoff + project instructions if relevant
5. **git** — when `--execute` or follow-up execute is likely

Do not inspect unrelated files. Do not duplicate work already authoritative in a pipeline handoff.

## Evidence status

For each factual claim in Repository Context:

| Status | Use when |
|--------|----------|
| **Observed** | Directly supported by file or command output |
| **Inferred** | Reasonable but not explicit — must be labeled |
| **Unknown** | Not found after reasonable task-scoped search |

Never present Inferred as Observed. Ask only **blocking** unknowns (see SKILL.md).

## Relevant Files pattern

Every listed file needs role + evidence. Do not list files without a why.

## Compact vs internal inspect

- **Generated prompt output** uses compact or full format per SKILL.md (default **compact**).
- **Internal inspect notes** do not need Observed/Inferred tags on every bullet — use tags in the emitted Repository Context section.

## Project instruction files

Summarize applicable conventions in **Project Instructions**; read only scoped rules/files.

## Git snapshot (execute)

Record branch, dirty paths, overlap with planned touch set. Protect pre-existing user changes (see [policies.md](policies.md)).
