#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""
Assembles a Paperclip company package from a draft JSON file.

Usage:
    uv run assemble-package.py <draft-json> <output-dir>

Generates a package matching the real Paperclip import format:
  COMPANY.md, .paperclip.yaml, PROJECT-INVENTORY.md, CONTRIBUTING.md,
  agents/{slug}/AGENTS.md (+SOUL.md, HEARTBEAT.md, TOOLS.md, memory/),
  projects/{slug}/PROJECT.md, skills/

Exit codes: 0=success, 2=error
"""

import argparse
import json
import sys
from pathlib import Path

import yaml


def load_draft(path: str) -> dict:
    """Load and validate the draft JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        draft = json.load(f)

    required_sections = ["vision", "company", "agents"]
    missing = [s for s in required_sections if s not in draft]
    if missing:
        print(
            f"Error: Draft missing required sections: {', '.join(missing)}",
            file=sys.stderr,
        )
        sys.exit(2)

    return draft


def slugify(name: str) -> str:
    """Convert a name to a URL-friendly slug."""
    slug = name.lower().strip()
    slug = "".join(c if c.isalnum() or c in ("-", " ") else "" for c in slug)
    slug = "-".join(slug.split())
    return slug


# --- Company-level files ---


def generate_company_md(draft: dict) -> str:
    """Generate COMPANY.md with slim frontmatter matching Paperclip schema."""
    company = draft["company"]
    vision = draft["vision"]

    frontmatter = {
        "name": company["name"],
        "description": company.get("description", vision.get("mission", "")),
        "schema": "agentcompanies/v1",
        "slug": slugify(company["name"]),
    }

    body_parts = [f"# {company['name']}\n"]
    body_parts.append(
        f"{company.get('description', vision.get('mission', ''))}\n"
    )

    if vision.get("successCriteria"):
        body_parts.append(
            f"## Success Criteria\n\n{vision['successCriteria']}\n"
        )

    fm_str = yaml.dump(
        frontmatter,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    )
    return f"---\n{fm_str}---\n\n" + "\n".join(body_parts)


def generate_project_inventory_md(draft: dict) -> str:
    """Generate PROJECT-INVENTORY.md — source of truth for all agents."""
    company = draft["company"]
    projects = draft.get("projects", [])
    agents = draft.get("agents", [])

    lines = [f"# {company['name']} — Project Inventory\n"]
    lines.append(
        "> **Every agent reads this before starting any task.** "
        "Do not recreate existing work.\n"
    )

    lines.append("## What We Are\n")
    lines.append(f"- **Company:** {company['name']}")
    desc = company.get("description", "")
    if desc:
        lines.append(f"- **Mission:** {desc}")
    if company.get("whatWeAre"):
        lines.append(f"- **We are:** {company['whatWeAre']}")
    if company.get("whatWeAreNot"):
        lines.append(f"- **We are NOT:** {company['whatWeAreNot']}")
    lines.append("")

    if projects:
        lines.append("## Active Projects\n")
        lines.append("| Project | Lead | Status |")
        lines.append("|---------|------|--------|")
        for p in projects:
            name = p.get("name", "Untitled")
            lead = p.get("leadAgent", "unassigned")
            status = p.get("status", "planned")
            lines.append(f"| {name} | {lead} | {status} |")
        lines.append("")

    lines.append("## Completed Deliverables\n")
    lines.append("| Deliverable | Agent | Date |")
    lines.append("|-------------|-------|------|")
    lines.append("| *(none yet)* | | |")
    lines.append("")

    lines.append("## Directory Ownership\n")
    role_dirs = {}
    for a in agents:
        role = a.get("role", "general")
        slug = a.get("slug", slugify(a["name"]))
        role_dirs.setdefault(role, []).append(slug)
    for role, slugs in role_dirs.items():
        lines.append(f"- **{role}:** {', '.join(slugs)}")
    lines.append("")

    return "\n".join(lines)


