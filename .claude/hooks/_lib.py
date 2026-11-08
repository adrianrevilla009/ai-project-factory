"""Shared helpers for factory hooks.

Contract (Claude Code hooks, verified 2026-11-06, see docs/architecture/claude-code-formats.md):
- event JSON arrives on stdin (tool_name, tool_input, cwd, ...)
- exit code 2 blocks the action; the reason goes to stderr
- exit code 0 allows
Hooks fail CLOSED on malformed input for security-relevant events.
"""
import json
import os
import sys
from pathlib import Path


def read_event() -> dict:
    raw = sys.stdin.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        block("hook: invalid JSON on stdin (fail closed)")
    if not isinstance(data, dict):
        block("hook: event is not a JSON object (fail closed)")
    return data


def block(reason: str) -> None:
    print(f"BLOCKED: {reason}", file=sys.stderr)
    sys.exit(2)


def allow() -> None:
    sys.exit(0)


def project_dir(event: dict) -> Path:
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or event.get("cwd") or os.getcwd()).resolve()


def target_path(event: dict) -> str:
    ti = event.get("tool_input") or {}
    return ti.get("file_path") or ti.get("path") or ti.get("notebook_path") or ""


def relative_to_project(event: dict, path: str) -> str:
    if not path:
        return ""
    p = Path(path)
    base = project_dir(event)
    if not p.is_absolute():
        p = base / p
    try:
        return p.resolve().relative_to(base).as_posix()
    except ValueError:
        return p.as_posix()


def written_text(event: dict) -> str:
    """All text the tool is about to write."""
    ti = event.get("tool_input") or {}
    parts = [ti.get("content"), ti.get("new_string"), ti.get("new_source")]
    for e in ti.get("edits") or []:
        if isinstance(e, dict):
            parts.append(e.get("new_string"))
    return "\n".join(p for p in parts if isinstance(p, str))


def load_config(root: Path) -> dict:
    """Optional per-project hook config: .claude/hooks/hooks-config.json (see docs/operating-model)."""
    p = root / ".claude" / "hooks" / "hooks-config.json"
    try:
        return json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return {}


def emit_context(event_name: str, text: str) -> None:
    """Add context for the model (SessionStart / PostToolUse additionalContext). Re-check field names against the Claude Code docs periodically."""
    print(json.dumps({"hookSpecificOutput": {"hookEventName": event_name, "additionalContext": text}}))


def glob_match(rel: str, globs) -> bool:
    from fnmatch import fnmatch
    return any(fnmatch(rel, g) or fnmatch(rel, g.replace("**/", "")) for g in globs)
