---
promptize:
  schema_version: 3
  skill_version: 2.3.0
  generated_at: 2026-09-16T14:59:00+03:30
  tier: full
  mode: prompt-only
---

# Static `--help` Blocks for All Pipeline Skills

Promptize specification version: 3  
Output tier: full  
Cache: DELTA

---

## 1. Objective

Add a verbatim static `## Help` section to each of the 5 pipeline skill `SKILL.md` files so that agents emit the pre-written help block immediately on `--help` / `-h` with **zero inspection, reasoning, generation, or tool calls**.

---

## 2. Engineering Decisions

Embed help as a verbatim Markdown code block under a dedicated `## Help` section. When `--help` / `-h` is detected as the only meaningful flag, the agent reads that block, emits it verbatim, and stops — bypassing all gates (reuse lookup, ultra/micro, delta inspect, specify, lint, render).

---

## 3. Assumptions

1. All five SKILL.md files can receive an additive `## Help` section without breaking existing skill activation or gate logic.
2. The help text is considered a static artifact — agents MUST NOT paraphrase, summarize, or regenerate it.
3. `--help` / `-h` used alone (no other action flag) always triggers this zero-cost path.
4. If `--help` appears alongside an action flag (e.g. `/dev-pipeline next --help`), the static block is still emitted and the action is NOT executed.

---

## 4. Repository Context

### Stack

Markdown-based skill definitions; no runtime; parsed by AI agents (Antigravity, Claude Code, Cursor, etc.).

### Relevant Files

| Alias | Path | Role |
|-------|------|------|
| `dp-skill` | `dev-pipeline/SKILL.md` | dev-pipeline activation + flags |
| `pz-skill` | `promptize/SKILL.md` | promptize activation + flags |
| `br-skill` | `bug-report/SKILL.md` | bug-report activation + flags |
| `cm-skill` | `commit/SKILL.md` | commit activation |
| `rt-skill` | `review-task/SKILL.md` | review-task activation + flags |

Evidence map: `dp-skill` → `dev-pipeline/SKILL.md`; `pz-skill` → `promptize/SKILL.md`; `br-skill` → `bug-report/SKILL.md`; `cm-skill` → `commit/SKILL.md`; `rt-skill` → `review-task/SKILL.md`

### Source Precedence

1. This spec (requirements and help text wording)
2. Existing SKILL.md content (for version numbers and current flags)
3. README.md help section (reference wording)

### Architecture

No runtime executable. Agents read SKILL.md files as instruction sets. The `## Help` section is a new terminal-branch that short-circuits all normal skill workflow. No changes to underlying gate logic are required — the branch is purely declarative prose that agents follow.

### Tests & Validation

No automated test harness. Validation: verify that each modified SKILL.md contains a `## Help` section with:
- Pre-written verbatim help block inside a fenced code block.
- Explicit instruction: "emit verbatim, then stop; no tool calls, no inspect, no generation."

### Project Instructions

Do not modify any file outside the Touch Set. Do not change existing flag definitions or activation rules. The `## Help` section is **additive only**.

---

## 5. Current Behavior

When an agent receives `/dev-pipeline --help` (or any skill with `--help`):
1. Agent reasons about the skill's purpose.
2. Agent inspects SKILL.md or generates help text from memory.
3. Agent produces a natural-language help response.
4. **Cost: 200–800 tokens of reasoning and generation per help call.**

---

## 6. Desired Behavior

When an agent receives `/dev-pipeline --help` (or any skill with `--help`):
1. Agent detects `--help` / `-h` as the only meaningful flag.
2. Agent locates `## Help` section in the current SKILL.md.
3. Agent emits the pre-written verbatim block from that section.
4. Agent stops. **No inspection. No reasoning. No generation.**
5. **Cost: ~0 additional tokens beyond reading the static block.**

---

## 7. Functional Requirements

**MUST-001:** Each of the 5 SKILL.md files MUST contain a `## Help` section with a fenced code block containing the complete, pre-written help text for that skill.

**MUST-002:** The `## Help` section MUST include an explicit agent instruction: "When `--help` or `-h` is detected as the only meaningful flag, emit the block below verbatim and stop. Do not inspect, reason, or generate."

**MUST-003:** Help text MUST include: usage line, all subcommands/options with descriptions, and a one-line footer citing the skill version.

**MUST-004:** On `--help` trigger, the agent MUST skip all pipeline stages: reuse lookup, ultra/micro gate, delta inspect, specify, lint, render.

**MUST-005:** If `--help` appears alongside an action flag, the static help block is emitted and the action is NOT executed.

---

## 8. Technical Requirements

