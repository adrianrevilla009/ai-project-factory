#!/usr/bin/env python3
"""PreToolUse: block edits in paths agents must never touch (git internals, build outputs, state, hook config)."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _lib import allow, block, read_event, relative_to_project, target_path  # noqa: E402

FORBIDDEN = [
    (r"(^|/)\.git/", "git internals"),
    (r"(^|/)node_modules/", "node_modules"),
    (r"(^|/)\.terraform/", ".terraform provider cache"),
    (r"(^|/)target/", "Maven build output"),
    (r"\.tfstate(\.backup)?$", "Terraform state (never committed/edited)"),
    (r"(^|/)\.claude/settings\.json$", "agent permission/hook settings are changed by humans only"),
    (r"(^|/)\.claude/hooks/", "hooks are protected code; change them via reviewed PR by a human"),
]
COMPILED = [(re.compile(p), why) for p, why in FORBIDDEN]


def main() -> None:
    event = read_event()
    if event.get("tool_name") not in {"Write", "Edit", "MultiEdit", "NotebookEdit"}:
        allow()
    rel = relative_to_project(event, target_path(event))
    for rx, why in COMPILED:
        if rx.search(rel):
            block(f"'{rel}' is forbidden for agents ({why}).")
    allow()


if __name__ == "__main__":
    main()
