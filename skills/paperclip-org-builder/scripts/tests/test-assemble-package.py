#!/usr/bin/env python3
"""Tests for assemble-package.py"""

import json
import sys
import tempfile
from pathlib import Path

# Add parent to path for import
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from importlib.util import spec_from_file_location, module_from_spec

_spec = spec_from_file_location(
    "assemble_package",
    Path(__file__).resolve().parent.parent / "assemble-package.py",
)
mod = module_from_spec(_spec)
_spec.loader.exec_module(mod)

slugify = mod.slugify
generate_company_md = mod.generate_company_md
generate_agent_md = mod.generate_agent_md
generate_paperclip_yaml = mod.generate_paperclip_yaml
generate_project_md = mod.generate_project_md
generate_soul_md = mod.generate_soul_md
generate_heartbeat_md = mod.generate_heartbeat_md
generate_tools_md = mod.generate_tools_md
generate_project_inventory_md = mod.generate_project_inventory_md
generate_contributing_md = mod.generate_contributing_md


MINIMAL_DRAFT = {
    "vision": {"mission": "Test mission", "successCriteria": "Ship it"},
    "company": {
        "name": "Test Company",
        "description": "A test company",
        "brandColor": "#3B82F6",
        "issuePrefix": "TEST",
    },
    "contributing": {
        "branchStrategy": "main",
        "commitFormat": "[agent-role]: description (TEST-XX)",
    },
    "agents": [
        {
            "name": "Alice",
            "slug": "alice",
            "role": "ceo",
            "title": "CEO",
            "instructions": "## Instructions\n\nLead the company.",
            "soul": "# Alice — Soul\n\nI am the CEO.\n",
            "heartbeat": "# Alice — Heartbeat\n\n1. Orient\n2. Check inbox\n",
            "tools": "# Alice — Tools\n\n## API\n",
        },
        {
            "name": "Bob",
            "slug": "bob",
            "role": "engineer",
            "title": "Senior Engineer",
            "reportsTo": "alice",
            "instructions": "## Instructions\n\nBuild things.",
            "heartbeat": "# Bob — Heartbeat\n\n1. Get assignments\n2. Work\n",
            "skills": ["code-review"],
        },
    ],
    "goals": [
        {
            "title": "Ship v1",
            "level": "company",
            "description": "Launch the product",
        }
    ],
    "projects": [
        {
            "name": "Launch Website",
            "slug": "launch-website",
            "description": "Build and deploy the company website",
            "status": "planned",
            "leadAgent": "bob",
        }
    ],
    "routines": [
        {
            "title": "Daily standup",
            "slug": "daily-standup",
            "assigneeAgent": "alice",
            "cronExpression": "0 9 * * 1-5",
            "timezone": "America/New_York",
            "concurrencyPolicy": "skip",
            "catchUpPolicy": "skip",
        }
    ],
    "budgets": {
        "companyTotal": 100000,
        "agentAllocations": {"alice": 40000, "bob": 60000},
    },
}


def test_slugify():
    assert slugify("My Cool Company") == "my-cool-company"
    assert slugify("  Spaces  ") == "spaces"
    assert slugify("Special!@#Chars") == "specialchars"
    assert slugify("Already-Slugged") == "already-slugged"
    print("PASS: test_slugify")


def test_generate_company_md():
    result = generate_company_md(MINIMAL_DRAFT)
    assert result.startswith("---\n")
    assert "schema: agentcompanies/v1" in result
    assert "slug: test-company" in result
    assert "name: Test Company" in result
    assert "# Test Company" in result
    # Should NOT have kind, budgetMonthlyCents, includes, requirements
    assert "kind:" not in result
    assert "budgetMonthlyCents" not in result
    assert "includes:" not in result
    assert "requirements:" not in result
    print("PASS: test_generate_company_md")


