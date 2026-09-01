# Detection (Scan phase)

**Discovery only.** Regex, grep, awk, find, hashes, filename heuristics MUST NOT alone justify a code change. Prefer existing repo tooling (AST, `tsc`, ESLint, unused-export, dep graph). **No new dependencies.**

## Variables

| Var | Definition |
|-----|------------|
| `$SCOPE` | Resolved path from SKILL.md Resolve |
| `$I` | `--include='*.ts' --include='*.tsx'` |
| `$X` | `\| grep -vE 'node_modules\|/dist/\|/build/\|/coverage/\|/\.next/\|/\.turbo/'` |
| `$F` | See **File discovery** below |

File scope → `grep -n` on file; skip `$F`. Use `head` on scan; expand on hits.

## File discovery (`$F`) — single source of truth

All pattern scans use this. Do not build per-pattern exclusions.

```bash
# 1. Base find
FIND_BASE='find "$SCOPE" \( -name "*.ts" -o -name "*.tsx" \)'

# 2. Standard excludes (always)
EXCL_STD='-not -path "*/node_modules/*" \
  -not -path "*/dist/*" -not -path "*/build/*" \
  -not -path "*/coverage/*" -not -path "*/.next/*" -not -path "*/.turbo/*"'

# 3. Repo-specific generated/vendor (from tsconfig exclude, .gitignore, package.json, conventions)
#    Examples: generated/, vendor/, .codegen/, prisma/generated/, openapi-generated/
#    Add -not -path for each Observed path — do not hard-code entire list if repo defines others

$F="$FIND_BASE $EXCL_STD <repo-specific -not -path entries>"
```

Run: `eval $F` or inline the expanded command. Protected areas in SKILL.md defer here.

## Catalog

|#|Name|Candidate|Confirm|
|-|-|-|-|
|1|Spaghetti|`APPROXIMATE_LONG_FN_CANDIDATE`, deep indent|control-flow, nesting, responsibilities — prefer AST/lint for fn boundaries|
|2|Golden Hammer|—|**manual only**|
|3|Lava Flow|`POSSIBLY_UNUSED_EXPORT`, comments, suppress|barrels, dynamic import, registration, tests, **cross-package** usage — in-package silence ≠ dead|
|4|God Object|`LARGE_MODULE_CANDIDATE`|mixed responsibilities/domains — coherent large modules OK|
|5|Premature Opt|—|**manual only** — evidence before removing optimizations|
|6|Identical files|`md5sum` match|identical **files** only — not duplicate blocks|
|7|Magic literals|bare nums/strings|domain meaning, reuse, non-obvious — retain obvious (e.g. `status === 200`) unless convention says otherwise|
|8|Hard-coded config|URLs, ports, literals in logic|use existing config mechanism — **not** a secret by itself|
|8b|Potential secret|literal credential/token/password/API-key patterns|candidate only; `process.env.X` is **not** hard-coded secret|
|9|`any`|`: any`, `as any`|see **any remediation** below|
|10|Suppressions|per-kind|documented `@ts-expect-error` may stay|

## any remediation

Preference order: (1) concrete type → (2) generic → (3) union/intersection → (4) `unknown` + narrowing → (5) justified escape.

**Never replace mechanically.** Do not change `any` when it alters assignability, generic inference, public API shape, overload resolution, control-flow narrowing, or runtime behavior. `any→unknown` only after downstream usage reviewed.

## Hard-coded config vs potential secret

| Kind | Example | Action |
|------|---------|--------|
| Config | `const PORT = 3000` | move to existing config/env if justified |
| Not secret | `process.env.API_KEY` | not a hard-coded secret |
| Potential secret | literal key/password in source | candidate → confirm → redact as `<REDACTED>`; never print value |

## Grep candidates

```bash
# 1 Spaghetti — APPROXIMATE_LONG_FN_CANDIDATE
eval $F | xargs awk '/^function |^export function |^const .* = \(/ {f=FILENAME;s=NR} /^}/ {if(NR-s>80) print f":"s" APPROXIMATE_LONG_FN_CANDIDATE ("NR-s" lines)"}'
grep -rn "^\s\{16,\}" $I "$SCOPE" $X | head -20

# 3 Lava Flow — POSSIBLY_UNUSED_EXPORT; check cross-package before confirm
# Prefer: tsc unused, eslint unused-exports, knip, depcheck
grep -rn "^export " $I "$SCOPE" $X | while read line; do
  file=$(echo "$line" | cut -d: -f1); name=$(echo "$line" | grep -oP 'export (?:function|const|type|interface|class) \K\w+')
  [ -z "$name" ] && continue
  count=$(grep -rlw "$name" $I "$SCOPE" $X | grep -v "$file" | wc -l)
  [ "$count" -eq 0 ] && echo "POSSIBLY_UNUSED_EXPORT: $line"
done

# 4 God Object — LARGE_MODULE_CANDIDATE
eval $F | xargs wc -l | sort -rn | head -20 | awk '{print "LARGE_MODULE_CANDIDATE:", $0}'

# 6 Identical files
eval $F | xargs md5sum | sort | uniq -d -w 32

# 7 Magic literals
grep -rn "[^a-zA-Z_][2-9][0-9]\+\b" $I "$SCOPE" $X | grep -v "//\|import\|export\|type\|interface" | head -20

# 8a Hard-coded config
grep -rn "http://\|https://" $I "$SCOPE" $X | grep -v "import\|href\|localhost" | head -20
grep -rn ":[0-9]\{4,5\}\b" $I "$SCOPE" $X | head -10

# 8b Potential secret — output location only; value <REDACTED>
grep -rln "password\|secret\|apikey\|api_key" $I "$SCOPE" $X | grep -v "import\|type\|interface\|//\|process\.env" | head -10

# 9 any
grep -rn ": any\|: any\[\]\|as any\|<any>" $I "$SCOPE" $X | grep -v "\.d\.ts" | head -30

# 10 Suppressions — classify per kind
grep -rn "@ts-ignore\|@ts-expect-error\|@ts-nocheck" $I "$SCOPE" $X
grep -rn "eslint-disable.*@typescript-eslint" $I "$SCOPE" $X
```

## Bounded inspection

Per candidate: (1) what it is, (2) anti-pattern?, (3) justified?, (4) smallest safe change, (5) risk + benefit.

Read: containing fn/class/module; imports/exports; **cross-package usages** for exports; tests; conventions.

**TSX before extraction:** hook order, closure capture, state ownership, ref identity, effect deps, context/provider, memo, forwarded refs, lifecycle. Escalate risk if affected.

## Finding record (remediation file)

When SKILL.md tracking threshold met and repo permits `docs/antipattern-remediation.md`:

```markdown
## Finding
- Status: candidate | inspected | confirmed | rejected | fixed | accepted | blocked
- Pattern: {name}
- File: {repo-relative}
- Location: {line/symbol}
- Evidence: {observed/inferred — no secrets}
- Risk: low | medium | high
- Decision: {confirm/reject/retain/block rationale}
- Action: {planned or taken fix — no secret values}
- Verification: {command or check}
- Reason: {required for accepted/blocked}
```

Never include literal secret values — use `<REDACTED>`.
