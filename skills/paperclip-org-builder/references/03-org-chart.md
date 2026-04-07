# Stage 3: Org Chart Design

## Goal

Design the complete organizational hierarchy — who reports to whom, why, and how information flows. This is the most consequential stage: the org chart determines communication costs, delegation efficiency, and task routing quality.

## How to Propose

Build the org chart based on the vision's capabilities and scale. Present:

- **Visual hierarchy** — ASCII tree showing reporting lines
- **Role rationale** — Why each position exists and what gap it fills
- **Communication flow** — How decisions propagate down and information flows up
- **Delegation patterns** — Which agents delegate to whom for what

### Design Considerations

- **Flat vs deep** — Fewer management layers = fewer delegation hops = lower token costs. Only add managers when span of control exceeds what one agent can coordinate effectively.
- **CEO scope** — The CEO should focus on strategy and coordination, not direct task execution. For companies with >3 agents, a CEO with managers is usually the right call.
- **Specialist vs generalist** — Prefer specialist roles (engineer, designer, marketer) when the domain warrants it. Use the "general" role only when no specific role fits.
- **No orphans** — Every non-CEO agent must report to someone. Ensure the tree is complete before presenting.

### Token Cost Awareness

Each layer in the hierarchy adds communication overhead. For the user's awareness:

- Direct CEO → worker: 1 hop (cheapest, but CEO becomes bottleneck at scale)
- CEO → manager → worker: 2 hops (balanced for most orgs)
- CEO → manager → lead → worker: 3 hops (only justified for large orgs, 10+ agents)

Recommend the shallowest structure that maintains clear ownership and manageable spans.

## Draft Update

Add `agents` array (slug, name, role, title, reportsTo for each) and an `orgChart` text field with the ASCII visualization. The `orgChart` field is a draft-only visualization aid — it is not written to the final package.

Set `currentStage: 4`.

## Progression

Present proposal: *"Anything to adjust, or shall we move on?"*

User approves → Confirm: *"Org chart locked. Progress saved."* → Load `./references/04-agent-deep-dive.md`
