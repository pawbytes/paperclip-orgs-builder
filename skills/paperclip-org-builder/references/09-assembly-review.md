# Stage 9: Package Assembly & Review

## Goal

Generate the complete importable Paperclip company package from all gathered data, validate it, and present for final approval.

## Assembly

Run the assembly script to generate the package:

```
uv run ./scripts/assemble-package.py {output_folder}/paperclip-org-draft.json {project-root}/.pawbytes/paperclip/companies/{company-slug}
```

If the script cannot execute, assemble the package directly by generating each file. See `./references/paperclip-domain.md` for exact formats.

The package contains:

**Company root:**
- `COMPANY.md` — Company definition with YAML frontmatter
- `.paperclip.yaml` — Agent configs (role, budget, adapter), sidebar ordering, routines, project configs
- `PROJECT-INVENTORY.md` — Source of truth for existing work (all agents read this)
- `CONTRIBUTING.md` — Commit conventions and branch strategy

**Per-agent files** (`agents/{slug}/`):
- `AGENTS.md` — Slim frontmatter (name/title/reportsTo/skills) + rich body (identity, responsibilities, DoD, communication protocol)
- `SOUL.md` — Persona and beliefs (CEO essential, managers recommended)
- `HEARTBEAT.md` — Execution state machine (CEO: quality gate, workers: self-check)
- `TOOLS.md` — Available tools (CEO essential)
- `memory/` — Agent memory directory

**Projects** (`projects/{slug}/`):
- `PROJECT.md` — Project definition with frontmatter

**Skills** (`skills/`):
- Placeholder `SKILL.md` for each referenced skill, or README explaining how to source skills

> **Note:** Tasks are runtime-created entities (auto-assigned identifiers like "MAR-42"), so they are not pre-seeded in the package.

## Validation

Run both validation scripts:

```
uv run ./scripts/validate-draft.py {output_folder}/paperclip-org-draft.json
uv run ./scripts/validate-package.py {project-root}/.pawbytes/paperclip/companies/{company-slug}
```

Key checks:
- All required files exist (COMPANY.md, .paperclip.yaml, agents with AGENTS.md)
- YAML frontmatter is valid in all markdown files
- .paperclip.yaml matches the real Paperclip schema (agents section, sidebar)
- Agent reportsTo references are consistent with the hierarchy
- Exactly one CEO exists with no reportsTo
- No circular reporting chains
- SOUL.md and HEARTBEAT.md present for CEO (warn if missing)

## Final Review

Present the user with:

1. **Directory tree** — The complete package structure showing all files
2. **Company summary** — Name, description, agent count, goal count, total budget
3. **Key file previews** — Show COMPANY.md, CEO's AGENTS.md, and .paperclip.yaml
4. **Validation results** — Any issues or warnings from both validators

## Import Instructions

After the user approves:

```bash
paperclipai company import {project-root}/.pawbytes/paperclip/companies/{company-slug} --target new --new-company-name "Company Name" --yes
```

Or they can review and manually adjust the files at `{project-root}/.pawbytes/paperclip/companies/{company-slug}/` before importing.

**Skills note:** If import shows warnings about missing skills, the user needs to source the skill files into the package's `skills/` directory or install them separately in their Paperclip instance.

## Draft Update

Set `currentStage: "complete"`.

## Completion

Before marking complete, offer: *"Want to revisit any stage before we finalize?"*

The workflow is done. The user has a complete, validated, ready-to-import Paperclip company package.
