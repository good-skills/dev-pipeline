# Caveman token policy

Selective Caveman rules for pipeline skills. This file is self-contained; it
does not require the external Caveman hooks, agents, CLI, or cloud services.

**Goal:** Reduce total context and output tokens without reducing correctness,
evidence quality, or human usability.

## Core rule

Apply compression only when expected savings exceed the instructions and tool
output needed to produce them. Never claim token savings without measurement.

Use this order:

```text
reuse → direct path → bounded inspect → compact handoff → concise response
```

Do not load more Caveman material before testing reuse and direct paths. A cache
hit is cheaper than recomputing or compressing the same result.

## Adaptive routing

| Situation | Action |
|-----------|--------|
| Exact file, symbol, or answer is known | Work inline; do not delegate |
| Broad localization is required | Use a cheap read-only explorer with compact evidence output |
| One or two known files need a surgical edit | Use a compact builder when available |
| A broad feature or cross-cutting change is required | Keep orchestration in the main agent |
| Human-facing persisted artifact is produced | Use clear normal prose, not Caveman fragments |
| Security or irreversible action is involved | Disable compression where it could create ambiguity |

## Optional Caveman bindings

Use installed Caveman capabilities only when available and applicable:

| Capability | Use |
|------------|-----|
| `caveman` | Compress conversational output after technical content is complete |
| `caveman-explore` | Broad read-only localization with path-and-line evidence only |
| `cavecrew-investigator` | Compact location lookup when its agent preset exists |
| `cavecrew-builder` | Surgical edit limited to one or two already-known files |
| `cavecrew-reviewer` | Compact findings-only review of a completed diff |
| `caveman-learn` | Token-cost measurement and consent-gated optimization only when explicitly requested |

Do not fail when these capabilities are absent. Apply this portable policy as
the fallback. Do not invoke Caveman cloud, experiment, hook, setup, or lifecycle
skills as part of normal Promptize or Bug Report operation.

## Compact exploration contract

For cold-start orientation, broad cross-file localization, or a failed direct
search, prefer `caveman-explore` or `cavecrew-investigator` when installed;
otherwise delegate parallel read-only searches to a suitable compact subagent.
Ask only where relevant code lives. Require this result shape:

```text
path/to/file.ext:START-END  short relevance reason
```

The explorer must:

- return evidence locations only, not architecture or implementation advice;
- cite only lines it read;
- keep the list short and specific;
- return `no relevant locations found` instead of guessing;
- stop when affected paths, conventions, and validation are known.

Skip delegation for a named file or symbol, a one-line answer, or when the
subagent output would cost more than direct inspection.

## Immutable spans

Never compress, paraphrase, or normalize:

- code and code symbols;
- commands and exact error messages;
- paths, URLs, API names, identifiers, and versions;
- numbers, units, negation, and exception clauses;
- security warnings and irreversible-action confirmations;
- user-provided wording marked as verbatim.

Redact secrets as `<REDACTED>`; do not shorten them into recoverable fragments.

## Prose compression

- State each fact once.
- Remove filler, repeated context, ceremonial sections, and long transitions.
- Use short active sentences with one idea each.
- Keep established technical terms exact.
- Use common technical acronyms only. Do not invent abbreviations.
- Do not use fragments when order, causality, or scope could become ambiguous.
- Preserve the user's dominant language in conversational output.

Compression must not increase output length. Clarity wins over terseness.

## Artifact boundary

Persisted content for humans uses normal professional prose:

- bug reports, issues, tickets, and defect reports;
- pull requests and review bodies;
- documentation, comments, and commit messages;
- security and migration instructions.

Use Caveman compression for internal extraction, evidence localization, context
handoffs, and conversational summaries. Do not apply terse fragments to the
final artifact unless the user explicitly requests that style.

## Measurement boundary

Treat savings as:

- **Measured** only when a tool reports comparable before/after token counts;
- **Inferred** when fewer files, reads, sections, or repeated facts are used;
- **Unknown** when no comparable data exists.

Never invent percentages or token counts. Do not combine measurements from
different methods into one savings claim.

## Stop conditions

Stop inspection when:

1. the affected area is identified or honestly Unknown;
2. relevant conventions and validation are known or Unknown;
3. no blocking conflict remains;
4. the planned touch set is plausible.

Resume normal detail whenever compression risks technical ambiguity.
