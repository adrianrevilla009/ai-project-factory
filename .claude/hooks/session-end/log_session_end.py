#!/usr/bin/env python3
"""SessionEnd: append a closing record to the audit log. SessionEnd hooks cannot block."""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _lib import project_dir, read_event  # noqa: E402


def main() -> None:
    event = read_event()
    entry = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "session": event.get("session_id"),
        "event": "SessionEnd",
        "reason": event.get("reason"),
    }
    log = project_dir(event) / ".claude" / "audit" / "actions.jsonl"
    try:
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass
    sys.exit(0)


if __name__ == "__main__":
    main()
