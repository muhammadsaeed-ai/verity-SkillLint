import json

from skilllint.models import Finding, ScanReport
from skilllint.reporters import render_json, render_sarif, render_text


def sample_report():
    report = ScanReport(root=".")
    report.files_scanned = 1
    report.findings.append(Finding("SLTEST001", "warning", "Example issue", "SKILL.md", 7, 3, "Fix the example."))
    return report


def test_json_report_has_stable_schema_and_summary():
    data = json.loads(render_json(sample_report()))
    assert data["schema_version"] == "1.0"
    assert data["tool"] == "SkillLint"
    assert data["summary"]["warnings"] == 1
    assert data["findings"][0]["rule_id"] == "SLTEST001"


def test_sarif_report_has_rule_and_region():
    data = json.loads(render_sarif(sample_report()))
    run = data["runs"][0]
    assert data["version"] == "2.1.0"
    assert run["tool"]["driver"]["rules"][0]["id"] == "SLTEST001"
    result = run["results"][0]
    assert result["level"] == "warning"
    assert result["locations"][0]["physicalLocation"]["region"]["startLine"] == 7


def test_text_report_includes_actionable_next_step():
    output = render_text(sample_report())
    assert "SLTEST001" in output
    assert "Fix the example." in output


def test_strict_mode_fails_on_warning():
    assert sample_report().exit_code(strict=False) == 0
    assert sample_report().exit_code(strict=True) == 1
