#!/usr/bin/env python3
"""PreToolUse: block writing secrets or secret-bearing files."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _lib import allow, block, read_event, relative_to_project, target_path, written_text  # noqa: E402

SECRET_PATTERNS = {
    "AWS access key id": re.compile(r"\b(AKIA|ASIA)[0-9A-Z]{16}\b"),
    "private key block": re.compile(r"-----BEGIN (RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY"),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    "Slack token": re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b"),
    "Anthropic/OpenAI style key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "hardcoded credential": re.compile(
        r"""(?ix)\b(password|passwd|secret|api[_-]?key|token)\b\s*[:=]\s*["'][^"'\s${}]{8,}["']"""),
}
# Well-known documentation placeholders are not secrets.
ALLOWED_VALUES = ("AKIAIOSFODNN7EXAMPLE", "changeme", "example", "placeholder", "<redacted>")
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
    for label, rx in SECRET_PATTERNS.items():
        for m in rx.finditer(text):
            if any(a.lower() in m.group(0).lower() for a in ALLOWED_VALUES):
                continue
            block(f"possible secret detected ({label}). Use Vault/env references instead of literals.")
    allow()


if __name__ == "__main__":
    main()
