#!/usr/bin/env python3
"""PreToolUse: gates are code, not a request in a prompt.

1. Agents can never write to `approvals/` or to `.factory/state.json`.
2. If `.factory/state.json` exists (a generated project), edits outside the always-allowed
   paths require valid approval records for every gate that precedes the current phase.
   Records live in `approvals/gate-N.json` and must satisfy gates/approval-record.schema.json
   (when the schema is available) with decision approved|approved_with_conditions.
No state file (e.g. the factory repo itself) -> only rule 1 applies.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _lib import allow, block, project_dir, read_event, relative_to_project, target_path  # noqa: E402

PHASE_REQUIRES = {
    "intake": [],
    "plan": [0],
    "implementation": [0, 1],
    "pull-request": [0, 1, 2],
    "release": [0, 1, 2, 3],
    "cloud-readiness": [0, 1, 2, 3, 4],
    "close": [0, 1, 2, 3, 4, 5],
}
PROTECTED = re.compile(r"^(approvals/|\.factory/state\.json$)")
ALWAYS_ALLOWED = re.compile(r"^(docs/|gates/|approvals/|\.factory/|\.claude/|CLAUDE\.md$|README\.md$|knowledge/)")
WRITE_VERBS = re.compile(r"(>|\btee\b|\brm\b|\bmv\b|\bcp\b|\bsed\s+-i|\btouch\b|\btruncate\b|\bdd\b|\bchmod\b|\bln\b|\binstall\b|python\S*\s+-c|\bperl\s+-i)")
PROTECTED_IN_CMD = re.compile(r"(^|[\s'\"=/])(approvals/|\.factory/state\.json)")


def valid_record(root: Path, gate: int) -> bool:
    p = root / "approvals" / f"gate-{gate}.json"
    try:
        rec = json.loads(p.read_text())
    except (OSError, json.JSONDecodeError):
        return False
    if rec.get("gate") != gate or rec.get("decision") not in {"approved", "approved_with_conditions"}:
        return False
    schema_path = root / "gates" / "approval-record.schema.json"
    if schema_path.exists():
        try:
            import jsonschema
            jsonschema.validate(rec, json.loads(schema_path.read_text()))
        except ImportError:
            pass  # structural checks above still apply
        except Exception:
            return False
    return True


def main() -> None:
    event = read_event()
    tool = event.get("tool_name", "")
    root = project_dir(event)

    if tool == "Bash":
        cmd = (event.get("tool_input") or {}).get("command", "")
        if isinstance(cmd, str) and PROTECTED_IN_CMD.search(cmd) and WRITE_VERBS.search(cmd):
            block("agents must not modify approvals/ or .factory/state.json; gate approvals are human-only")
        allow()

    if tool not in {"Write", "Edit", "MultiEdit", "NotebookEdit"}:
        allow()

    rel = relative_to_project(event, target_path(event))
    if PROTECTED.search(rel):
        block(f"'{rel}' is protected: gate approvals are created by humans, never by agents")

    state_file = root / ".factory" / "state.json"
    if not state_file.exists() or ALWAYS_ALLOWED.search(rel):
        allow()
    try:
        phase = json.loads(state_file.read_text()).get("phase")
    except (OSError, json.JSONDecodeError):
        block(".factory/state.json is unreadable (fail closed)")
    if phase not in PHASE_REQUIRES:
        block(f"unknown phase '{phase}' in .factory/state.json (fail closed)")
    missing = [g for g in PHASE_REQUIRES[phase] if not valid_record(root, g)]
    if missing:
        block(f"phase '{phase}' requires valid human approval for gate(s) {missing}. Stop and request review (skill gate-protocol).")
    allow()


if __name__ == "__main__":
    main()
