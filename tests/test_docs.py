"""@trace FR-050 (README), FR-051 (AGENTS.md/CLAUDE.md) — delivery docs.

Unit: asserts the repo's front-door docs exist and carry the required content.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_readme_explains_and_runs_the_project():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    low = readme.lower()
    assert "askdocs" in low  # what it is
    # why it exists: grounded / cited / honest-miss idea
    assert any(k in low for k in ("цит", "джерел", "cite", "sourc", "grounded"))
    # how to run it: the compose commands
    assert "docker compose" in low
    assert "askdocs.cli" in readme


def test_agent_rules_present_and_wired():
    assert (ROOT / "AGENTS.md").exists()
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "askdocs" in agents.lower()
    # CLAUDE.md points at AGENTS.md so every tool resolves the same rules
    claude = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert "AGENTS.md" in claude
