"""Conservative frontmatter reader for common Agent Skills metadata values.

SkillLint handles scalar, list, block-text, and shallow mapping forms needed
for skill metadata. It never executes YAML tags or loads arbitrary objects.
Unsupported constructs get actionable diagnostics rather than guesses.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

from skilllint.models import Finding

_KEY = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$")
_PAIR = re.compile(r"^(?P<indent> *)(?P<key>[A-Za-z_][A-Za-z0-9_-]*)\s*:\s*(?P<value>.*)$")


@dataclass
class FrontmatterResult:
    values: dict[str, Any] = field(default_factory=dict)
    body_line: int = 1
    findings: list[Finding] = field(default_factory=list)
    present: bool = False


def _scalar(raw: str) -> Any:
    raw = raw.strip()
    if not raw:
        return ""
    if raw.startswith('"'):
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError("invalid double-quoted scalar") from exc
    if raw.startswith("'"):
        if len(raw) < 2 or not raw.endswith("'"):
            raise ValueError("invalid single-quoted scalar")
        return raw[1:-1].replace("''", "'")
    if raw == "[]":
        return []
    if raw == "{}":
        return {}
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        if not inner:
            return []
        parts = [part.strip() for part in re.split(r",(?=(?:[^'\"]|'[^']*'|\"[^\"]*\")*$)", inner)]
        return [_scalar(part) for part in parts]
    if raw.lower() in ("true", "false"):
        return raw.lower() == "true"
    if raw.lower() in ("null", "~"):
        return None
    return raw


def parse_frontmatter(text: str, path: str) -> FrontmatterResult:
    raw_lines = text.lstrip("\ufeff").splitlines()
    result = FrontmatterResult()
    if not raw_lines or raw_lines[0].strip() != "---":
        result.findings.append(Finding(
            "SL001", "error", "Missing YAML frontmatter", path, 1, 1,
            "Start SKILL.md with a YAML frontmatter block opened by ---.",
        ))
        return result
    result.present = True
    closing = next((i for i in range(1, len(raw_lines)) if raw_lines[i].strip() in ("---", "...")), None)
    if closing is None:
        result.findings.append(Finding(
            "SL002", "error", "Unclosed YAML frontmatter", path, 1, 1,
            "Add a closing --- line after the metadata block.",
        ))
        return result
    result.body_line = closing + 2
    lines = raw_lines[1:closing]
    index = 0
    seen: set[str] = set()
    while index < len(lines):
        line = lines[index]
        line_number = index + 2
        index += 1
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if "\t" in line[:len(line) - len(line.lstrip())]:
            result.findings.append(Finding(
                "SL003", "error", "Tabs used for YAML indentation", path, line_number, 1,
                "Use spaces for YAML indentation.",
            ))
            continue
        match = _PAIR.match(line)
        if not match or match.group("indent"):
            result.findings.append(Finding(
                "SL004", "error", "Unsupported frontmatter syntax", path, line_number, 1,
                "Use simple key: value metadata, scalar lists, or a shallow mapping. Avoid YAML tags and complex syntax.",
                {"line": line.strip()[:120]},
            ))
            continue
        key, raw = match.group("key"), match.group("value")
        if not _KEY.fullmatch(key):
            result.findings.append(Finding(
                "SL004", "error", "Invalid metadata key", path, line_number, 1,
                "Use a simple YAML identifier for each metadata key.",
            ))
            continue
        if key in seen:
            result.findings.append(Finding(
                "SL005", "error", "Duplicate metadata key", path, line_number, 1,
                f"Remove the duplicate {key!r} key; parsers may disagree about which value wins.",
                {"key": key},
            ))
            continue
        seen.add(key)

        if raw in ("|", ">", "|-", ">-", "|+", ">+"):
            block: list[str] = []
            while index < len(lines):
                next_line = lines[index]
                if next_line.strip() and not next_line.startswith((" ", "\t")):
                    break
                block.append(next_line.strip())
                index += 1
            separator = "\n" if raw.startswith("|") else " "
            result.values[key] = separator.join(item for item in block if item or raw.startswith("|")).strip()
            continue

        if raw == "":
            lookahead = index
            while lookahead < len(lines) and (not lines[lookahead].strip() or lines[lookahead].lstrip().startswith("#")):
                lookahead += 1
            if lookahead >= len(lines) or not lines[lookahead].startswith(" "):
                result.values[key] = ""
                continue
            child_lines: list[str] = []
            while index < len(lines) and (not lines[index].strip() or lines[index].startswith(" ")):
                child_lines.append(lines[index])
                index += 1
            meaningful = [item.strip() for item in child_lines if item.strip() and not item.lstrip().startswith("#")]
            if meaningful and all(item.startswith("- ") for item in meaningful):
                try:
                    result.values[key] = [_scalar(item[2:]) for item in meaningful]
                except ValueError as exc:
                    result.findings.append(Finding("SL004", "error", "Invalid list value", path, line_number, 1, str(exc)))
                    result.values[key] = []
            else:
                mapping: dict[str, Any] = {}
                bad = False
                for child in meaningful:
                    sub = _PAIR.match(child)
                    if not sub or sub.group("key") in mapping:
                        bad = True
                        break
                    try:
                        mapping[sub.group("key")] = _scalar(sub.group("value"))
                    except ValueError:
                        bad = True
                        break
                if bad:
                    result.findings.append(Finding(
                        "SL004", "error", "Unsupported nested metadata", path, line_number, 1,
                        "Use a simple mapping (for example metadata: followed by indented key: value pairs).",
                    ))
                    result.values[key] = {}
                else:
                    result.values[key] = mapping
            continue
        try:
            result.values[key] = _scalar(raw)
        except ValueError as exc:
            result.findings.append(Finding(
                "SL004", "error", "Invalid metadata value", path, line_number, 1,
                str(exc), {"key": key},
            ))
    return result
