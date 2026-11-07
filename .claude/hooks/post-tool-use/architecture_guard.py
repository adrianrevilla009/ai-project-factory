#!/usr/bin/env python3
"""PostToolUse: lightweight hexagonal guard on edited Java files (domain must not import frameworks).

Full enforcement is ArchUnit in the generated project; this hook gives immediate feedback at edit time.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _lib import allow, block, project_dir, read_event, relative_to_project, target_path  # noqa: E402

DOMAIN = re.compile(r"/(domain|core)/")
FORBIDDEN_IMPORTS = re.compile(
    r"^import\s+(static\s+)?(org\.springframework\.|jakarta\.persistence\.|javax\.persistence\.|org\.hibernate\.|com\.fasterxml\.jackson\.|software\.amazon\.awssdk\.|org\.apache\.kafka\.)", re.M)


def main() -> None:
    event = read_event()
    rel = relative_to_project(event, target_path(event))
    if not rel.endswith(".java") or not DOMAIN.search("/" + rel) or "/src/test/" in rel:
        allow()
    f = project_dir(event) / rel
    if not f.exists():
        allow()
    m = FORBIDDEN_IMPORTS.search(f.read_text(encoding="utf-8", errors="ignore"))
    if m:
        block(f"hexagonal violation in {rel}: domain code imports '{m.group(0).strip()}'. Move framework code to an adapter (skill hexagonal).")
    allow()


if __name__ == "__main__":
    main()
