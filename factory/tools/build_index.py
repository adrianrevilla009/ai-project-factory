"""Generate docs/skills-index.md (per block/tier) and report coverage against catalog/skills-inventory.yaml.

Usage: python3 factory/tools/build_index.py [--check]   (--check fails if the committed index is stale)
"""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
FM = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def load_skills():
    out = {}
    for d in sorted((ROOT / ".claude" / "skills").iterdir()):
        f = d / "SKILL.md"
        if d.name.startswith("_") or not f.exists():
            continue
        m = FM.match(f.read_text(encoding="utf-8"))
        if m:
            fm = yaml.safe_load(m.group(1)) or {}
            out[d.name] = fm
    return out


def build() -> tuple[str, list[str]]:
    inv = yaml.safe_load((ROOT / "catalog" / "skills-inventory.yaml").read_text())
    skills = load_skills()
    expected = {s["name"] for b in inv["blocks"] for s in b["skills"]}
    missing = sorted(expected - set(skills))
    extra = sorted(set(skills) - expected)
    lines = ["# Índice de skills", "", "> Generado por `factory/tools/build_index.py`. No editar a mano.", "",
             f"Skills: **{len(skills)}** de {len(expected)} previstos en `catalog/skills-inventory.yaml`.", ""]
    by_block = {}
    for name, fm in skills.items():
        by_block.setdefault((fm.get("metadata") or {}).get("block", "sin-bloque"), []).append((name, fm))
    for b in inv["blocks"]:
        items = sorted(by_block.get(b["block"], []))
        lines += [f"## {b['block']} ({b['tier']}) — {len(items)}/{len(b['skills'])}", ""]
        for name, fm in items:
            t = (fm.get("metadata") or {}).get("tier", "?")
            lines.append(f"- `{name}` ({t}) — {fm.get('description', '')}")
        lines.append("")
    if extra:
        lines += ["## Fuera del inventario", ""] + [f"- `{n}`" for n in extra] + [""]
    return "\n".join(lines), missing


def rules_of(name: str) -> str:
    body = (ROOT / ".claude" / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
    m = re.search(r"^##\s+Reglas\s*$(.*?)(?=^##\s)", body, re.M | re.S)
    return m.group(1).strip() if m else ""


def build_standards() -> dict[str, str]:
    """One human-readable standards page per block, aggregated from each skill's Reglas section."""
    skills = load_skills()
    out = {}
    by_block = {}
    for name, fm in skills.items():
        by_block.setdefault((fm.get("metadata") or {}).get("block", "sin-bloque"), []).append(name)
    for block, names in sorted(by_block.items()):
        lines = [f"# Estándares · {block}", "", "> Generado desde los skills por `factory/tools/build_index.py`. La fuente de verdad es cada `SKILL.md`; no editar a mano.", ""]
        for n in sorted(names):
            lines += [f"## {n}", "", rules_of(n), ""]
        out[f"standards/{block}.md"] = "\n".join(lines)
    return out


def main() -> int:
    text, missing = build()
    out = ROOT / "docs" / "skills-index.md"
    standards = build_standards()
    if "--check" in sys.argv:
        stale = [] if out.exists() and out.read_text(encoding="utf-8") == text else ["docs/skills-index.md"]
        for rel, content in standards.items():
            f = ROOT / rel
            if not f.exists() or f.read_text(encoding="utf-8") != content:
                stale.append(rel)
        if stale:
            print("stale generated files (run python3 factory/tools/build_index.py):", *stale, sep="\n  ")
            return 1
        return 0
    out.write_text(text, encoding="utf-8")
    for rel, content in standards.items():
        (ROOT / rel).write_text(content, encoding="utf-8")
    print(f"index written; missing skills: {len(missing)}")
    for m in missing:
        print("  missing:", m)
    return 0


if __name__ == "__main__":
    sys.exit(main())
