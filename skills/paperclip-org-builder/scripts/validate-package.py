#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml>=6.0"]
# ///
"""
Validates a Paperclip company package structure.

Usage:
    uv run validate-package.py <package-dir>

Checks: required files, .paperclip.yaml schema, agent files (AGENTS.md,
SOUL.md, HEARTBEAT.md, TOOLS.md), cross-references, hierarchy consistency.

Exit codes: 0=valid, 1=issues found, 2=error
"""

import argparse
import json
import sys
from pathlib import Path

import yaml

# Canonical roles — see references/paperclip-domain.md Agent Fields
VALID_ROLES = {"ceo", "cto", "cmo", "cfo", "engineer", "designer", "pm", "qa", "devops", "researcher", "general"}

VALID_ADAPTER_TYPES = {
    "process", "http", "claude_local", "codex_local", "gemini_local",
    "opencode_local", "pi_local", "cursor", "openclaw_gateway", "hermes_local",
}


def extract_frontmatter(content: str) -> dict | None:
    """Extract YAML frontmatter from markdown content."""
    if not content.startswith("---"):
        return None
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        return yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return None


def validate(package_dir: str, verbose: bool = False) -> dict:
    """Validate a Paperclip company package."""
    pkg = Path(package_dir)
    issues = []
    warnings = []

    if not pkg.is_dir():
        return {
            "status": "error",
            "message": f"Package directory not found: {package_dir}",
        }

    company_md = pkg / "COMPANY.md"
    paperclip_yaml = pkg / ".paperclip.yaml"
    agents_dir = pkg / "agents"

    if not company_md.exists():
        issues.append("Missing required file: COMPANY.md")
    if not paperclip_yaml.exists():
        issues.append("Missing required file: .paperclip.yaml")
    if not agents_dir.exists():
        issues.append("Missing required directory: agents/")

    # Validate COMPANY.md frontmatter (slim: name, description, schema, slug)
    if company_md.exists():
        content = company_md.read_text(encoding="utf-8")
        company_fm = extract_frontmatter(content)
        if company_fm is None:
            issues.append("COMPANY.md: Invalid or missing YAML frontmatter")
        else:
            for field in ["schema", "slug", "name"]:
                if field not in company_fm:
                    issues.append(
                        f"COMPANY.md: Missing required field '{field}'"
                    )
            if company_fm.get("schema") != "agentcompanies/v1":
                warnings.append(
                    f"COMPANY.md: Expected schema 'agentcompanies/v1', "
                    f"got '{company_fm.get('schema')}'"
                )

    # Validate .paperclip.yaml
    pc_data: dict = {}
    pc_agents: dict = {}
    if paperclip_yaml.exists():
        try:
            pc_data = yaml.safe_load(
                paperclip_yaml.read_text(encoding="utf-8")
            )
            if not isinstance(pc_data, dict):
                issues.append(".paperclip.yaml: Expected a YAML mapping")
                pc_data = {}
            else:
                if pc_data.get("schema") != "paperclip/v1":
                    warnings.append(
                        f".paperclip.yaml: Expected schema 'paperclip/v1', "
                        f"got '{pc_data.get('schema')}'"
                    )
                pc_agents = pc_data.get("agents", {})
                if not isinstance(pc_agents, dict):
                    issues.append(
                        ".paperclip.yaml: 'agents' should be a mapping"
                    )
                    pc_agents = {}

                # Validate agent entries in yaml
                for slug, agent_cfg in pc_agents.items():
                    if not isinstance(agent_cfg, dict):
                        issues.append(
                            f".paperclip.yaml: agents.{slug} should be a mapping"
                        )
                        continue
                    role = agent_cfg.get("role", "")
                    if role and role not in VALID_ROLES:
                        issues.append(
                            f".paperclip.yaml: agents.{slug} has invalid role "
                            f"'{role}' (expected: {', '.join(sorted(VALID_ROLES))})"
                        )
                    adapter = agent_cfg.get("adapter", {})
                    if isinstance(adapter, dict) and adapter.get("type"):
                        if adapter["type"] not in VALID_ADAPTER_TYPES:
                            warnings.append(
                                f".paperclip.yaml: agents.{slug} has unknown "
                                f"adapter type '{adapter['type']}'"
                            )

                # Validate sidebar
                sidebar = pc_data.get("sidebar", {})
                if isinstance(sidebar, dict):
                    sidebar_agents = sidebar.get("agents", [])
                    if isinstance(sidebar_agents, list):
                        for s in sidebar_agents:
                            if s not in pc_agents:
                                warnings.append(
                                    f".paperclip.yaml: sidebar agent '{s}' "
                                    f"not in agents section"
                                )

                # Validate routines
                routines = pc_data.get("routines", {})
                if isinstance(routines, dict):
                    for r_slug, r_cfg in routines.items():
                        if not isinstance(r_cfg, dict):
                            continue
                        triggers = r_cfg.get("triggers", [])
                        if isinstance(triggers, list):
                            for t in triggers:
                                if isinstance(t, dict) and t.get("kind") == "schedule":
                                    if not t.get("cronExpression"):
                                        warnings.append(
                                            f".paperclip.yaml: routine '{r_slug}' "
                                            f"schedule trigger missing cronExpression"
                                        )

        except yaml.YAMLError as e:
            issues.append(f".paperclip.yaml: Invalid YAML — {e}")

    # Validate agents
    agent_slugs = set()
    agent_reports_to = {}
    ceo_count = 0

    if agents_dir.exists():
        for agent_dir in sorted(agents_dir.iterdir()):
            if not agent_dir.is_dir():
                continue

            agent_md = agent_dir / "AGENTS.md"
            if not agent_md.exists():
                issues.append(
                    f"agents/{agent_dir.name}/: Missing AGENTS.md"
                )
                continue

            content = agent_md.read_text(encoding="utf-8")
            fm = extract_frontmatter(content)
            if fm is None:
                issues.append(
                    f"agents/{agent_dir.name}/AGENTS.md: Invalid or missing YAML frontmatter"
                )
                continue

            slug = agent_dir.name
            agent_slugs.add(slug)

            # Required AGENTS.md fields: name
            if "name" not in fm:
                issues.append(
                    f"agents/{slug}/AGENTS.md: Missing required field 'name'"
                )

            # Role comes from .paperclip.yaml, not AGENTS.md
            role = ""
            if slug in pc_agents and isinstance(pc_agents[slug], dict):
                role = pc_agents[slug].get("role", "")

            if role == "ceo":
                ceo_count += 1
                if fm.get("reportsTo"):
                    issues.append(
                        f"agents/{slug}/AGENTS.md: CEO should not have reportsTo"
                    )
                # CEO should have SOUL.md, HEARTBEAT.md, TOOLS.md
                if not (agent_dir / "SOUL.md").exists():
                    warnings.append(
                        f"agents/{slug}/: CEO missing SOUL.md"
                    )
                if not (agent_dir / "HEARTBEAT.md").exists():
                    warnings.append(
                        f"agents/{slug}/: CEO missing HEARTBEAT.md"
                    )
                if not (agent_dir / "TOOLS.md").exists():
                    warnings.append(
                        f"agents/{slug}/: CEO missing TOOLS.md"
                    )
            else:
                reports_to = fm.get("reportsTo")
                if reports_to:
                    agent_reports_to[slug] = reports_to
                else:
                    warnings.append(
                        f"agents/{slug}/AGENTS.md: Non-CEO agent missing reportsTo"
                    )
                # All agents should have HEARTBEAT.md
                if not (agent_dir / "HEARTBEAT.md").exists():
                    warnings.append(
                        f"agents/{slug}/: Missing HEARTBEAT.md"
                    )

            if verbose:
                print(
                    f"  Validated agents/{slug}/", file=sys.stderr
                )

    # Cross-reference: yaml agents vs filesystem agents
    for slug in pc_agents:
        if slug not in agent_slugs and agents_dir.exists():
            warnings.append(
                f".paperclip.yaml: agent '{slug}' configured but no "
                f"agents/{slug}/ directory found"
            )

    # CEO check
    if ceo_count == 0 and agents_dir.exists():
        issues.append(
            "No CEO agent found — every company needs exactly one CEO"
        )
    elif ceo_count > 1:
        issues.append(
            f"Found {ceo_count} CEO agents — only one is allowed"
        )

    # reportsTo cross-ref
    for slug, reports_to in agent_reports_to.items():
        if reports_to not in agent_slugs:
            issues.append(
                f"agents/{slug}/AGENTS.md: reportsTo '{reports_to}' "
                f"does not match any agent slug"
            )

    # Cycle detection
    cycle = _detect_cycle(agent_reports_to)
    if cycle:
        issues.append(
            f"Circular reporting chain detected: {' → '.join(cycle)}"
        )

    # Cross-ref: project leadAgentSlug
    projects_dir = pkg / "projects"
    if projects_dir.exists():
        for proj_dir in sorted(projects_dir.iterdir()):
            if not proj_dir.is_dir():
                continue
            proj_md = proj_dir / "PROJECT.md"
            if proj_md.exists():
                proj_content = proj_md.read_text(encoding="utf-8")
                proj_fm = extract_frontmatter(proj_content)
                if proj_fm:
                    lead = proj_fm.get("leadAgentSlug", proj_fm.get("leadAgent"))
                    if lead and lead not in agent_slugs:
                        warnings.append(
                            f"projects/{proj_dir.name}/PROJECT.md: "
                            f"leadAgentSlug '{lead}' does not match any agent"
                        )

    # Cross-ref: .paperclip.yaml projects
    if isinstance(pc_data.get("projects"), dict):
        for p_slug, p_cfg in pc_data["projects"].items():
            if isinstance(p_cfg, dict):
                lead = p_cfg.get("leadAgentSlug")
                if lead and lead not in agent_slugs:
                    warnings.append(
                        f".paperclip.yaml: project '{p_slug}' "
                        f"leadAgentSlug '{lead}' does not match any agent"
                    )

    # Cross-ref: routine assigneeAgentSlug
    if isinstance(pc_data.get("routines"), dict):
        for r_slug, r_cfg in pc_data["routines"].items():
            if isinstance(r_cfg, dict):
                assignee = r_cfg.get("assigneeAgentSlug")
                if assignee and assignee not in agent_slugs:
                    warnings.append(
                        f".paperclip.yaml: routine '{r_slug}' "
                        f"assigneeAgentSlug '{assignee}' does not match any agent"
                    )

    # Check for company-level files
    if not (pkg / "PROJECT-INVENTORY.md").exists():
        warnings.append("Missing recommended file: PROJECT-INVENTORY.md")
    if not (pkg / "CONTRIBUTING.md").exists():
        warnings.append("Missing recommended file: CONTRIBUTING.md")

    return {
        "status": "valid" if not issues else "invalid",
        "packageDir": str(pkg),
        "agentCount": len(agent_slugs),
        "issues": issues,
        "warnings": warnings,
    }


def _detect_cycle(reports_to: dict[str, str]) -> list[str] | None:
    """Detect cycles in the reporting hierarchy. Returns cycle path or None."""
    visited: set[str] = set()
    for start in reports_to:
        if start in visited:
            continue
        path: list[str] = []
        path_set: set[str] = set()
        current = start
        while current in reports_to and current not in visited:
            if current in path_set:
                cycle_start = path.index(current)
                return path[cycle_start:] + [current]
            path.append(current)
            path_set.add(current)
            current = reports_to[current]
        visited.update(path_set)
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Validate a Paperclip company package structure."
    )
    parser.add_argument(
        "package", help="Path to the company package directory"
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Print progress to stderr"
    )

    args = parser.parse_args()
    result = validate(args.package, args.verbose)

    print(json.dumps(result, indent=2))

    if result["status"] == "error":
        sys.exit(2)
    elif result["status"] == "invalid":
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
