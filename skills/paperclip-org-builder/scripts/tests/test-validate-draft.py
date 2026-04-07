#!/usr/bin/env python3
"""Tests for validate-draft.py"""

import json
import sys
import tempfile
from pathlib import Path

from importlib.util import spec_from_file_location, module_from_spec

_spec = spec_from_file_location(
    "validate_draft",
    Path(__file__).resolve().parent.parent / "validate-draft.py",
)
mod = module_from_spec(_spec)
_spec.loader.exec_module(mod)

validate_draft = mod.validate_draft
detect_cycle = mod.detect_cycle
validate_cron = mod.validate_cron


def write_draft(tmpdir, draft):
    path = Path(tmpdir) / "draft.json"
    path.write_text(json.dumps(draft))
    return str(path)


STAGE3_DRAFT = {
    "currentStage": 3,
    "vision": {"mission": "Test mission", "successCriteria": "Ship it"},
    "company": {"name": "Test Company"},
    "agents": [
        {"name": "Alice", "slug": "alice", "role": "ceo", "title": "CEO"},
        {
            "name": "Bob",
            "slug": "bob",
            "role": "engineer",
            "title": "Dev",
            "reportsTo": "alice",
        },
    ],
}

FULL_DRAFT = {
    "currentStage": 8,
    "vision": {"mission": "Test mission"},
    "company": {"name": "Test Co"},
    "agents": [
        {
            "name": "A",
            "slug": "a",
            "role": "ceo",
            "instructions": "Lead.",
        },
        {
            "name": "B",
            "slug": "b",
            "role": "engineer",
            "reportsTo": "a",
            "instructions": "Build.",
        },
    ],
    "goals": [{"title": "Ship", "level": "company", "ownerAgent": "a"}],
    "projects": [{"name": "Web", "slug": "web", "leadAgent": "b"}],
    "budgets": {
        "companyTotal": 100000,
        "agentAllocations": {"a": 40000, "b": 60000},
    },
    "routines": [
        {
            "title": "Standup",
            "assigneeAgent": "a",
            "cronExpression": "0 9 * * 1-5",
        }
    ],
}


def test_valid_stage3():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = write_draft(tmpdir, STAGE3_DRAFT)
        result = validate_draft(path)
        assert result["status"] == "valid", result["issues"]
        assert result["currentStage"] == 3
    print("PASS: test_valid_stage3")


def test_valid_full_draft():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = write_draft(tmpdir, FULL_DRAFT)
        result = validate_draft(path)
        assert result["status"] == "valid", result["issues"]
    print("PASS: test_valid_full_draft")


def test_missing_current_stage():
    with tempfile.TemporaryDirectory() as tmpdir:
        draft = {"vision": {"mission": "x"}}
        path = write_draft(tmpdir, draft)
        result = validate_draft(path)
        assert any("currentStage" in i for i in result["issues"])
    print("PASS: test_missing_current_stage")


def test_missing_vision():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = write_draft(tmpdir, {"currentStage": 1})
        result = validate_draft(path)
        assert any("vision" in i for i in result["issues"])
    print("PASS: test_missing_vision")


def test_missing_company():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = write_draft(
            tmpdir, {"currentStage": 2, "vision": {"mission": "x"}}
        )
        result = validate_draft(path)
        assert any("company" in i for i in result["issues"])
    print("PASS: test_missing_company")


def test_no_ceo():
    with tempfile.TemporaryDirectory() as tmpdir:
        draft = dict(STAGE3_DRAFT)
        draft["agents"] = [
            {"slug": "dev", "name": "Dev", "role": "engineer"}
        ]
        path = write_draft(tmpdir, draft)
        result = validate_draft(path)
        assert any("No CEO" in i for i in result["issues"])
    print("PASS: test_no_ceo")


def test_duplicate_slugs():
    with tempfile.TemporaryDirectory() as tmpdir:
        draft = dict(STAGE3_DRAFT)
        draft["agents"] = [
            {"slug": "alice", "name": "A", "role": "ceo"},
            {
                "slug": "alice",
                "name": "B",
                "role": "engineer",
                "reportsTo": "alice",
            },
        ]
        path = write_draft(tmpdir, draft)
        result = validate_draft(path)
        assert any("Duplicate" in i for i in result["issues"])
    print("PASS: test_duplicate_slugs")


def test_cycle_detection():
    chain = {"a": "b", "b": "c", "c": "a"}
    cycle = detect_cycle(chain)
    assert cycle is not None
    print("PASS: test_cycle_detection")


def test_no_cycle():
    chain = {"b": "a", "c": "a"}
    cycle = detect_cycle(chain)
    assert cycle is None
    print("PASS: test_no_cycle")


def test_orphan_reports_to():
    with tempfile.TemporaryDirectory() as tmpdir:
        draft = dict(STAGE3_DRAFT)
        draft["agents"] = [
            {"slug": "alice", "name": "A", "role": "ceo"},
            {
                "slug": "bob",
                "name": "B",
                "role": "engineer",
                "reportsTo": "nonexistent",
            },
        ]
        path = write_draft(tmpdir, draft)
        result = validate_draft(path)
        assert any("nonexistent" in i for i in result["issues"])
    print("PASS: test_orphan_reports_to")


