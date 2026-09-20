# Phases

**Product:** [docs/PRODUCT.md](../PRODUCT.md)
**Last refreshed:** 2026-09-20 (init)

## Phase Index

| PH-ID | Name | Slug | Status | Active | Surface | Current Epic |
|-------|------|------|--------|--------|---------|--------------|
| PH-00 | Intake | intake | planned | No | - | None |

## Phase Rules

- Every phase needs Status (`planned`/`active`/`parked`/`done`)
- `ACTIVE = PH-XX` designates the current working phase
- Active phases can have a CONTEXT.md frozen contracts map
- Switching from PH-01 to PH-02 does not delete PH-01 docs
- Parked phases remain readable; done phases can be deprecated

## Next steps

Consider running:
```bash
/dev-pipeline phase new <name> --set-active
```