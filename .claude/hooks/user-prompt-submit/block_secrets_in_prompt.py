#!/usr/bin/env python3
"""UserPromptSubmit: refuse a prompt that contains a secret, before it reaches the model or the transcript."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from _lib import allow, find_secret, read_event  # noqa: E402


def main() -> None:
    event = read_event()
    label = find_secret(str(event.get("prompt", "")))
    if not label:
        allow()
    reason = f"El prompt parece contener un secreto ({label}). Quítalo y usa una referencia (variable de entorno o Vault); si ya es real, rótalo."
    print(json.dumps({"decision": "block", "reason": reason}))
    sys.exit(0)


if __name__ == "__main__":
    main()
