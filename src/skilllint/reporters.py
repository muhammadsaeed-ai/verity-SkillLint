"""Text, JSON, and SARIF renderers for diagnostics and CI."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from skilllint.models import ScanReport


def render_json(report: ScanReport) -> str:
    return json.dumps(report.to_dict(), indent=2, sort_keys=True, ensure_ascii=False)


def render_text(report: ScanReport, color: bool = False) -> str:
    reset = "\033[0m" if color else ""
    cyan = "\033[96m" if color else ""
    red = "\033[91m" if color else ""
    yellow = "\033[93m" if color else ""
    green = "\033[92m" if color else ""
    dim = "\033[2m" if color else ""
    rule = "━" * 72
    status_color = red if report.errors else yellow if report.warnings else green
    lines = [
        rule,
        f"{cyan}SKILLLINT  v1.0.0{reset}",
        f"Root     : {report.root}",
        f"Status   : {status_color}{report.status.upper().replace('_', ' ')}{reset}",
        f"Scanned  : {report.files_scanned} instruction file(s) · {report.skills_scanned} skill(s)",
        rule,
    ]
    if not report.findings:
        lines.append(f"{green}✓ No findings. The scanned files passed the enabled checks.{reset}")
    for finding in sorted(report.findings, key=lambda f: (f.path, f.line, f.column, f.rule_id)):
        marker, tone = {
            "error": ("✖", red),
            "warning": ("!", yellow),
            "info": ("i", cyan),
        }[finding.severity]
        lines.append(f"{tone}{marker} [{finding.severity.upper():7}] {finding.rule_id}{reset} · {finding.message}")
        lines.append(f"  {dim}{finding.path}:{finding.line}:{finding.column}{reset}")
        if finding.evidence:
            encoded = json.dumps(finding.evidence, ensure_ascii=False, sort_keys=True)
            lines.append(f"  Evidence: {encoded[:260]}")
        if finding.recommendation:
            lines.append(f"  Next    : {finding.recommendation}")
    lines.extend([
        rule,
        f"Summary: {report.errors} error(s), {report.warnings} warning(s), {report.infos} info · {len(report.findings)} total",
        rule,
    ])
    return "\n".join(lines)


def render_sarif(report: ScanReport) -> str:
    rules: dict[str, dict[str, Any]] = {}
    results: list[dict[str, Any]] = []
    for finding in sorted(report.findings, key=lambda f: (f.path, f.line, f.rule_id)):
        rules.setdefault(finding.rule_id, {
            "id": finding.rule_id,
            "shortDescription": {"text": finding.message[:160]},
            "help": {"text": finding.recommendation or finding.message},
            "properties": {"tags": ["security", "quality", "ai-agent-instructions"]},
        })
        level = {"error": "error", "warning": "warning", "info": "note"}[finding.severity]
        result: dict[str, Any] = {
            "ruleId": finding.rule_id,
            "level": level,
            "message": {"text": finding.message},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {"uri": finding.path.replace("\\", "/")},
                    "region": {"startLine": max(1, finding.line), "startColumn": max(1, finding.column)},
                }
            }],
            "properties": {"recommendation": finding.recommendation},
        }
        if finding.evidence:
            result["properties"]["evidence"] = finding.evidence
        results.append(result)
    sarif = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {
                "driver": {
                    "name": "SkillLint",
                    "version": "1.0.0",
                    "informationUri": "https://github.com/muhammadsaeed-ai/verity-SkillLint",
                    "rules": [rules[key] for key in sorted(rules)],
                }
            },
            "results": results,
            "properties": {"summary": report.to_dict()["summary"], "status": report.status},
        }],
    }
    return json.dumps(sarif, indent=2, sort_keys=True, ensure_ascii=False)


def write_output(path: str | Path, content: str) -> None:
    output = Path(path).expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content.rstrip() + "\n", encoding="utf-8")
