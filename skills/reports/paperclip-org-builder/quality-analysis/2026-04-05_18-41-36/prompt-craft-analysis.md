# Prompt Craft Analysis: paperclip-org-builder

| Field | Value |
|-------|-------|
| Skill | `paperclip-org-builder` |
| Type | Complex Workflow (9 stages), Interactive HITL |
| Analyzer | PromptCraftBot |
| Date | 2026-04-05 |

## Executive Summary

This is a well-architected skill. Progressive disclosure is excellent — SKILL.md is a lean 851-token routing table while all stage logic lives in `references/`. Every stage has explicit progression conditions and draft-state persistence for compaction recovery. Deterministic work (assembly, validation) is correctly delegated to scripts. The main opportunities are pruning inferable guidance from mid-tier stages and adding config headers for tooling interop. No critical issues found.

**Token budget:** ~851 (SKILL.md) + ~150-200 per stage loaded on demand + ~800 domain ref when needed. Effective per-turn footprint is well-managed.

---

## 1. SKILL.md Routing Hub

**Rating: Strong**

### Strengths

- **Mission clarity (line 10):** "Act as a seasoned organizational designer who proposes complete solutions at each stage" — excellent theory of mind in one sentence. Sets HITL interaction pattern immediately.
- **Design Principles (lines 24-29):** Four principles, each one sentence with a bolded label. Every one is load-bearing — "Suggest, don't interrogate" fundamentally shapes all 9 stages. Zero filler.
- **Progressive disclosure:** Stage table is a pure routing table pointing to `./references/`. SKILL.md never duplicates stage content. This is the correct architecture for a 9-stage workflow.
- **Compaction Recovery (lines 47-49):** Three lines. Draft JSON as state file is the right pattern. No over-explanation.
- **Scripts section (lines 55-60):** Exact invocation syntax, fallback instruction. Tight.

### Observations

- **On Activation (lines 14-22):** The config-loading instructions are precise and actionable. The `output_folder` default and draft file creation are necessary bootstrapping. The instruction to "Greet the user and explain what you'll build together" could be trimmed — the LLM will do this naturally given the Overview framing — but it's only a few tokens and sets an explicit first action, so it's acceptable.
- **No config header:** The frontmatter has `name` and `description` but lacks a structured config block (e.g., `type: workflow`, `stages: 9`, `interaction: hitl`). This is why the pre-pass scanner reported 0 prompts with config headers. Not functionally broken, but reduces tooling interop.

### Recommendation

| ID | Severity | Issue | Suggestion |
|----|----------|-------|------------|
| S1 | Low | No structured config header | Consider adding `type`, `interaction-model`, `stage-count` to frontmatter for scanner/tooling compatibility |

---

## 2. Stage Prompt Craft

### 2.1 Structural Consistency (All Stages)

**Rating: Strong**

Every stage file follows the same template:
```
# Stage N: Title
## Goal          — One paragraph, outcome-focused
## How to Propose — Behavioral guidance + specifics
## Draft Update   — JSON schema for state persistence
## Progression    — Explicit gate condition → next load
```

This consistency is a strength. The LLM can internalize the pattern after Stage 1 and execute subsequent stages with less cognitive overhead. Each stage is fully self-contained — it doesn't need to re-read other stages to function.

**Progression conditions are present in all 9 stages.** The pre-pass reported 0 because it scanned only SKILL.md (which is the routing table, not the prompt itself). This is a scanner limitation, not a skill defect.

### 2.2 Per-Stage Assessment

#### Stage 1: Brainstorm & Vision (40 lines) — Clean

- Good dual-path handling: "Whether they arrive with a vague idea or a detailed plan"
- Draft JSON schema with exact field structure — essential for downstream stages
- No waste detected

#### Stage 2: Company Identity (41 lines) — Clean

- Field-level specifics (Issue Prefix format, Brand Color as hex) are necessary for deterministic output
- "Present as a cohesive card the user can review" — good HITL framing
- No waste detected

#### Stage 3: Org Chart Design (41 lines) — Load-bearing depth

- Design Considerations subsection: Flat vs deep, CEO scope, specialist vs generalist, no orphans — this is **domain knowledge the LLM may not have** about AI org design specifically. Load-bearing.
- Token Cost Awareness: Hop-count cost framing is Paperclip-specific domain knowledge. Justified.
- This stage correctly gets the most design guidance — it's the most consequential architectural decision.

#### Stage 4: Agent Configuration (39 lines) — Mostly clean

- Runtime Config model-tier guidance (CEO=capable, Workers=efficient) is useful defaults the LLM might not infer for this specific domain
- "Writing Good Agent Instructions" (lines 26-30): 5 bullets of meta-instruction on instruction writing. The LLM knows how to write instructions — the value here is the **specific framing** (authority boundaries, communication style with reports/manager). Borderline but acceptable given the Paperclip context.

#### Stage 5: Skills Discovery (51 lines) — Has pruning opportunity

