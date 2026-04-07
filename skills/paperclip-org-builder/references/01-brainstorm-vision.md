# Stage 1: Brainstorm & Vision

## Goal

Capture the user's vision for their AI company. Whether they arrive with a vague idea or a detailed plan, synthesize it into a clear mission statement with defined success criteria.

## How to Propose

Listen to everything the user shares — they may dump a paragraph or ask "what should I build?" Either way, synthesize and propose back a structured vision:

- **Mission** — One sentence: what this company exists to do
- **Industry/Domain** — The space it operates in
- **Key Capabilities** — What the company needs to be able to do
- **Success Criteria** — How the user will know it's working
- **Scale** — Expected number of agents, complexity level

If the user is vague, propose a concrete vision based on whatever they've shared and ask them to refine. If they're detailed, reflect their vision back in structured form. The goal is to get to a clear, shared understanding — not to interrogate.

## Draft Update

Write to `{output_folder}/paperclip-org-draft.json`:

```json
{
  "schema": "paperclip-org-builder/v1",
  "currentStage": 2,
  "vision": {
    "mission": "...",
    "industry": "...",
    "capabilities": ["..."],
    "successCriteria": "...",
    "scale": "..."
  }
}
```

## Progression

Present proposal: *"Anything to adjust, or shall we move on?"*

If the user shares details beyond this stage (company names, agent ideas, etc.), capture them in the draft under a `notes` field for later stages — don't interrupt the current flow.

User approves → Confirm: *"Vision locked in. Your progress is saved — you can pause and come back anytime."* → Load `./references/02-company-identity.md`