def test_generate_agent_md_slim_frontmatter():
    """AGENTS.md should have slim frontmatter: name, title, reportsTo, skills only."""
    agent = MINIMAL_DRAFT["agents"][0]
    result = generate_agent_md(agent)
    assert result.startswith("---\n")
    assert "name: Alice" in result
    assert "title: CEO" in result
    assert "Lead the company" in result
    # Should NOT have role, budget, permissions, capabilities in frontmatter
    assert "role:" not in result
    assert "budgetMonthlyCents" not in result
    assert "permissions:" not in result
    assert "capabilities:" not in result
    print("PASS: test_generate_agent_md_slim_frontmatter")


def test_generate_agent_md_with_reports_to():
    agent = MINIMAL_DRAFT["agents"][1]
    result = generate_agent_md(agent)
    assert "reportsTo: alice" in result
    assert "skills:" in result
    assert "code-review" in result
    # role should NOT be in AGENTS.md frontmatter
    assert "role:" not in result
    print("PASS: test_generate_agent_md_with_reports_to")


def test_generate_soul_md():
    agent = MINIMAL_DRAFT["agents"][0]
    result = generate_soul_md(agent)
    assert "Alice — Soul" in result
    assert "I am the CEO" in result
    print("PASS: test_generate_soul_md")


def test_generate_soul_md_default():
    """Agent without soul content gets a default."""
    agent = {"name": "Test", "role": "engineer"}
    result = generate_soul_md(agent)
    assert "Test — Soul" in result
    assert "engineer" in result
    print("PASS: test_generate_soul_md_default")


def test_generate_heartbeat_md():
    agent = MINIMAL_DRAFT["agents"][0]
    result = generate_heartbeat_md(agent)
    assert "Alice — Heartbeat" in result
    assert "Orient" in result
    print("PASS: test_generate_heartbeat_md")


def test_generate_tools_md():
    agent = MINIMAL_DRAFT["agents"][0]
    result = generate_tools_md(agent)
    assert "Alice — Tools" in result
    assert "API" in result
    print("PASS: test_generate_tools_md")


def test_generate_project_inventory_md():
    result = generate_project_inventory_md(MINIMAL_DRAFT)
    assert "Test Company" in result
    assert "Project Inventory" in result
    assert "Launch Website" in result
    assert "bob" in result
    assert "Every agent reads this" in result
    print("PASS: test_generate_project_inventory_md")


def test_generate_contributing_md():
    result = generate_contributing_md(MINIMAL_DRAFT)
    assert "Contributing to Test Company" in result
    assert "[agent-role]: description (TEST-XX)" in result
    assert "main" in result
    print("PASS: test_generate_contributing_md")


def test_generate_project_md():
    project = MINIMAL_DRAFT["projects"][0]
    result = generate_project_md(project)
    assert result.startswith("---\n")
    assert "name: Launch Website" in result
    assert "status: planned" in result
    assert "leadAgentSlug: bob" in result
    assert "# Launch Website" in result
    print("PASS: test_generate_project_md")


def test_generate_paperclip_yaml():
    result = generate_paperclip_yaml(MINIMAL_DRAFT)
    assert "schema: paperclip/v1" in result
    # Agents section with per-agent config
    assert "agents:" in result
    assert "alice:" in result
    assert "bob:" in result
    assert "role: ceo" in result
    assert "role: engineer" in result
    assert "claude_local" in result
    # Sidebar
    assert "sidebar:" in result
    # Should NOT have old format
    assert "adapters:" not in result
    assert "environment:" not in result
    assert "secrets:" not in result
    print("PASS: test_generate_paperclip_yaml")


def test_generate_paperclip_yaml_routines():
    result = generate_paperclip_yaml(MINIMAL_DRAFT)
    assert "routines:" in result
    assert "daily-standup:" in result
    assert "cronExpression:" in result
    assert "0 9 * * 1-5" in result
    assert "America/New_York" in result
    print("PASS: test_generate_paperclip_yaml_routines")


