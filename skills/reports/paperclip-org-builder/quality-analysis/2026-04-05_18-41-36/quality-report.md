# BMad Method · Quality Analysis: paperclip-org-builder

**Analyzed:** 2026-04-05T18:41:36Z | **Path:** skills/paperclip-org-builder
**Interactive report:** quality-report.html

## Assessment
**Good** — A well-architected 9-stage HITL workflow with excellent progressive disclosure, consistent stage templates, and correct intelligence placement. The primary opportunity is closing the gap between what stages produce and what the assembly script outputs — users do meaningful work in stages 5–8 that doesn't fully materialize in the final package. Secondary concerns center on Stage 4 scaling for larger orgs and under-specified compaction recovery.

## What's Broken

No critical or blocking issues. The 9 critical findings from the workflow-integrity prepass (missing stage files) are **all false positives** — the scanner searched the skill root instead of `references/`. All stage files exist and resolve correctly.

## Opportunities

### 1. Deferred Validation — Errors Only Caught at Stage 9 (medium — 7 observations)

All automated validation is concentrated in the final stage. Eight stages of data accumulation rely solely on the LLM for integrity checks. Errors discovered during assembly require expensive backtracking through potentially hours of prior work. A mid-workflow draft validator would catch structural issues at the stage where they're introduced.

**Fix:** Create a unified `validate-draft.py` script that validates the draft JSON at any stage transition, with progressive checks (org tree integrity at stage ≥3, budget arithmetic at stage ≥7, cron syntax at stage ≥8). Call it after each stage gate approval.

**Observations:**
- All validation concentrated at Stage 9 — script-opportunities: SKILL.md
- No draft JSON schema validation at stage transitions — script-opportunities SO-1: SKILL.md
- Org chart tree integrity could validate 6 stages earlier at Stage 3 — script-opportunities SO-3: references/03-org-chart.md
- No centralized draft schema contract between stages and scripts — skill-cohesion: references/
- validate-package.py missing cross-ref checks for goals/projects/routines → agents — skill-cohesion: scripts/validate-package.py
- validate-package.py has no cycle detection in agent hierarchy — enhancement-opportunities: scripts/validate-package.py
- Hardcoded role enum in validator requires code changes to extend — enhancement-opportunities: scripts/validate-package.py

### 2. Assembly Output Gap — Package Doesn't Reflect All Stage Work (high — 6 observations)

The assembly script creates `projects/`, `skills/`, and `tasks/` directories but never populates them. Users invest effort designing goals, discovering skills, and configuring budgets/routines in stages 5–8, but this data only partially appears in the final package. Additionally, a "permissions" field is referenced in Stage 4 but has no schema, assembly path, or validation — a ghost field.

**Fix:** Either update `assemble-package.py` to emit project files, skill references, and routine configurations, or explicitly document in stage instructions that these entities are captured for runtime seeding (not file-based packaging) and remove the empty directories.

**Observations:**
- `skills/` directory created but never populated by assembly script — workflow-integrity WI-L2: references/09-assembly-review.md
- `projects/` directory created but never populated — skill-cohesion: scripts/assemble-package.py
- `tasks/` directory created but never populated — skill-cohesion: scripts/assemble-package.py
- Draft routines and budgets not written to any package file — enhancement-opportunities: scripts/assemble-package.py
- Permissions ghost field — referenced in Stage 4 but no schema, assembly, or validation — skill-cohesion: references/04-agent-deep-dive.md
- `orgChart` field in draft not defined in domain schema — workflow-integrity WI-L1: references/03-org-chart.md

### 3. Compaction Recovery and Session Continuity Under-Specified (high — 6 observations)

