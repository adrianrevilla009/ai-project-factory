"""Validate the structure of skills (brief section 4.2) and CLAUDE.md length."""
import re
import sys
from datetime import date
from pathlib import Path

import yaml

from common import REPO_ROOT, Finding

REQUIRED_SECTIONS = [
    ("cuándo aplicar", r"cu[aá]ndo aplicar"),
    ("reglas", r"reglas"),
    ("por qué", r"por qu[eé]"),
    ("ejemplos", r"ejemplos"),
    ("criterios de decisión y trampas", r"criterios de decisi[oó]n"),
    ("checklist de revisión", r"checklist"),
    ("enforcement", r"enforcement"),
    ("relacionados/fuentes", r"relacionados|fuentes"),
]
REQUIRED_META = ["block", "tier", "owner", "last_reviewed", "enforcement"]
MAX_DESCRIPTION = 200
MAX_SKILL_LINES = 400
MAX_CLAUDE_MD_LINES = 80
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def parse(text: str):
    m = FRONTMATTER.match(text)
    if not m:
        return None, text
    try:
        return yaml.safe_load(m.group(1)) or {}, text[m.end():]
    except yaml.YAMLError:
        return "invalid", text[m.end():]


def validate_skill(path: Path, root: Path = REPO_ROOT) -> list[Finding]:
    rel = path.relative_to(root).as_posix() if path.is_relative_to(root) else str(path)
    out: list[Finding] = []
    err = lambda m: out.append(Finding(rel, m))  # noqa: E731
    text = path.read_text(encoding="utf-8")
    fm, body = parse(text)
    if fm is None:
        return [Finding(rel, "missing YAML frontmatter")]
    if fm == "invalid" or not isinstance(fm, dict):
        return [Finding(rel, "invalid YAML frontmatter")]
    name = fm.get("name")
    if not name:
        err("frontmatter 'name' missing")
    elif name != path.parent.name:
        err(f"name '{name}' must equal folder name '{path.parent.name}'")
    desc = fm.get("description")
    if not isinstance(desc, str) or not desc.strip():
        err("frontmatter 'description' missing")
    elif len(desc) > MAX_DESCRIPTION:
        err(f"description too long ({len(desc)} > {MAX_DESCRIPTION}); must be short and precise")
    meta = fm.get("metadata")
    if not isinstance(meta, dict):
        err("frontmatter 'metadata' missing")
    else:
        for k in REQUIRED_META:
            if not meta.get(k):
                err(f"metadata.{k} missing")
        if meta.get("tier") and meta["tier"] not in {"T1", "T2", "T3"}:
            err("metadata.tier must be T1, T2 or T3")
        lr = meta.get("last_reviewed")
        if lr:
            try:
                date.fromisoformat(str(lr))
            except ValueError:
                err("metadata.last_reviewed must be YYYY-MM-DD")
    headings = [h.lower() for h in re.findall(r"^#{2,3}\s+(.+)$", body, re.M)]
    for label, rx in REQUIRED_SECTIONS:
        if not any(re.search(rx, h) for h in headings):
            err(f"missing required section: {label}")
    enf = re.search(r"^##\s+Enforcement\s*$(.*?)(?=^##\s|\Z)", body, re.M | re.S | re.I)
    if enf is not None:
        content = enf.group(1)
        has_row = re.search(r"^\|(?!\s*Mecanismo)(?!\s*-)[^|\n]+\|", content, re.M)
        if not (has_row or re.search(r"revisi[oó]n humana|human review", content, re.I)):
            err("Enforcement section declares no mechanism (a skill without enforcement is a suggestion)")
    if "```" not in body:
        err("no code examples found (good/bad examples required)")
    if text.count("\n") > MAX_SKILL_LINES:
        out.append(Finding(rel, f"longer than {MAX_SKILL_LINES} lines; move detail to references/", "warning"))
    return out


def validate_claude_md(root: Path = REPO_ROOT) -> list[Finding]:
    p = root / "CLAUDE.md"
    if not p.exists():
        return [Finding("CLAUDE.md", "missing")]
    n = p.read_text(encoding="utf-8").count("\n")
    if n > MAX_CLAUDE_MD_LINES:
        return [Finding("CLAUDE.md", f"{n} lines > {MAX_CLAUDE_MD_LINES}; keep it short", "warning")]
    return []


def validate_all(root: Path = REPO_ROOT) -> list[Finding]:
    out: list[Finding] = []
    skills_dir = root / ".claude" / "skills"
    if skills_dir.is_dir():
        for d in sorted(skills_dir.iterdir()):
            if not d.is_dir() or d.name.startswith("_"):
                continue
            f = d / "SKILL.md"
            if not f.exists():
                out.append(Finding(f"{d.relative_to(root).as_posix()}", "SKILL.md missing"))
            else:
                out += validate_skill(f, root)
    out += validate_claude_md(root)
    return out


if __name__ == "__main__":
    findings = validate_all()
    for f in findings:
        print(f)
    sys.exit(1 if any(f.severity == "error" for f in findings) else 0)
