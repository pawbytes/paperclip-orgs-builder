# Stage 4: Agent Configuration

## Goal

Configure each agent with their full operating files. Paperclip agents can have up to 4 files, each serving a distinct purpose. Use tiered presentation to keep review effort proportional — the CEO gets the most attention, workers get batched.

## Agent Files Overview

Each agent directory can contain:

| File | Purpose | Who Gets It |
|------|---------|-------------|
| AGENTS.md | Identity, instructions, responsibilities, Definition of Done, communication protocol | All agents |
| SOUL.md | Persona, beliefs, quality philosophy, anti-patterns, boundaries | CEO (essential), managers (recommended), workers (optional) |
| HEARTBEAT.md | Execution checklist — state machine for every heartbeat | CEO (essential, 12-step with quality gate), all workers (7-step with self-check) |
| TOOLS.md | Available tools, API endpoints, file system access | CEO (essential), workers with tool access (optional) |

**AGENTS.md frontmatter is slim** — only `name`, `title`, `reportsTo`, `skills`. Operational fields like `role`, `budgetMonthlyCents`, `capabilities`, `permissions`, and `adapter` go into `.paperclip.yaml` and are configured in later stages or noted in the draft now.

## Presentation Tiers

Sort agents from the org chart and process in this order:

1. **CEO (solo, full treatment)** — All 4 files. This agent is the quality gate for the entire company, so every file deserves focused review.
2. **Managers (grouped)** — AGENTS.md + HEARTBEAT.md + SOUL.md (recommended). Present all managers together; user approves the group.
3. **Workers by role (batched)** — AGENTS.md + HEARTBEAT.md. Group by role (all engineers, all designers). Present the first, offer template reuse: *"Apply this to all [N remaining engineers]? You can override individuals after."*

Show a **progress indicator** at each step: `[Agent 3 of 10 · Tier: Workers — Engineers · 2 approved]`

## Configuring AGENTS.md

For each agent, draft the complete AGENTS.md:

**Frontmatter** (slim):
```yaml
---
name: "Agent Name"
title: "Job Title"
reportsTo: manager-slug
skills:
  - skill-slug-one
---
```

**Body** (rich — this IS the agent's operating manual):

- **Identity** — "I am the [Role] at [Company]. I [core responsibility]. I report to [Manager]."
- **Reporting Line** — Direct manager, CEO, company context
- **Responsibilities** — Numbered list of what this agent does
- **Definition of Done** — Concrete, checkable criteria. Not "code works" but "page loads without errors, all links tested, self-check completed, completion comment posted."
- **Communication Protocol** — Workers: "Paperclip only. No email. No direct Founder contact." CEO: may use email.
- **What I Don't Do** — Explicit boundaries. Include: "Generate work when queue is empty", "Skip self-check", "Mark done without verifying."

## Configuring SOUL.md (CEO + Managers)

The SOUL defines who the agent IS. Without it, agents default to "helpful assistant" — wrong for roles that need judgment and boundaries.

For the CEO, propose:
- **Identity** — Role, authority, reporting to the Founder
- **What We Are / Are NOT** — Company identity anchors prevent drift
- **Quality Control Is My Most Important Job** — The CEO's core belief
- **What I Believe In** — Quality over speed, verify before report, idle is success, mission above activity
- **What I Don't Do** — Report without verifying, forward agent output unchecked, generate busywork, merge PRs
- **North Star** — The primary business goal everything traces back to

For managers, propose a lighter SOUL focused on their domain boundaries and quality responsibilities.

## Configuring HEARTBEAT.md

The HEARTBEAT is a numbered state machine — always run in order, no shortcuts.

### CEO Heartbeat (12 steps)

1. Orient — Read memory, PROJECT-INVENTORY, check wake context
2. Inbox Check — Check for Founder messages
3. Review Assignments — Dashboard, stale tasks, priorities
4. Status Check — All departments, current phase
5. Pre-Creation Gate — 4 questions before creating any task
6. **Quality Control Gate (MANDATORY)** — Verify every deliverable before reporting to Founder
7. Delegation Quality Check — Every task has acceptance criteria
8. Anti-Drift Check — "Am I about to skip verification?"
9. Proactive Communication — Email Founder with verified status
10. Feedback Loop — After corrections: update instructions, verify fix
11. Memory Update — Daily notes, decisions, blockers
12. Phase Completion Check — All done? Report and wait.

### Worker Heartbeat (7 steps)

1. Identity & Context — Agent ID, company, reporting line
2. Get Assignments — Check for assigned issues; if nothing, exit cleanly
3. Checkout & Work — Always checkout before working
4. **Self-Check (MANDATORY)** — Generic checks (deliverable exists, matches request, no placeholders) + role-specific checks
5. Complete Issue — Mark done with completion comment
6. Anti-Patterns — Check the growing table of past mistakes
7. Exit — Comment on in-progress work before exiting

**The anti-patterns table** starts empty and grows as mistakes are caught. This is institutional memory.

## Configuring TOOLS.md (CEO)

For the CEO, propose a TOOLS.md covering:
- **Paperclip API** — Base URL, common endpoints (dashboard, issues, checkout, comments, goals, projects, agent pause/resume)
- **File System** — Company root, agent home, documentation paths
- **Email** — Tool and address for Founder communication (if applicable)

## Draft Update

For each agent, store in the `agents` array:
- `name`, `slug`, `role`, `title`, `reportsTo`, `skills` (identity fields)
- `instructions` — The AGENTS.md body content
- `soul` — The SOUL.md content (if applicable)
- `heartbeat` — The HEARTBEAT.md content
- `tools` — The TOOLS.md content (if applicable)
- `adapterType` — Default `claude_local`; note for .paperclip.yaml
- `capabilities` — Note for .paperclip.yaml
- `permissions` — Note for .paperclip.yaml

Track per-agent approval: `approved: true`.

Update `stageProgress` as agents are configured: `{ "agentsConfigured": ["ceo-slug", "manager-slug"] }`

Set `currentStage: 5` after all agents are configured.

## Progression

After all agents configured: *"All [N] agents configured with their operating files. Anything to adjust, or shall we move on to skills?"*

**Remember:** Capture-don't-interrupt. If the user mentions goals, budget, or downstream topics, note in draft for later.

User approves → Confirm: *"All agents locked in. Progress saved."* → Load `./references/05-skills-discovery.md`
