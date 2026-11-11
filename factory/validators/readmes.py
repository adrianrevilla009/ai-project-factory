"""Keep READMEs and docs truthful.

- Every directory in REQUIRED_READMES has a README with real content (no placeholder wording).
- Counts stated in prose ("490 skills", "28 agentes", ...) match the repository.
- Relative markdown links in READMEs and docs resolve.

Not required: .claude/agents, .claude/commands and .claude/skills. Claude Code registers every .md under
agents/ and commands/ as an agent or a command, so a README there would become one; those folders are
documented in .claude/README.md.
"""
import re
import sys
from pathlib import Path

from common import REPO_ROOT, Finding, rel

REQUIRED_READMES = [
    ".claude", ".claude/hooks", ".devcontainer", ".github", "capabilities", "catalog", "catalog/adr",
    "catalog/golden-paths", "compliance-framework", "docs", "docs/architecture", "docs/operating-model",
    "domain-framework", "factory", "factory/validators", "gates", "gates/checklists", "knowledge", "policies",
    "policies/semgrep", "policies/opa-conftest", "policies/kyverno", "policies/archunit",
    "policies/frontend-boundaries", "policies/maven-enforcer", "policies/iac-checks", "prompts", "standards",
    "tests", "tests/hooks", "tests/validators", "tests/semgrep", "tests/agent-evals",
]
PLACEHOLDERS = re.compile(r"[Cc]ontenido pendiente|[Ee]structura creada|Oleada|\bTODO\b|[Ll]orem ipsum")
MIN_LINES = 5


def counts(root: Path) -> dict[str, int]:
    return {
        "skills": len([p for p in (root / ".claude" / "skills").glob("*/SKILL.md") if p.parent.name != "_template"]),
        "agentes": len(list((root / ".claude" / "agents").glob("*/*.md"))),
        "comandos": len(list((root / ".claude" / "commands").glob("*/*.md"))),
        "hooks": len([p for p in (root / ".claude" / "hooks").glob("*/*.py")]),
        "ADR": len(list((root / "catalog" / "adr").glob("[0-9][0-9][0-9][0-9]-*.md"))),
        "gates": len(list((root / "gates").glob("gate-[0-9]-*.md"))),
    }


CLAIM = re.compile(r"\b(\d+)\s+(skills|agentes|comandos|hooks|ADR|gates)\b")
LINK = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")


def doc_files(root: Path):
    for p in sorted(root.rglob("*.md")):
        parts = set(p.relative_to(root).parts)
        if parts & {".git", ".pytest_cache", "skills", "standards"} or p.name == "FACTORY_BRIEF.md":
            continue
        if p.name in {"CHANGELOG.md", "skills-index.md"}:
            continue
        yield p


def validate_all(root: Path = REPO_ROOT) -> list[Finding]:
    findings = []
    for d in REQUIRED_READMES:
        readme = root / d / "README.md"
        if not readme.exists():
            findings.append(Finding(d, "README.md missing"))
            continue
        text = readme.read_text()
        if len(text.strip().splitlines()) < MIN_LINES:
            findings.append(Finding(rel(root, readme), f"README too short (< {MIN_LINES} lines)"))
        m = PLACEHOLDERS.search(text)
        if m and m.group(0) != "todo":
            findings.append(Finding(rel(root, readme), f"placeholder or obsolete wording: '{m.group(0)}'"))
    actual = counts(root)
    for p in doc_files(root):
        text = p.read_text()
        for n, kind in CLAIM.findall(text):
            if int(n) != actual[kind] and not (kind == "hooks" and int(n) <= actual[kind] and "casos" in text):
                findings.append(Finding(rel(root, p), f"states {n} {kind}, but there are {actual[kind]}"))
        for target in LINK.findall(text):
            if target.startswith(("http", "mailto")):
                continue
            if not (p.parent / target).resolve().exists():
                findings.append(Finding(rel(root, p), f"broken link: {target}"))
    return findings


if __name__ == "__main__":
    out = validate_all()
    for f in out:
        print(f)
    sys.exit(1 if out else 0)
