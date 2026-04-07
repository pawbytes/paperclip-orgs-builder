# Stage 5: Skills Discovery

## Goal

Find and assign relevant skills to each agent using the skills.sh ecosystem. Skills extend agent capabilities with specialized knowledge, workflows, and tools.

## How to Discover

For each agent, based on their role and capabilities:

1. **Identify skill needs** — What specialized knowledge or workflows would make this agent more effective?
2. **Search skills.sh** — Use `npx skills find [query]` to discover relevant skills. Try specific queries based on the agent's domain.
3. **Verify quality** — Prefer skills with 1K+ installs from reputable sources (`vercel-labs`, `anthropics`, `microsoft`). Be cautious with low-install-count skills.
4. **Present findings** — Show matched skills with install counts, descriptions, and which agent they're for.

### Search Strategy

- Search by the agent's domain/industry first (e.g., "react" for frontend engineers, "SEO" for marketers)
- Then by specific capabilities they need (e.g., "testing", "deployment", "content writing")
- Try alternative terms if initial searches don't match
- Check the [skills.sh leaderboard](https://skills.sh/) for popular options in each category

### Presenting Options

For each recommended skill, show:
- **Skill name and description**
- **Install count and source**
- **Which agent(s) it should go to**
- **Install command:** `npx skills add <owner/repo@skill> -g -y`
- **Learn more link:** `https://skills.sh/<owner>/<repo>/<skill>`

### When the User Can't Install

If the user doesn't have the skills CLI or prefers manual setup:
- Provide the skills.sh URL for each skill
- Note which agent needs it in the company package
- The user can install skills into their Paperclip instance later

### Skills in the Package

Discovered skills are recorded in each agent's `skills` list in the draft. During package assembly, skills become the `skills` array in AGENTS.md frontmatter. The assembly also creates a `skills/` directory in the package with placeholder references for each discovered skill.

**Important:** For skills to work after import, the actual skill files (SKILL.md + supporting files) must be present in the package's `skills/` directory or already installed in the target Paperclip instance. If the user has access to skill source directories (e.g., `.claude/skills/`), offer to note those paths for inclusion during assembly.

## Draft Update

Add `skills` array to each relevant agent in the `agents` data.

Set `currentStage: 6`.

## Progression

Present proposal: *"Anything to adjust, or shall we move on?"*

User approves → Confirm: *"Skills assigned. Progress saved."* → Load `./references/06-goals-projects.md`
