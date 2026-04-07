# Skill Cohesion Analysis: paperclip-org-builder

**Skill:** `paperclip-org-builder`
**Type:** 9-Stage Complex Workflow (Suggestive HITL)
**Analyzed:** 2026-04-05T18:41:36

---

## Executive Summary

This is a well-structured skill. The nine stages trace a defensible arc from abstract vision to concrete deliverable, the suggestive-HITL philosophy is consistently upheld, and the scripts close the loop with real validation. That said, there are a few structural tensions worth addressing — none fatal, but some would sharpen the experience notably.

**Overall Cohesion Grade: B+**

---

## 1. Stage Flow Coherence

### The Arc

```
Vision → Identity → Structure → Config → Skills → Goals → Budget → Scheduling → Assembly
  (why)    (what)     (who)      (how)   (with    (toward  (within  (when)        (ship)
                                          what)    what)    what)
```

The progression moves from abstract to concrete, which is correct. Each stage narrows the design space. You can't configure agents (4) without an org chart (3), and you can't assign skills (5) without knowing the agents. This is sound.

### Data Dependency Chain (What Each Stage Produces → Consumes)

| Stage | Produces | Required By |
|-------|----------|-------------|
| 1 — Vision | `vision.mission`, `vision.capabilities`, `vision.scale` | 2, 3, 6 |
| 2 — Identity | `company.*` (name, prefix, color, governance) | 9 |
| 3 — Org Chart | `agents[]` (slug, name, role, title, reportsTo), `orgChart` | 4, 5, 6, 7, 8 |
| 4 — Agent Config | `agents[].instructions`, `runtimeConfig`, `capabilities` | 5, 7, 9 |
| 5 — Skills | `agents[].skills` | 9 |
| 6 — Goals & Projects | `goals[]`, `projects[]` | 9 |
| 7 — Budget | `budgets`, `agents[].budgetMonthlyCents` | 9 |
| 8 — Routines | `routines[]` | 9 |
| 9 — Assembly | Package files | (terminal) |

**Verdict: Coherent.** Each stage reads data produced by prior stages and writes data consumed by later ones. No stage requires data from a future stage. The dependency graph is a proper DAG.

### One Tension: Stage 4 → 5 Ordering

Stage 4 (Agent Config) asks the AI to define `capabilities` per agent. Stage 5 (Skills Discovery) then searches for skills based on those capabilities. This is logical, but there's a feedback loop risk: discovering a skill in Stage 5 might reveal a capability the agent should have had defined in Stage 4. The "capture-don't-interrupt" principle partially mitigates this — if the user notices, the draft can be updated — but the stage files don't explicitly instruct the AI to revisit agent capabilities after skill discovery. Consider adding a note in Stage 5 to prompt a quick capabilities reconciliation.

---

## 2. Purpose Alignment

### Design Principles vs. Stage Instructions

| Principle | Honor Rate | Notes |
|-----------|-----------|-------|
| **Suggest, don't interrogate** | ✅ Strong | Every stage says "propose" / "suggest" — none say "ask the user." Stage 1 explicitly handles the vague-user case ("propose a concrete vision"). |
| **HITL at every gate** | ✅ Strong | Every stage ends with "User approves → Load next." Progression is always gated. |
| **Capture-don't-interrupt** | ⚠️ Stated but not reinforced | This principle is declared in SKILL.md but *never mentioned in any stage file*. A user might drop budget preferences during Stage 3. The stage instructions don't remind the AI to capture that. This principle relies entirely on the AI internalizing SKILL.md, which works when context is fresh but may fail after compaction. |
| **Soft gates** | ⚠️ Implicit only | The phrasing "Anything to adjust, or shall we move on?" is in SKILL.md but no stage file includes it or a variant. Stages just say "User approves → next." The soft-gate spirit should be echoed in the progression sections. |

### Package Output vs. Domain Schema

The assembly script (`assemble-package.py`) generates:
- `COMPANY.md` ✅
- `.paperclip.yaml` ✅
- `agents/*/AGENTS.md` ✅
- `projects/` directory (created but **never populated** ❌)
- `skills/` directory (created but **never populated** ❌)
- `tasks/` directory (created but **never populated** ❌)

Stage 6 designs projects, Stage 5 discovers skills, yet the assembly script only writes `COMPANY.md`, `.paperclip.yaml`, and agent files. Projects, skills, and tasks directories are `mkdir`'d but left empty. This is a **purpose-to-output gap** — the user does work in Stages 5 and 6 that doesn't land in the final package.

**Recommendation:** Either update `assemble-package.py` to emit project and skill files, or clarify in the stage instructions that these entities are captured in the draft for *runtime seeding* (not file-based packaging) if that's the intended Paperclip import model.

---

## 3. Complexity Appropriateness

### Is 9 Stages Right?

For a *complete AI org builder* with suggestive HITL? **Yes, 9 is defensible.**

This isn't a simple template stamper. The user is designing:
- Organizational structure with reporting lines
- Per-agent AI configurations (models, temperatures, instructions)
- External skill integrations
- Hierarchical goal systems
- Budget allocation with cost optimization
- Scheduled routines with cron expressions

