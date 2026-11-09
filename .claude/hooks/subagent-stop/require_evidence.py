#!/usr/bin/env python3
"""SubagentStop: reviewers and testers must close with evidence (file:line, command output or a report path)."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _lib import allow, block, load_config, project_dir, read_event  # noqa: E402

DEFAULT_AGENTS = [
    "code-reviewer", "security-reviewer", "architecture-guardian", "cloud-readiness-reviewer",
    "qa-engineer", "performance", "chaos", "eval-engineer",
]
FILE_LINE = re.compile(r"[\w./-]+\.\w+:\d+")
MARKER = re.compile(r"(?i)\b(evidencia|evidence)\b")


def main() -> None:
    event = read_event()
    if event.get("stop_hook_active"):
        allow()  # never loop
    cfg = load_config(project_dir(event)).get("subagent_evidence", {})
    if event.get("agent_type") not in cfg.get("agents", DEFAULT_AGENTS):
        allow()
    msg = str(event.get("last_assistant_message", ""))
    if MARKER.search(msg) or FILE_LINE.search(msg):
        allow()
    block("falta evidencia: añade una sección 'Evidencia' con rutas fichero:línea, comandos ejecutados y su resultado, o di explícitamente que no pudiste comprobarlo.")


if __name__ == "__main__":
    main()
