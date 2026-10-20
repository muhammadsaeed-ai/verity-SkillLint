"""Discover skills and well-known AI coding-agent instruction files."""
from __future__ import annotations

import fnmatch
import os
from pathlib import Path

from skilllint.conflicts import check_conflicts
from skilllint.models import Finding, ScanReport, relative_display
from skilllint.skills import lint_instruction_document, lint_skill

EXCLUDED_DIRS = {
    ".git", ".venv", "venv", "env", "node_modules", "dist", "build",
    "__pycache__", ".pytest_cache", ".ruff_cache", ".tox", ".mypy_cache",
    "site-packages", ".next", ".turbo", "coverage", ".idea", ".vscode",
}
INSTRUCTION_NAMES = {
    "AGENTS.md", "CLAUDE.md", "GEMINI.md", "CODEX.md", "COPILOT.md",
    ".windsurfrules", ".clinerules", ".cursorrules",
}
MAX_SCAN_BYTES = 1_000_000


def _is_instruction(path: Path) -> bool:
    if path.name == "SKILL.md" or path.name in INSTRUCTION_NAMES:
        return True
    if path.name.lower().endswith(".instructions.md"):
        return True
    if path.suffix.lower() == ".mdc" and ".cursor" in path.parts and "rules" in path.parts:
        return True
    return path.name == "copilot-instructions.md" and ".github" in path.parts


def _discover(target: Path, excludes: list[str]) -> tuple[Path, list[Path]]:
    if target.is_file():
        return target.parent, [target] if _is_instruction(target) else []
    root = target
    candidates: list[Path] = []
    for current, directories, filenames in os.walk(root, followlinks=False):
        current_path = Path(current)
        directories[:] = [
            name for name in directories
            if name not in EXCLUDED_DIRS and not (current_path / name).is_symlink()
        ]
        for filename in filenames:
            path = current_path / filename
            if not _is_instruction(path):
                continue
            relative = path.relative_to(root).as_posix()
            if any(fnmatch.fnmatch(relative, pattern) or fnmatch.fnmatch(path.name, pattern) for pattern in excludes):
                continue
            candidates.append(path)
    return root, sorted(set(candidates))


def scan_path(target: str | Path, excludes: list[str] | None = None) -> ScanReport:
    requested = Path(target).expanduser()
    if not requested.exists():
        root = requested.parent if requested.parent != Path("") else Path.cwd()
        return ScanReport(str(root.resolve()), [Finding(
            "SL000", "error", "Scan target does not exist", str(requested), 1, 1,
            "Provide an existing file or directory path.",
        )])
    if not requested.is_file() and not requested.is_dir():
        return ScanReport(str(requested.resolve()), [Finding(
            "SL000", "error", "Scan target is not a regular file or directory", str(requested), 1, 1,
            "Pass a readable file or directory.",
        )])

    root, paths = _discover(requested, excludes or [])
    report = ScanReport(root=str(root.resolve()))
    documents: list[tuple[str, str]] = []
    for path in paths:
        display = relative_display(path, root)
        try:
            size = path.stat().st_size
            if size > MAX_SCAN_BYTES:
                report.add(Finding(
                    "SLFILE004", "error", "Instruction document exceeds the scan safety limit", display, 1, 1,
                    "The file is over 1 MB. Split or inspect it separately before scanning.",
                    {"bytes": size, "maximum": MAX_SCAN_BYTES},
                ))
                continue
            text = path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            report.add(Finding(
                "SL000", "error", "Instruction document is not valid UTF-8", display, 1, 1,
                "Save the instruction file as UTF-8 before scanning.",
            ))
            continue
        except OSError as exc:
            report.add(Finding(
                "SL000", "error", "Instruction document could not be read", display, 1, 1,
                f"Could not read the file ({type(exc).__name__}). Check access permissions.",
            ))
            continue

        report.files_scanned += 1
        documents.append((display, text))
        if path.name == "SKILL.md":
            report.skills_scanned += 1
            report.extend(lint_skill(path, text, display))
        else:
            report.extend(lint_instruction_document(path, text, display, root))

    report.extend(check_conflicts(documents))
    if not paths:
        report.add(Finding(
            "SL000", "warning", "No supported instruction files found", ".", 1, 1,
            "Point SkillLint at a folder containing SKILL.md, AGENTS.md, CLAUDE.md, GEMINI.md, or a supported agent instruction file.",
        ))
    return report
