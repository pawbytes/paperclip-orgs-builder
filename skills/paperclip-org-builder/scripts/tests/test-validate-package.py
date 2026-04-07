#!/usr/bin/env python3
"""Tests for validate-package.py"""

import json
import sys
import tempfile
from pathlib import Path

from importlib.util import spec_from_file_location, module_from_spec

_spec = spec_from_file_location(
    "validate_package",
    Path(__file__).resolve().parent.parent / "validate-package.py",
)
mod = module_from_spec(_spec)
_spec.loader.exec_module(mod)

extract_frontmatter = mod.extract_frontmatter
validate = mod.validate


def make_package(tmpdir, agents=None, company_fm=None, yaml_agents=None):
    """Create a minimal valid package for testing.

    Args:
        agents: list of agent dicts with slug, name, reportsTo, skills
        company_fm: COMPANY.md frontmatter override
        yaml_agents: dict of agent configs for .paperclip.yaml
    """
    pkg = Path(tmpdir) / "test-company"
    pkg.mkdir(parents=True, exist_ok=True)

    if company_fm is None:
        company_fm = {
            "schema": "agentcompanies/v1",
            "slug": "test-company",
            "name": "Test Company",
        }

    import yaml

    fm_str = yaml.dump(company_fm, default_flow_style=False, sort_keys=False)
    (pkg / "COMPANY.md").write_text(f"---\n{fm_str}---\n\n# Test\n")

    if agents is None:
        agents = [
            {"slug": "ceo-agent", "name": "CEO"},
        ]

    if yaml_agents is None:
        # Default: build from agent list
        yaml_agents = {}
        for agent in agents:
            slug = agent["slug"]
            yaml_agents[slug] = {
                "role": agent.get("role", "general"),
                "adapter": {"type": "claude_local"},
            }

    # Write .paperclip.yaml
    pc_yaml = {
        "schema": "paperclip/v1",
        "agents": yaml_agents,
        "sidebar": {"agents": list(yaml_agents.keys())},
    }
    (pkg / ".paperclip.yaml").write_text(
        yaml.dump(pc_yaml, default_flow_style=False, sort_keys=False)
    )

    agents_dir = pkg / "agents"
    agents_dir.mkdir(exist_ok=True)

    for agent in agents:
        agent_dir = agents_dir / agent["slug"]
        agent_dir.mkdir(parents=True, exist_ok=True)

        fm = {"name": agent["name"]}
        if agent.get("title"):
            fm["title"] = agent["title"]
        if agent.get("reportsTo"):
            fm["reportsTo"] = agent["reportsTo"]
        if agent.get("skills"):
            fm["skills"] = agent["skills"]

        fm_str = yaml.dump(fm, default_flow_style=False, sort_keys=False)
        (agent_dir / "AGENTS.md").write_text(
            f"---\n{fm_str}---\n\n## Instructions\n"
        )

    return str(pkg)


def test_extract_frontmatter_valid():
    content = "---\nname: Test\ntitle: CEO\n---\n\n# Body"
    fm = extract_frontmatter(content)
    assert fm is not None
    assert fm["name"] == "Test"
    assert fm["title"] == "CEO"
    print("PASS: test_extract_frontmatter_valid")


def test_extract_frontmatter_missing():
    assert extract_frontmatter("No frontmatter here") is None
    assert extract_frontmatter("---\nonly one separator") is None
    print("PASS: test_extract_frontmatter_missing")


def test_valid_package():
    with tempfile.TemporaryDirectory() as tmpdir:
        agents = [{"slug": "ceo-agent", "name": "CEO", "role": "ceo"}]
        yaml_agents = {
            "ceo-agent": {"role": "ceo", "adapter": {"type": "claude_local"}},
        }
        pkg_path = make_package(tmpdir, agents=agents, yaml_agents=yaml_agents)
        result = validate(pkg_path)
        assert result["status"] == "valid", result["issues"]
        assert result["agentCount"] == 1
        assert len(result["issues"]) == 0
        print("PASS: test_valid_package")