def generate_contributing_md(draft: dict) -> str:
    """Generate CONTRIBUTING.md — commit conventions and branch strategy."""
    company = draft["company"]
    contributing = draft.get("contributing", {})

    prefix = company.get("issuePrefix", "ORG")
    branch = contributing.get("branchStrategy", "main")
    commit_fmt = contributing.get(
        "commitFormat", f"[agent-role]: description ({prefix}-XX)"
    )

    lines = [f"# Contributing to {company['name']}\n"]
    lines.append("## Commit Format\n")
    lines.append(f"```\n{commit_fmt}\n```\n")
    lines.append("## Branch Strategy\n")
    if branch == "main":
        lines.append("All work on `main`. No feature branches.\n")
    else:
        lines.append(
            "Use feature branches: `feature/{PREFIX}-{number}-short-desc`\n"
        )
    lines.append("## Rules\n")
    lines.append("1. Read PROJECT-INVENTORY.md before starting any task")
    lines.append("2. Do not recreate existing deliverables")
    lines.append("3. Update PROJECT-INVENTORY.md after completing work")
    lines.append("4. Follow the commit format above")
    lines.append("")

    return "\n".join(lines)


# --- .paperclip.yaml ---


def generate_paperclip_yaml(draft: dict) -> str:
    """Generate .paperclip.yaml matching the real Paperclip import schema."""
    agents = draft.get("agents", [])
    company = draft.get("company", {})
    budgets = draft.get("budgets", {})
    agent_allocations = budgets.get("agentAllocations", {})

    config: dict = {"schema": "paperclip/v1"}

    # Company section (brandColor)
    company_section: dict = {}
    if company.get("brandColor"):
        company_section["brandColor"] = company["brandColor"]
    if company_section:
        config["company"] = company_section

    # Agents section — role, budget, adapter, capabilities, permissions
    agents_section: dict = {}
    for agent in agents:
        slug = agent.get("slug", slugify(agent["name"]))
        entry: dict = {}

        if agent.get("role"):
            entry["role"] = agent["role"]

        budget = agent.get(
            "budgetMonthlyCents", agent_allocations.get(slug)
        )
        if budget:
            entry["budgetMonthlyCents"] = budget

        if agent.get("capabilities"):
            entry["capabilities"] = agent["capabilities"]

        if agent.get("permissions"):
            entry["permissions"] = agent["permissions"]

        adapter_type = agent.get("adapterType", "claude_local")
        entry["adapter"] = {"type": adapter_type}

        agents_section[slug] = entry

    if agents_section:
        config["agents"] = agents_section

    # Sidebar — agent ordering (CEO first, then managers, then workers)
    sidebar_agents = [
        a.get("slug", slugify(a["name"])) for a in agents
    ]
    config["sidebar"] = {"agents": sidebar_agents}

    # Projects in sidebar
    projects = draft.get("projects", [])
    if projects:
        config["sidebar"]["projects"] = [
            p.get("slug", slugify(p["name"])) for p in projects
        ]

    # Routines section — keyed by slug
    routines = draft.get("routines", [])
    if routines:
        routines_section: dict = {}
        for r in routines:
            r_slug = r.get("slug", slugify(r.get("title", "routine")))
            entry = {}
            if r.get("concurrencyPolicy"):
                entry["concurrencyPolicy"] = r["concurrencyPolicy"]
            if r.get("catchUpPolicy"):
                entry["catchUpPolicy"] = r["catchUpPolicy"]

            triggers = []
            cron = r.get("cronExpression", r.get("schedule"))
            if cron:
                trigger: dict = {
                    "kind": "schedule",
                    "cronExpression": cron,
                }
                if r.get("timezone"):
                    trigger["timezone"] = r["timezone"]
                triggers.append(trigger)
            if triggers:
                entry["triggers"] = triggers

            if r.get("assigneeAgent"):
                entry["assigneeAgentSlug"] = r["assigneeAgent"]

            routines_section[r_slug] = entry

        config["routines"] = routines_section

    # Projects section — keyed by slug
    if projects:
        projects_section: dict = {}
        for p in projects:
            p_slug = p.get("slug", slugify(p["name"]))
            entry = {}
            if p.get("leadAgent"):
                entry["leadAgentSlug"] = p["leadAgent"]
            if p.get("status"):
                entry["status"] = p["status"]
            projects_section[p_slug] = entry
        config["projects"] = projects_section

    return yaml.dump(
        config,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    )


