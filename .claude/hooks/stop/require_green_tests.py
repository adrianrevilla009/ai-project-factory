#!/usr/bin/env python3
"""Stop: when relevant files changed (git working tree), run the project's test command; block stop if red.

Config (.claude/hooks/hooks-config.json): {"test_command": "make test", "test_trigger_globs": ["src/**", "*.java"]}
No test_command configured -> allow. Never loops (honors stop_hook_active).
"""
import shlex
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _lib import allow, block, glob_match, load_config, project_dir, read_event  # noqa: E402


def changed_files(root: Path) -> list[str]:
    r = subprocess.run(["git", "status", "--porcelain"], cwd=root, capture_output=True, text=True)
    return [ln[3:].strip() for ln in r.stdout.splitlines() if ln]


def main() -> None:
    event = read_event()
    if event.get("stop_hook_active"):
        allow()
    root = project_dir(event)
    cfg = load_config(root)
    cmd = cfg.get("test_command")
    if not cmd:
        allow()
    globs = cfg.get("test_trigger_globs", ["*"])
    if not any(glob_match(f, globs) for f in changed_files(root)):
        allow()
    r = subprocess.run(shlex.split(cmd), cwd=root, capture_output=True, text=True, timeout=1500)
    if r.returncode != 0:
        block(f"tests are red ({cmd}). Fix them before finishing:\n{(r.stdout + r.stderr)[-2000:]}")
    allow()


if __name__ == "__main__":
    main()
