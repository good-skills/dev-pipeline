# Detection (Scan phase)

**Discovery only.** Regex/grep/awk/find/hashes MUST NOT alone justify a code change. Use tooling **already in the repository/toolchain** — do not install or invoke globally unavailable tools. **No new dependencies.**

## Canonical file discovery (`$FILES`)

**Single source of truth** for all pattern scans. Never use `eval`. Never grep-traverse `$SCOPE` independently — scan only files from `$FILES`.

```bash
# Build once per scan. Add -not -path for each Observed repo-specific generated/vendor dir.
FILES=$(find "$SCOPE" \
  \( -name '*.ts' -o -name '*.tsx' \) \
  -not -path '*/node_modules/*' \
  -not -path '*/dist/*' \
  -not -path '*/build/*' \
  -not -path '*/coverage/*' \
  -not -path '*/.next/*' \
  -not -path '*/.turbo/*' \
  <observed: -not -path '*/generated/*' -not -path '*/vendor/*' ...>)
```

Use `xargs -r` when piping `$FILES` to `wc`, `md5sum`, `awk`. File scope → single file path in `$FILES`.

**`.d.ts`:** do not modify unless repo evidence shows authoritative source and finding directly concerns it.

## Catalog (patterns 1–10)

|#|Name|Scan|Confirm|
|-|-|-|-|
|1|Spaghetti|auto|`APPROXIMATE_LONG_FN_CANDIDATE` — prefer AST/lint; awk line-count is approximate only|
|2|Golden Hammer|**manual only**|no auto-scan; report only via inspection or user request|
|3|Lava Flow|auto|see **Lava Flow rules** below|
|4|God Object|auto|`LARGE_MODULE_CANDIDATE` — coherent large modules OK|
|5|Premature Opt|**manual only**|no auto-scan; evidence before removing optimizations|
|6|Identical files|auto|identical **files** via `md5sum` — not duplicate blocks|
|7|Magic literals|auto|domain meaning, reuse, non-obvious|
|8|Hard-coded config / secret|auto|**8a** config (URLs, ports, literals) · **8b** potential secret (literal credentials)|
|9|`any`|auto|see **any remediation**|
|10|Suppressions|auto|per-kind; documented `@ts-expect-error` may stay|

## Lava Flow rules

- `POSSIBLY_UNUSED_EXPORT` is **not** dead-code proof.
- **Zero-result textual search MUST never prove dead code.** Absence of references is only a candidate signal.
- Does not model: re-exports, `export *`, aliased imports, dynamic `import()`, framework registration.
- Prefer repo unused-export tooling (tsc, ESLint, knip, depcheck) when available in toolchain.
- **Type/interface exports:** assume external/public usage possible unless package visibility proves internal-only.
- **Library/public packages:** treat exports as externally consumable unless evidence proves private API.

## any remediation

(1) concrete → (2) generic → (3) union/intersection → (4) `unknown` + narrowing → (5) escape.

Never replace mechanically. Do not change when it alters assignability, inference, public API, overload resolution, narrowing, or runtime behavior. `any→unknown` only after downstream usage reviewed.

**Third-party boundaries:** prefer narrow adapter or runtime validation per project conventions; do not spread unsafe casts.

## Pattern 8 — config vs secret

| Sub | Example | Action |
|-----|---------|--------|
| **8a** config | `const PORT = 3000` | existing config/env if justified |
| **8a** not secret | `process.env.API_KEY` | not hard-coded secret |
| **8b** secret | literal credential in source | candidate → `<REDACTED>`; never print value |

## Grep candidates (on `$FILES` only)

```bash
# 1 Spaghetti — APPROXIMATE_LONG_FN_CANDIDATE
echo "$FILES" | xargs -r awk '/^function |^export function |^const .* = \(/ {f=FILENAME;s=NR} /^}/ {if(NR-s>80) print f":"s" APPROXIMATE_LONG_FN_CANDIDATE ("NR-s" lines)"}'
echo "$FILES" | xargs -r grep -n "^\s\{16,\}" | head -20

# 3 Lava Flow — POSSIBLY_UNUSED_EXPORT; zero count ≠ dead code
echo "$FILES" | xargs -r grep -Hn "^export " | while IFS= read -r line; do
  file=$(echo "$line" | cut -d: -f1); name=$(echo "$line" | grep -oP 'export (?:function|const|type|interface|class) \K\w+')
  [ -z "$name" ] && continue
  count=$(echo "$FILES" | xargs -r grep -rlw "$name" | grep -v "$file" | wc -l)
  [ "$count" -eq 0 ] && echo "POSSIBLY_UNUSED_EXPORT: $line"
done

# 4 God Object — LARGE_MODULE_CANDIDATE
echo "$FILES" | xargs -r wc -l | sort -rn | head -20 | awk '{print "LARGE_MODULE_CANDIDATE:", $0}'

# 6 Identical files
echo "$FILES" | xargs -r md5sum | sort | uniq -d -w 32

# 7 Magic literals
echo "$FILES" | xargs -r grep -n "[^a-zA-Z_][2-9][0-9]\+\b" | grep -v "//\|import\|export\|type\|interface" | head -20

# 8a Config
echo "$FILES" | xargs -r grep -n "http://\|https://" | grep -v "import\|href\|localhost" | head -20

# 8b Potential secret — path only
echo "$FILES" | xargs -r grep -rln "password\|secret\|apikey\|api_key" | grep -v "import\|type\|interface\|//\|process\.env" | head -10

# 9 any — skip .d.ts unless authoritative source
echo "$FILES" | grep -v '\.d\.ts$' | xargs -r grep -n ": any\|: any\[\]\|as any\|<any>" | head -30

# 10 Suppressions
echo "$FILES" | xargs -r grep -n "@ts-ignore\|@ts-expect-error\|@ts-nocheck"
echo "$FILES" | xargs -r grep -n "eslint-disable.*@typescript-eslint"
```

## Bounded inspection

Per candidate: what → anti-pattern? → justified? → smallest safe change → risk + benefit.

Read beyond modification scope when needed (cross-package usage, public API). **TSX:** hook order, closures, state, refs, effects, context, memo, forwarded refs.

## Finding record

`docs/antipattern-remediation.md` — **metadata only**; never scan, analyze, or remediate this file.

Never include literal secrets — `<REDACTED>` only.
