#!/usr/bin/env python3
"""PostToolUse: after editing a build file, reject forbidden libraries (catalog/forbidden-libraries.yaml, e.g. Lombok)."""
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _lib import allow, block, project_dir, read_event, relative_to_project, target_path  # noqa: E402

BUILD_FILES = re.compile(r"(^|/)(pom\.xml|build\.gradle(\.kts)?|package\.json|pnpm-lock\.yaml|requirements.*\.txt)$")


def find_catalog(root: Path) -> Path | None:
    for c in (root / "catalog" / "forbidden-libraries.yaml", Path(__file__).resolve().parents[3] / "catalog" / "forbidden-libraries.yaml"):
        if c.exists():
            return c
    return None


def main() -> None:
    event = read_event()
    rel = relative_to_project(event, target_path(event))
    if not BUILD_FILES.search(rel):
        allow()
    root = project_dir(event)
    cat = find_catalog(root)
    f = root / rel
    if not cat or not f.exists():
        allow()
    text = f.read_text(encoding="utf-8", errors="ignore").lower()
    for entry in yaml.safe_load(cat.read_text()).get("forbidden", []):
        for needle in entry.get("match", []):
            if needle.lower() in text:
                block(f"forbidden library '{entry['id']}' found in {rel}: {entry['reason']} Alternative: {entry.get('alternative', '-')}")
    allow()


if __name__ == "__main__":
    main()
