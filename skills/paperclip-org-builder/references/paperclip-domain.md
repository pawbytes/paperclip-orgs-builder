# Paperclip Domain Reference

## Entity Hierarchy

```
Company
├── Agents (tree via reportsTo)
│   ├── Skills (per-agent capabilities)
│   └── Routines (scheduled work)
├── Goals (hierarchical: company → team → agent → task)
│   └── Projects
│       └── Issues/Tasks
└── Budget Policies
```

## Company Fields

| Field | Type | Notes |
|-------|------|-------|
| name | string | Company display name |
| description | string | Mission/purpose description |
| slug | string | URL-friendly identifier |
| status | enum | active, paused, archived |
| issuePrefix | string | 3-4 chars, uppercase (e.g., "MAR") |
| budgetMonthlyCents | integer | Company-wide monthly budget in cents |
| brandColor | string | Hex color code (e.g., "#3B82F6") |

## Agent Fields

### AGENTS.md Frontmatter (slim — identity only)

| Field | Type | Notes |
|-------|------|-------|
| name | string | Agent display name |
| title | string | Job title (e.g., "VP of Engineering") |
| reportsTo | slug/null | Parent agent slug — null only for CEO |
| skills | string[] | Skill slugs assigned to this agent |

### .paperclip.yaml Agent Config (operational details)

| Field | Type | Notes |
|-------|------|-------|
| role | enum | ceo, cto, cmo, cfo, engineer, designer, pm, qa, devops, researcher, general |
| title | string | Optional override |
| capabilities | string | What the agent can do |
| budgetMonthlyCents | integer | Per-agent monthly budget in cents |
| permissions | json | Access controls |
| adapter.type | enum | claude_local, codex_local, gemini_local, opencode_local, pi_local, cursor, hermes_local, process, http, openclaw_gateway |
| adapter.config | json | Adapter-specific settings |
| metadata | json | Arbitrary metadata |

### Agent Files

Each agent directory contains up to 4 files:

| File | Required | Purpose |
|------|----------|---------|
| AGENTS.md | Yes | Identity, reporting line, responsibilities, Definition of Done, communication protocol, "What I Don't Do". Frontmatter has name/title/reportsTo/skills. Body is the agent's instructions. |
| SOUL.md | Recommended (CEO essential) | Persona, beliefs, quality philosophy, anti-patterns, north star. Defines who the agent IS and how they should act. |
| HEARTBEAT.md | Recommended (CEO essential) | Execution checklist — a state machine run every heartbeat. CEO: quality gate + verification. Workers: self-check before "done". |
| TOOLS.md | Optional (CEO essential) | Available tools: API endpoints, email access, file system paths. Prevents wrong-tool usage. |

### Agent Hierarchy Rules

- Exactly one CEO (reportsTo = null) per company
- All other agents must have reportsTo pointing to a valid agent slug
- No cycles — strict tree structure
- Hierarchy determines communication and delegation flow

## Goal Fields

| Field | Type | Notes |
|-------|------|-------|
| title | string | Goal name |
| description | string | What this goal achieves |
| level | enum | company, team, agent, task |
| parentId | uuid/null | Parent goal for hierarchy |
| ownerAgentId | uuid | Agent responsible |
| status | enum | planned, active, achieved, cancelled |

## Project Fields

| Field | Type | Notes |
|-------|------|-------|
| name | string | Project name |
| description | string | Project purpose |
| status | enum | backlog, planned, in_progress, completed, cancelled |
| leadAgentSlug | slug | Lead agent |
| targetDate | date/null | Target completion |

## Issue/Task Fields

| Field | Type | Notes |
|-------|------|-------|
| title | string | Task name |
| identifier | string | Auto-generated (e.g., "MAR-42") |
| status | enum | backlog, todo, in_progress, in_review, done, blocked, cancelled |
| priority | enum | critical, high, medium, low |
| assigneeAgentId | uuid | Single assignee |
| parentId | uuid/null | For subtasks |

## Routine Fields

Routines live in `.paperclip.yaml` under `routines.{slug}`:

| Field | Type | Notes |
|-------|------|-------|
| concurrencyPolicy | string | How to handle overlapping runs |
| catchUpPolicy | string | What to do with missed runs |
| status | enum | active, paused, archived |
| triggers | array | One or more trigger definitions |

### Routine Triggers

| Field | Type | Notes |
|-------|------|-------|
| kind | string | `schedule` or `webhook` |
| cronExpression | string | Standard cron (e.g., `0 9 * * 1-5`) |
| timezone | string | IANA timezone (e.g., `America/New_York`) |
| enabled | boolean | Whether trigger is active |

## Skill Fields

| Field | Type | Notes |
|-------|------|-------|
| key | string | Hierarchical key (e.g., `company/{id}/{slug}`) |
| slug | string | URL-friendly name |
| name | string | Display name |
| description | string | What the skill does |

Skills are packaged as directories containing at minimum a `SKILL.md` file with YAML frontmatter.

## Budget Policy Fields

| Field | Type | Notes |
|-------|------|-------|
| scopeType | enum | company, agent, project, goal |
| metric | string | What's being budgeted |
| windowKind | string | Budget window type |
| amount | integer | Budget amount in cents |
| warnPercent | integer | Warning threshold (e.g., 80) |
| hardStopEnabled | boolean | Stop work when budget exhausted |