def test_invalid_role():
    with tempfile.TemporaryDirectory() as tmpdir:
        draft = dict(STAGE3_DRAFT)
        draft["agents"] = [
            {"slug": "alice", "name": "A", "role": "ceo"},
            {
                "slug": "bob",
                "name": "B",
                "role": "wizard",
                "reportsTo": "alice",
            },
        ]
        path = write_draft(tmpdir, draft)
        result = validate_draft(path)
        assert any("wizard" in i for i in result["issues"])
    print("PASS: test_invalid_role")


def test_budget_overflow():
    with tempfile.TemporaryDirectory() as tmpdir:
        draft = dict(FULL_DRAFT)
        draft["budgets"] = {
            "companyTotal": 50000,
            "agentAllocations": {"a": 40000, "b": 60000},
        }
        path = write_draft(tmpdir, draft)
        result = validate_draft(path)
        assert any("exceed" in i for i in result["issues"])
    print("PASS: test_budget_overflow")


def test_budget_unknown_agent():
    with tempfile.TemporaryDirectory() as tmpdir:
        draft = dict(FULL_DRAFT)
        draft["budgets"] = {
            "companyTotal": 100000,
            "agentAllocations": {"a": 40000, "ghost": 60000},
        }
        path = write_draft(tmpdir, draft)
        result = validate_draft(path)
        assert any("ghost" in i for i in result["issues"])
    print("PASS: test_budget_unknown_agent")


def test_negative_budget():
    with tempfile.TemporaryDirectory() as tmpdir:
        draft = dict(FULL_DRAFT)
        draft["budgets"] = {
            "companyTotal": -100,
            "agentAllocations": {},
        }
        path = write_draft(tmpdir, draft)
        result = validate_draft(path)
        assert any("negative" in i.lower() for i in result["issues"])
    print("PASS: test_negative_budget")


def test_valid_cron():
    assert validate_cron("0 9 * * 1-5") is None
    assert validate_cron("*/5 * * * *") is None
    assert validate_cron("0 0 1 * *") is None
    print("PASS: test_valid_cron")


def test_invalid_cron():
    assert validate_cron("bad cron") is not None
    assert validate_cron("60 9 * * 1") is not None
    assert validate_cron("0 25 * * 1") is not None
    print("PASS: test_invalid_cron")


def test_stage_override():
    with tempfile.TemporaryDirectory() as tmpdir:
        draft = {"currentStage": 8, "vision": {"mission": "x"}}
        path = write_draft(tmpdir, draft)
        result = validate_draft(path, stage_override=1)
        assert not any("company" in i for i in result["issues"])
    print("PASS: test_stage_override")


def test_project_unknown_lead():
    with tempfile.TemporaryDirectory() as tmpdir:
        draft = dict(FULL_DRAFT)
        draft["projects"] = [{"name": "X", "leadAgent": "nobody"}]
        path = write_draft(tmpdir, draft)
        result = validate_draft(path)
        assert any("nobody" in i for i in result["issues"])
    print("PASS: test_project_unknown_lead")


def test_routine_unknown_agent():
    with tempfile.TemporaryDirectory() as tmpdir:
        draft = dict(FULL_DRAFT)
        draft["routines"] = [
            {
                "title": "X",
                "assigneeAgent": "ghost",
                "cronExpression": "0 9 * * 1-5",
            }
        ]
        path = write_draft(tmpdir, draft)
        result = validate_draft(path)
        assert any("ghost" in i for i in result["issues"])
    print("PASS: test_routine_unknown_agent")


def test_goal_unknown_owner():
    with tempfile.TemporaryDirectory() as tmpdir:
        draft = dict(FULL_DRAFT)
        draft["goals"] = [
            {"title": "Goal", "level": "agent", "ownerAgent": "phantom"}
        ]
        path = write_draft(tmpdir, draft)
        result = validate_draft(path)
        assert any("phantom" in i for i in result["issues"])
    print("PASS: test_goal_unknown_owner")


def test_bad_json():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "draft.json"
        path.write_text("{bad json")
        result = validate_draft(str(path))
        assert result["status"] == "error"
    print("PASS: test_bad_json")


def test_missing_file():
    result = validate_draft("/nonexistent/path/draft.json")
    assert result["status"] == "error"
    print("PASS: test_missing_file")


if __name__ == "__main__":
    test_valid_stage3()
    test_valid_full_draft()
    test_missing_current_stage()
    test_missing_vision()
    test_missing_company()
    test_no_ceo()
    test_duplicate_slugs()
    test_cycle_detection()
    test_no_cycle()
    test_orphan_reports_to()
    test_invalid_role()
    test_budget_overflow()
    test_budget_unknown_agent()
    test_negative_budget()
    test_valid_cron()
    test_invalid_cron()
    test_stage_override()
    test_project_unknown_lead()
    test_routine_unknown_agent()
    test_goal_unknown_owner()
    test_bad_json()
    test_missing_file()
    print("\nAll validate-draft tests passed.")
