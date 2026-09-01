# Detection (Scan phase)

**Discovery only.** Regex/grep/awk/find/hashes MUST NOT alone justify a code change. Use tooling **already in the repository/toolchain** (AST, `tsc`, ESLint, unused-export scripts in `package.json`) — do not install or invoke globally unavailable tools. **No new dependencies.**

## Variables

| Var | Definition |
|-----|------------|
| `$SCOPE` | Resolved path from SKILL.md |
| `$I` | `--include='*.ts' --include='*.tsx'` |
| `$X` | `\| grep -vE 'node_modules\|/dist/\|/build/\|/coverage/\|/\.next/\|/\.turbo/'` |

File scope → `grep -n` on file. Use `head` on scan.

## File discovery — canonical rule

**Protected areas** = standard exclusions + **observed** repo-specific exclusions (from tsconfig exclude, `.gitignore`, package layout, conventions). All pattern scans use this — no per-pattern exclusions.

```bash
# Inline find — no eval. Add -not -path for each Observed repo-specific generated/vendor dir.
find "$SCOPE" \
  \( -name '*.ts' -o -name '*.tsx' \) \
  -not -path '*/node_modules/*' \
  -not -path '*/dist/*' \
  -not -path '*/build/*' \
  -not -path '*/coverage/*' \
  -not -path '*/.next/*' \
  -not -path '*/.turbo/*' \
  <observed: -not -path '*/generated/*' -not -path '*/vendor/*' ...>
```

Use `xargs -r` when piping to `wc`, `md5sum`, `awk` (avoid empty-input misleading output).

**`.d.ts`:** never modify unless it is an explicit repository source file and the finding directly concerns it. Skip generated declaration files.

## Catalog

|#|Name|Scan|Confirm|
|-|-|-|-|
|1|Spaghetti|auto|`APPROXIMATE_LONG_FN_CANDIDATE` — prefer AST/lint for fn boundaries|
|2|Golden Hammer|**not auto-scanned**|manual review only — never autonomous remediation|
|3|Lava Flow|auto|`POSSIBLY_UNUSED_EXPORT` is **not** usage/dead-code proof — prefer tsc/AST/dep graph; re-exports, dynamic import, registration; **type/interface exports may have external consumers** unless package visibility proves otherwise|
|4|God Object|auto|`LARGE_MODULE_CANDIDATE` — coherent large modules OK|
|5|Premature Opt|**not auto-scanned**|manual only — evidence before removing optimizations|
|6|Identical files|auto|`md5sum` = identical **files** only|
|7|Magic literals|auto|domain meaning, reuse, non-obvious — retain obvious literals unless convention says otherwise|
|8|Hard-coded config|auto|existing config mechanism — not a secret by itself|
|8b|Potential secret|auto|literal credential patterns; `process.env.X` ≠ hard-coded secret|
|9|`any`|auto|see **any remediation**|
|10|Suppressions|auto|per-kind; documented `@ts-expect-error` may stay|

## any remediation

Preference: (1) concrete type → (2) generic → (3) union/intersection → (4) `unknown` + narrowing → (5) justified escape.

**Never replace mechanically.** Do not change when it alters assignability, inference, public API, overload resolution, narrowing, or runtime behavior.

**Third-party/untyped boundaries** (`thirdPartyResult: any`): prefer narrow adapter or runtime validation when consistent with project conventions; do not spread unsafe casts through the codebase.

## Hard-coded config vs potential secret

| Kind | Example | Action |
|------|---------|--------|
| Config | `const PORT = 3000` | existing config/env if justified |
| Not secret | `process.env.API_KEY` | not hard-coded secret |
| Potential secret | literal key in source | confirm → `<REDACTED>`; never print value |

## Grep candidates

```bash
# Shared find prefix (abbreviated FIND) — expand with observed repo excludes
FIND='find "$SCOPE" \( -name "*.ts" -o -name "*.tsx" \) -not -path "*/node_modules/*" ...'

# 1 Spaghetti
$FIND | xargs -r awk '/^function |^export function |^const .* = \(/ {f=FILENAME;s=NR} /^}/ {if(NR-s>80) print f":"s" APPROXIMATE_LONG_FN_CANDIDATE ("NR-s" lines)"}'
grep -rn "^\s\{16,\}" $I "$SCOPE" $X | head -20

# 3 Lava Flow — counts are NOT proof; prefer repo unused-export tooling when available
grep -rn "^export " $I "$SCOPE" $X | while read line; do
  file=$(echo "$line" | cut -d: -f1); name=$(echo "$line" | grep -oP 'export (?:function|const|type|interface|class) \K\w+')
  [ -z "$name" ] && continue
  count=$(grep -rlw "$name" $I "$SCOPE" $X | grep -v "$file" | wc -l)
  [ "$count" -eq 0 ] && echo "POSSIBLY_UNUSED_EXPORT: $line"
done

# 4 God Object
$FIND | xargs -r wc -l | sort -rn | head -20 | awk '{print "LARGE_MODULE_CANDIDATE:", $0}'

# 6 Identical files
$FIND | xargs -r md5sum | sort | uniq -d -w 32

# 7 Magic literals
grep -rn "[^a-zA-Z_][2-9][0-9]\+\b" $I "$SCOPE" $X | grep -v "//\|import\|export\|type\|interface" | head -20

# 8a Config
grep -rn "http://\|https://" $I "$SCOPE" $X | grep -v "import\|href\|localhost" | head -20

# 8b Potential secret — path only; value <REDACTED>
grep -rln "password\|secret\|apikey\|api_key" $I "$SCOPE" $X | grep -v "import\|type\|interface\|//\|process\.env" | head -10

# 9 any — skip generated .d.ts; do not modify .d.ts unless explicit source
grep -rn ": any\|: any\[\]\|as any\|<any>" $I "$SCOPE" $X | grep -v '\.d\.ts' | head -30

# 10 Suppressions
grep -rn "@ts-ignore\|@ts-expect-error\|@ts-nocheck" $I "$SCOPE" $X
grep -rn "eslint-disable.*@typescript-eslint" $I "$SCOPE" $X
```

## Bounded inspection

Per candidate: what it is → anti-pattern? → justified? → smallest safe change → risk + benefit.

Read: fn/class/module; imports/exports; **cross-package** usages; tests; conventions.

**TSX:** hook order, closures, state, refs, effects, context, memo, forwarded refs, lifecycle.

## Finding record

Metadata file (`docs/antipattern-remediation.md`) — **not a scan/remediation target**.

```markdown
- Status: candidate | inspected | confirmed | rejected | fixed | accepted | blocked
- Pattern / File / Location / Evidence / Risk / Decision / Action / Verification
- Reason: {required for accepted/blocked}
```

Never include literal secrets — `<REDACTED>` only.
