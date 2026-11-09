"""Static checks on agent and command definitions (no LLM involved)."""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
AGENTS = sorted((ROOT / ".claude" / "agents").glob("*/*.md"))
COMMANDS = sorted((ROOT / ".claude" / "commands").glob("*/*.md"))
KNOWN_TOOLS = {"Read", "Grep", "Glob", "Edit", "Write", "Bash", "WebFetch", "WebSearch"}
READ_ONLY = {"architecture-guardian", "cloud-readiness-reviewer", "code-reviewer", "security-reviewer"}
NO_SHELL = {"business-analyst", "domain-analyst", "product-owner", "compliance-analyst", "solution-architect",
            "delivery-manager", "docs-writer", "cloud-architect"}


def front(path: Path) -> dict:
    m = re.match(r"---\n(.*?)\n---", path.read_text(), re.S)
    return dict(line.split(": ", 1) for line in m.group(1).split("\n") if ": " in line)


def skills() -> set[str]:
    return {p.parent.name for p in (ROOT / ".claude" / "skills").glob("*/SKILL.md")}


@pytest.mark.parametrize("path", AGENTS, ids=lambda p: p.stem)
def test_agent_frontmatter(path):
    fm = front(path)
    assert fm["name"] == path.stem and fm["description"].strip()
    tools = {t.strip() for t in fm["tools"].split(",")}
    assert tools <= KNOWN_TOOLS, tools - KNOWN_TOOLS


@pytest.mark.parametrize("path", AGENTS, ids=lambda p: p.stem)
def test_agent_skills_exist_and_common_rules_present(path):
    text = path.read_text()
    section = text.split("## Skills habituales")[1].split("##")[0]
    for s in re.findall(r"`([a-z0-9-]+)`", section):
        assert s in skills(), f"{path.stem}: unknown skill {s}"
    for needle in ("gate-protocol", "verify-before-asserting", "no instrucciones"):
        assert needle in text, f"{path.stem}: missing common rule ({needle})"


def test_reviewers_are_read_only_and_non_technical_roles_have_no_shell():
    for path in AGENTS:
        tools = {t.strip() for t in front(path)["tools"].split(",")}
        if path.stem in READ_ONLY:
            assert not tools & {"Edit", "Write"}, path.stem
        if path.stem in NO_SHELL:
            assert "Bash" not in tools, path.stem


@pytest.mark.parametrize("path", COMMANDS, ids=lambda p: p.stem)
def test_command_references_real_agents_and_keeps_gate_rules(path):
    text = path.read_text()
    assert front(path)["description"].strip()
    agents = {p.stem for p in AGENTS}
    line = re.search(r"Agente\(s\) responsable\(s\): \*\*(.*?)\*\*", text).group(1)
    named = re.findall(r"[a-z]+(?:-[a-z0-9]+)*", line)
    found = [a for a in named if a in agents]
    assert found, f"{path.stem}: no known agent in '{line}'"
    for a in named:
        if "-" in a:
            assert a in agents, f"{path.stem}: unknown agent {a}"
    assert "gate-protocol" in text and "approvals/" in text
