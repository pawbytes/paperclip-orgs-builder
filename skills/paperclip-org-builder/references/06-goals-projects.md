# Stage 6: Goals, Projects & Inventory

## Goal

Define the company's goal hierarchy, initial projects, and create a PROJECT-INVENTORY.md that serves as the source of truth for all agents.

## How to Propose

Based on the approved vision and org chart:

### Goals Hierarchy

- **Company goals** — 1-3 top-level goals derived from the mission and success criteria. These are the "why" of the company.
- **Team goals** — Sub-goals owned by managers or team leads, aligned to company goals. Each team goal should map to a specific capability area.
- **Agent goals** — Optional per-agent objectives for specialized outcomes.

Each goal needs: title, description, level, owner agent, and status (usually "planned" for new orgs).

### Initial Projects

- **1-3 starter projects** — Concrete work streams that advance the company goals
- Each needs: name, description, lead agent, initial status
- Projects should be immediately actionable — things agents can start working on
- Every project should align to at least one goal

Present the complete goal tree and project list together so the user can see alignment between vision → goals → projects → agents.

### Project Inventory

Also propose a PROJECT-INVENTORY.md for the company root. This is a critical operational file — every agent reads it before starting tasks to avoid duplicate work.

Include:
- **What We Are** — Company type, product name, domain, what we do NOT do (from Stage 2)
- **The Product** — Current status, key features, location
- **Directory Ownership** — Which directories belong to which agent roles
- **Completed Deliverables** — Empty table for tracking (grows over time)
- **Current Phase** — Phase name, status, what it covers
- **Rules** — "Read this before starting any task", "Do not recreate existing work"

## Draft Update

Add `goals` array (with hierarchy via parentId), `projects` array, and `projectInventory` content.

Set `currentStage: 7`.

## Progression

Present proposal: *"Anything to adjust, or shall we move on?"*

User approves → Confirm: *"Goals and projects set. Progress saved."* → Load `./references/07-budget-optimization.md`
