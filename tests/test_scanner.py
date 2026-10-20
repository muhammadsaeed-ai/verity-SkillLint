from pathlib import Path

from skilllint.scanner import scan_path


def test_reference_skill_scans_clean(skill_dir: Path):
    report = scan_path(skill_dir)
    assert report.files_scanned == 1
    assert report.skills_scanned == 1
    assert report.errors == 0
    assert report.warnings == 0
    assert report.status == "passed"


def test_project_instruction_file_is_discovered(tmp_path: Path):
    (tmp_path / "AGENTS.md").write_text("# Guidance\n\nKeep changes small and test them.\n", encoding="utf-8")
    report = scan_path(tmp_path)
    assert report.files_scanned == 1
    assert report.skills_scanned == 0


def test_common_generated_directories_are_excluded(tmp_path: Path):
    (tmp_path / "node_modules" / "untrusted").mkdir(parents=True)
    (tmp_path / "node_modules" / "untrusted" / "SKILL.md").write_text("invalid", encoding="utf-8")
    report = scan_path(tmp_path)
    assert report.files_scanned == 0
    assert report.warnings == 1


def test_missing_target_is_error(tmp_path: Path):
    report = scan_path(tmp_path / "missing")
    assert report.errors == 1
    assert report.findings[0].rule_id == "SL000"


def test_exclude_glob_works(tmp_path: Path):
    (tmp_path / "AGENTS.md").write_text("# Main instructions\n", encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text("# Alternate instructions\n", encoding="utf-8")
    report = scan_path(tmp_path, excludes=["CLAUDE.md"])
    assert report.files_scanned == 1
