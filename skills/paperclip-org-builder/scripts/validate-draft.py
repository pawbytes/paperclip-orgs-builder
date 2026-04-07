#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
Validates a Paperclip org draft JSON at any stage transition.

Usage:
    uv run validate-draft.py <draft-json> [--stage N]

Progressive checks based on currentStage (or --stage override):
  Always: JSON structure, currentStage field
  Stage ≥1: vision section present
  Stage ≥2: company section present
  Stage ≥3: Org chart integrity (CEO, orphans, cycles, role enum)
  Stage ≥4: Agent config completeness
  Stage ≥6: Goal/project cross-refs against agent roster
  Stage ≥7: Budget arithmetic (allocations ≤ total, non-negative)
  Stage ≥8: Cron syntax and routine cross-refs

Exit codes: 0=valid, 1=issues found, 2=error
"""

import argparse
import json
import re
import sys

# Canonical roles — see references/paperclip-domain.md Agent Fields
VALID_ROLES = {"ceo", "cto", "cmo", "cfo", "engineer", "designer", "pm", "qa", "devops", "researcher", "general"}


def validate_draft(draft_path: str, stage_override: int | None = None) -> dict:
    """Validate the draft JSON with progressive checks."""
    issues: list[str] = []
    warnings: list[str] = []

    try:
        with open(draft_path, "r", encoding="utf-8") as f:
            draft = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError, OSError) as e:
        return {"status": "error", "message": f"Cannot read draft: {e}"}

    if not isinstance(draft, dict):
        return {"status": "error", "message": "Draft must be a JSON object"}

    stage = (
        stage_override
        if stage_override is not None
        else draft.get("currentStage", 0)
    )
    if not isinstance(stage, int) or stage < 0:
        issues.append("currentStage must be a non-negative integer")
        stage = 0

    # === Always: basic structure ===
    if "currentStage" not in draft and stage_override is None:
        issues.append("Missing 'currentStage' field")

    # === Stage ≥1: vision ===
    if stage >= 1:
        vision = draft.get("vision")
        if not isinstance(vision, dict):
            issues.append("Stage 1+: Missing 'vision' object")
        elif not vision.get("mission"):
            issues.append("Stage 1+: vision.mission is empty or missing")

    # === Stage ≥2: company ===
    if stage >= 2:
        company = draft.get("company")
        if not isinstance(company, dict):
            issues.append("Stage 2+: Missing 'company' object")
        elif not company.get("name"):
            issues.append("Stage 2+: company.name is empty or missing")

    # === Stage ≥3: org chart integrity ===
    agent_slugs: set[str] = set()
    if stage >= 3:
        agents = draft.get("agents", [])
        if not isinstance(agents, list) or len(agents) == 0:
            issues.append("Stage 3+: 'agents' array is missing or empty")
        else:
            ceo_count = 0
            reports_to_map: dict[str, str] = {}

            for i, agent in enumerate(agents):
                if not isinstance(agent, dict):
                    issues.append(f"Stage 3+: agents[{i}] is not an object")
                    continue

                slug = agent.get("slug", agent.get("name", f"agent-{i}"))
                if slug in agent_slugs:
                    issues.append(f"Stage 3+: Duplicate agent slug '{slug}'")
                agent_slugs.add(slug)

                role = agent.get("role", "")
                if role and role not in VALID_ROLES:
                    issues.append(
                        f"Stage 3+: Agent '{slug}' has invalid role '{role}' "
                        f"(valid: {', '.join(sorted(VALID_ROLES))})"
                    )

                if role == "ceo":
                    ceo_count += 1
                    if agent.get("reportsTo"):
                        issues.append(
                            f"Stage 3+: CEO '{slug}' should not have reportsTo"
                        )
                else:
                    rt = agent.get("reportsTo")
                    if rt:
                        reports_to_map[slug] = rt
                    elif role:
                        warnings.append(
                            f"Stage 3+: Non-CEO agent '{slug}' has no reportsTo"
                        )

            if ceo_count == 0:
                issues.append(
                    "Stage 3+: No CEO agent found — exactly one required"
                )
            elif ceo_count > 1:
                issues.append(
                    f"Stage 3+: Found {ceo_count} CEO agents — only one allowed"
                )

            for slug, rt in reports_to_map.items():
                if rt not in agent_slugs:
                    issues.append(
                        f"Stage 3+: Agent '{slug}' reportsTo '{rt}' "
                        f"which doesn't exist"
                    )

            cycle = detect_cycle(reports_to_map)
            if cycle:
                issues.append(
                    f"Stage 3+: Circular reporting chain: "
                    f"{' → '.join(cycle)}"
                )

    # === Stage ≥4: agent config completeness ===
    if stage >= 4:
        for agent in draft.get("agents", []):
            if not isinstance(agent, dict):
                continue
            slug = agent.get("slug", agent.get("name", "?"))
            if not agent.get("instructions"):
                warnings.append(
                    f"Stage 4+: Agent '{slug}' has no instructions"
                )

    # === Stage ≥6: goal/project cross-refs ===
    if stage >= 6:
        if not agent_slugs:
            agent_slugs = {
                a.get("slug", a.get("name", ""))
                for a in draft.get("agents", [])
                if isinstance(a, dict)
            }

        for goal in draft.get("goals", []):
            if not isinstance(goal, dict):
                continue
            owner = goal.get("ownerAgentId") or goal.get("ownerAgent")
            if owner and owner not in agent_slugs:
                issues.append(
                    f"Stage 6+: Goal '{goal.get('title', '?')}' references "
                    f"unknown agent '{owner}'"
                )

        for project in draft.get("projects", []):
            if not isinstance(project, dict):
                continue
            lead = project.get("leadAgentId") or project.get("leadAgent")
            if lead and lead not in agent_slugs:
                issues.append(
                    f"Stage 6+: Project '{project.get('name', '?')}' "
                    f"references unknown lead agent '{lead}'"
                )

    # === Stage ≥7: budget arithmetic ===
    if stage >= 7:
        budgets = draft.get("budgets", {})
        if isinstance(budgets, dict):
            total = budgets.get("companyTotal", 0)
            allocations = budgets.get("agentAllocations", {})

            if isinstance(total, (int, float)) and total < 0:
                issues.append("Stage 7+: companyTotal budget is negative")

            if isinstance(allocations, dict):
                alloc_sum = sum(
                    v
                    for v in allocations.values()
                    if isinstance(v, (int, float))
                )
                if (
                    isinstance(total, (int, float))
                    and total > 0
                    and alloc_sum > total
                ):
                    issues.append(
                        f"Stage 7+: Agent allocations ({alloc_sum}) exceed "
                        f"company total ({total})"
                    )

                if not agent_slugs:
                    agent_slugs = {
                        a.get("slug", a.get("name", ""))
                        for a in draft.get("agents", [])
                        if isinstance(a, dict)
                    }
                for slug in allocations:
                    if slug not in agent_slugs:
                        issues.append(
                            f"Stage 7+: Budget allocation for "
                            f"unknown agent '{slug}'"
                        )

                for slug, amount in allocations.items():
                    if isinstance(amount, (int, float)) and amount < 0:
                        issues.append(
                            f"Stage 7+: Negative budget for agent '{slug}'"
                        )

    # === Stage ≥8: cron syntax and routine cross-refs ===
    if stage >= 8:
        if not agent_slugs:
            agent_slugs = {
                a.get("slug", a.get("name", ""))
                for a in draft.get("agents", [])
                if isinstance(a, dict)
            }

        for routine in draft.get("routines", []):
            if not isinstance(routine, dict):
                continue
            title = routine.get("title", "?")
            cron = routine.get("cronExpression") or routine.get("schedule")
            if cron:
                cron_err = validate_cron(cron)
                if cron_err:
                    issues.append(
                        f"Stage 8+: Routine '{title}' cron error: {cron_err}"
                    )

            assignee = routine.get("assigneeAgent") or routine.get(
                "assigneeAgentId"
            )
            if assignee and assignee not in agent_slugs:
                issues.append(
                    f"Stage 8+: Routine '{title}' references "
                    f"unknown agent '{assignee}'"
                )

    return {
        "status": "valid" if not issues else "invalid",
        "draftPath": draft_path,
        "currentStage": stage,
        "issues": issues,
        "warnings": warnings,
    }


def detect_cycle(reports_to: dict[str, str]) -> list[str] | None:
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


def validate_cron(expr: str) -> str | None:
    """Basic cron expression validation (5 fields). Returns error or None."""
    fields = expr.strip().split()
    if len(fields) != 5:
        return f"Expected 5 fields, got {len(fields)}"

    field_specs = [
        ("minute", 0, 59),
        ("hour", 0, 23),
        ("day-of-month", 1, 31),
        ("month", 1, 12),
        ("day-of-week", 0, 7),
    ]

    cron_token = re.compile(r"^(\*|\d+)(-\d+)?(/\d+)?$")

    for field, (name, lo, hi) in zip(fields, field_specs):
        for part in field.split(","):
            m = cron_token.match(part)
            if not m:
                return f"Invalid {name} token: '{part}'"
            base = m.group(1)
            if base != "*":
                val = int(base)
                if val < lo or val > hi:
                    return f"{name} value {val} out of range ({lo}-{hi})"
            if m.group(2):
                end = int(m.group(2)[1:])
                if end < lo or end > hi:
                    return f"{name} range end {end} out of range ({lo}-{hi})"
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Validate a Paperclip org draft JSON at any stage."
    )
    parser.add_argument("draft", help="Path to the draft JSON file")
    parser.add_argument(
        "--stage",
        type=int,
        default=None,
        help="Override the stage for validation (default: read from draft)",
    )

    args = parser.parse_args()
    result = validate_draft(args.draft, args.stage)

    print(json.dumps(result, indent=2))

    if result["status"] == "error":
        sys.exit(2)
    elif result["status"] == "invalid":
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
