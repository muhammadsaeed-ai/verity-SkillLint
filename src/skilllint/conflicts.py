"""Heuristic conflict detection for explicit modal instructions."""
from __future__ import annotations

import re
from collections import defaultdict

from skilllint.models import Finding

_MODAL = re.compile(
    r"(?i)\b(?P<modal>must\s+not|should\s+not|shall\s+not|do\s+not|don't|cannot|can't|never|avoid|must|should|always|shall)\s+(?P<action>[A-Za-z0-9_./:@+-][^.!?;\n]{3,150})"
)
_NEGATIVE = {"must not", "should not", "shall not", "do not", "don't", "cannot", "can't", "never", "avoid"}
_STOP = {"a", "an", "the", "to", "for", "of", "in", "on", "when", "with"}


def _normalize(action: str) -> str:
    words = re.findall(r"[a-z0-9_./:@+-]+", action.lower())
    while words and words[-1] in {"always", "never", "please"}:
        words.pop()
    return " ".join(word for word in words if word not in _STOP)


def check_conflicts(documents: list[tuple[str, str]]) -> list[Finding]:
    seen: dict[str, list[tuple[str, bool, int, str]]] = defaultdict(list)
    findings: list[Finding] = []
    emitted: set[tuple[str, str, int, str, int]] = set()
    for path, content in documents:
        in_fence = False
        fence_char = ""
        fence_len = 0
        for line_number, line in enumerate(content.splitlines(), 1):
            fence = re.match(r"^\s*(\x60{3,}|~{3,})", line)
            if fence:
                token = fence.group(1)
                if not in_fence:
                    in_fence, fence_char, fence_len = True, token[0], len(token)
                elif token[0] == fence_char and len(token) >= fence_len:
                    in_fence, fence_char, fence_len = False, "", 0
                continue
            if in_fence:
                continue
            for match in _MODAL.finditer(line):
                modal = re.sub(r"\s+", " ", match.group("modal").lower())
                action = match.group("action").strip(" \t-*")
                key = _normalize(action)
                if len(key.split()) < 2:
                    continue
                negative = modal in _NEGATIVE
                for other_path, other_negative, other_line, other_action in seen[key]:
                    if other_negative == negative:
                        continue
                    identity = (path, other_path, line_number, key, other_line)
                    if identity in emitted:
                        continue
                    emitted.add(identity)
                    findings.append(Finding(
                        "SLCONF001", "warning", "Potentially conflicting instructions",
                        path, line_number, max(1, match.start() + 1),
                        "Review both statements and make the intended behavior explicit. This heuristic can produce false positives.",
                        {"statement": line.strip()[:180], "conflicts_with": f"{other_path}:{other_line}", "other_statement": other_action[:180]},
                    ))
                seen[key].append((path, negative, line_number, line.strip()))
    return findings
