# Detection (Scan → Classify → Inspect → Confirm → Risk)

**Heuristics = candidates only.** Risk is assessed **after** contextual confirmation.

Vars: `$SCOPE`; `$I`=`--include='*.ts' --include='*.tsx'`; `$X`=`| grep -v node_modules`; `$F`=find ts/tsx excluding generated/vendor paths.

Prefer repo AST/lint/unused-export tooling over grep when available. File scope → `grep -n`; use `head` on scan.

## Catalog

|#|Name|Candidate heuristic|Confirm before fix|
|-|-|-|-|
|1|Spaghetti|approx long-fn, deep indent|control-flow, nesting, responsibilities, readability — prefer AST/lint for fn boundaries; awk is approximate only|
|2|Golden Hammer|—|**manual only**|
|3|Lava Flow|comments, suppress, possibly unreferenced export|barrels, dynamic import, registration, tests, external API — grep name-match is imprecise; prefer repo unused-export tooling|
|4|God Object|`LARGE_MODULE_CANDIDATE` (line count)|mixed responsibilities/domains, coupled state — coherent large modules OK|
|5|Premature Opt|—|**manual only** — evidence before removing optimizations|
|6|Identical files|`md5sum` match|identical **files** only — not duplicate blocks|
|7|Magic literals|bare nums/strings|domain meaning, reuse, non-obvious — obvious locals stay inline|
|8|Hard Coding|URLs, ports, secret-like names|config vs potential secret — redact; never `cat`/echo secrets|
|9|`any`|`: any`, `as any`|concrete → generic → union → `unknown`+narrow → escape|
|10|Suppressions|various suppress kinds|`@ts-expect-error` may stay if intentional+documented|

## Grep candidates (discovery only)

```bash
# 1 Spaghetti — APPROXIMATE_LONG_FN_CANDIDATE (first } ≠ fn end; nested fns false-positive)
# Prefer repo AST/lint for function length/structure when available
$F | xargs awk '/^function |^export function |^const .* = \(/ {f=FILENAME;s=NR} /^}/ {if(NR-s>80) print f":"s" APPROXIMATE_LONG_FN_CANDIDATE ("NR-s" lines)"}'
grep -rn "^\s\{16,\}" $I "$SCOPE" $X | head -20

# 3 Lava Flow — POSSIBLY_UNUSED_EXPORT (substring false positives; incomplete export forms)
# Prefer: tsc --noEmit unused, eslint unused-exports, knip, depcheck, etc.
grep -rn "^export " $I "$SCOPE" $X | while read line; do
  file=$(echo "$line" | cut -d: -f1); name=$(echo "$line" | grep -oP 'export (?:function|const|type|interface|class) \K\w+')
  [ -z "$name" ] && continue
  count=$(grep -rlw "$name" $I "$SCOPE" $X | grep -v "$file" | wc -l)
  [ "$count" -eq 0 ] && echo "POSSIBLY_UNUSED_EXPORT: $line"
done
grep -rn "//.*\(function\|const\|return\|if \)" $I "$SCOPE" $X | head -20

# 4 God Object — LARGE_MODULE_CANDIDATE (line count ≠ God Object)
$F | xargs wc -l | sort -rn | head -20 | awk '{print "LARGE_MODULE_CANDIDATE:", $0}'

# 6 Identical files
$F | xargs md5sum | sort | uniq -d -w 32

# 7 Magic literals
grep -rn "[^a-zA-Z_][2-9][0-9]\+\b\|[^a-zA-Z_]1[0-9]\{2,\}\b" $I "$SCOPE" $X | grep -v "//\|import\|export\|type\|interface" | head -20

# 8 Hard Coding — redact in output; never cat/print secret files or values
grep -rn "http://\|https://" $I "$SCOPE" $X | grep -v "import\|href\|localhost" | head -20
grep -rn ":[0-9]\{4,5\}\b" $I "$SCOPE" $X | head -10
grep -rn "password\|secret\|token\|apikey\|api_key" $I "$SCOPE" $X | grep -v "import\|type\|interface\|//" | head -10

# 9 any
grep -rn ": any\|: any\[\]\|as any\|<any>" $I "$SCOPE" $X | grep -v "\.d\.ts" | head -30

# 10 Suppressions
grep -rn "@ts-ignore\|@ts-expect-error\|@ts-nocheck" $I "$SCOPE" $X
grep -rn "eslint-disable.*@typescript-eslint" $I "$SCOPE" $X
```

## Bounded contextual inspection

Per candidate until sufficient: (1) what it is, (2) truly anti-pattern?, (3) remediation justified?, (4) smallest safe change, (5) **risk** + engineering benefit.

**TSX:** hook order, closures, state, context, memo before extraction.

## Remediation file

When >15 confirmed or >10 files **and** path permitted by repo conventions:

```markdown
# Anti-Pattern Remediation
Scope: {path} | Generated: {timestamp}

## Finding
- Pattern: {name}
- Risk: low | medium | high
- Status: pending | fixed | accepted | blocked
- File: {path}
- Issue: {no secrets}
- Evidence: {observed/inferred}
- Fix: {minimal change}
- Verification: {command}
```

Never include secret contents.
