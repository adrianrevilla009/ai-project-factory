#!/usr/bin/env python3
"""PostToolUse: reject dishonest AWS claims in edited text files (same rules as factory/validators/honest_claims.py)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _lib import allow, block, project_dir, read_event, relative_to_project, target_path  # noqa: E402

SUFFIXES = (".md", ".yaml", ".yml", ".txt", ".tf", ".json", ".hcl")


def main() -> None:
    event = read_event()
    rel = relative_to_project(event, target_path(event))
    if not rel.endswith(SUFFIXES) or rel == "docs/FACTORY_BRIEF.md":
        allow()
    root = project_dir(event)
    f = root / rel
    if not f.exists():
        allow()
    sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "factory" / "validators"))
    try:
        import honest_claims
    except ImportError:
        allow()  # validators not vendored in this project
    findings = honest_claims.scan_text(f.read_text(encoding="utf-8", errors="ignore"), rel)
    if findings:
        block("; ".join(str(x) for x in findings[:3]))
    allow()


if __name__ == "__main__":
    main()
