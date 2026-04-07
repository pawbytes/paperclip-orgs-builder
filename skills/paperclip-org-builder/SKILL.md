---
name: paperclip-org-builder
description: Step-by-step AI org builder for Paperclip. Use when user says 'create an organization', 'build a company', or 'setup my org'.
---

# Paperclip Org Builder

## Overview

This skill helps you design and build a complete Paperclip AI company — from initial brainstorm to importable package — through guided, AI-assisted creation. Act as a seasoned organizational designer who proposes complete solutions at each stage. The user steers by approving, adjusting, or redirecting — not by answering interview questions.

Through nine stages, you'll collaboratively shape the company's identity, org chart, agent configurations (with all operating files — AGENTS.md, SOUL.md, HEARTBEAT.md, TOOLS.md), skills, goals, budgets, and routines. Your output is a ready-to-import Paperclip company package following the real Paperclip schema.

## On Activation

Use sensible defaults for anything not configured.

Resolve: `user_name`, `communication_language`, `document_output_language`, `output_folder` (default: `{project-root}/.pawbytes/paperclip`).

Create a working draft at `{output_folder}/paperclip-org-draft.json` to accumulate decisions across stages. This file is your compaction-safe state — each stage reads it on entry and updates it on completion. Track intra-stage progress in `stageProgress` so recovery can resume mid-stage (e.g., which agents are configured in Stage 4).

Greet the user and explain what you'll build together. Mention that progress is saved automatically — they can leave and resume anytime. Then load `./references/01-brainstorm-vision.md` and begin.

## Design Principles

- **Suggest, don't interrogate** — Propose complete suggestions at every stage based on what you know. The user refines, not fills blanks.
- **HITL at every gate** — Present your proposal clearly, get explicit approval before advancing.
- **Capture-don't-interrupt** — When the user shares info beyond the current stage, note it in the draft for later.
- **Soft gates** — "Anything to adjust, or shall we move on?" invites additions without pressure.

## Stages

| # | Stage | Load |
|---|-------|------|
| 1 | Brainstorm & Vision | `./references/01-brainstorm-vision.md` |
| 2 | Company Identity | `./references/02-company-identity.md` |
| 3 | Org Chart Design | `./references/03-org-chart.md` |
| 4 | Agent Configuration | `./references/04-agent-deep-dive.md` |
| 5 | Skills Discovery | `./references/05-skills-discovery.md` |
| 6 | Goals & Projects | `./references/06-goals-projects.md` |
| 7 | Budget & Cost Optimization | `./references/07-budget-optimization.md` |
| 8 | Routines & Scheduling | `./references/08-routines-scheduling.md` |
| 9 | Package Assembly & Review | `./references/09-assembly-review.md` |

Load each stage reference when entering that stage. The draft file tracks `currentStage` and `stageProgress` for recovery.

## Compaction Recovery

If context is lost, read `{output_folder}/paperclip-org-draft.json` and recover with this pattern:

1. **Orient** — Summarize completed decisions at headline depth (one sentence per stage completed, not full detail).
2. **Locate** — State the current stage and any intra-stage progress (e.g., "We're in Stage 4 — 3 of 7 agents configured").
3. **Offer adjustment** — "Before we continue, want to revisit or adjust anything above?"
4. **Resume** — Load the current stage reference and continue from where `stageProgress` left off.

## Backward Navigation

If the user wants to revisit an earlier stage (e.g., budget insights in Stage 7 prompt rethinking the org chart from Stage 3), navigate back: load the requested stage reference, present the current data for that stage, and let them adjust. Update the draft and re-advance through affected downstream stages, noting what changed.

## Domain Reference

For Paperclip entity schemas, field definitions, and package format: `./references/paperclip-domain.md`

## Scripts

- `./scripts/validate-draft.py` — Progressive draft validation. Call at every stage gate to catch issues early. Run: `uv run ./scripts/validate-draft.py <draft-json> [--stage N]`
- `./scripts/assemble-package.py` — Generates the importable company folder from the draft JSON. Run: `uv run ./scripts/assemble-package.py <draft-json> <output-dir>`
- `./scripts/validate-package.py` — Validates the generated package structure. Run: `uv run ./scripts/validate-package.py <package-dir>`

If scripts cannot execute, perform equivalent assembly and validation directly.

## Playbook Principles

The following principles (from the Paperclip Company Playbook) should inform how you guide agent configuration in Stage 4:

- **Two-layer verification** — Workers self-check, CEO verifies before Founder sees it
- **Quality gate, not postman** — CEO verifies deliverables independently, never forwards unchecked agent output
- **Idle is success** — Agents with no remaining work should wait, not generate busywork
- **Definition of Done** — Every agent needs concrete, checkable completion criteria
- **Anti-patterns table** — HEARTBEAT.md includes a growing record of past mistakes
- **Feedback loops** — After corrections, update instructions AND verify the fix next time
