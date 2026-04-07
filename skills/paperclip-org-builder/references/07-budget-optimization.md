# Stage 7: Budget & Cost Optimization

## Goal

Set the company's budget allocation and help the user understand cost implications. Provide actionable optimization guidance.

## How to Propose

### Company Budget

Suggest a reasonable monthly budget based on org size and expected workload. Present in both cents (for the config) and dollars (for the user). Explain the reasoning.

### Per-Agent Allocation

Distribute the budget based on role complexity and expected usage:

- **CEO / Managers** — Higher allocation. They handle complex reasoning, coordination, and multi-step decision-making.
- **Engineers / Workers** — Lower allocation. Their tasks are more routine and use simpler models.

Show a clear breakdown table: agent name, role, model, estimated monthly cost, allocated budget.

### Cost Optimization Strategies

Propose specific strategies tailored to this company's design:

- **Model selection** — Match model capability to task complexity. Not every agent needs the most expensive model.
- **Heartbeat frequency** — Less frequent heartbeats = lower costs. Suggest appropriate intervals per role (CEOs might check in daily, workers every few hours).
- **Task batching** — Agents that batch work use fewer tokens than agents handling one item at a time.
- **Delegation depth** — Remind the user of their org chart's depth and its cost implications.

### Budget Policies

For each scope (company-wide and per-agent), suggest:

- Warning threshold percentage (typically 80%)
- Whether hard stop should be enabled (recommended for cost control, optional for flexibility)
- Brief rationale for the recommendation

## Draft Update

Add `budgets` section with company total, per-agent allocations, and budget policies.

Set `currentStage: 8`.

## Progression

Present proposal: *"Anything to adjust, or shall we move on?"*

If budget realities suggest rethinking the org size or model choices, proactively offer: *"This budget works, but we could save [X] by [adjustment]. Want to revisit the org chart or agent configs?"* Navigate back if the user agrees.

User approves → Confirm: *"Budget locked. Progress saved."* → Load `./references/08-routines-scheduling.md`