## Company Package Format

```
company-slug/
├── COMPANY.md                    # Company definition
├── .paperclip.yaml               # Agent configs, sidebar, routines, projects
├── PROJECT-INVENTORY.md          # Source of truth for existing work
├── CONTRIBUTING.md               # Commit conventions, branch strategy
├── agents/
│   ├── {ceo-slug}/
│   │   ├── AGENTS.md             # Identity + instructions
│   │   ├── SOUL.md               # Persona, beliefs, quality philosophy
│   │   ├── HEARTBEAT.md          # 12-step execution state machine
│   │   ├── TOOLS.md              # API endpoints, email, filesystem
│   │   └── memory/               # Agent memory directory
│   └── {worker-slug}/
│       ├── AGENTS.md             # Identity + instructions
│       ├── HEARTBEAT.md          # 7-step execution with self-check
│       └── memory/               # Agent memory directory
├── projects/
│   └── {project-slug}/
│       └── PROJECT.md            # Project definition
└── skills/
    └── company/
        └── {prefix}/
            └── {skill-slug}/
                └── SKILL.md      # Skill definition + supporting files
```

### COMPANY.md Format

```markdown
---
name: "Company Name"
slug: company-slug
description: "Company mission and purpose"
schema: agentcompanies/v1
---

# Company Name

Company mission and purpose.

## Success Criteria

What success looks like for this company.
```

### AGENTS.md Format

Frontmatter is slim — only identity fields. Body contains rich instructions.

```markdown
---
name: "Agent Name"
title: "Job Title"
reportsTo: manager-slug
skills:
  - skill-one
  - skill-two
---

# Agent Name — Company Name

## Identity

I am the **Agent Name** at Company Name. I [role description].
I report to **Manager Name**.

## Responsibilities

1. Primary responsibility
2. Secondary responsibility

## Definition of Done

A task is only "done" when ALL of the following are true:
1. The deliverable exists and is accessible
2. Self-check from HEARTBEAT.md completed
3. Completion comment posted with what was done and where it lives

## Communication Protocol

- Paperclip only. No email. No direct Founder contact.
- Report to manager via issue comments.

## What I Don't Do

- Contact the Founder directly
- Generate work when queue is empty
- Skip self-check steps
- Mark work done without verifying it works
```

### SOUL.md Format (CEO essential, managers optional)

```markdown
# CEO SOUL — Company Name

## Identity
I am the CEO of Company Name. I delegate, coordinate, verify, escalate.

## What We Are
We are [company type]. We are NOT [misconception].

## Quality Control Is My Most Important Job
I verify EVERY deliverable before reporting to the Founder.

## What I Believe In
- Quality over speed
- I verify before I report
- Mission above activity
- Done means done — idle is success, not failure

## What I Don't Do
- Report work as done without personally verifying it
- Forward agent comments as my own assessment
- Generate tasks to fill idle time

## North Star
[Primary business goal]
```

### HEARTBEAT.md Format

CEO gets a 12-step state machine with quality gate. Workers get a 7-step
checklist with mandatory self-check. Both are run every heartbeat, in order.

**CEO critical steps:** Orient → Review Assignments → Status Check →
Pre-Creation Gate → Quality Control Gate (verify deliverables) →
Anti-Drift Check → Proactive Communication → Feedback Loop → Memory Update.

**Worker critical steps:** Identity & Context → Get Assignments → Checkout &
Work → Self-Check (MANDATORY — generic + role-specific) → Complete Issue → Exit.

### TOOLS.md Format (CEO essential)

```markdown
# CEO Tools — Company Name

## Paperclip API
Base URL: http://localhost:3100/api
Common endpoints: dashboard, issues, checkout, comments, goals, projects.

## File System
Company root, agent home, documentation paths.

## Email
Tool and address for Founder communication.
```

### .paperclip.yaml Format

```yaml
schema: paperclip/v1

company:
  brandColor: "#3B82F6"

sidebar:
  agents:
    - ceo-slug
    - manager-slug
    - worker-slug

agents:
  ceo-slug:
    role: ceo
    budgetMonthlyCents: 10000
    adapter:
      type: claude_local
  manager-slug:
    role: pm
    budgetMonthlyCents: 5000
    adapter:
      type: claude_local
  worker-slug:
    role: engineer
    budgetMonthlyCents: 5000
    adapter:
      type: claude_local

routines:
  daily-standup:
    concurrencyPolicy: skip
    catchUpPolicy: skip
    triggers:
      - kind: schedule
        cronExpression: "0 9 * * 1-5"
        timezone: America/New_York
        enabled: true

projects:
  project-slug:
    leadAgentSlug: manager-slug
    status: in_progress
```

### PROJECT-INVENTORY.md Format

Source of truth preventing duplicate work. All agents read this before starting tasks.

```markdown
# Project Inventory — Company Name

## What We Are
- Company type and description
- Product name and domain
- What we do NOT do

## Directory Ownership
| Directory | Owner | Notes |
|-----------|-------|-------|

## Completed Deliverables
| ID | Title | Agent | Output Location |
|----|-------|-------|----------------|

## Current Phase
Phase name, status, description.
```

## Import Command

```bash
paperclipai company import <package-path> --target new --new-company-name "Company Name" --yes
```