Nine stages, each laser-focused on one entity type, keeps the cognitive load per-stage manageable. A user never has to think about budgets while designing the org chart.

### Could Stages Be Merged?

| Candidate Merge | Verdict |
|----------------|---------|
| Stages 1+2 (Vision + Identity) | **Possible but inadvisable.** Vision is strategic ("what do we build?"), Identity is tactical ("what do we call it?"). Merging them conflates two distinct decisions. |
| Stages 7+8 (Budget + Routines) | **Tempting but risky.** Both relate to "operational parameters," but budget decisions should inform routine frequency (more routines = higher cost). Keeping them separate lets Stage 8 reference Stage 7's budget as a constraint. The current order is correct. |
| Stages 3+4 (Org Chart + Agent Config) | **No.** Stage 3 is structural design (who exists, who reports to whom). Stage 4 is per-agent deep configuration. These are categorically different activities. |

**Verdict: Keep all 9.** The stage count matches the entity surface area of the Paperclip domain. Fewer stages would require more context-switching within stages; more stages would add unnecessary ceremony.

### One Concern: Stage 4 Time Scaling

Stage 4 iterates per-agent. For a 10-agent org, this stage alone could involve 10 review-approve cycles. The stage instructions say "Present each agent individually. The user reviews and approves before moving to the next." For large orgs this could become grueling.

**Recommendation:** Add a batch-approval option to Stage 4 — present all worker-level agents together when they share a role type and let the user approve the batch with per-agent overrides. CEOs and managers still get individual review.

---

## 4. Gap Detection

### Missing Stages or Concerns

| Gap | Severity | Analysis |
|-----|----------|----------|
| **No inter-agent communication design** | Medium | Stage 3 designs reporting lines, but there's no stage for defining *how* agents communicate — message formats, escalation protocols, handoff conventions. The agent instructions in Stage 4 touch on "communication expectations," but this is buried in prose, not structured data. For complex orgs, this matters. |
| **No testing / dry-run stage** | Low | The workflow goes straight from configuration to package assembly. There's no "run a simulation" or "test one agent" step. This may be outside the scope of a *builder* (vs. an *operator*), but it's worth noting. |
| **No permissions design** | Medium | Stage 4 mentions "Permissions — What resources and tools this agent can access" in its proposal template, but the domain reference has no `permissions` schema, the assembly script doesn't emit permissions, and the validation script doesn't check them. Permissions are a ghost field — mentioned but never materialized. Either define the schema or remove the reference. |
| **No issue/task seeding** | Low | Stage 6 defines projects but not initial tasks/issues within those projects. The domain schema supports issues with identifiers like "MAR-42." The `tasks/` directory is created by assembly but never populated. If the package format supports initial tasks, a half-stage in Stage 6 could seed them. |

### Not a Gap (Anticipated Objections)

- **"No agent personality/tone stage"** — Correctly absorbed into Stage 4's instructions writing. A separate stage would be overkill.
- **"No onboarding/tutorial stage"** — Out of scope. This skill builds the org; operating it is a different concern.

---

## 5. Redundancy Detection

### Overlapping Concerns

| Overlap | Severity | Analysis |
|---------|----------|----------|
| **Model selection in Stage 4 AND Stage 7** | Low | Stage 4 proposes `runtimeConfig` (model, temperature) per agent. Stage 7 proposes budget optimization including "model selection — match model capability to task complexity." This is intentional — 4 sets the initial config, 7 reviews it through a cost lens — but the relationship isn't explicit. Stage 7 should say "Review the models selected in Stage 4 and recommend downgrades where cost savings outweigh capability loss." |
| **Cost awareness in Stage 3 AND Stage 7** | Low | Stage 3's "Token Cost Awareness" section discusses hierarchy depth and communication overhead. Stage 7 discusses budget optimization. Again, this is intentional (Stage 3 informs structure, Stage 7 quantifies cost), but it could confuse the AI into giving premature budget advice in Stage 3. The current framing ("for the user's awareness") in Stage 3 is adequate but borderline. |
| **Agent capabilities in Stage 4 AND Stage 5** | See §1 | Already discussed under flow coherence. Skills extend capabilities; capabilities inform skill search. Minor feedback loop. |

**Verdict: No harmful redundancy.** The overlaps are complementary perspectives (structural vs. financial) on the same entity, not duplicated work.

---

## 6. Dependency Graph Logic

### Draft JSON as State Machine

The `currentStage` field in the draft JSON creates a linear state machine:

```
1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → "complete"
```

This is strictly sequential — no branching, no optional stages, no parallel paths. For this domain, that's appropriate. Every stage depends on at least one prior stage's output.

### Compaction Recovery

The recovery strategy is sound: read the draft, resume from `currentStage`. The draft is the single source of truth. However:

- **Risk:** If compaction occurs *mid-stage* (after partial data is written but before `currentStage` is incremented), the AI may re-propose a partially-completed stage. This is acceptable behavior (HITL means the user can say "we already did that"), but the recovery instructions could note: "Check if the current stage's data section already has content. If so, present it for confirmation rather than re-proposing from scratch."