def test_generate_paperclip_yaml_projects():
    result = generate_paperclip_yaml(MINIMAL_DRAFT)
    assert "projects:" in result
    assert "launch-website:" in result
    assert "leadAgentSlug: bob" in result
    print("PASS: test_generate_paperclip_yaml_projects")


def test_generate_paperclip_yaml_brand_color():
    result = generate_paperclip_yaml(MINIMAL_DRAFT)
    assert "company:" in result
    assert "brandColor:" in result
    assert "#3B82F6" in result
    print("PASS: test_generate_paperclip_yaml_brand_color")


def test_assemble_creates_all_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        draft_path = Path(tmpdir) / "draft.json"
        draft_path.write_text(json.dumps(MINIMAL_DRAFT))
        output_dir = Path(tmpdir) / "output"

        mod.assemble(str(draft_path), str(output_dir))

        # Company-level files
        assert (output_dir / "COMPANY.md").exists()
        assert (output_dir / ".paperclip.yaml").exists()
        assert (output_dir / "PROJECT-INVENTORY.md").exists()
        assert (output_dir / "CONTRIBUTING.md").exists()

        # Agent files — CEO gets all 4 + memory/
        assert (output_dir / "agents" / "alice" / "AGENTS.md").exists()
        assert (output_dir / "agents" / "alice" / "SOUL.md").exists()
        assert (output_dir / "agents" / "alice" / "HEARTBEAT.md").exists()
        assert (output_dir / "agents" / "alice" / "TOOLS.md").exists()
        assert (output_dir / "agents" / "alice" / "memory").is_dir()

        # Worker gets AGENTS.md + HEARTBEAT.md + memory/
        assert (output_dir / "agents" / "bob" / "AGENTS.md").exists()
        assert (output_dir / "agents" / "bob" / "HEARTBEAT.md").exists()
        assert (output_dir / "agents" / "bob" / "memory").is_dir()
        # Bob has no soul or tools defined — should not be created
        assert not (output_dir / "agents" / "bob" / "SOUL.md").exists()
        assert not (output_dir / "agents" / "bob" / "TOOLS.md").exists()

        # Projects: projects/{slug}/PROJECT.md
        assert (output_dir / "projects" / "launch-website" / "PROJECT.md").exists()

        # Skills directory
        assert (output_dir / "skills").is_dir()
        assert (output_dir / "skills" / "README.md").exists()

        print("PASS: test_assemble_creates_all_files")


def test_assemble_agent_frontmatter_is_slim():
    """Verify assembled AGENTS.md has slim frontmatter."""
    with tempfile.TemporaryDirectory() as tmpdir:
        draft_path = Path(tmpdir) / "draft.json"
        draft_path.write_text(json.dumps(MINIMAL_DRAFT))
        output_dir = Path(tmpdir) / "output"

        mod.assemble(str(draft_path), str(output_dir))

        bob_md = (output_dir / "agents" / "bob" / "AGENTS.md").read_text()
        assert "name: Bob" in bob_md
        assert "reportsTo: alice" in bob_md
        assert "skills:" in bob_md
        # These should NOT be in AGENTS.md
        assert "role:" not in bob_md
        assert "budgetMonthlyCents" not in bob_md
        assert "permissions:" not in bob_md

        print("PASS: test_assemble_agent_frontmatter_is_slim")


if __name__ == "__main__":
    test_slugify()
    test_generate_company_md()
    test_generate_agent_md_slim_frontmatter()
    test_generate_agent_md_with_reports_to()
    test_generate_soul_md()
    test_generate_soul_md_default()
    test_generate_heartbeat_md()
    test_generate_tools_md()
    test_generate_project_inventory_md()
    test_generate_contributing_md()
    test_generate_project_md()
    test_generate_paperclip_yaml()
    test_generate_paperclip_yaml_routines()
    test_generate_paperclip_yaml_projects()
    test_generate_paperclip_yaml_brand_color()
    test_assemble_creates_all_files()
    test_assemble_agent_frontmatter_is_slim()
    print("\nAll assemble-package tests passed.")
