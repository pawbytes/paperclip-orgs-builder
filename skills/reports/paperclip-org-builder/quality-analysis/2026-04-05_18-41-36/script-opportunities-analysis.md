# Script Opportunities Analysis: paperclip-org-builder

**Analyst:** ScriptHunter  
**Date:** 2026-04-05  
**Skill:** `skills/paperclip-org-builder`  
**Workflow:** 9-stage HITL org builder → importable Paperclip company package

---

## 1. Existing Scripts Inventory

Two scripts exist, both covering **Stage 9 (Package Assembly & Review)** only:

| Script | Purpose | Coverage |
|--------|---------|----------|
| `assemble-package.py` | Draft JSON → package files (COMPANY.md, .paperclip.yaml, agents/*/AGENTS.md) | Stage 9 assembly |
| `validate-package.py` | Validates final package structure, YAML frontmatter, cross-references, CEO uniqueness | Stage 9 post-assembly |

**Gap:** All validation is deferred to Stage 9. Stages 2–8 accumulate decisions into a draft JSON with zero automated integrity checks. The LLM is the sole validator for 8 stages of data accumulation. Errors caught at Stage 9 require expensive backtracking.

---

## 2. Findings

### Finding SO-1: Draft JSON Validation (Mid-Workflow)

**Location:** Every stage transition (Stages 1→2, 2→3, ..., 8→9)  
**What the LLM does:** Implicitly validates that the draft JSON is well-formed and contains the expected sections before writing new data. Each stage reads the draft, checks `currentStage`, confirms prior sections exist, then updates.  
**Why it's deterministic:** JSON schema validation, required-field checks, and `currentStage` consistency are pure structure checks — no judgment involved.

**Proposed script:** `validate-draft.py <draft-json> [--stage N]`  
Validates the draft at any stage:
- JSON well-formedness
- `schema` field is `paperclip-org-builder/v1`
- `currentStage` is an integer 1–9 or `"complete"`
- Required sections present for the declared stage (e.g., stage ≥3 requires `vision` + `company` + `agents`)
- All agent entries have `name`, `role`, `slug`
- `currentStage` matches expected progression

**Estimated LLM Tax:** ~200–400 tokens per stage transition × 8 transitions = **~1,600–3,200 tokens/run**

---

### Finding SO-2: Issue Prefix & Brand Color Format Validation

**Location:** Stage 2 (Company Identity)  
**What the LLM does:** Proposes an issue prefix ("3-4 uppercase characters") and a brand color (hex code), then self-checks the format.  
**Why it's deterministic:** Regex: `^[A-Z]{3,4}$` for prefix, `^#[0-9A-Fa-f]{6}$` for color. Zero ambiguity.

**Proposed addition to `validate-draft.py`:**
- `issuePrefix` matches `^[A-Z]{3,4}$`
- `brandColor` matches `^#[0-9A-Fa-f]{6}$`

**Estimated LLM Tax:** ~50–100 tokens per field × 2 = **~100–200 tokens/run**  
*Small individually, but free to add to the draft validator.*

---

### Finding SO-3: Org Chart Tree Integrity (Pre-Assembly)

**Location:** Stage 3 (Org Chart Design)  
**What the LLM does:** Manually verifies: exactly one CEO, no orphans, all `reportsTo` references resolve, no cycles, tree is connected.  
**Why it's deterministic:** Graph validation — cycle detection, connectivity, root-count are textbook algorithms.

**Current state:** `validate-package.py` checks this *after* assembly on the final file system. But the draft JSON already contains the full `agents` array with `reportsTo` at Stage 3. This validation could run 6 stages earlier.

**Proposed addition to `validate-draft.py` (when stage ≥ 3):**
- Exactly one agent with `role: "ceo"`
- CEO has no `reportsTo` (or `reportsTo: null`)
- All non-CEO agents have `reportsTo` referencing a valid slug
- No cycles (DFS/BFS cycle detection)
- Tree is connected (all agents reachable from CEO)
- `role` values are in the valid enum: `ceo, manager, engineer, designer, marketer, general`

**Estimated LLM Tax:** ~300–800 tokens (scales with agent count) = **~300–800 tokens/run**  
*Higher value because errors caught here avoid cascading through Stages 4–8.*

---

### Finding SO-4: Cron Expression Validation

**Location:** Stage 8 (Routines & Scheduling)  
**What the LLM does:** Generates cron expressions like `0 9 * * 1-5` and implicitly validates syntax while explaining what they mean in natural language.  
**Why it's deterministic:** Cron syntax is a formal grammar. Libraries like `croniter` can validate in microseconds.

**Proposed addition to `validate-draft.py` (when stage ≥ 8):**
- Each routine's trigger `cronExpression` is syntactically valid
- Timezone strings are valid IANA identifiers (check against `zoneinfo` or `pytz`)

**Estimated LLM Tax:** ~100–200 tokens per routine × N routines = **~300–1,000 tokens/run** (for 3-5 routines)

---

### Finding SO-5: Budget Arithmetic Verification

**Location:** Stage 7 (Budget & Cost Optimization)  
**What the LLM does:** Proposes per-agent budgets, sums them, verifies the total fits within the company budget, calculates percentages for the breakdown table.  
**Why it's deterministic:** Addition. Comparison. Percentage calculation. LLMs are notoriously unreliable at arithmetic, especially with multi-digit cent values.

**Proposed addition to `validate-draft.py` (when stage ≥ 7):**
- `budgetMonthlyCents` is a positive integer on company and each agent
- Sum of agent `budgetMonthlyCents` ≤ company `budgetMonthlyCents`
- `warnPercent` is 0–100
- Budget policies reference valid scope types

**Also consider:** `budget-summary.py <draft-json>` — Outputs a compact budget table (agent, role, model, allocation, % of total) that the LLM can present directly instead of computing it.

**Estimated LLM Tax:** ~200–500 tokens for arithmetic + table generation = **~200–500 tokens/run**  
*Higher risk of LLM error than other findings due to arithmetic.*

---

### Finding SO-6: Cross-Reference Validation (Goals, Projects, Routines → Agents)

**Location:** Stages 6, 8 (Goals & Projects, Routines)  
**What the LLM does:** Ensures `ownerAgentId` on goals, `leadAgentId` on projects, and `assigneeAgentId` on routines reference agents that actually exist in the `agents` array.  
**Why it's deterministic:** Set membership check — does the referenced slug/ID exist in the agent list?

**Current state:** `validate-package.py` checks `reportsTo` cross-refs on the final package but does NOT check goal/project/routine → agent references.

**Proposed addition to `validate-draft.py`:**
- Goal `ownerAgentId` → valid agent slug
- Project `leadAgentId` → valid agent slug
- Routine `assigneeAgentId` → valid agent slug
- Goal `parentId` references a valid goal (if hierarchical goals exist)
- Project alignment to at least one goal (if that mapping exists in draft)

**Estimated LLM Tax:** ~200–400 tokens = **~200–400 tokens/run**

---

### Finding SO-7: Draft Summary for Compaction Recovery

**Location:** Compaction Recovery (any stage), Stage 9 (Final Review)  
**What the LLM does:** On context loss, reads the full draft JSON and produces a narrative summary of all decisions made so far. At Stage 9, generates "Company summary — Name, description, agent count, goal count, total budget."  
**Why it's deterministic:** The data extraction and counting is pure parsing. Only the natural-language narrative wrapper needs the LLM.

**Proposed script:** `summarize-draft.py <draft-json>`  
Outputs a compact, structured summary:
```
Company: Acme AI Corp (ACME) | Stage: 5/9
Agents (4): ceo-agent (CEO), eng-lead (Manager→ceo-agent), dev-1 (Engineer→eng-lead), dev-2 (Engineer→eng-lead)
Goals (2): "Ship v1" (company), "Build MVP" (team)
Projects (1): "Alpha Release" (lead: eng-lead)
Budget: $50.00/mo company, $35.00/mo allocated (70%)
Routines: 0 configured
```

This gives the LLM a compact input (~150 tokens) instead of parsing raw JSON (~500–2,000+ tokens depending on org size).

**Estimated LLM Tax:** ~500–2,000 tokens per compaction event = **~500–2,000 tokens/event**  
*Compaction can happen multiple times per run in long sessions.*

---

### Finding SO-8: Stage-Entry Context Extraction

**Location:** Every stage entry (Stages 2–9)  
**What the LLM does:** Reads the full draft JSON to extract only the data relevant to the current stage. E.g., Stage 4 (Agent Deep Dive) only needs the agent list and org chart; it doesn't need to re-process goals or routines.  
**Why it's deterministic:** Filtering a JSON object to a subset of keys is trivial.

**Proposed script:** `extract-stage-context.py <draft-json> <stage-number>`  
Returns only the draft sections relevant to the target stage:
- Stage 4: `vision.capabilities`, `agents` (names, roles, reportsTo only), `orgChart`
- Stage 7: `agents` (names, roles, runtimeConfig.model), `goals` (titles), `company.name`
- Stage 9: everything (full draft)

**Estimated LLM Tax:** ~200–800 tokens per stage of irrelevant context loaded = **~1,000–4,000 tokens/run**  
*Scales with org complexity — larger orgs waste more tokens on irrelevant context.*

---

## 3. Summary & Prioritization

| # | Finding | Type | Est. Token Savings | Effort | Priority |
|---|---------|------|-------------------|--------|----------|
| SO-1 | Draft JSON validation per stage | Post-processing | 1,600–3,200/run | Medium | **HIGH** |
| SO-3 | Org chart tree integrity | Post-processing | 300–800/run | Low | **HIGH** |
| SO-7 | Draft summary for compaction | Pre-processing | 500–2,000/event | Low | **HIGH** |
| SO-8 | Stage-entry context extraction | Pre-processing | 1,000–4,000/run | Medium | **MEDIUM** |
| SO-5 | Budget arithmetic verification | Post-processing | 200–500/run | Low | **MEDIUM** |
| SO-6 | Cross-ref validation (goals/projects/routines) | Post-processing | 200–400/run | Low | **MEDIUM** |
| SO-4 | Cron expression validation | Post-processing | 300–1,000/run | Low | **LOW** |
| SO-2 | Issue prefix & color format | Post-processing | 100–200/run | Trivial | **LOW** |

### Estimated Total LLM Tax on Deterministic Work: **~4,200–12,100 tokens per full workflow run**

*(Plus ~500–2,000 tokens per compaction recovery event)*

---

## 4. Recommended Implementation

### Script 1: `validate-draft.py` (combines SO-1, SO-2, SO-3, SO-4, SO-5, SO-6)

A single script that validates the draft JSON at any point in the workflow. Subsumes findings SO-1 through SO-6 into one tool. Called after each stage gate approval.

```
uv run ./scripts/validate-draft.py <draft-json> [--stage N] [--strict]
```

**Output:** JSON with `issues[]` and `warnings[]`, same format as `validate-package.py` for consistency.

**Checks by stage threshold:**
- Stage ≥ 1: JSON valid, schema field, currentStage present
- Stage ≥ 2: company section complete, issuePrefix format, brandColor format
- Stage ≥ 3: org chart tree integrity (one CEO, no orphans, no cycles, valid roles)
- Stage ≥ 4: all agents have instructions, runtimeConfig
- Stage ≥ 6: goal/project → agent cross-references valid
- Stage ≥ 7: budget arithmetic (sum ≤ total, warnPercent range)
- Stage ≥ 8: cron syntax valid, timezone valid, routine → agent refs valid

**Rationale:** One script, one invocation per stage gate. Catches errors 1–8 stages earlier than the current flow. Reduces the risk of expensive Stage 9 backtracking.

### Script 2: `summarize-draft.py` (combines SO-7, SO-8)

A single script that produces a compact, stage-aware summary of the draft.

```
uv run ./scripts/summarize-draft.py <draft-json> [--stage N] [--for-recovery]
```

**Modes:**
- Default: compact summary for stage-entry context (only relevant sections)
- `--for-recovery`: full summary for compaction recovery (all decisions, no raw JSON)

**Rationale:** Reduces context-loading cost and makes compaction recovery cheaper. The LLM receives a pre-digested ~150-token summary instead of parsing a growing JSON blob.

---

## 5. What I Did NOT Flag

The following are **not** script opportunities — they're the core value of the LLM in this HITL workflow:

- **Vision synthesis** (Stage 1) — Creative interpretation of user intent
- **Name/description generation** (Stage 2) — Creative branding
- **Org chart design rationale** (Stage 3) — Strategic organizational reasoning
- **Agent instruction writing** (Stage 4) — Prose generation requiring domain judgment
- **Skills discovery & evaluation** (Stage 5) — Qualitative assessment of skill relevance
- **Goal/project proposal** (Stage 6) — Strategic alignment reasoning
- **Budget strategy recommendations** (Stage 7) — Cost-optimization judgment
- **Routine design** (Stage 8) — Operational scheduling judgment
- **Final review narrative** (Stage 9) — Synthesizing the complete package for human review

These are the stages' primary outputs and represent the LLM's core contribution. The script opportunities above target only the *plumbing* around these creative acts — validating inputs, checking outputs, and reducing context overhead.
