#!/usr/bin/env python3
"""PostToolUse(all): append an audit line (JSONL) to .claude/audit/actions.jsonl, redacting secrets."""
import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _lib import project_dir, read_event, relative_to_project, target_path  # noqa: E402

REDACT = re.compile(r"(AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9_-]{20,}|(?i:password|secret|token|api[_-]?key)\s*[=:]\s*\S+)")


def main() -> None:
    event = read_event()
    ti = event.get("tool_input") or {}
    entry = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "session": event.get("session_id"),
        "tool": event.get("tool_name"),
        "path": relative_to_project(event, target_path(event)) or None,
        "command": REDACT.sub("<redacted>", str(ti.get("command", ""))[:300]) or None,
    }
    log = project_dir(event) / ".claude" / "audit" / "actions.jsonl"
    try:
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass  # auditing must never break the session
    sys.exit(0)


if __name__ == "__main__":
    main()