- **Search Strategy (lines 20-23):** "Search by the agent's domain/industry first, then by specific capabilities" — the LLM would do this naturally. These 4 bullets are inferable.
- **"Presenting Options" (lines 25-31):** The exact format (name, install count, source, install command, learn-more link) is useful template-level guidance. Keep.
- **"When the User Can't Install" (lines 33-38):** Good HITL edge-case handling. Keep.
- **"Skills in the Package" (lines 40-41):** Necessary bridge to draft state. Keep.

| ID | Severity | Issue | Suggestion |
|----|----------|-------|------------|
| P1 | Medium | Search Strategy subsection (lines 20-23) is inferable | Collapse to one line: "Search skills.sh by agent domain, then specific capabilities. Try alternative terms if initial queries miss." Saves ~40 tokens. |

#### Stage 6: Goals & Projects (36 lines) — Clean

- "vision → goals → projects → agents" alignment framing is excellent
- Appropriate depth for the complexity of the stage
- No waste detected

#### Stage 7: Budget & Cost Optimization (47 lines) — Minor over-specification

- **Cost Optimization Strategies (lines 24-29):** "Model selection — Match model capability to task complexity" is already covered in Stage 4's runtime config guidance. "Delegation depth — Remind the user of their org chart's depth" references Stage 3 content the user already approved.
- The budget allocation breakdown (CEO/Managers higher, Workers lower) duplicates Stage 4's model-tier guidance.
- **Budget Policies (lines 31-37):** The specific defaults (80% warning, hard stop recommendation) are useful — the LLM needs to propose concrete numbers.

| ID | Severity | Issue | Suggestion |
|----|----------|-------|------------|
| P2 | Medium | Cost Optimization Strategies partially duplicates earlier stage guidance | Trim to: "Propose cost optimizations based on the org design: model selection per role, heartbeat frequency, task batching, and delegation depth tradeoffs." One line, still outcome-complete. Saves ~60 tokens. |

#### Stage 8: Routines & Scheduling (41 lines) — Minor over-specification

- **Common Patterns by Role (lines 13-18):** These example routines (CEO=weekly review, Managers=daily standup, Engineers=hourly heartbeat) are useful **starting-point examples** that accelerate proposal generation. However, the LLM could generate these from role semantics alone.
- The value is in accelerating a good first proposal, not in providing information the LLM lacks. Borderline — the examples are concrete enough to keep for proposal quality.
- **Cost Reminder (lines 30-31):** Brief, justified. The token-cost framing is Paperclip-specific.

| ID | Severity | Issue | Suggestion |
|----|----------|-------|------------|
| P3 | Low | Role-pattern examples are inferable but accelerate proposals | Keep as-is. The concrete examples (cron expressions, role mappings) improve first-proposal quality enough to justify ~50 tokens. |

#### Stage 9: Package Assembly & Review (65 lines) — Has redundancy

- Script invocation blocks: Essential, exact syntax matters.
- **Validation key checks (lines 33-38):** This list partially duplicates what `validate-package.py` already checks. The script outputs issues as JSON — the LLM could just report the script's output.
- **Final Review (lines 42-48):** Useful checklist — ensures the LLM presents a complete summary, not just "it's done."
- **Import Instructions (lines 50-57):** Essential — exact CLI syntax.

| ID | Severity | Issue | Suggestion |
|----|----------|-------|------------|
| P4 | Medium | Validation key checks (lines 33-38) duplicate script logic | Replace with: "Run the validation script and report results. If the script can't execute, verify: required files exist, YAML frontmatter is valid, agent hierarchy is consistent (one CEO, no orphans)." Saves ~30 tokens and defers to the script as source of truth. |

---

## 3. Token Efficiency

### Budget Breakdown

| Component | Tokens (est.) | Loaded When |
|-----------|--------------|-------------|
| SKILL.md | ~851 | Always (activation) |
| Stage prompt (avg) | ~175 | On stage entry |
| paperclip-domain.md | ~800 | Stage 9 (assembly) or on-demand |
| **Per-turn ceiling** | **~1,850** | Worst case: SKILL.md + stage + domain |

This is efficient for a 9-stage complex workflow. The progressive disclosure architecture means the LLM never holds all 9 stages simultaneously.

### Waste Assessment

| Category | Amount | Notes |
|----------|--------|-------|
| Structural repetition | None | Stages don't repeat SKILL.md content |
| Defensive padding | None | No "make sure to...", "remember to..." filler |
| Meta-explanation | None | No "this section explains..." preamble |
| Cross-stage duplication | ~100 tokens | Model-tier guidance appears in Stage 4 and Stage 7 |
| Inferable guidance | ~80 tokens | Skills search strategy, some cost optimization bullets |
| Script-prompt redundancy | ~30 tokens | Validation checks listed in both prompt and script |
| **Total prunable** | **~210 tokens** | ~2.4% of total skill content across all files |

**Verdict:** Token waste is minimal. The ~210 prunable tokens are spread across 3 stages and represent genuine micro-optimizations, not structural problems.

---

## 4. Outcome vs Implementation Balance

**Rating: Strong**

This skill correctly leans **outcome-heavy with implementation rails**:

