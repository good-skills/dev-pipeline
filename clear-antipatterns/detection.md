# Detection (Scan → Classify → Inspect)

**Heuristics produce candidates, not confirmed anti-patterns.** Confirm via contextual inspection before any edit.

Vars: `$SCOPE`; `$I`=`--include='*.ts' --include='*.tsx'`; `$X`=`| grep -v node_modules`; `$F`=find ts/tsx excluding `node_modules`/`dist`/`build` + repo-generated paths.

File scope → `grep -n`; use `head` on scan. If repo has AST/lint duplicate/unused-export tooling, prefer it over fragile regex.

## Catalog

|#|Name|Candidate heuristic|Confirm before fix|
|-|-|-|-|
|1|Spaghetti|long fn, deep indent|control-flow complexity, nesting, responsibility count, readability, local patterns — not line count alone|
|2|Golden Hammer|—|**manual only** — pattern forced where unsuitable|
|3|Lava Flow|comment blocks, stale suppress, possibly unreferenced export|barrels, dynamic import, framework registration, tests, external API — **"possibly unused" ≠ dead**|
|4|God Object|large file, many params|mixed responsibilities/domains, coupled state, distinct change reasons — coherent large modules OK|
|5|Premature Opt|—|**manual only** — need evidence before removing memo/cache; absence of profiling ≠ proof|
|6|Identical files|`md5sum` duplicate files|**not** general duplicate-block detection; same hash = identical file candidate only|
|7|Magic literals|bare nums/strings in logic|domain meaning, reuse, independent change, non-obvious — obvious locals (e.g. HTTP status) stay inline|
|8|Hard Coding|URLs, ports, secret-like names|split: **config** vs **potential secret** — redact secrets; use existing config mechanism|
|9|`any`|`: any`, `as any`|prefer: concrete type → generic → union → `unknown`+narrow → justified escape; no mechanical `any→unknown`|
|10|Suppressions|`@ts-ignore`, `@ts-nocheck`, eslint-disable|`@ts-expect-error` may stay if intentional+documented; treat suppression kinds separately|

## Grep candidates (discovery only)

```bash
# 1 Spaghetti — candidate generators
$F | xargs awk '/^function |^export function |^const .* = \(/ {f=FILENAME;s=NR} /^}/ {if(NR-s>80) print f":"s" CANDIDATE long-fn ("NR-s" lines)"}'
grep -rn "^\s\{16,\}" $I "$SCOPE" $X | head -20

# 3 Lava Flow
grep -rn "^export " $I "$SCOPE" $X | while read line; do
  file=$(echo "$line" | cut -d: -f1); name=$(echo "$line" | grep -oP 'export (?:function|const|type|interface|class) \K\w+')
  count=$(grep -rl "$name" $I "$SCOPE" $X | grep -v "$file" | wc -l)
  [ "$count" -eq 0 ] && echo "POSSIBLY_UNUSED: $line"
done
grep -rn "//.*\(function\|const\|return\|if \)" $I "$SCOPE" $X | head -20

# 4 God Object
$F | xargs wc -l | sort -rn | head -20

# 6 Identical files (not duplicate blocks)
$F | xargs md5sum | sort | uniq -d -w 32

# 7 Magic literals
grep -rn "[^a-zA-Z_][2-9][0-9]\+\b\|[^a-zA-Z_]1[0-9]\{2,\}\b" $I "$SCOPE" $X | grep -v "//\|import\|export\|type\|interface" | head -20

# 8 Hard Coding — redact matches in reports; never copy secret values
grep -rn "http://\|https://" $I "$SCOPE" $X | grep -v "import\|href\|localhost" | head -20
grep -rn ":[0-9]\{4,5\}\b" $I "$SCOPE" $X | head -10
grep -rn "password\|secret\|token\|apikey\|api_key" $I "$SCOPE" $X | grep -v "import\|type\|interface\|//" | head -10

# 9 any
grep -rn ": any\|: any\[\]\|as any\|<any>" $I "$SCOPE" $X | grep -v "\.d\.ts" | head -30

# 10 Suppressions (kinds differ — confirm each)
grep -rn "@ts-ignore\|@ts-expect-error\|@ts-nocheck" $I "$SCOPE" $X
grep -rn "eslint-disable.*@typescript-eslint" $I "$SCOPE" $X
```

## Bounded contextual inspection

Per candidate, read until sufficient:

1. What it represents
2. Whether it is truly an anti-pattern
3. Whether remediation is justified
4. Smallest safe change

Inspect: containing function/class/module; immediate imports/exports; direct usages; relevant tests; project conventions. **TSX:** hook order, closures, state, context, memo, component boundaries before extraction.

## Remediation file format

`docs/antipattern-remediation.md` when >15 confirmed or >10 files:

```markdown
# Anti-Pattern Remediation
Scope: {path} | Generated: {timestamp}

## Finding
- Pattern: {1-10 name}
- Risk: low | medium | high
- Status: pending | fixed | accepted | blocked
- File: {repo-relative path}
- Issue: {description — no secret values}
- Evidence: {observed/inferred — cite paths}
- Fix: {minimal planned change}
- Verification: {command or check run}
```

- `fixed` — remediated
- `accepted` — intentionally retained (document why)
- `blocked` — cannot safely execute
- **Never** include secret contents
