# Stage 8: Routines & Scheduling

## Goal

Configure recurring routines for agents that need scheduled work — heartbeats, reviews, reports, and maintenance tasks.

## How to Propose

Based on each agent's role and responsibilities, suggest appropriate routines:

### Common Patterns by Role

- **CEO** — Weekly strategy review, monthly company health check
- **Managers** — Daily standup summary, weekly team report, sprint/cycle planning
- **Engineers** — Task processing heartbeat (hourly to every few hours), code review cycles
- **Marketers** — Content calendar check, campaign performance reviews
- **Designers** — Design review cycle, asset pipeline check

### For Each Routine, Propose

- **Title** — Clear name (e.g., "Morning Standup Summary")
- **Description** — What the routine accomplishes
- **Assigned Agent** — Who runs it
- **Cron Expression** — Standard cron syntax (e.g., `0 9 * * 1-5` for weekdays at 9am)
- **Timezone** — User's timezone or UTC
- **Concurrency Policy** — What if the previous run hasn't finished: skip, queue, or parallel
- **Catch-up Policy** — What about missed runs: skip, run once, or run all

### Cost Reminder

Each routine execution costs tokens. Higher frequency = higher cost. Suggest the minimum viable frequency for each routine. Agents can always be triggered on-demand between scheduled runs when something urgent needs attention.

## Draft Update

Add `routines` array with all configured routines.

Set `currentStage: 9`.

## Progression

Present proposal: *"Anything to adjust, or shall we move on to final assembly?"*

User approves → Confirm: *"Routines configured. Progress saved — almost done!"* → Load `./references/09-assembly-review.md`
