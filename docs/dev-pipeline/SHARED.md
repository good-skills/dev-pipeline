# Shared Source of Truth

**Product:** [docs/PRODUCT.md](../PRODUCT.md)
**Last refreshed:** 2026-09-20 (init)

## Rule (non-negotiable)

All surfaces and phases consume the paths below as the product-wide contract spine.
Do **not** invent parallel API/DTO/entity/business-rule/user-story trees for a new service.
User stories under `docs/user-stories/` are product-wide — not owned by frontend, backend, or any single surface.
Extend additively; breaking changes need an explicit task + dual-surface note.

## Surfaces

| Surface ID | Slug             | Kind         | Status | Owning phases | Notes                    |
|------------|------------------|--------------|--------|---------------|--------------------------|
| SUR-01     | skills           | other        | planned| PH-00         | dev-pipeline skill docs  |

Kind values: `frontend` \| `backend` \| `worker` \| `mobile` \| `bff` \| `shared-lib` \| `other`
Status: `planned` \| `active` \| `parked` \| `done`

## Authoritative shared paths

| Category                | Path                                                                    | Consumers (surfaces) | Evidence           |
|-------------------------|-------------------------------------------------------------------------|----------------------|--------------------|
| Entities                | (none discovered yet)                                                   | —                    | —                  |
| API / DTO               | (none discovered yet)                                                   | —                    | —                  |
| Business rules          | (none discovered yet)                                                   | —                    | —                  |
| User stories / flows    | (none discovered yet)                                                   | all                  | —                  |
| Architecture boundaries | [docs/README.md](../../README.md)                                      | all                  | Observed from repo |
| Decisions / ADR         | (none discovered yet)                                                   | —                    | —                  |

## Inheritance log

| Event | What was inherited / added                       |
|-------|--------------------------------------------------|
| init  | Seeded with repo context + defined surface      |