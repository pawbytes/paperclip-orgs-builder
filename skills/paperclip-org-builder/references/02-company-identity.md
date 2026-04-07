# Stage 2: Company Identity

## Goal

Define the company's identity — name, description, configuration, and governance preferences. Also establish contribution conventions that all agents will follow.

## How to Propose

Based on the vision, suggest a complete "company card":

- **Name** — A fitting company name (creative but professional, relevant to the domain)
- **Description** — 1-2 sentence mission statement
- **Issue Prefix** — 3-4 uppercase characters derived from the name (e.g., "MARK" for a marketing company, "DEV" for a dev shop)
- **Brand Color** — A hex color that fits the industry and personality
- **"What We Are / What We Are NOT"** — One sentence each. This anchors agent identity and prevents drift. E.g., "We are a SaaS product company. We are NOT an agency."

Present as a cohesive card the user can review and adjust field by field.

### Contribution Conventions

Also propose a CONTRIBUTING.md for the company. This governs how all agents work:

- **Commit format** — `[agent-role]: description (PREFIX-XX)` with a prefix per role
- **Branch strategy** — All on main (early/small teams) or feature branches (mature teams)
- **File ownership** — Which directories belong to which agent roles

Present these alongside the company card. They inform the package's CONTRIBUTING.md file.

## Draft Update

Add `company` section and `contributing` section to the draft:

```json
{
  "company": {
    "name": "...",
    "description": "...",
    "issuePrefix": "...",
    "brandColor": "#...",
    "whatWeAre": "...",
    "whatWeAreNot": "..."
  },
  "contributing": {
    "branchStrategy": "main",
    "commitFormat": "[agent-role]: description (PREFIX-XX)"
  }
}
```

Set `currentStage: 3`.

## Progression

Present proposal: *"Anything to adjust, or shall we move on?"*

If the user mentions agents, skills, or other downstream details, note them in the draft for later — don't redirect the conversation.

User approves → Confirm: *"Identity set. Progress saved."* → Load `./references/03-org-chart.md`
