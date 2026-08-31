---
name: commit
description: >-
  Commits current working-tree changes with a concise, repo-style message
  derived from the diff. Prefer including TASK-ID or Feature-ID in the subject
  when the change is pipeline task work. Use when the user starts with /commit,
  attaches this skill, or explicitly asks to commit via the commit skill. Does
  not push unless the user also asks to push.
disable-model-invocation: true
version: 1.1.0
---

# Commit

When the user message begins with `/commit`, this skill is attached, or they explicitly ask to **commit the latest / current changes** via this skill, run the commit workflow below **immediately**.

**Purpose:** Stage relevant changes and create **one** git commit with a proper message that matches the repository’s style. Do not push unless the user also explicitly asks.

## Activation

| Form | Behavior |
|------|----------|
| `/commit` | Commit all relevant current changes |
| `/commit <hint>` | Same, using `<hint>` to steer the message (still base it on the diff) |
| Skill attached + “commit” / “commit the latest changes” | Same as `/commit` |

Do not treat unrelated coding requests as this skill unless `/commit` or an explicit commit-skill ask is present.

## Safety

Follow the user’s Cursor **git commit rules** when present (hooks, amend policy, no force-push). In addition, this skill requires:

- **NEVER** update git config
- **NEVER** skip hooks unless the user explicitly requests it
- **NEVER** push unless the user explicitly asks
- **NEVER** use interactive git (`-i`)
- Do **not** commit secrets (`.env`, credentials, private keys). Warn and exclude them

## Workflow

Independent reads may be parallel; stage → commit → verify are sequential.

### 1. Inspect (parallel)

```bash
git status
git diff
git diff --cached
git log -8 --oneline
```

Use `git log` to match this repo’s message style (tense, prefixes like `feat:`, scope, length).

**Resolve pipeline task id (optional but recommended):**

1. Explicit id in user message or `/commit` hint (`TASK-…` or feature id like `ASK-01`)
2. `agent-prompts/TASK-*.md` path from conversation
3. Active `in_progress` row in phase `TASK-QUEUE.md`

### 2. Decide what to commit

- Include tracked modifications and relevant untracked source/docs that belong to the change
- Exclude secrets, build artifacts, and unrelated junk unless the user explicitly requires them
- Prefer **task-scoped** commits when the work is a pipeline task — do not bundle unrelated concerns
- If there are **no** changes to commit: tell the user and **stop** — do not create an empty commit
- If scope is ambiguous and grouping would be wrong: ask before committing

### 3. Draft the message

- 1–2 sentences, focus on **why** over a file laundry list
- Match repo style from `git log` (e.g. `feat:`, `fix:`, `docs:`, `refactor:`)
- **Pipeline task work:** include id in subject for `/review-task` traceability, e.g.:
  - `feat(ASK-01): add login validation` (feature id)
  - `fix(TASK-ASK-01-01): handle empty email` (full task id)
  - `feat(TASK-USER-02-01): …` when repo uses full task ids in scopes
- If the user passed `/commit <hint>`, incorporate the hint only where it fits the actual diff

### 4. Stage and commit

```bash
git add <relevant paths>
git commit -m "$(cat <<'EOF'
Message here.

EOF
)"
git status
```

Always pass the message via a HEREDOC so formatting stays intact.

### 5. Report

Confirm: commit hash/subject, whether the branch is ahead of remote, working tree state, and the task id used in the message (if any).

## Failure handling

- **Hook failure:** fix and create a **new** commit (follow user amend rules if applicable)
- **Nothing to commit:** say so; stop
- **Secrets in change set:** unstage/exclude, warn, commit the rest if safe; otherwise stop and ask

## Out of scope

- Creating pull requests
- Pushing to remote (unless the user explicitly asks)
- Rebase, merge, or branch management beyond what’s required to commit
