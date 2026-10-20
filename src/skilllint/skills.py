"""Agent Skill format and quality rules."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from skilllint.frontmatter import parse_frontmatter
from skilllint.links import check_links
from skilllint.models import Finding
from skilllint.security import check_allowed_tools, check_security

_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_ALLOWED_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
MAX_SKILL_BYTES = 100_000
MAX_SKILL_LINES = 500


def lint_skill(path: Path, text: str, display_path: str) -> list[Finding]:
    findings: list[Finding] = []
    byte_count = len(text.encode("utf-8", errors="replace"))
    line_count = len(text.splitlines())
    if byte_count > MAX_SKILL_BYTES:
        findings.append(Finding(
            "SLFILE001", "error", "SKILL.md exceeds the size limit", display_path, 1, 1,
            "Reduce SKILL.md to 100,000 bytes or less. Move substantial reference material into linked files.",
            {"bytes": byte_count, "limit": MAX_SKILL_BYTES},
        ))
    if line_count > MAX_SKILL_LINES:
        findings.append(Finding(
            "SLFILE002", "warning", "SKILL.md is longer than the recommended budget", display_path, 1, 1,
            "Keep the main skill instruction concise; move detailed references and examples into linked files.",
            {"lines": line_count, "recommended_max": MAX_SKILL_LINES},
        ))
    parsed = parse_frontmatter(text, display_path)
    findings.extend(parsed.findings)
    if parsed.present and not parsed.findings:
        metadata: dict[str, Any] = parsed.values
        name = metadata.get("name")
        description = metadata.get("description")

        if "name" not in metadata:
            findings.append(Finding(
                "SL006", "error", "Required name field is missing", display_path, 2, 1,
                "Add a name field to the YAML frontmatter.",
            ))
        elif not isinstance(name, str) or not name.strip():
            findings.append(Finding(
                "SL006", "error", "Name must be a non-empty string", display_path, 2, 1,
                "Set name to a lowercase hyphenated identifier such as data-audit.",
            ))
        else:
            if len(name) > 64:
                findings.append(Finding(
                    "SL007", "error", "Skill name is too long", display_path, 2, 1,
                    "Keep the name at 64 characters or fewer.",
                    {"length": len(name), "maximum": 64},
                ))
            if not _NAME.fullmatch(name):
                findings.append(Finding(
                    "SL008", "error", "Skill name is not kebab-case", display_path, 2, 1,
                    "Use lowercase letters, digits, and single hyphens; do not start or end with a hyphen.",
                    {"name": name[:100]},
                ))
            if path.parent.name != name:
                findings.append(Finding(
                    "SL009", "warning", "Skill name differs from its directory",
                    display_path, 2, 1,
                    "For portable Agent Skills packaging, make the containing directory name match the metadata name.",
                    {"metadata_name": name, "directory_name": path.parent.name},
                ))

        if "description" not in metadata:
            findings.append(Finding(
                "SL010", "error", "Required description field is missing", display_path, 2, 1,
                "Add a concise description of what the skill does and when an agent should use it.",
            ))
        elif not isinstance(description, str) or not description.strip():
            findings.append(Finding(
                "SL010", "error", "Description must be a non-empty string", display_path, 2, 1,
                "Use a plain-text description that explains the skill's purpose and trigger conditions.",
            ))
        elif len(description) > 1024:
            findings.append(Finding(
                "SL011", "error", "Description exceeds 1,024 characters", display_path, 2, 1,
                "Shorten the description so agents can identify the skill without loading the entire instructions.",
                {"length": len(description), "maximum": 1024},
            ))
        elif len(description) < 20:
            findings.append(Finding(
                "SL012", "warning", "Description may be too vague", display_path, 2, 1,
                "Explain both the skill's job and the situations in which it should be selected.",
                {"length": len(description)},
            ))

        compatibility = metadata.get("compatibility")
        if compatibility is not None:
            if not isinstance(compatibility, str):
                findings.append(Finding(
                    "SL013", "error", "Compatibility must be a string", display_path, 2, 1,
                    "Describe required agent products, runtime, or platform constraints in a plain string.",
                ))
            elif len(compatibility) > 500:
                findings.append(Finding(
                    "SL014", "warning", "Compatibility field is unusually long", display_path, 2, 1,
                    "Keep compatibility details under 500 characters and move explanation into the body.",
                    {"length": len(compatibility)},
                ))
        for field in sorted(set(metadata) - _ALLOWED_FIELDS):
            findings.append(Finding(
                "SL015", "warning", "Unrecognized frontmatter field", display_path, 2, 1,
                f"The field {field!r} is outside SkillLint's documented common skill metadata set. Confirm that the target agent supports it.",
                {"field": field},
            ))
        findings.extend(check_allowed_tools(metadata.get("allowed-tools"), display_path, 2))

        body = "\n".join(text.lstrip("\ufeff").splitlines()[parsed.body_line - 1:])
        if not body.strip():
            findings.append(Finding(
                "SL016", "warning", "Skill instructions are empty", display_path, parsed.body_line, 1,
                "Add a short instruction body explaining the workflow, constraints, and expected output.",
            ))
        elif len(body.strip()) < 80:
            findings.append(Finding(
                "SL017", "warning", "Skill body is unusually short", display_path, parsed.body_line, 1,
                "Include enough concrete steps and completion criteria for an agent to use the skill reliably.",
                {"body_characters": len(body.strip())},
            ))

    findings.extend(check_links(text, path, display_path, path.parent))
    findings.extend(check_security(text, display_path))
    return findings


def lint_instruction_document(path: Path, text: str, display_path: str, scope_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    if len(text.encode("utf-8", errors="replace")) > MAX_SKILL_BYTES:
        findings.append(Finding(
            "SLFILE003", "warning", "Instruction file is unusually large", display_path, 1, 1,
            "Split long project instructions into focused files and link to them from the main instruction document.",
            {"bytes": len(text.encode("utf-8", errors="replace")), "recommended_max": MAX_SKILL_BYTES},
        ))
    findings.extend(check_links(text, path, display_path, scope_root))
    findings.extend(check_security(text, display_path))
    return findings
