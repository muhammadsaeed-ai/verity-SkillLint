"""Validate local Markdown links without network access."""
from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

from skilllint.models import Finding

_MARKDOWN_LINK = re.compile(r"!?(?:\[[^\]]*\])\(([^)]+)\)")
_HTML_REF = re.compile(r'''(?i)\b(?:href|src)\s*=\s*["']([^"']+)["']''')


def visible_markdown_lines(text: str) -> list[tuple[int, str]]:
    """Return lines outside fenced code blocks, retaining original line numbers."""
    visible: list[tuple[int, str]] = []
    fence_char: str | None = None
    fence_len = 0
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.lstrip()
        fence = re.match(r"(\x60{3,}|~{3,})", stripped)
        if fence:
            token = fence.group(1)
            if fence_char is None:
                fence_char, fence_len = token[0], len(token)
            elif token[0] == fence_char and len(token) >= fence_len:
                fence_char, fence_len = None, 0
            continue
        if fence_char is None:
            visible.append((number, line))
    return visible


def _link_target(raw: str) -> str:
    value = raw.strip()
    if value.startswith("<") and ">" in value:
        value = value[1:value.index(">")]
    else:
        value = re.split(r'\s+["\']', value, maxsplit=1)[0]
    return value.strip()


def check_links(text: str, path: Path, display_path: str, scope_root: Path) -> list[Finding]:
    findings: list[Finding] = []
    seen: set[tuple[int, str]] = set()
    for line_number, line in visible_markdown_lines(text):
        targets = [_link_target(match.group(1)) for match in _MARKDOWN_LINK.finditer(line)]
        targets.extend(match.group(1).strip() for match in _HTML_REF.finditer(line))
        for target in targets:
            if not target or target.startswith("#"):
                continue
            parsed = urlsplit(target)
            if parsed.scheme or target.startswith("//"):
                if parsed.scheme.lower() == "http" and parsed.netloc:
                    findings.append(Finding(
                        "SLLINK003", "warning", "Insecure HTTP link", display_path, line_number, 1,
                        "Prefer HTTPS for external links when the destination supports it.",
                        {"url": target[:180]},
                    ))
                continue
            local_path = unquote(parsed.path)
            if not local_path:
                continue
            resolved = (path.parent / local_path).resolve()
            try:
                resolved.relative_to(scope_root.resolve())
            except (OSError, ValueError):
                item = (line_number, target)
                if item not in seen:
                    seen.add(item)
                    findings.append(Finding(
                        "SLLINK002", "error", "Link escapes the scanned scope", display_path, line_number, 1,
                        "Keep relative references within the skill or repository scope; avoid paths that traverse outside it.",
                        {"target": target[:180]},
                    ))
                continue
            if not resolved.exists():
                item = (line_number, target)
                if item not in seen:
                    seen.add(item)
                    findings.append(Finding(
                        "SLLINK001", "error", "Broken local link", display_path, line_number, 1,
                        "Correct the relative path or add the referenced file to the repository.",
                        {"target": target[:180]},
                    ))
    return findings
