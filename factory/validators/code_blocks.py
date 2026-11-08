"""Check that fenced code blocks in skills are syntactically valid.

Covers yaml, json, xml, python (compile), hcl/terraform (via `terraform fmt`, skipped if
terraform is absent) and bash (`bash -n`). Java and TypeScript are not checked: the skills
use them as illustrative fragments with `...` placeholders. A block opts out when the line before its opening fence contains
`code-block: ignore`.
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

from common import REPO_ROOT, Finding, rel

FENCE = re.compile(r"(?m)^([^\n]*)\n```(\w+)\n(.*?)```", re.S)


def check_block(lang: str, code: str) -> str | None:
    """Return an error message, or None when the block is valid (or not checked)."""
    lang = lang.lower()
    if lang in ("yaml", "yml"):
        try:
            list(yaml.safe_load_all(code))
        except yaml.YAMLError as e:
            return "invalid yaml: " + str(e).split("\n")[0]
    elif lang == "json":
        try:
            json.loads(code)
        except ValueError as e:
            return f"invalid json: {e}"
    elif lang == "xml":
        try:
            ET.fromstring("<r>" + re.sub(r"<\?xml[^>]*\?>", "", code) + "</r>")
        except ET.ParseError as e:
            return f"invalid xml: {e}"
    elif lang == "python":
        try:
            compile(code, "<block>", "exec")
        except SyntaxError as e:
            return f"invalid python: {e}"
    elif lang in ("hcl", "terraform") and shutil.which("terraform"):
        with tempfile.TemporaryDirectory() as d:
            Path(d, "a.tf").write_text(code)
            r = subprocess.run(["terraform", "fmt", "-check", "-no-color", d], capture_output=True, text=True)
            if "Error" in r.stderr:
                return "invalid hcl: " + r.stderr.strip().split("\n")[0]
    elif lang in ("bash", "sh", "shell"):
        r = subprocess.run(["bash", "-n"], input=code, capture_output=True, text=True)
        if r.returncode:
            return "invalid bash: " + r.stderr.strip().split("\n")[0]
    return None


def validate_text(text: str, path: str) -> list[Finding]:
    findings = []
    for m in FENCE.finditer(text):
        before, lang, code = m.groups()
        if "code-block: ignore" in before:
            continue
        err = check_block(lang, code)
        if err:
            line = text[: m.start()].count("\n") + 3
            findings.append(Finding(f"{path}:{line}", err))
    return findings


def validate_all(root: Path = REPO_ROOT) -> list[Finding]:
    findings = []
    for f in sorted((root / ".claude" / "skills").glob("*/SKILL.md")):
        findings += validate_text(f.read_text(), rel(root, f))
    return findings


if __name__ == "__main__":
    out = validate_all()
    for f in out:
        print(f)
    sys.exit(1 if out else 0)