# --- Agent files ---


def generate_agent_md(agent: dict) -> str:
    """Generate AGENTS.md with slim frontmatter + rich body."""
    frontmatter: dict = {
        "name": agent["name"],
        "title": agent.get("title", agent["name"]),
    }

    if agent.get("reportsTo"):
        frontmatter["reportsTo"] = agent["reportsTo"]

    if agent.get("skills"):
        frontmatter["skills"] = agent["skills"]

    body = agent.get(
        "instructions",
        f"## Instructions\n\nAgent instructions for {agent['name']}.",
    )

    fm_str = yaml.dump(
        frontmatter,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    )
    return f"---\n{fm_str}---\n\n{body}\n"


def generate_soul_md(agent: dict) -> str:
    """Generate SOUL.md from agent's soul content."""
    content = agent.get("soul", "")
    if not content:
        name = agent["name"]
        role = agent.get("role", "agent")
        content = (
            f"# {name} — Soul\n\n"
            f"I am the {role} of this company.\n\n"
            "## What I Believe In\n\n"
            "- Quality over speed\n"
            "- Verify before reporting\n"
        )
    return content + ("\n" if not content.endswith("\n") else "")


def generate_heartbeat_md(agent: dict) -> str:
    """Generate HEARTBEAT.md from agent's heartbeat content."""
    content = agent.get("heartbeat", "")
    if not content:
        name = agent["name"]
        content = (
            f"# {name} — Heartbeat\n\n"
            "## Execution Checklist\n\n"
            "1. Check assignments\n"
            "2. Work on highest priority task\n"
            "3. Self-check deliverable\n"
            "4. Mark complete\n"
        )
    return content + ("\n" if not content.endswith("\n") else "")


def generate_tools_md(agent: dict) -> str:
    """Generate TOOLS.md from agent's tools content."""
    content = agent.get("tools", "")
    if not content:
        name = agent["name"]
        content = (
            f"# {name} — Tools\n\n"
            "## Available Tools\n\n"
            "*(Configure tools for this agent)*\n"
        )
    return content + ("\n" if not content.endswith("\n") else "")


# --- Project files ---


def generate_project_md(project: dict) -> str:
    """Generate PROJECT.md for a project directory."""
    frontmatter: dict = {
        "name": project["name"],
        "status": project.get("status", "planned"),
    }

    if project.get("description"):
        frontmatter["description"] = project["description"]
    if project.get("leadAgent"):
        frontmatter["leadAgentSlug"] = project["leadAgent"]

    body = project.get("description", f"Project: {project['name']}")

    fm_str = yaml.dump(
        frontmatter,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
    )
    return f"---\n{fm_str}---\n\n# {project['name']}\n\n{body}\n"


# --- Main assembly ---


