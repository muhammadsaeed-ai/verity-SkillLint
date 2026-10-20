from pathlib import Path

from skilllint.links import check_links


def test_valid_local_link_passes(tmp_path: Path):
    (tmp_path / "ref.md").write_text("# Reference", encoding="utf-8")
    path = tmp_path / "SKILL.md"
    findings = check_links("See [reference](ref.md).", path, "SKILL.md", tmp_path)
    assert findings == []


def test_broken_local_link_is_error(tmp_path: Path):
    path = tmp_path / "SKILL.md"
    findings = check_links("See [missing](missing.md).", path, "SKILL.md", tmp_path)
    assert len(findings) == 1
    assert findings[0].rule_id == "SLLINK001"
    assert findings[0].severity == "error"


def test_path_escape_is_error(tmp_path: Path):
    skill = tmp_path / "skill"
    skill.mkdir()
    path = skill / "SKILL.md"
    findings = check_links("See [outside](../secret.md).", path, "SKILL.md", skill)
    assert findings[0].rule_id == "SLLINK002"


def test_http_link_is_warned_without_fetching(tmp_path: Path):
    path = tmp_path / "AGENTS.md"
    findings = check_links("[site](http://example.com)", path, "AGENTS.md", tmp_path)
    assert findings[0].rule_id == "SLLINK003"


def test_code_fences_are_ignored(tmp_path: Path):
    path = tmp_path / "SKILL.md"
    text = "~~~md\n[not a real link](missing.md)\n~~~\n[real link](missing.md)\n"
    findings = check_links(text, path, "SKILL.md", tmp_path)
    assert len(findings) == 1
    assert findings[0].line == 4
