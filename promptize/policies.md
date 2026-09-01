# Promptize Policies

Apply only relevant sections. Unrelated → omit or `N/A`.

## Git / working tree

### Baseline (before implementation)

```bash
git rev-parse HEAD
git rev-parse --abbrev-ref HEAD
git status -sb
git diff --stat
git diff --cached --stat
```

### Protected state

Never overwrite, revert, reset, or discard unstaged or **staged** changes.

**Untracked paths:**

| Case | Rule |
|------|------|
| Pre-existing untracked | Protected |
| Planned new (in Touch Set, task requires) | Allowed at execution |
| Unexpected new during execution | Protected — reassess |

For dirty **existing** Touch Set paths: `git diff -- <path>` + `git diff --cached -- <path>` before editing.

Unrelated dirty paths → protected.

## Dependency policy

Add a dependency **only when all** are true:

1. No suitable existing dependency in repo.
2. No adequate platform/framework API.
3. Meaningful reduction in complexity or risk (not marginal).
4. Compatible with project constraints.
5. Justified in **Engineering Decisions**.

If benefit is marginal → **do not add**. Do not swap dependencies without explicit user intent.

## Security (risk analysis)

For security-sensitive tasks, analyze — do not just checklist:

- Trust boundaries
- Attacker-controlled inputs
- Privileged operations
- Sensitive data flows
- Relevant abuse/failure modes

Then document applicable controls (authn/z, validation, injection, XSS/CSRF, secrets, uploads, path traversal, SSRF, permissions, deps).

Confirmation required before destructive or security-sensitive execution.

## Database / migrations

When schema/data changes:

- Affected schema/models; repo migration mechanism.
- Follow repo conventions; no destructive production changes without confirmation.
- **Strategy** when applicable: expand → migrate/backfill → switch reads/writes → contract.
- Backward compatibility and rollback considerations.

## Interface compatibility

Classify surface changes (use what applies):

| Surface | Document |
|---------|----------|
| HTTP API | New / modified / breaking / internal-only; method, path, request/response, errors, auth |
| GraphQL | Schema/query/mutation changes, deprecation |
| RPC / gRPC | Service, method, message compatibility |
| Events / messages | Topic, payload, ordering, idempotency |
| CLI | Command, flags, exit codes, output |
| Webhooks | Payload, signature, retry semantics |
| Internal interfaces | Module/API between packages |

## UI / UX

Inspect existing design system, spacing, a11y, states, responsive behavior. Extend — do not invent a new system.

## Non-functional requirements

When implied: performance, a11y, security, reliability, scalability, observability, maintainability, i18n, compatibility. Derive measurable targets or mark Unknown.

## Impact analysis

Direct/indirect components, public APIs, data models, shared utils, tests, build/deploy.

## Protected areas

Generated/vendor/fixtures/migration history/build artifacts — list under Constraints. Edit source-of-truth, not generated output, unless repo convention requires.

## Acceptance vs Definition of Done

| | Acceptance Criteria | Definition of Done |
|-|---------------------|-------------------|
| **Answers** | What the software **must do** (observable behavior) | What **engineering completion** means |
| **Example** | `POST /login` returns 401 for invalid credentials | Relevant tests pass; no unrelated files changed |
| **Bad** | "Login works" | — |

Do not merge into one checklist.

## Conflict resolution

Priority: (1) explicit user requirements → (2) repo conventions/evidence → (3) inferences → (4) assumptions.

**Security and destructive operations** override convenience defaults.

When user request, repo convention, and policy conflict → **surface the conflict**; do not silently pick one unless hierarchy explicitly resolves it (e.g. security blocks unsafe user request).

## Definition of Done (detail)

- Behavior matches acceptance criteria
- No unrelated files modified (verified by diff review)
- APIs/interfaces compatible unless explicitly changed
- Lint/format pass where configured
- Relevant tests pass
- No unjustified dependencies
- No task TODOs left
- User working-tree changes preserved