### Assembly Script Validation

The `load_draft()` function requires `vision`, `company`, and `agents` — the outputs of Stages 1-4. It doesn't require `goals`, `projects`, `budgets`, or `routines` — these are optional. This means a user could technically skip Stages 5-8 and still get a valid package. That may be intentional (minimum viable org), but it's not communicated in SKILL.md. If early assembly is a supported path, document it. If not, the script should warn on missing optional sections.

---

## 7. External Skill Integration (skills.sh — Stage 5)

### Strengths

- Uses `npx skills find` for discovery — real CLI integration, not just advice.
- Quality heuristics are sensible (1K+ installs, reputable sources).
- Graceful degradation: "If the user can't install, note it for later."

### Concerns

| Concern | Severity | Analysis |
|---------|----------|----------|
| **CLI availability assumption** | Low | Stage 5 assumes `npx skills` is available. The fallback is documented, but the AI should *check* before running commands (e.g., `npx skills --version`). |
| **skills.sh is an external dependency** | Medium | The skill hardcodes reliance on a third-party skill registry. If skills.sh goes down, changes its API, or the user has no internet, Stage 5 partially fails. The fallback path (manual URLs) is adequate but could be more prominent — it reads as an afterthought. |
| **No skill compatibility validation** | Low | Stage 5 discovers skills but doesn't verify they're compatible with the Paperclip runtime. skills.sh skills are generic MCP/agent skills; not all may work in Paperclip's process adapter model. A note about compatibility checking would be prudent. |
| **Skills in draft vs. package** | Medium | Skills are recorded in `agents[].skills` in the draft. The assembly script writes them to AGENTS.md frontmatter. But the `skills/` directory in the package is never populated. If Paperclip expects skill *files* (not just references), this is a packaging bug. If skills are reference-only in AGENTS.md, the empty `skills/` directory is misleading — remove it or add a README explaining its purpose. |

---

## 8. Additional Observations

### Draft JSON Schema Drift Risk

Each stage independently defines what it writes to the draft. There's no centralized schema for `paperclip-org-draft.json`. Over time, as stages evolve, the draft structure could drift — Stage 3 might rename `agents[].reportsTo` to `agents[].managerId` without Stage 9 updating its assembly logic.

**Recommendation:** Add a `draft-schema.json` (JSON Schema) to `references/` that defines the canonical draft structure. Stages reference it; scripts validate against it.

### Validation Script Coverage

`validate-package.py` checks:
- ✅ Required files exist
- ✅ YAML frontmatter validity
- ✅ Required fields (schema, kind, slug, name for company; name, role for agents)
- ✅ CEO existence and uniqueness
- ✅ `reportsTo` cross-references
- ✅ Valid role enums

Does **not** check:
- ❌ `.paperclip.yaml` adapter references match agent slugs
- ❌ Goal `ownerAgentId` references valid agents
- ❌ Project `leadAgentId` references valid agents
- ❌ Routine `assigneeAgentId` references valid agents
- ❌ Budget amounts are positive integers

These are lower-priority (the fields may not be in the package files), but worth noting for future hardening.

### SKILL.md Activation Section

The activation section references `{project-root}/_bmad/config.yaml` — this is BMad Builder infrastructure. Good for BMad-hosted skills. But if this skill is ever used outside a BMad context, this activation path fails silently. The fallback ("Use sensible defaults for anything not configured") handles it, but the coupling should be noted.

---

## Summary Scorecard

| Dimension | Score | Notes |
|-----------|-------|-------|
| Stage Flow Coherence | **A** | Clean DAG, no circular deps, logical progression |
| Purpose Alignment | **B** | Principles honored in spirit; some not reinforced in stage files; assembly script has output gaps |
| Complexity Appropriateness | **A-** | 9 stages matches domain surface area; Stage 4 scaling concern for large orgs |
| Gap Detection | **B** | Permissions ghost field, empty package directories, no inter-agent comms design |
| Redundancy Detection | **A** | Overlaps are complementary, not duplicative |
| Dependency Graph Logic | **A-** | Linear state machine is appropriate; mid-compaction recovery could be crisper |
| External Integration | **B+** | skills.sh integration is practical; fallback paths need prominence; skills/ directory disconnect |

---

## Top 5 Actionable Recommendations

1. **Fix the assembly gap:** Update `assemble-package.py` to emit project files and skill references, or remove the empty directories and clarify these entities are runtime-seeded.

2. **Reinforce design principles in stage files:** Add a one-line reminder about "capture-don't-interrupt" and soft-gate phrasing to each stage's Progression section. Don't rely on SKILL.md surviving compaction.

3. **Add a draft schema:** Create `references/draft-schema.json` as the canonical contract between stages and scripts. Validate on assembly.

4. **Resolve the permissions ghost:** Either add permissions to the domain schema, assembly script, and validation — or remove the reference from Stage 4's proposal template.

5. **Add batch-approval to Stage 4:** For orgs with 5+ agents, present same-role workers as a group with per-agent override capability to prevent review fatigue.
