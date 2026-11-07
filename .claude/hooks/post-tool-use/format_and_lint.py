#!/usr/bin/env python3
"""PostToolUse: run configured formatter/linter commands for the edited file.

Config (.claude/hooks/hooks-config.json):
  {"format": {"*.py": ["python3 -m black -q {file}"]}, "lint": {"*.java": ["mvn -q checkstyle:check"]}}
Formatters never block; linters block (exit 2) so the agent fixes the issue. Without config this is a no-op.
Commands are run without a shell; {file} is substituted. TODO-VERIFY concrete Java/TS tool invocations per project.
"""
import shlex
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _lib import allow, block, glob_match, load_config, project_dir, read_event, relative_to_project, target_path  # noqa: E402


def run(cmds, root, rel):
    for c in cmds:
        argv = [a.replace("{file}", rel) for a in shlex.split(c)]
        r = subprocess.run(argv, cwd=root, capture_output=True, text=True, timeout=120)
        yield c, r


def main() -> None:
    event = read_event()
    root = project_dir(event)
    rel = relative_to_project(event, target_path(event))
    if not rel or not (root / rel).exists():
        allow()
    cfg = load_config(root)
    for pat, cmds in (cfg.get("format") or {}).items():
        if glob_match(rel, [pat]):
            for _c, _r in run(cmds, root, rel):
                pass
    for pat, cmds in (cfg.get("lint") or {}).items():
        if glob_match(rel, [pat]):
            for c, r in run(cmds, root, rel):
                if r.returncode != 0:
                    block(f"lint failed ({c}):\n{(r.stdout + r.stderr)[-1500:]}")
    allow()


if __name__ == "__main__":
    main()
