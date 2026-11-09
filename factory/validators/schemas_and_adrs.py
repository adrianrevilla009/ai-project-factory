"""Validate that JSON/YAML schemas parse as valid JSON Schema and that every decision has an ADR."""
import json
import re
import sys
from pathlib import Path

import jsonschema
import yaml

from common import REPO_ROOT, Finding, rel

SCHEMA_FILES = [
    "gates/approval-record.schema.json",
    "domain-framework/domain-profile.schema.yaml",
    "domain-framework/assumptions-register.schema.yaml",
    "compliance-framework/regulation-entry.schema.yaml",
    "compliance-framework/obligation-to-control-mapping.schema.yaml",
]
YAML_FILES = ["capabilities/capabilities.yaml", "capabilities/modules-map.yaml", "compliance-framework/applicability-questionnaire.yaml"]
ADR_REQUIRED = range(1, 28)  # D1..D27
ADR_STATUS = re.compile(r"\*\*Estado:\*\*\s*(aceptado|propuesto|rechazado|sustituido)", re.I)


def validate_schemas(root: Path = REPO_ROOT) -> list[Finding]:
    out = []
    for f in SCHEMA_FILES:
        p = root / f
        if not p.exists():
            out.append(Finding(f, "schema missing"))
            continue
        try:
            data = json.loads(p.read_text()) if p.suffix == ".json" else yaml.safe_load(p.read_text())
            jsonschema.Draft202012Validator.check_schema(data)
        except Exception as e:  # noqa: BLE001
            out.append(Finding(f, f"invalid schema: {str(e).splitlines()[0]}"))
    for f in YAML_FILES:
        p = root / f
        try:
            yaml.safe_load(p.read_text())
        except Exception as e:  # noqa: BLE001
            out.append(Finding(f, f"invalid YAML: {e}"))
    return out


def validate_adrs(root: Path = REPO_ROOT) -> list[Finding]:
    out = []
    d = root / "catalog" / "adr"
    files = {int(m.group(1)): p for p in d.glob("[0-9][0-9][0-9][0-9]-*.md") if (m := re.match(r"(\d{4})-", p.name))}
    for n in ADR_REQUIRED:
        if n not in files:
            out.append(Finding("catalog/adr", f"ADR for decision D{n} (ADR-{n:04d}) missing"))
    for n, p in files.items():
        if not ADR_STATUS.search(p.read_text(encoding="utf-8")):
            out.append(Finding(rel(root, p), "ADR has no valid '**Estado:**' line"))
    return out


if __name__ == "__main__":
    findings = validate_schemas() + validate_adrs()
    for f in findings:
        print(f)
    sys.exit(1 if findings else 0)


def validate_mcp_catalog(root: Path = REPO_ROOT) -> list[Finding]:
    """catalog/mcp-servers.yaml: known roles and skills, pinned versions, no literal secrets, no cloud credentials by default."""
    path = root / "catalog" / "mcp-servers.yaml"
    if not path.exists():
        return []
    name = rel(root, path)
    data = yaml.safe_load(path.read_text()) or {}
    agents = {p.stem for p in (root / ".claude" / "agents").glob("*/*.md")}
    skills = {p.parent.name for p in (root / ".claude" / "skills").glob("*/SKILL.md")}
    findings, seen = [], set()
    for s in data.get("servers", []):
        sid = s.get("id", "?")
        if sid in seen:
            findings.append(Finding(name, f"{sid}: duplicate id"))
        seen.add(sid)
        for key in ("purpose", "transport", "launch", "registry", "access", "credentials", "data_leaves_machine", "roles", "default"):
            if key not in s:
                findings.append(Finding(name, f"{sid}: missing '{key}'"))
        if s.get("access") not in ("read-only", "read-write"):
            findings.append(Finding(name, f"{sid}: access must be read-only or read-write"))
        if s.get("credentials") not in ("none", "token", "cloud"):
            findings.append(Finding(name, f"{sid}: credentials must be none, token or cloud"))
        if s.get("credentials") == "cloud" and s.get("default"):
            findings.append(Finding(name, f"{sid}: cloud credentials cannot be a default server (ADR-0004)"))
        launch = json.dumps(s.get("launch", {}))
        if re.search(r"@latest|:latest", launch):
            findings.append(Finding(name, f"{sid}: never use 'latest'; pin the version in the project BOM"))
        for value in re.findall(r'"(?:Authorization|[A-Z_]*(?:TOKEN|KEY|SECRET|URI))": "([^"]*)"', launch):
            if value and "${" not in value:
                findings.append(Finding(name, f"{sid}: credential values must be ${{VAR}} references"))
        for r in s.get("roles", []):
            if r not in agents:
                findings.append(Finding(name, f"{sid}: unknown agent role '{r}'"))
        for sk in s.get("skills", []):
            if sk not in skills:
                findings.append(Finding(name, f"{sid}: unknown skill '{sk}'"))
    return findings


def validate_knowledge_links(root: Path = REPO_ROOT) -> list[Finding]:
    """knowledge/*.md: every backticked kebab-case token must be an existing skill; ADR-NNNN mentions must exist."""
    skills = {p.parent.name for p in (root / ".claude" / "skills").glob("*/SKILL.md")}
    adrs = {m.group(1) for p in (root / "catalog" / "adr").glob("[0-9]*.md") if (m := re.match(r"(\d{4})", p.name))}
    findings = []
    for f in sorted((root / "knowledge").glob("*.md")):
        text = f.read_text()
        for token in sorted(set(re.findall(r"`([a-z0-9]+(?:-[a-z0-9]+)+)`", text))):
            if token not in skills:
                findings.append(Finding(rel(root, f), f"unknown skill '{token}'"))
        for num in sorted(set(re.findall(r"ADR-(\d{4})", text))):
            if num not in adrs:
                findings.append(Finding(rel(root, f), f"unknown ADR-{num}"))
    return findings
