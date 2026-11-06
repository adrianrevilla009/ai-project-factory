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