**MUST-006:** The `## Help` section MUST be placed after the `## Activation` / `## Flag parsing` sections and before any `## Workflow` or `## References` sections so agents encounter it early in the file.

**MUST-007:** The help code block MUST use the fenced ` ```text ` format (not markdown) so agents do not interpret its content as instructions.

**MUST-008:** Version numbers in help text MUST match the `version:` field in SKILL.md frontmatter.

---

## 9. Impact Analysis

- **Direct:** 5 SKILL.md files receive one additive section each.
- **Indirect:** All future `--help` calls across all agents using these skills become zero-cost static lookups.
- **No breaking changes:** Existing activation, flags, gate logic, and companion references remain unchanged.
- **Public API:** None. These are agent instruction files, not executable code.

---

## 10. Edge Cases & Error Handling

| Edge Case | Handling |
|-----------|----------|
| `--help` + action flag (e.g. `--help --execute`) | Emit help block; do NOT execute action |
| SKILL.md lacks `## Help` section | Agent falls back to generating help — acceptable for non-updated skills |
| Agent does not find `## Help` heading | Emit: "Help not available. See SKILL.md for usage." and stop |
| Multilingual user asks for help in Farsi/other | Emit the static English block; do not translate |

---

## 11. Security Considerations

None applicable. These are read-only instruction files with no executable code, secrets, or authentication.

---

## 12. Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| Token cost of `--help` call | ~0 additional tokens (static read + emit) |
| Help text completeness | All flags and subcommands documented |
| Consistency | All 5 skills use identical `## Help` section structure |

---

## 13. Constraints

- Touch Set only: do not modify any file outside the 5 listed SKILL.md files.
- Do not change existing SKILL.md section order beyond inserting `## Help` at the specified location.
- Do not rename, relocate, or restructure existing sections.

---

## 14. Out of Scope

- ❌ Implementing a runtime `--help` executable or CLI parser.
- ❌ Translating help text to languages other than English.
- ❌ Adding `## Help` to shared reference files (`inspect.md`, `token-efficiency.md`, etc.).
- ❌ Modifying gate logic code — the short-circuit is declarative prose only.

---

## 15. Testing & Validation Strategy

### Automated
None available (Markdown files, no test runner).

### Manual Verification (per skill)
1. Open each modified SKILL.md.
2. Confirm `## Help` section exists after `## Flag parsing` / `## Activation`.
3. Confirm the fenced ` ```text ` block is present and complete.
4. Confirm agent instruction "emit verbatim, then stop" is present.
5. Confirm version number matches `version:` frontmatter.

### Functional Test (agent)
Call `/dev-pipeline --help` in an agent session. Verify:
- Output matches the static block exactly.
- No inspection tool calls were made.
- Agent stopped after emitting the block.

---

## 16. Acceptance Criteria

1. Each of the 5 SKILL.md files contains a `## Help` section with a complete ` ```text ` block.
2. The `## Help` section includes the agent instruction to emit verbatim and stop.
3. Help text covers all flags and subcommands documented in the skill's `## Activation` and `## Flag parsing` tables.
4. Version numbers in help text match SKILL.md frontmatter `version:` field.
5. No existing SKILL.md section is modified or removed.
6. No file outside the Touch Set is changed.

---

## 17. Definition of Done

- AC 1–6 all met.
- No unrelated files modified (verified by `git diff --stat`).
- All 5 SKILL.md files pass a manual read-through confirming structure and completeness.

---

## 18. Implementation Plan

**Step 1 — `dev-pipeline/SKILL.md`**  
Insert `## Help` section after `## Flag parsing`, before `## Product prose routing`. Pre-write complete help block for all 16 subcommands and 16 flags at version `1.9.0`.

**Step 2 — `promptize/SKILL.md`**  
Insert `## Help` section after `## Flag parsing`, before `## Save rules`. Pre-write complete help block for all activation forms, flags, tiers, and cache labels at version `2.3.0`.

**Step 3 — `bug-report/SKILL.md`**  
Insert `## Help` section after `## Activation`, before `## Evidence contract`. Pre-write help block for all flags and evidence classification rubric at version `1.1.0`.

**Step 4 — `commit/SKILL.md`**  
Insert `## Help` section after the opening description paragraph, before `## Inspect`. Pre-write help block for usage and safety rules at version `1.2.0`.

**Step 5 — `review-task/SKILL.md`**  
Insert `## Help` section after `## Flag parsing`, before `## Discover conventions`. Pre-write help block for all flags and verdict rubrics at version `1.1.0`.

**Step 6 — Verify**  
Run `git diff --stat` to confirm only 5 files changed. Manually verify each `## Help` section for completeness.
