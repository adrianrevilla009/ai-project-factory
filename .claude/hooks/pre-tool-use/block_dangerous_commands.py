#!/usr/bin/env python3
"""PreToolUse(Bash): block destructive or policy-violating shell commands.

Includes ADR-0004: the factory never deploys to AWS (terraform apply/destroy, aws mutating calls).
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _lib import allow, block, read_event  # noqa: E402

RULES = [
    (r"\brm\s+(-[a-zA-Z]*[rR][a-zA-Z]*\s+)+(-[a-zA-Z]+\s+)*(/|~|\$HOME|\*|\.\.?)(\s|/?$)", "recursive delete of root/home/cwd"),
    (r"\bgit\s+push\b.*(\s--force\b|\s-f\b|--force-with-lease)", "force push"),
    (r"\bgit\s+reset\s+--hard\b", "git reset --hard"),
    (r"\bgit\s+clean\s+-[a-zA-Z]*f", "git clean -f"),
    (r"\bgit\s+(commit|push|merge)\b.*--no-verify", "skipping git hooks"),
    (r"(curl|wget)\b[^|;]*\|\s*(sudo\s+)?(ba|z)?sh\b", "pipe from network to shell"),
    (r"\bchmod\s+(-R\s+)?777\b", "chmod 777"),
    (r"\b(mkfs(\.\w+)?|dd\s+.*of=/dev/)", "disk-destroying command"),
    (r":\(\)\s*\{\s*:\|:&\s*\};:", "fork bomb"),
    (r"\bterraform\s+(apply|destroy|import|state\s+(rm|push))\b", "terraform mutation: the factory never deploys (ADR-0004)"),
    (r"\btofu\s+(apply|destroy)\b", "tofu mutation: the factory never deploys (ADR-0004)"),
    (r"\baws\s+\S+\s+(create|delete|put|update|terminate|run|start|stop|modify|attach|detach)[-\w]*", "mutating AWS CLI call: the factory never deploys (ADR-0004)"),
    (r"\bkubectl\s+(delete|apply)\b.*--all-namespaces|\bkubectl\s+delete\s+(ns|namespace)\b", "broad kubectl deletion"),
    (r"\bdocker\s+system\s+prune\b.*(-a|--all)", "docker system prune -a"),
    (r">\s*/dev/sd[a-z]", "write to block device"),
]
COMPILED = [(re.compile(p), why) for p, why in RULES]


def main() -> None:
    event = read_event()
    if event.get("tool_name") != "Bash":
        allow()
    cmd = (event.get("tool_input") or {}).get("command", "")
    if not isinstance(cmd, str):
        block("command is not a string (fail closed)")
    for rx, why in COMPILED:
        if rx.search(cmd):
            block(f"dangerous command ({why}). Ask the human to run it if truly needed.")
    allow()


if __name__ == "__main__":
    main()