- **Outcome-driven:** Every stage's `## Goal` section states *what* to achieve, not step-by-step *how*. "Capture the user's vision" not "First ask about X, then ask about Y."
- **Implementation rails where needed:** Draft JSON schemas, package format specifications, and script invocation commands are appropriately prescriptive — these are deterministic operations where exact format matters.
- **HITL interaction model:** "Propose, then user steers" is the right pattern for this skill type. It's stated once in SKILL.md Overview and reinforced by Design Principles. Stages don't re-state it — they just follow it.

The balance is correct for a complex interactive workflow: outcomes for creative/adaptive work, implementation specifics for structural/format-sensitive work.

---

## 5. Intelligence Placement

**Rating: Strong**

| Operation | Placement | Correct? |
|-----------|-----------|----------|
| Package assembly (file generation) | Script (`assemble-package.py`) | ✅ Deterministic, format-sensitive |
| Package validation | Script (`validate-package.py`) | ✅ Deterministic, rule-based |
| Org chart design | Prompt (Stage 3) | ✅ Creative, requires user context |
| Agent instruction writing | Prompt (Stage 4) | ✅ Creative, domain-adaptive |
| Skills search | Prompt (Stage 5) | ✅ Requires reasoning about agent needs |
| Draft JSON state management | Prompt (all stages) | ✅ Adaptive, context-dependent |
| Budget calculation | Prompt (Stage 7) | ✅ Requires reasoning about org design |

No misplaced intelligence detected. The scripts handle what scripts should (deterministic file I/O, structural validation), and the prompts handle what requires reasoning.

The fallback pattern in SKILL.md line 60 ("If scripts cannot execute, perform equivalent assembly and validation directly") is a good resilience design — it keeps the workflow functional even if the runtime can't execute Python.

---

## 6. Domain Reference Assessment

**`paperclip-domain.md` (~800 tokens, 203 lines)**

This file is **entirely load-bearing**. It contains:
- Exact field names, types, and enum values the LLM needs for draft JSON
- Package directory structure and file format specifications
- YAML frontmatter templates for COMPANY.md, AGENTS.md, .paperclip.yaml

Without this, the LLM would hallucinate field names and formats. The tables are dense and well-structured — no narrative filler.

**Loading strategy concern:** The file is referenced in SKILL.md (`## Domain Reference`, line 51-53) but there's no explicit instruction on *when* to load it. Stage 9 references it ("See `./references/paperclip-domain.md` for exact formats"), but earlier stages also need field names for draft JSON updates.

| ID | Severity | Issue | Suggestion |
|----|----------|-------|------------|
| D1 | Low | Domain reference loading is implicit | The LLM will likely load it when it needs field names, but an explicit note in SKILL.md like "Load domain reference as needed for field names and formats" would make this deterministic. |

---

## 7. Consolidated Findings

### By Severity

| ID | Severity | Category | Summary |
|----|----------|----------|---------|
| P1 | Medium | Token waste | Stage 5 Search Strategy subsection is inferable (~40 tokens) |
| P2 | Medium | Cross-stage duplication | Stage 7 Cost Optimization duplicates Stage 4 model-tier guidance (~60 tokens) |
| P4 | Medium | Script-prompt redundancy | Stage 9 validation checks duplicate script logic (~30 tokens) |
| S1 | Low | Tooling interop | No structured config header in SKILL.md frontmatter |
| P3 | Low | Inferable content | Stage 8 role-pattern examples are inferable but improve proposal quality |
| D1 | Low | Loading strategy | Domain reference loading is implicit rather than explicit |

### What NOT to change

- **Design Principles section:** All four principles are load-bearing behavioral framing. Do not prune.
- **Stage 3 design guidance:** Org chart considerations are Paperclip-specific domain knowledge. Do not prune.
- **Draft JSON schemas in stages:** Essential for state persistence and downstream consistency. Do not prune.
- **Compaction Recovery:** Three lines, fully justified. Do not prune.
- **Domain reference tables:** Every field definition is needed for correct output format. Do not prune.

---

## 8. Scorecard

| Dimension | Score | Notes |
|-----------|-------|-------|
| Progressive disclosure | 9/10 | Excellent stage-in-references architecture. Minor: no explicit domain-ref loading trigger. |
| Token efficiency | 8/10 | ~210 tokens prunable out of ~8,700 total. Well within budget. |
| Outcome-driven balance | 9/10 | Outcomes for creative work, implementation rails for format work. Correct for skill type. |
| Stage self-containment | 10/10 | Every stage has Goal, Proposal guidance, Draft Update, Progression. Fully self-contained. |
| Progression conditions | 10/10 | All 9 stages have explicit user-approval gates. |
| Intelligence placement | 10/10 | Scripts for deterministic ops, prompts for reasoning. Fallback pattern included. |
| HITL interaction design | 9/10 | "Propose and steer" is well-implemented. Design Principles section is excellent. |
| **Overall** | **9/10** | **A well-crafted skill with minimal waste. Findings are optimization-tier, not structural.** |
