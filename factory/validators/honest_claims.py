"""Reject dishonest claims about AWS (brief 4.6, ADR-0004).

The factory never deploys to AWS. Text must not claim that anything is production-ready,
tested or verified on real AWS. Correct wording: "preparado para AWS, no verificado en real".

A line may opt out with the marker `honest-claims: ignore` (e.g. when quoting a bad example).
Also checks that directories holding Terraform carry a maturity label in their README.
"""
import re
import sys
from pathlib import Path

from common import REPO_ROOT, Finding, iter_files, rel

FORBIDDEN = [
    r"list[oa]s?\s+para\s+producci[oó]n(\s+(en|sobre)\s+aws)?",
    r"production[- ]ready(\s+(on|in|for)\s+aws)?",
    r"(probad[oa]s?|testad[oa]s?|verificad[oa]s?|validad[oa]s?|desplegad[oa]s?)\s+(en|sobre)\s+(un\s+)?(entorno\s+)?(real\s+de\s+)?aws\s*(real)?",
    r"(tested|verified|validated|deployed|proven)\s+(on|in)\s+(real\s+|production\s+)?aws",
    r"battle[- ]tested\s+(on|in)\s+aws",
    r"funciona\s+en\s+aws\s+real",
]
# "listo para producción" alone is only forbidden near AWS/infra wording; keep the generic form scoped.
SCOPED = re.compile(r"(?i)\b(aws|terraform|eks|infra(estructura)?|cloud|nube)\b")
COMPILED = [re.compile(p, re.I) for p in FORBIDDEN]
# A mention directly preceded by a negation/prohibition ("no está listo...", "Prohibido afirmar '...'") is honest.
NEGATION_BEFORE = re.compile(
    r"(?i)(\bno\b|\bnunca\b|\bnot\b|\bnever\b|\bjam[aá]s\b|prohibid[oa]\b[^.]*|must not\b[^.]*|rechaza\b[^.]*|reject\w*\b[^.]*)"
    r"\W*(\b(est[aá]n?|es|son|is|are|estar|ser|be)\b\W*)?$"
)
IGNORE = "honest-claims: ignore"
EXCLUDED_FILES = {"docs/FACTORY_BRIEF.md"}  # the brief quotes forbidden phrases as examples
TEXT_SUFFIXES = (".md", ".yaml", ".yml", ".txt", ".tf", ".json", ".hcl", ".tpl", ".j2")
MATURITY_RX = re.compile(r"(?i)(no verificad[oa] en real|not verified (on|in) real|validad[oa] est[aá]ticamente|statically validated)")


def scan_text(text: str, path: str) -> list[Finding]:
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        if IGNORE in line:
            continue
        for rx in COMPILED:
            m = rx.search(line)
            if not m:
                continue
            generic = m.group(0).lower().startswith(("list", "production"))
            if generic and not (SCOPED.search(line) or "aws" in m.group(0).lower()):
                continue
            if NEGATION_BEFORE.search(line[: m.start()]):
                continue
            out.append(Finding(f"{path}:{i}", f"dishonest AWS claim '{m.group(0)}'. Use: 'preparado para AWS, no verificado en real'"))
            break
    return out


def scan_repo(root: Path = REPO_ROOT) -> list[Finding]:
    out: list[Finding] = []
    for p in iter_files(root, TEXT_SUFFIXES):
        r = rel(root, p)
        if r in EXCLUDED_FILES or r.startswith("tests/"):
            continue
        try:
            out += scan_text(p.read_text(encoding="utf-8"), r)
        except UnicodeDecodeError:
            continue
    # maturity labels: any directory with .tf files needs a README carrying the label
    tf_dirs = {p.parent for p in iter_files(root, (".tf",))}
    for d in sorted(tf_dirs):
        readme = d / "README.md"
        if not readme.exists() or not MATURITY_RX.search(readme.read_text(encoding="utf-8")):
            out.append(Finding(rel(root, d), "Terraform directory lacks a README with a maturity label ('validado estáticamente' / 'no verificado en real')"))
    return out


if __name__ == "__main__":
    findings = scan_repo()
    for f in findings:
        print(f)
    sys.exit(1 if findings else 0)
