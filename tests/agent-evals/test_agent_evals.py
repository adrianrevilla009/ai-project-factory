"""Agent evals. Hook cases run the real hook; scenario cases (need a model) are validated structurally.

Case files live in tests/agent-evals/cases/. See the skill `agent-evals` for the format.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
CASES = Path(__file__).resolve().parent / "cases"
HOOKS = ROOT / ".claude" / "hooks"
SCHEMA = (ROOT / "gates" / "approval-record.schema.json").read_text()
AWS_KEY = "AKIA" + "ABCDEFGHIJKLMNOP"  # assembled at runtime: no literal secret in the repo


def load(name):
    return yaml.safe_load((CASES / name).read_text())


def fill(value, project):
    if isinstance(value, str):
        return value.replace("{{PROJECT}}", str(project)).replace("{{AWS_KEY}}", AWS_KEY).replace("{{SCHEMA}}", SCHEMA)
    if isinstance(value, dict):
        return {k: fill(v, project) for k, v in value.items()}
    if isinstance(value, list):
        return [fill(v, project) for v in value]
    return value


HOOK_CASES = load("hooks.yaml")
SCENARIOS = load("scenarios.yaml")


@pytest.mark.parametrize("case", HOOK_CASES, ids=lambda c: c["id"])
def test_hook_case(case, tmp_path):
    for rel, content in fill(case.get("setup", {}).get("files", {}), tmp_path).items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    event = fill(case["event"], tmp_path)
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(tmp_path))
    r = subprocess.run([sys.executable, str(HOOKS / case["hook"])], input=json.dumps(event), text=True, capture_output=True, env=env)
    exp = case["expect"]
    assert r.returncode == exp["exit"], (r.stdout, r.stderr)
    if "stdout_contains" in exp:
        assert exp["stdout_contains"] in r.stdout
    if exp.get("stdout_empty"):
        assert r.stdout == ""


def test_case_ids_are_unique_and_areas_covered():
    ids = [c["id"] for c in HOOK_CASES + SCENARIOS]
    assert len(ids) == len(set(ids))
    areas = {c["area"] for c in HOOK_CASES + SCENARIOS}
    assert {"gates", "secrets", "aws-honesty", "prompt-injection", "dangerous-actions", "evidence"} <= areas


@pytest.mark.parametrize("case", SCENARIOS, ids=lambda c: c["id"])
def test_scenario_case_is_well_formed(case):
    agents = {p.stem for p in (ROOT / ".claude" / "agents").glob("*/*.md")}
    commands = {p.stem for p in (ROOT / ".claude" / "commands").glob("*/*.md")}
    skills = {p.parent.name for p in (ROOT / ".claude" / "skills").glob("*/SKILL.md")}
    assert case["agent"] in agents
    assert case.get("command", "project-init") in commands
    assert case["scenario"].strip() and len(case["rubric"]) >= 2
    for s in case["skills"]:
        assert s in skills, s
