from skilllint.frontmatter import parse_frontmatter


def test_parses_scalar_list_and_shallow_mapping():
    parsed = parse_frontmatter(
        '---\nname: demo-skill\ndescription: "A sufficiently detailed description."\n'
        'allowed-tools:\n  - Read\n  - Grep\nmetadata:\n  owner: VerityAgent\n---\nBody\n',
        "SKILL.md",
    )
    assert parsed.present
    assert parsed.findings == []
    assert parsed.values["name"] == "demo-skill"
    assert parsed.values["allowed-tools"] == ["Read", "Grep"]
    assert parsed.values["metadata"] == {"owner": "VerityAgent"}


def test_parses_folded_and_literal_block_text():
    parsed = parse_frontmatter(
        "---\nname: demo-skill\ndescription: >\n  Read the project files\n  and summarize verified changes.\nnotes: |\n  first line\n  second line\n---\nBody\n",
        "SKILL.md",
    )
    assert parsed.values["description"] == "Read the project files and summarize verified changes."
    assert parsed.values["notes"] == "first line\nsecond line"


def test_missing_frontmatter_is_error():
    parsed = parse_frontmatter("# Skill\nNo metadata.", "SKILL.md")
    assert parsed.findings[0].rule_id == "SL001"
    assert parsed.findings[0].severity == "error"


def test_unclosed_frontmatter_is_error():
    parsed = parse_frontmatter("---\nname: demo-skill\n", "SKILL.md")
    assert parsed.findings[0].rule_id == "SL002"


def test_duplicate_key_is_reported():
    parsed = parse_frontmatter("---\nname: one\nname: two\ndescription: A description long enough for testing.\n---\nbody", "SKILL.md")
    assert any(f.rule_id == "SL005" for f in parsed.findings)


def test_invalid_double_quoted_scalar_is_reported():
    parsed = parse_frontmatter('---\nname: "oops\n---\n', "SKILL.md")
    assert any(f.rule_id == "SL004" for f in parsed.findings)


def test_utf8_bom_is_accepted():
    parsed = parse_frontmatter('\ufeff---\nname: demo-skill\ndescription: A meaningful skill description.\n---\nBody', "SKILL.md")
    assert parsed.present
    assert not parsed.findings
