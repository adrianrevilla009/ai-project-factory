"""Tests for UserPromptSubmit, SubagentStop, PreCompact and SessionEnd hooks."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
HOOKS = ROOT / ".claude" / "hooks"
AWS_KEY = "AKIA" + "ABCDEFGHIJKLMNOP"  # assembled at runtime: no literal secret in the repo


def run(rel: str, event: dict, project: Path):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(project))
    return subprocess.run([sys.executable, str(HOOKS / rel)], input=json.dumps(event), text=True, capture_output=True, env=env)


# ------------------------------------------------------------ UserPromptSubmit
def test_prompt_with_secret_is_blocked(tmp_path):
    r = run("user-prompt-submit/block_secrets_in_prompt.py", {"prompt": f"usa esta clave {AWS_KEY}"}, tmp_path)
    out = json.loads(r.stdout)
    assert r.returncode == 0 and out["decision"] == "block" and "secreto" in out["reason"]


@pytest.mark.parametrize("prompt", ["haz un resumen del ADR-0004", "password = ${DB_PASSWORD}", "AKIAIOSFODNN7EXAMPLE"])
def test_clean_prompt_passes(prompt, tmp_path):
    r = run("user-prompt-submit/block_secrets_in_prompt.py", {"prompt": prompt}, tmp_path)
    assert r.returncode == 0 and r.stdout == ""


def test_prompt_hook_fails_closed_on_bad_json(tmp_path):
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(tmp_path))
    r = subprocess.run([sys.executable, str(HOOKS / "user-prompt-submit/block_secrets_in_prompt.py")], input="no", text=True, capture_output=True, env=env)
    assert r.returncode == 2


# ---------------------------------------------------------------- SubagentStop
def stop(agent, msg, **extra):
    return {"hook_event_name": "SubagentStop", "agent_type": agent, "last_assistant_message": msg, **extra}


def test_reviewer_without_evidence_is_blocked(tmp_path):
    assert run("subagent-stop/require_evidence.py", stop("code-reviewer", "Todo parece bien."), tmp_path).returncode == 2


@pytest.mark.parametrize("msg", ["Evidencia: make check en verde", "Hallazgo en src/A.java:42", "Evidence: 12 passed"])
def test_reviewer_with_evidence_passes(msg, tmp_path):
    assert run("subagent-stop/require_evidence.py", stop("security-reviewer", msg), tmp_path).returncode == 0


def test_other_agents_are_not_checked(tmp_path):
    assert run("subagent-stop/require_evidence.py", stop("docs-writer", "listo"), tmp_path).returncode == 0


def test_evidence_hook_never_loops(tmp_path):
    assert run("subagent-stop/require_evidence.py", stop("code-reviewer", "ok", stop_hook_active=True), tmp_path).returncode == 0


def test_evidence_agents_are_configurable(tmp_path):
    cfg = tmp_path / ".claude" / "hooks"
    cfg.mkdir(parents=True)
    (cfg / "hooks-config.json").write_text(json.dumps({"subagent_evidence": {"agents": ["docs-writer"]}}))
    assert run("subagent-stop/require_evidence.py", stop("docs-writer", "listo"), tmp_path).returncode == 2
    assert run("subagent-stop/require_evidence.py", stop("code-reviewer", "listo"), tmp_path).returncode == 0


# ------------------------------------------------------------------ PreCompact
def test_precompact_emits_state(tmp_path):
    (tmp_path / ".factory").mkdir()
    (tmp_path / ".factory" / "state.json").write_text(json.dumps({"phase": "plan", "tier": 1, "active_modules": ["outbox"]}))
    (tmp_path / "approvals").mkdir()
    (tmp_path / "approvals" / "gate-0.json").write_text("{}")
    r = run("pre-compact/preserve_state.py", {"hook_event_name": "PreCompact"}, tmp_path)
    assert r.returncode == 0 and "plan" in r.stdout and "outbox" in r.stdout and "gate-0" in r.stdout
    assert len(r.stdout) < 10000


def test_precompact_without_state(tmp_path):
    r = run("pre-compact/preserve_state.py", {"hook_event_name": "PreCompact"}, tmp_path)
    assert r.returncode == 0 and "ninguno" in r.stdout


# ------------------------------------------------------------------ SessionEnd
def test_session_end_is_logged_and_never_blocks(tmp_path):
    r = run("session-end/log_session_end.py", {"hook_event_name": "SessionEnd", "session_id": "s1", "reason": "other"}, tmp_path)
    assert r.returncode == 0
    line = json.loads((tmp_path / ".claude" / "audit" / "actions.jsonl").read_text().splitlines()[0])
    assert line["event"] == "SessionEnd" and line["reason"] == "other"


def test_settings_registers_new_events():
    hooks = json.loads((ROOT / ".claude" / "settings.json").read_text())["hooks"]
    for event, name in [("UserPromptSubmit", "block_secrets_in_prompt"), ("SubagentStop", "require_evidence"),
                        ("PreCompact", "preserve_state"), ("SessionEnd", "log_session_end")]:
        assert name in json.dumps(hooks[event]), event
