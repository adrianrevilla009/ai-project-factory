"""Tests for factory validators: they must catch malformed skills and dishonest AWS claims."""
import shutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "factory" / "validators"))

import code_blocks  # noqa: E402
import honest_claims  # noqa: E402
import schemas_and_adrs  # noqa: E402
import skill_structure  # noqa: E402

GOOD_SKILL = (ROOT / ".claude" / "skills" / "n-plus-one" / "SKILL.md").read_text()


def make_skill(tmp_path, text, name="demo"):
    d = tmp_path / ".claude" / "skills" / name
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text(text)
    return d / "SKILL.md"


# ------------------------------------------------------------- skill_structure
def test_repo_skills_are_valid():
    errors = [f for f in skill_structure.validate_all(ROOT) if f.severity == "error"]
    assert errors == []


def test_valid_skill_passes(tmp_path):
    text = GOOD_SKILL.replace("name: n-plus-one", "name: demo")
    assert skill_structure.validate_skill(make_skill(tmp_path, text), tmp_path) == []


def test_missing_frontmatter(tmp_path):
    f = skill_structure.validate_skill(make_skill(tmp_path, "# no frontmatter\n"), tmp_path)
    assert any("frontmatter" in x.message for x in f)


def test_name_must_match_folder(tmp_path):
    f = skill_structure.validate_skill(make_skill(tmp_path, GOOD_SKILL), tmp_path)  # name n-plus-one in folder demo
    assert any("must equal folder name" in x.message for x in f)


def test_long_description_rejected(tmp_path):
    text = GOOD_SKILL.replace("name: n-plus-one", "name: demo")
    text = text.replace("description: Usar", "description: " + "x" * 250 + " Usar", 1)
    assert any("too long" in x.message for x in skill_structure.validate_skill(make_skill(tmp_path, text), tmp_path))


def test_missing_sections_detected(tmp_path):
    text = "---\nname: demo\ndescription: algo\nmetadata:\n  block: b\n  tier: T1\n  owner: o\n  last_reviewed: 2026-01-01\n  enforcement: hook\n---\n# Demo\n\n## Reglas\n- x\n```java\n```\n"
    msgs = [x.message for x in skill_structure.validate_skill(make_skill(tmp_path, text), tmp_path)]
    for s in ("cuándo aplicar", "por qué", "checklist de revisión", "enforcement", "relacionados/fuentes"):
        assert any(s in m for m in msgs), s


def test_bad_tier_and_date(tmp_path):
    text = GOOD_SKILL.replace("name: n-plus-one", "name: demo").replace("tier: T1", "tier: T9").replace('last_reviewed: "2026-11-06"', 'last_reviewed: "ayer"')
    msgs = [x.message for x in skill_structure.validate_skill(make_skill(tmp_path, text), tmp_path)]
    assert any("tier" in m for m in msgs) and any("last_reviewed" in m for m in msgs)


def test_enforcement_without_mechanism_rejected(tmp_path):
    text = GOOD_SKILL.replace("name: n-plus-one", "name: demo")
    start = text.index("## Enforcement")
    end = text.index("## Relacionados")
    text = text[:start] + "## Enforcement\nSe espera que el equipo lo recuerde.\n\n" + text[end:]
    assert any("no mechanism" in x.message for x in skill_structure.validate_skill(make_skill(tmp_path, text), tmp_path))


def test_missing_code_examples_rejected(tmp_path):
    text = GOOD_SKILL.replace("name: n-plus-one", "name: demo").replace("```", "")
    assert any("code examples" in x.message for x in skill_structure.validate_skill(make_skill(tmp_path, text), tmp_path))


def test_missing_skill_md_reported(tmp_path):
    (tmp_path / ".claude" / "skills" / "empty").mkdir(parents=True)
    (tmp_path / "CLAUDE.md").write_text("x\n")
    assert any("SKILL.md missing" in f.message for f in skill_structure.validate_all(tmp_path))


# --------------------------------------------------------------- honest_claims
@pytest.mark.parametrize(
    "line",
    [
        "El módulo EKS está listo para producción en AWS.",
        "Esta infraestructura está lista para producción en AWS",
        "The stack is production-ready on AWS.",
        "Terraform probado en AWS real.",
        "Validated in AWS with a sandbox account.",
        "Despliegue verificado en AWS.",
        "Our Terraform is battle-tested in AWS.",
    ],
)
def test_dishonest_claims_detected(line):
    assert honest_claims.scan_text(line, "x.md"), line


@pytest.mark.parametrize(
    "line",
    [
        "Preparado para AWS, no verificado en real.",
        "Validado estáticamente (nivel 2).",
        "No está listo para producción en AWS.",
        "Prohibido afirmar 'listo para producción en AWS'.",
        "El servicio es production-ready en local con tests.",
        "Ejemplo malo: listo para producción en AWS  # honest-claims: ignore",
    ],
)
def test_honest_text_passes(line):
    assert honest_claims.scan_text(line, "x.md") == [], line


def test_repo_has_no_dishonest_claims():
    assert honest_claims.scan_repo(ROOT) == []


