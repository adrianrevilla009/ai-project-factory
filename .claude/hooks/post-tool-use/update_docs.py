#!/usr/bin/env python3
"""PostToolUse: remember which source files changed so the Stop hook can require docs updates."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _lib import glob_match, load_config, project_dir, read_event, relative_to_project, target_path  # noqa: E402

DEFAULT_SOURCE = ["*.java", "*.ts", "*.tsx", "*.tf", "*.py", "pom.xml", "*.yaml"]
DOC_GLOBS = ["*.md", "docs/*", "CHANGELOG*"]


def main() -> None:
    event = read_event()
    if event.get("tool_name") not in {"Write", "Edit", "MultiEdit"}:
        sys.exit(0)
    root = project_dir(event)
    rel = relative_to_project(event, target_path(event))
    cfg = load_config(root)
    kind = "docs" if glob_match(rel, DOC_GLOBS) else ("source" if glob_match(rel, cfg.get("source_globs", DEFAULT_SOURCE)) else None)
    if kind:
        log = root / ".claude" / "audit" / "pending-docs.txt"
        try:
            log.parent.mkdir(parents=True, exist_ok=True)
            with log.open("a") as fh:
                fh.write(f"{kind}\t{rel}\n")
        except OSError:
            pass
    sys.exit(0)


if __name__ == "__main__":
    main()
