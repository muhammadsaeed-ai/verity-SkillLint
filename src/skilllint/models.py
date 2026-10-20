"""Stable diagnostic models used by the CLI and CI integrations."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

Severity = Literal["error", "warning", "info"]


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: Severity
    message: str
    path: str
    line: int = 1
    column: int = 1
    recommendation: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ScanReport:
    root: str
    findings: list[Finding] = field(default_factory=list)
    files_scanned: int = 0
    skills_scanned: int = 0

    @property
    def errors(self) -> int:
        return sum(item.severity == "error" for item in self.findings)

    @property
    def warnings(self) -> int:
        return sum(item.severity == "warning" for item in self.findings)

    @property
    def infos(self) -> int:
        return sum(item.severity == "info" for item in self.findings)

    @property
    def status(self) -> str:
        if self.errors:
            return "failed"
        if self.warnings:
            return "passed_with_warnings"
        return "passed"

    def add(self, finding: Finding) -> None:
        self.findings.append(finding)

    def extend(self, findings: list[Finding]) -> None:
        self.findings.extend(findings)

    def exit_code(self, strict: bool = False) -> int:
        return 1 if self.errors or (strict and self.warnings) else 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "1.0",
            "tool": "SkillLint",
            "tool_version": "1.0.0",
            "root": self.root,
            "status": self.status,
            "summary": {
                "files_scanned": self.files_scanned,
                "skills_scanned": self.skills_scanned,
                "errors": self.errors,
                "warnings": self.warnings,
                "infos": self.infos,
                "total_findings": len(self.findings),
            },
            "findings": [item.to_dict() for item in sorted(
                self.findings, key=lambda f: (f.path, f.line, f.column, f.rule_id)
            )],
        }


def relative_display(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except (OSError, ValueError):
        return path.as_posix()
