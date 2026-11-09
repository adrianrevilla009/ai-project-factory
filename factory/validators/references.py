"""Check cross-references inside skills.

- Backticked kebab-case tokens on cross-reference lines (Relacionados, "ver `x`", "Skills relacionados")
  must be an existing skill, agent or command.
- Backticked paths under factory-only roots (policies/, catalog/, factory/, ...) must exist, unless the line
  says "pendiente" (the artefact is declared as not written yet).
Paths under docs/ are skipped: they usually refer to files of the generated project.
"""
import re
import sys
from pathlib import Path

from common import REPO_ROOT, Finding, rel

ROOTS = ("policies/", "catalog/", "factory/", "capabilities/", "gates/", "knowledge/", "tests/", "prompts/",
         "domain-framework/", "compliance-framework/", "standards/", ".claude/")
VER_LIST = re.compile(r"(?i)(?:\bver|véase)\s+((?:`[^`\n]+`(?:,\s*|\s+y\s+|\s*)?)+)")
RUNTIME = (".claude/audit/",)  # created while an agent works, never committed
KEBAB = re.compile(r"[a-z0-9]+(-[a-z0-9]+)+")


def names(root: Path) -> set[str]:
    out = {p.parent.name for p in (root / ".claude" / "skills").glob("*/SKILL.md")}
    out |= {p.stem for p in (root / ".claude" / "agents").glob("*/*.md")}
    out |= {p.stem for p in (root / ".claude" / "commands").glob("*/*.md")}
    return out


def validate_text(text: str, path: str, root: Path, known: set[str]) -> list[Finding]:
    findings = []
    for n, line in enumerate(text.split("\n"), 1):
        pending = "pendiente" in line.lower() or "honest-claims: ignore" in line
        xref_tokens = set()
        if "relacionad" in line.lower():
            xref_tokens = set(re.findall(r"`([^`\n]+)`", line))
        else:
            for lst in VER_LIST.findall(line):
                xref_tokens |= set(re.findall(r"`([^`\n]+)`", lst))
        for m in re.finditer(r"`([^`\n]+)`", line):
            tok = m.group(1)
            if tok in xref_tokens and KEBAB.fullmatch(tok) and tok not in known:
                findings.append(Finding(f"{path}:{n}", f"cross-reference to unknown skill '{tok}'"))
            if tok.startswith(ROOTS) and not tok.startswith(RUNTIME) and not pending:
                p = tok.split("#")[0].split(" ")[0].rstrip("/.,;:)")
                if any(c in p for c in "*<{") or "NNNN" in p or p.endswith("-N.md"):
                    continue
                if not (root / p).exists():
                    findings.append(Finding(f"{path}:{n}", f"path does not exist: {p}"))
    return findings


def validate_all(root: Path = REPO_ROOT) -> list[Finding]:
    known = names(root)
    findings = []
    for f in sorted((root / ".claude" / "skills").glob("*/SKILL.md")):
        findings += validate_text(f.read_text(), rel(root, f), root, known)
    return findings


if __name__ == "__main__":
    out = validate_all()
    for f in out:
        print(f)
    sys.exit(1 if out else 0)
