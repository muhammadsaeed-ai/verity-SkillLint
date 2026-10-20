from pathlib import Path

from skilllint.skills import lint_skill


def test_valid_skill_has_no_findings(skill_dir: Path):
    findings = lint_skill(skill_dir / "SKILL.md", (skill_dir / "SKILL.md").read_text(encoding="utf-8"), "SKILL.md")
    assert findings == []


def test_missing_required_metadata_is_reported(tmp_path: Path):
    directory = tmp_path / "missing-meta"
    directory.mkdir()
    text = "---\nlicense: MIT\n---\nA body with enough content to satisfy the minimum body length requirement for this test."
    findings = lint_skill(directory / "SKILL.md", text, "SKILL.md")
    ids = {item.rule_id for item in findings}
    assert "SL006" in ids
    assert "SL010" in ids


def test_name_format_and_directory_match_are_reported(tmp_path: Path):
    directory = tmp_path / "WrongFolder"
    directory.mkdir()
    text = "---\nname: Wrong_Name\ndescription: A detailed description that explains when to use this particular skill.\n---\n" + ("Specific instructions. " * 8)
    findings = lint_skill(directory / "SKILL.md", text, "SKILL.md")
    ids = {item.rule_id for item in findings}
    assert "SL008" in ids
    assert "SL009" in ids


def test_description_over_limit_is_reported(tmp_path: Path):
    directory = tmp_path / "long-desc"
    directory.mkdir()
    description = "x" * 1025
    text = f"---\nname: long-desc\ndescription: {description}\n---\n" + ("Instruction body. " * 8)
    findings = lint_skill(directory / "SKILL.md", text, "SKILL.md")
    assert any(item.rule_id == "SL011" for item in findings)


def test_long_skill_gets_budget_warning(tmp_path: Path):
    directory = tmp_path / "long-skill"
    directory.mkdir()
    text = "---\nname: long-skill\ndescription: A detailed description of this skill for release workflow review.\n---\n" + ("instruction line\n" * 510)
    findings = lint_skill(directory / "SKILL.md", text, "SKILL.md")
    assert any(item.rule_id == "SLFILE002" for item in findings)


def test_allowed_tools_bad_type_is_error(tmp_path: Path):
    directory = tmp_path / "bad-tools"
    directory.mkdir()
    text = '---\nname: bad-tools\ndescription: A detailed description of this skill for release workflow review.\nallowed-tools: true\n---\n' + ("Instruction body. " * 8)
    findings = lint_skill(directory / "SKILL.md", text, "SKILL.md")
    assert any(item.rule_id == "SLPERM001" for item in findings)


def test_skill_body_too_short_warns(tmp_path: Path):
    directory = tmp_path / "short-body"
    directory.mkdir()
    text = "---\nname: short-body\ndescription: A detailed description of this skill for release workflow review.\n---\nDo work."
    findings = lint_skill(directory / "SKILL.md", text, "SKILL.md")
    assert any(item.rule_id == "SL017" for item in findings)


def test_valid_example_contains_link_target(skill_dir: Path):
    skill = skill_dir / "SKILL.md"
    assert (skill_dir / "references" / "checklist.md").exists()
    assert not [f for f in lint_skill(skill, skill.read_text(encoding="utf-8"), "SKILL.md") if f.rule_id.startswith("SLLINK")]