def test_missing_company_md():
    with tempfile.TemporaryDirectory() as tmpdir:
        agents = [{"slug": "ceo-agent", "name": "CEO", "role": "ceo"}]
        yaml_agents = {"ceo-agent": {"role": "ceo", "adapter": {"type": "claude_local"}}}
        pkg_path = make_package(tmpdir, agents=agents, yaml_agents=yaml_agents)
        Path(pkg_path, "COMPANY.md").unlink()
        result = validate(pkg_path)
        assert result["status"] == "invalid"
        assert any("COMPANY.md" in i for i in result["issues"])
        print("PASS: test_missing_company_md")


def test_no_ceo():
    with tempfile.TemporaryDirectory() as tmpdir:
        agents = [{"slug": "worker", "name": "Worker", "role": "engineer"}]
        yaml_agents = {
            "worker": {"role": "engineer", "adapter": {"type": "claude_local"}},
        }
        pkg_path = make_package(tmpdir, agents=agents, yaml_agents=yaml_agents)
        result = validate(pkg_path)
        assert any("No CEO" in i for i in result["issues"])
        print("PASS: test_no_ceo")


def test_multiple_ceos():
    with tempfile.TemporaryDirectory() as tmpdir:
        agents = [
            {"slug": "ceo-one", "name": "CEO One", "role": "ceo"},
            {"slug": "ceo-two", "name": "CEO Two", "role": "ceo"},
        ]
        yaml_agents = {
            "ceo-one": {"role": "ceo", "adapter": {"type": "claude_local"}},
            "ceo-two": {"role": "ceo", "adapter": {"type": "claude_local"}},
        }
        pkg_path = make_package(tmpdir, agents=agents, yaml_agents=yaml_agents)
        result = validate(pkg_path)
        assert any("2 CEO" in i for i in result["issues"])
        print("PASS: test_multiple_ceos")


def test_invalid_reports_to():
    with tempfile.TemporaryDirectory() as tmpdir:
        agents = [
            {"slug": "ceo-agent", "name": "CEO", "role": "ceo"},
            {
                "slug": "dev",
                "name": "Dev",
                "role": "engineer",
                "reportsTo": "nonexistent",
            },
        ]
        yaml_agents = {
            "ceo-agent": {"role": "ceo", "adapter": {"type": "claude_local"}},
            "dev": {"role": "engineer", "adapter": {"type": "claude_local"}},
        }
        pkg_path = make_package(tmpdir, agents=agents, yaml_agents=yaml_agents)
        result = validate(pkg_path)
        assert any("nonexistent" in i for i in result["issues"])
        print("PASS: test_invalid_reports_to")


def test_nonexistent_dir():
    result = validate("/nonexistent/path/xyz")
    assert result["status"] == "error"
    print("PASS: test_nonexistent_dir")


def test_cycle_detection():
    """Two agents reporting to each other should be caught."""
    with tempfile.TemporaryDirectory() as tmpdir:
        agents = [
            {"slug": "ceo-agent", "name": "CEO", "role": "ceo"},
            {
                "slug": "alice",
                "name": "Alice",
                "role": "cto",
                "reportsTo": "bob",
            },
            {
                "slug": "bob",
                "name": "Bob",
                "role": "engineer",
                "reportsTo": "alice",
            },
        ]
        yaml_agents = {
            "ceo-agent": {"role": "ceo", "adapter": {"type": "claude_local"}},
            "alice": {"role": "cto", "adapter": {"type": "claude_local"}},
            "bob": {"role": "engineer", "adapter": {"type": "claude_local"}},
        }
        pkg_path = make_package(tmpdir, agents=agents, yaml_agents=yaml_agents)
        result = validate(pkg_path)
        assert any("Circular" in i for i in result["issues"])
        print("PASS: test_cycle_detection")


def test_invalid_role_in_yaml():
    """Invalid role in .paperclip.yaml should be flagged."""
    with tempfile.TemporaryDirectory() as tmpdir:
        agents = [{"slug": "ceo-agent", "name": "CEO", "role": "ceo"}]
        yaml_agents = {
            "ceo-agent": {"role": "ceo", "adapter": {"type": "claude_local"}},
            "bad-agent": {"role": "wizard", "adapter": {"type": "claude_local"}},
        }
        pkg_path = make_package(tmpdir, agents=agents, yaml_agents=yaml_agents)
        result = validate(pkg_path)
        assert any("wizard" in i for i in result["issues"])
        print("PASS: test_invalid_role_in_yaml")


