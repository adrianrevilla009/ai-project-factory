#!/usr/bin/env python3
"""PreToolUse: block writing secrets or secret-bearing files."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _lib import allow, block, find_secret, read_event, relative_to_project, target_path, written_text  # noqa: E402

SENSITIVE_FILES = re.compile(r"(^|/)(\.env(\..+)?|.*\.pem|.*\.p12|.*\.pfx|id_rsa|id_ed25519|credentials|.*\.tfstate(\..*)?)$")
SAFE_FILES = re.compile(r"\.(example|sample|template)$")


def main() -> None:
    event = read_event()
    tool = event.get("tool_name", "")
    if tool not in {"Write", "Edit", "MultiEdit", "NotebookEdit"}:
        allow()
    rel = relative_to_project(event, target_path(event))
    if rel and SENSITIVE_FILES.search(rel) and not SAFE_FILES.search(rel):
        block(f"writing to sensitive file '{rel}' is not allowed")
    text = written_text(event)
    label = find_secret(text)
    if label:
        block(f"possible secret detected ({label}). Use Vault/env references instead of literals.")
    allow()


if __name__ == "__main__":
    main()