The draft JSON stores `currentStage` but not intra-stage progress (e.g., which agent was last configured in Stage 4's per-agent walkthrough). Recovery has no UX choreography — no preamble templates, no tiered summary depth, no "want to adjust anything?" gate. Users are never told their progress persists, creating abandonment risk in a 30–60+ minute workflow. Two design principles stated in SKILL.md are not reinforced in any stage file, meaning they may not survive compaction.

**Fix:** Add `stageProgress` to draft JSON for intra-stage state. Add a recovery preamble pattern to the Compaction Recovery section. Include "Your progress is saved" messaging at every stage gate. Add one-line principle reminders to each stage's Progression section.

**Observations:**
- No intra-stage progress tracking in draft JSON — enhancement-opportunities: SKILL.md:47
- No recovery UX choreography or preamble templates — enhancement-opportunities: SKILL.md:47
- No "save and quit" messaging at stage gates — enhancement-opportunities: SKILL.md
- "Capture-don't-interrupt" principle not reinforced in any stage file — skill-cohesion: SKILL.md:24
- Soft-gate phrasing not echoed in stage progression sections — skill-cohesion: SKILL.md:24
- No backward navigation mechanism for revisiting earlier decisions — enhancement-opportunities: SKILL.md

### 4. Stage 4 Agent Configuration Doesn't Scale (high — 5 observations)

Stage 4 processes agents one-by-one with individual HITL approval. For a 10-agent org, this creates 10 sequential review cycles with no batch option, no progress indicator, no diff-from-template view. This is where user abandonment peaks — by agent 5, users rubber-stamp. The progression gate is also implicit about how multi-agent approval state is tracked.

**Fix:** Add batch-approval mode — present CEO solo, managers as a group, then same-role workers as a batch with per-agent override. Show progress ("Agent 3 of 10 — 60% complete"). Offer "apply this template to all [engineers]" after the first of a role type.

**Observations:**
- Per-agent sequential review doesn't scale beyond 5-7 agents — skill-cohesion: references/04-agent-deep-dive.md
- No batch-approval option for similar-role agents — enhancement-opportunities: references/04-agent-deep-dive.md
- No progress indicator during per-agent walkthrough — enhancement-opportunities: references/04-agent-deep-dive.md
- Progression gate implicit for multi-agent iteration tracking — workflow-integrity WI-M1: references/04-agent-deep-dive.md
- First-timer drop-off risk by agent 5+ due to review fatigue — enhancement-opportunities: references/04-agent-deep-dive.md

### 5. Minor Cross-Stage Prompt Duplication (low — 5 observations)

~210 tokens of prunable content scattered across stages 5, 7, 8, and 9 — inferable guidance, cross-stage duplication of model-tier advice, and validation checks that duplicate script logic. Individually negligible (~2.4% of total skill content), but collectively a micro-optimization opportunity.

**Fix:** Collapse Stage 5 search strategy to one line, trim Stage 7 cost optimization to reference Stage 4, replace Stage 9 validation checks with "run script and report results." Consider adding a config header to SKILL.md frontmatter for tooling interop.

**Observations:**
- Stage 5 Search Strategy subsection is inferable (~40 tokens) — prompt-craft P1: references/05-skills-discovery.md:20
- Stage 7 Cost Optimization duplicates Stage 4 model-tier guidance (~60 tokens) — prompt-craft P2: references/07-budget-optimization.md:24
- Stage 9 validation checks duplicate script logic (~30 tokens) — prompt-craft P4: references/09-assembly-review.md:33
- Stage 8 role-pattern examples inferable but improve proposal quality — prompt-craft P3: references/08-routines-scheduling.md:13
- No structured config header in SKILL.md frontmatter — prompt-craft S1: SKILL.md:1

## Strengths

- **Excellent progressive disclosure architecture** — SKILL.md is an 851-token routing hub; all stage logic lives in `references/`. The LLM never holds all 9 stages simultaneously. Per-turn token ceiling is ~1,850.
- **Consistent, self-contained stage templates** — Every stage follows the same Goal → How to Propose → Draft Update → Progression structure. Fully self-contained; no stage needs to read another to function.
- **Correct intelligence placement** — Deterministic work (assembly, validation) delegated to scripts. Creative/adaptive work (org design, instruction writing, budget strategy) stays in prompts. Fallback pattern included for environments without Python.
- **Strong HITL design philosophy** — "Suggest, don't interrogate" is implemented throughout. Every stage proposes complete solutions, not questionnaires. Design Principles section is compact and load-bearing.
- **Complete cross-reference integrity** — All 9 stage file paths resolve. Progression chains are consistent. Inter-stage references (scripts, domain ref) all verified. Zero orphaned files.
- **Clean path standards** — Zero findings from path-standards scanner. No double prefixes, no bare paths, no absolute paths.
- **Sound dependency chain** — The stage ordering forms a proper DAG with no artificial bottlenecks. Sequential progression is justified by both data dependencies and HITL decision coherence.
- **Well-structured supporting scripts** — Both Python scripts have proper exit codes, dependency declarations, and companion test files. Assembly and validation are cleanly separated.
- **Compact domain reference** — `paperclip-domain.md` (204 lines) is entirely load-bearing with zero narrative filler. Dense tables of field definitions, types, and enum values.

## Detailed Analysis

### Structure & Integrity

The skill is structurally complete: SKILL.md frontmatter is valid, all 7 required sections present, all 9 stage files exist in `references/` with correct paths. The 10 prepass findings (9 critical missing-stage + 1 medium naming) are **all false positives** — the prepass scanner searched the skill root instead of `references/`, and the `bmad-*` naming prefix isn't required for standalone skills. No template artifacts, no TODOs, no orphaned files. Config integration is proper (loads `_bmad/config.yaml`, sensible defaults, draft persistence). The only structural note is that `orgChart` appears in the Stage 3 draft update but isn't defined in the domain schema — benign draft-only metadata.

### Craft & Writing Quality

SKILL.md scores 9/10 for progressive disclosure. The ~851-token routing hub has zero duplication with stage content. Token efficiency is strong: ~210 prunable tokens out of ~8,700 total (2.4%). Outcome-driven balance is correct — outcomes for creative work, implementation rails for format-sensitive work. Each stage's Goal section states *what* to achieve, not step-by-step *how*. The main craft gap is the absence of a structured config header (`type`, `interaction-model`, `stage-count`) in frontmatter, which reduces tooling interop. Domain reference loading strategy is implicit rather than explicit — an eager agent might load the 800-token file unnecessarily at every stage.

### Cohesion & Design

Stage flow coherence is rated A — clean DAG, no circular dependencies, logical abstract-to-concrete progression. The 9-stage count is defensible for the Paperclip domain surface area (org structure, agent config, skills, goals, budget, routines). Purpose alignment is B — the "suggest, don't interrogate" principle is consistently honored, but "capture-don't-interrupt" is stated in SKILL.md and never mentioned in any stage file. The assembly output gap (empty directories, missing routine/budget files) creates a purpose-to-output disconnect. Redundancy between stages is complementary rather than duplicative (structural vs. financial views of the same entities). One feedback loop risk exists between Stage 4 (capabilities) and Stage 5 (skills discovery) — discovering a skill might reveal a capability gap that should have been defined earlier.

### Execution Efficiency

Rated 92/100. The HITL nature means the user is the bottleneck, not the system. Inter-stage sequencing is correct by design — parallelization would violate HITL gates and produce incoherent results. Four intra-stage opportunities exist: Stage 5 skill searches can be parallelized across agents (~5-15s saved), Stage 9 review reads can be batched, activation config loads can be batched, and domain reference loading should have explicit lazy-load guidance. No subagent delegation is needed — the draft JSON is compact enough for a single context window even at maximum state. Scripts are appropriately efficient for the expected workload scale (5-7 agents, microsecond file operations).

### User Experience

The skill serves first-timers well through stages 1-3 via the propose-and-refine pattern. Friction emerges at Stage 4 (technical config complexity without contextualized explanations) and Stage 7 (budget with no cost anchoring or benchmarks). Expert users are frustrated by the mandatory 9-stage linear walk when they arrive with complete org specs. The confused user is handled well by the suggestive approach but may struggle in later domain-specific stages. Edge cases (solo agent, 30+ agent org, no-CEO request) have no detection or adaptation. The hostile environment (no `uv`, no `npx`, no network) has no upfront detection — failures surface at stages 5 and 9. A headless mode is assessed as "partially adaptable" with a hybrid review-only mode as the lowest-effort, highest-value improvement.

### Script Opportunities

Two existing scripts (`assemble-package.py`, `validate-package.py`) are well-implemented with zero lint findings and companion tests. Two new scripts are recommended: `validate-draft.py` (consolidates 6 findings — JSON schema, org tree integrity, cron syntax, budget arithmetic, cross-refs) and `summarize-draft.py` (compact stage-aware summaries for compaction recovery and context reduction). Estimated total LLM tax on deterministic work: **~4,200–12,100 tokens per full workflow run** plus ~500–2,000 tokens per compaction recovery event. The highest-value script opportunity is draft validation at stage transitions — catches errors 1–8 stages earlier than the current flow.

## Recommendations

1. **Create `validate-draft.py` mid-workflow validator** — Validates draft JSON at every stage transition with progressive checks. Catches structural errors at introduction rather than Stage 9. Resolves 7 findings. Effort: medium.
2. **Fix assembly output gap** — Either populate package directories with project/skill/routine files, or remove empty directories and clarify runtime-seeding model. Resolves 6 findings. Effort: medium.
3. **Improve compaction recovery** — Add `stageProgress` to draft JSON, write recovery preamble templates, add "save and quit" messaging, reinforce design principles in stage files. Resolves 6 findings. Effort: medium.
4. **Add batch-approval mode to Stage 4** — Group agents by role tier, offer templates for similar agents, show progress indicators. Resolves 5 findings. Effort: medium.
5. **Trim cross-stage prompt duplication** — Collapse inferable guidance, deduplicate model-tier advice, defer validation listing to script output, add config header. Resolves 5 findings. Effort: low.
6. **Add environment detection on activation** — Check for `uv` and `npx` availability upfront, adapt flow accordingly. Resolves 3 findings. Effort: low.
7. **Add quick-start mode for expert users** — Detect structured input on activation, offer to pre-populate draft and skip to combined review. Resolves 2 findings. Effort: medium.