def test_project_unknown_lead():
    """Project referencing a nonexistent leadAgentSlug should warn."""
    with tempfile.TemporaryDirectory() as tmpdir:
        agents = [{"slug": "ceo-agent", "name": "CEO", "role": "ceo"}]
        yaml_agents = {"ceo-agent": {"role": "ceo", "adapter": {"type": "claude_local"}}}
        pkg_path = make_package(tmpdir, agents=agents, yaml_agents=yaml_agents)

        import yaml
        proj_dir = Path(pkg_path) / "projects" / "web-app"
        proj_dir.mkdir(parents=True)
        fm = {"name": "Web App", "leadAgentSlug": "ghost"}
        fm_str = yaml.dump(fm, default_flow_style=False, sort_keys=False)
        (proj_dir / "PROJECT.md").write_text(
            f"---\n{fm_str}---\n\n# Web App\n"
        )
        result = validate(pkg_path)
        assert any("ghost" in w for w in result["warnings"])
        print("PASS: test_project_unknown_lead")


def test_routine_unknown_assignee():
    """Routine referencing a nonexistent assigneeAgentSlug should warn."""
    with tempfile.TemporaryDirectory() as tmpdir:
        agents = [{"slug": "ceo-agent", "name": "CEO", "role": "ceo"}]
        yaml_agents = {"ceo-agent": {"role": "ceo", "adapter": {"type": "claude_local"}}}
        pkg_path = make_package(tmpdir, agents=agents, yaml_agents=yaml_agents)
        import yaml

        pc_data = {
            "schema": "paperclip/v1",
            "agents": yaml_agents,
            "sidebar": {"agents": ["ceo-agent"]},
            "routines": {
                "standup": {
                    "assigneeAgentSlug": "phantom",
                    "triggers": [{"kind": "schedule", "cronExpression": "0 9 * * 1-5"}],
                }
            },
        }
        (Path(pkg_path) / ".paperclip.yaml").write_text(
            yaml.dump(pc_data, default_flow_style=False)
        )
        result = validate(pkg_path)
        assert any("phantom" in w for w in result["warnings"])
        print("PASS: test_routine_unknown_assignee")


def test_ceo_missing_files_warning():
    """CEO without SOUL.md, HEARTBEAT.md, TOOLS.md should warn."""
    with tempfile.TemporaryDirectory() as tmpdir:
        agents = [{"slug": "ceo-agent", "name": "CEO", "role": "ceo"}]
        yaml_agents = {"ceo-agent": {"role": "ceo", "adapter": {"type": "claude_local"}}}
        pkg_path = make_package(tmpdir, agents=agents, yaml_agents=yaml_agents)
        result = validate(pkg_path)
        # Should warn about missing SOUL.md, HEARTBEAT.md, TOOLS.md for CEO
        assert any("SOUL.md" in w for w in result["warnings"])
        assert any("HEARTBEAT.md" in w for w in result["warnings"])
        assert any("TOOLS.md" in w for w in result["warnings"])
        print("PASS: test_ceo_missing_files_warning")


def test_missing_recommended_files():
    """Missing PROJECT-INVENTORY.md and CONTRIBUTING.md should warn."""
    with tempfile.TemporaryDirectory() as tmpdir:
        agents = [{"slug": "ceo-agent", "name": "CEO", "role": "ceo"}]
        yaml_agents = {"ceo-agent": {"role": "ceo", "adapter": {"type": "claude_local"}}}
        pkg_path = make_package(tmpdir, agents=agents, yaml_agents=yaml_agents)
        result = validate(pkg_path)
        assert any("PROJECT-INVENTORY" in w for w in result["warnings"])
        assert any("CONTRIBUTING" in w for w in result["warnings"])
        print("PASS: test_missing_recommended_files")


if __name__ == "__main__":
    test_extract_frontmatter_valid()
    test_extract_frontmatter_missing()
    test_valid_package()
    test_missing_company_md()
    test_no_ceo()
    test_multiple_ceos()
    test_invalid_reports_to()
    test_nonexistent_dir()
    test_cycle_detection()
    test_invalid_role_in_yaml()
    test_project_unknown_lead()
    test_routine_unknown_assignee()
    test_ceo_missing_files_warning()
    test_missing_recommended_files()
    print("\nAll validate-package tests passed.")
