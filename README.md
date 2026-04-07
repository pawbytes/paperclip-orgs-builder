# 🏢 Paperclip Org Builder

> A guided AI skill that walks you through building a complete AI-powered organization on [Paperclip](https://paperclip.ing/) — from your first idea to a ready-to-import company.

No blank forms. No prior experience needed. Just a conversation.

---

## What Is This?

**Paperclip Org Builder** is a skill for AI assistants (like GitHub Copilot) that turns a brainstorming session into a fully configured AI company you can import into Paperclip.

You describe what you want to build. The AI proposes the whole thing — team structure, agent roles, schedules, goals, budgets. You approve, adjust, and move on. At the end, you get a package you can import directly.

---

## How It Works

The skill guides you through **9 stages**, one conversation at a time. Your progress is saved after every stage — you can stop and come back whenever you want.

```
Stage 1 → Vision         What's your company for?
Stage 2 → Identity       Name, brand, conventions
Stage 3 → Org Chart      Who works here and how do they connect?
Stage 4 → Agents         Each agent's full operating instructions
Stage 5 → Skills         What tools and skills should agents have?
Stage 6 → Goals          What is the company trying to achieve?
Stage 7 → Budget         How much does each agent cost per month?
Stage 8 → Routines       What recurring tasks run automatically?
Stage 9 → Export         Review and download your company package
```

Every stage follows the same pattern:

1. The AI reads what you've built so far
2. It **proposes a complete draft** for this stage
3. You review, adjust anything you want, and say "move on"
4. Done — next stage loads automatically

---

## Getting Started

Just tell your AI assistant to set up a company. Any of these work:

- *"I want to create an organization"*
- *"Help me build a company on Paperclip"*
- *"Set up my org"*

The skill activates and starts the conversation.

---

## What You Get at the End

A complete, ready-to-use AI company — every team member configured with their own role, responsibilities, and working style. Import it into Paperclip and your team starts working immediately.

At the end of the process, the AI gives you a single command to run:

```bash
npx paperclipai company import ./your-company
```

```
your-company/
├── Company profile          # Identity, mission, brand
├── Team configuration       # Every agent: who they are, what they do, how they work
├── Project list             # Goals and active projects
└── Schedule                 # Recurring tasks that run automatically
```

---

## What Each Agent Is Made Of

Every person on your AI team gets their own profile — drafted by the AI, reviewed by you.

| Part | What It Defines |
|------|----------------|
| **Identity** | Job title, responsibilities, what they will and won't do |
| **Personality** | Values, quality standards, how they handle edge cases |
| **Working style** | A step-by-step checklist they follow every time they work |
| **Access** | Which tools and resources they can use |

---

## The Approval Process

You're always in control. At every stage, the AI shows you a proposal and asks:

> *"Anything to adjust, or shall we move on?"*

You can:
- Say **"looks good"** to approve and advance
- **Edit specific parts** — the AI incorporates your changes
- **Go back** to an earlier stage if you change your mind (e.g., rethinking your team after seeing the budget in Stage 7)

### Reviewing your team (Stage 4)

For larger teams, the AI groups reviews to avoid fatigue:

| Who | How |
|-----|-----|
| **CEO** | Reviewed individually, in full detail |
| **Managers** | Reviewed as a group |
| **Workers** | First of each role reviewed, then *"Apply this to all 3 remaining engineers?"* |

A counter keeps you oriented throughout: `Agent 3 of 10 · Workers — Engineers · 2 approved`

---

## Your Progress Is Always Saved

Everything is saved automatically after each stage. If you close the chat or need to take a break, just start again — the AI will pick up exactly where you left off, even if you were mid-stage.

---

## Going Back to Change Something

You can revisit any earlier stage at any time. Just say it:

> *"Actually, I want to change the org chart"*
> *"Let's revisit the budget"*

The AI navigates back, shows you what's there, lets you change it, and re-advances through anything affected downstream.

---

## Validation & Quality Checks

The skill quietly checks your work at every stage — catching issues as they happen rather than surfacing them all at the end.

| Stage | What Gets Checked |
|-------|------------------|
| After naming your company | Name format, unique identifier |
| After building your org chart | Exactly one CEO, everyone has a manager |
| After configuring agents | All team members have instructions |
| After setting goals | Every goal and project has an owner who exists |
| After setting budgets | Numbers add up, nothing is negative |
| Before export | Full review of the entire package |

If something looks off, you're told right away — not after hours of work.

---

## License

MIT
