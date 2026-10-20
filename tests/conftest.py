from __future__ import annotations

from pathlib import Path

import pytest


GOOD_SKILL = """---
name: changelog-auditor
description: Review repository changes and produce an evidence-backed changelog draft for release preparation.
license: MIT
allowed-tools:
  - Read
  - Grep
metadata:
  author: VerityAgent
  version: "1.0"
---

# Changelog Auditor

Review the release diff, group user-visible changes, cite evidence, and mark unsupported claims as open questions. Never fabricate release behavior.

See the [checklist](references/checklist.md).
"""


@pytest.fixture
def skill_dir(tmp_path: Path) -> Path:
    directory = tmp_path / "changelog-auditor"
    (directory / "references").mkdir(parents=True)
    (directory / "references" / "checklist.md").write_text("# Checklist\n\n- Verify each release note.\n", encoding="utf-8")
    (directory / "SKILL.md").write_text(GOOD_SKILL, encoding="utf-8")
    return directory
