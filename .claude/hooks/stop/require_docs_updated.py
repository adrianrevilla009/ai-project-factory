#!/usr/bin/env python3
"""Stop: if source files changed this session and no docs were touched, ask the agent to update docs first."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _lib import allow, block, project_dir, read_event  # noqa: E402


def main() -> None:
    event = read_event()
    if event.get("stop_hook_active"):
        allow()  # avoid infinite loops
    log = project_dir(event) / ".claude" / "audit" / "pending-docs.txt"
    if not log.exists():
        allow()
    kinds = [ln.split("\t")[0] for ln in log.read_text().splitlines() if ln]
    if "source" in kinds and "docs" not in kinds:
        log.unlink(missing_ok=True)
        block("source files changed but no documentation was updated. Update README/docs/ADR/CHANGELOG (skill living-readme) or state why not needed.")
    log.unlink(missing_ok=True)
    allow()


if __name__ == "__main__":
    main()
