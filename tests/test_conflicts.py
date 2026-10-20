from skilllint.conflicts import check_conflicts


def test_opposite_modal_polarity_is_reported():
    findings = check_conflicts([("AGENTS.md", "Always use pnpm for package installs.\nNever use pnpm for package installs.\n")])
    assert len(findings) == 1
    assert findings[0].rule_id == "SLCONF001"
    assert findings[0].severity == "warning"


def test_same_polarity_is_not_conflict():
    findings = check_conflicts([("AGENTS.md", "Always use pnpm for package installs.\nAlways use pnpm for package installs.\n")])
    assert findings == []


def test_conflicts_across_files_are_detected():
    findings = check_conflicts([
        ("AGENTS.md", "Always use pnpm for package installs.\n"),
        ("CLAUDE.md", "Never use pnpm for package installs.\n"),
    ])
    assert len(findings) == 1
    assert findings[0].evidence["conflicts_with"] == "AGENTS.md:1"


def test_code_block_is_not_interpreted_as_instruction():
    findings = check_conflicts([("AGENTS.md", "~~~text\nAlways use pnpm for package installs.\n~~~\nNever use pnpm for package installs.\n")])
    assert findings == []