def assemble(draft_path: str, output_dir: str, verbose: bool = False) -> None:
    """Assemble the complete company package."""
    draft = load_draft(draft_path)
    out = Path(output_dir)

    out.mkdir(parents=True, exist_ok=True)
    (out / "agents").mkdir(exist_ok=True)

    # --- COMPANY.md ---
    company_md = generate_company_md(draft)
    (out / "COMPANY.md").write_text(company_md, encoding="utf-8")
    if verbose:
        print("  Created COMPANY.md", file=sys.stderr)

    # --- .paperclip.yaml ---
    pc_yaml = generate_paperclip_yaml(draft)
    (out / ".paperclip.yaml").write_text(pc_yaml, encoding="utf-8")
    if verbose:
        print("  Created .paperclip.yaml", file=sys.stderr)

    # --- PROJECT-INVENTORY.md ---
    inventory_md = generate_project_inventory_md(draft)
    (out / "PROJECT-INVENTORY.md").write_text(inventory_md, encoding="utf-8")
    if verbose:
        print("  Created PROJECT-INVENTORY.md", file=sys.stderr)

    # --- CONTRIBUTING.md ---
    contributing_md = generate_contributing_md(draft)
    (out / "CONTRIBUTING.md").write_text(contributing_md, encoding="utf-8")
    if verbose:
        print("  Created CONTRIBUTING.md", file=sys.stderr)

    # --- Agent files ---
    for agent in draft.get("agents", []):
        slug = agent.get("slug", slugify(agent["name"]))
        role = agent.get("role", "general")
        agent_dir = out / "agents" / slug
        agent_dir.mkdir(parents=True, exist_ok=True)

        # AGENTS.md — always created
        agent_md = generate_agent_md(agent)
        (agent_dir / "AGENTS.md").write_text(agent_md, encoding="utf-8")

        # SOUL.md — CEO essential, managers recommended, others if provided
        if role == "ceo" or agent.get("soul"):
            soul_md = generate_soul_md(agent)
            (agent_dir / "SOUL.md").write_text(soul_md, encoding="utf-8")

        # HEARTBEAT.md — CEO essential, all workers get one
        heartbeat_md = generate_heartbeat_md(agent)
        (agent_dir / "HEARTBEAT.md").write_text(
            heartbeat_md, encoding="utf-8"
        )

        # TOOLS.md — CEO essential, others if provided
        if role == "ceo" or agent.get("tools"):
            tools_md = generate_tools_md(agent)
            (agent_dir / "TOOLS.md").write_text(tools_md, encoding="utf-8")

        # memory/ directory
        memory_dir = agent_dir / "memory"
        memory_dir.mkdir(exist_ok=True)

        if verbose:
            print(f"  Created agents/{slug}/", file=sys.stderr)

    # --- Projects ---
    projects = draft.get("projects", [])
    if projects:
        (out / "projects").mkdir(exist_ok=True)
        for project in projects:
            proj_slug = project.get("slug", slugify(project["name"]))
            proj_dir = out / "projects" / proj_slug
            proj_dir.mkdir(parents=True, exist_ok=True)
            project_md = generate_project_md(project)
            (proj_dir / "PROJECT.md").write_text(
                project_md, encoding="utf-8"
            )
            if verbose:
                print(
                    f"  Created projects/{proj_slug}/PROJECT.md",
                    file=sys.stderr,
                )

    # --- Skills directory ---
    skills_dir = out / "skills"
    skills_dir.mkdir(exist_ok=True)
    # Collect all referenced skills from agents
    all_skills = set()
    for agent in draft.get("agents", []):
        for skill in agent.get("skills", []):
            all_skills.add(skill)
    if all_skills:
        readme_lines = [
            "# Skills\n",
            "Referenced skills in this company package:\n",
        ]
        for skill in sorted(all_skills):
            readme_lines.append(f"- `{skill}`")
        readme_lines.append(
            "\nTo use these skills, ensure the skill files are "
            "installed in your Paperclip instance or included in "
            "this package under `skills/company/<prefix>/<slug>/`."
        )
        readme_lines.append("")
        (skills_dir / "README.md").write_text(
            "\n".join(readme_lines), encoding="utf-8"
        )
    if verbose:
        print("  Created skills/", file=sys.stderr)

    # --- Summary ---
    agent_slugs = [
        a.get("slug", slugify(a["name"])) for a in draft.get("agents", [])
    ]
    summary = {
        "status": "success",
        "outputDir": str(out),
        "files": {
            "COMPANY.md": True,
            ".paperclip.yaml": True,
            "PROJECT-INVENTORY.md": True,
            "CONTRIBUTING.md": True,
            "agents": agent_slugs,
            "projects": [
                p.get("slug", slugify(p["name"])) for p in projects
            ],
            "skills": sorted(all_skills),
        },
        "agentCount": len(draft.get("agents", [])),
        "goalCount": len(draft.get("goals", [])),
        "projectCount": len(projects),
        "routineCount": len(draft.get("routines", [])),
    }

    print(json.dumps(summary, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Assemble a Paperclip company package from a draft JSON file."
    )
    parser.add_argument("draft", help="Path to the draft JSON file")
    parser.add_argument(
        "output", help="Output directory for the company package"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Print progress to stderr"
    )

    args = parser.parse_args()
    assemble(args.draft, args.output, args.verbose)


if __name__ == "__main__":
    main()