def test_scan_repo_flags_file(tmp_path):
    (tmp_path / "README.md").write_text("Todo está listo para producción en AWS.\n")
    assert len(honest_claims.scan_repo(tmp_path)) == 1


def test_terraform_dir_requires_maturity_label(tmp_path):
    (tmp_path / "infra").mkdir()
    (tmp_path / "infra" / "main.tf").write_text("# tf\n")
    assert honest_claims.scan_repo(tmp_path)
    (tmp_path / "infra" / "README.md").write_text("Madurez: validado estáticamente; preparado para AWS, no verificado en real.\n")
    assert honest_claims.scan_repo(tmp_path) == []


# ------------------------------------------------------------ schemas_and_adrs
def test_repo_schemas_and_adrs_valid():
    assert schemas_and_adrs.validate_schemas(ROOT) == []
    assert schemas_and_adrs.validate_adrs(ROOT) == []


def test_missing_adr_detected(tmp_path):
    shutil.copytree(ROOT / "catalog" / "adr", tmp_path / "catalog" / "adr")
    next((tmp_path / "catalog" / "adr").glob("0005-*.md")).unlink()
    assert any("D5" in f.message for f in schemas_and_adrs.validate_adrs(tmp_path))


# ------------------------------------------------------------------ build_index
def test_generated_index_and_standards_are_fresh():
    import subprocess
    r = subprocess.run([sys.executable, str(ROOT / "factory" / "tools" / "build_index.py"), "--check"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout


# ----------------------------------------------------------------- code_blocks
def test_repo_code_blocks_are_valid():
    assert code_blocks.validate_all(ROOT) == []


@pytest.mark.parametrize(
    "lang,code",
    [("yaml", "a: b: c\n"), ("json", "{\"a\": 1, }"), ("bash", "if then\n"), ("xml", "<a><b></a>"), ("python", "x = (")],
)
def test_invalid_blocks_detected(lang, code):
    assert code_blocks.check_block(lang, code)


@pytest.mark.parametrize("lang,code", [("yaml", "a: 1\n"), ("json", "{}"), ("bash", "echo hi\n"), ("xml", "<a/><b/>"), ("python", "x = 1"), ("java", "class {")])
def test_valid_or_unchecked_blocks_pass(lang, code):
    assert code_blocks.check_block(lang, code) is None


def test_block_can_opt_out():
    text = "<!-- code-block: ignore -->\n```json\n{bad\n```\n"
    assert code_blocks.validate_text(text, "x.md") == []
    assert code_blocks.validate_text(text.replace("<!-- code-block: ignore -->", "texto"), "x.md")


# ----------------------------------------------------------------- mcp catalog
def test_repo_mcp_catalog_is_valid():
    assert schemas_and_adrs.validate_mcp_catalog(ROOT) == []


def test_mcp_catalog_rejects_latest_and_literal_secrets(tmp_path):
    (tmp_path / ".claude" / "agents" / "x").mkdir(parents=True)
    (tmp_path / ".claude" / "agents" / "x" / "dba.md").write_text("x")
    (tmp_path / ".claude" / "skills" / "git-workflow").mkdir(parents=True)
    (tmp_path / ".claude" / "skills" / "git-workflow" / "SKILL.md").write_text("x")
    (tmp_path / "catalog").mkdir()
    base = {"id": "s", "purpose": "p", "transport": "stdio", "registry": {}, "access": "read-only",
            "credentials": "none", "data_leaves_machine": False, "roles": ["dba"], "default": False}
    bad = dict(base, launch={"command": "npx", "args": ["pkg@latest"], "env": {"API_TOKEN": "abc123"}}, roles=["ghost"], skills=["nope"])
    (tmp_path / "catalog" / "mcp-servers.yaml").write_text(__import__("yaml").safe_dump({"servers": [bad]}))
    msgs = " ".join(f.message for f in schemas_and_adrs.validate_mcp_catalog(tmp_path))
    for needle in ("latest", "${VAR}", "unknown agent role", "unknown skill"):
        assert needle in msgs, needle
    good = dict(base, launch={"command": "npx", "args": ["pkg@1.0.0"], "env": {"API_TOKEN": "${TOKEN}"}}, skills=["git-workflow"])
    (tmp_path / "catalog" / "mcp-servers.yaml").write_text(__import__("yaml").safe_dump({"servers": [good]}))
    assert schemas_and_adrs.validate_mcp_catalog(tmp_path) == []


def test_cloud_credentials_cannot_be_default(tmp_path):
    (tmp_path / "catalog").mkdir()
    s = {"id": "s", "purpose": "p", "transport": "stdio", "launch": {}, "registry": {}, "access": "read-only",
         "credentials": "cloud", "data_leaves_machine": False, "roles": [], "default": True}
    (tmp_path / "catalog" / "mcp-servers.yaml").write_text(__import__("yaml").safe_dump({"servers": [s]}))
    assert any("cloud credentials" in f.message for f in schemas_and_adrs.validate_mcp_catalog(tmp_path))
