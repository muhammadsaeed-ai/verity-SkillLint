"""Static checks for high-risk command patterns and broad tool permissions."""
from __future__ import annotations

import re

from skilllint.models import Finding

_PATTERNS: tuple[tuple[str, str, str, str, re.Pattern[str]], ...] = (
    ("SLSEC001", "error", "Download piped directly to a shell",
     "Downloading a remote script and executing it in one pipeline makes the source difficult to inspect.",
     re.compile(r"(?i)\b(?:curl|wget)\b[^\n|]{0,240}\|\s*(?:sudo\s+)?(?:ba)?sh\b")),
    ("SLSEC002", "error", "Destructive recursive deletion",
     "A broad recursive delete can destroy user data or the host filesystem.",
     re.compile(r"(?i)\brm\s+(?:-[A-Za-z]*r[A-Za-z]*f[A-Za-z]*|-[A-Za-z]*f[A-Za-z]*r[A-Za-z]*)\s+(?:/\s*$|/\*|~(?:/|\s|$)|\$HOME(?:/|\s|$))")),
    ("SLSEC003", "warning", "World-writable recursive permissions",
     "Recursive mode 777 grants every local user write and execute access.",
     re.compile(r"(?i)\bchmod\s+-R\s+777\b")),
    ("SLSEC004", "warning", "PowerShell execution-policy bypass",
     "A policy bypass can conceal the risk of an untrusted script.",
     re.compile(r"(?i)\b(?:powershell|pwsh)\b[^\n]{0,180}(?:-ExecutionPolicy\s+Bypass|-ep\s+Bypass)")),
    ("SLSEC005", "warning", "Force-push instruction",
     "Force pushes can rewrite shared history; prefer an explicit recovery procedure.",
     re.compile(r"(?i)\bgit\s+push\b[^\n]{0,100}\s--force(?:-with-lease)?\b")),
    ("SLSEC006", "warning", "Aggressive Git clean",
     "This command removes untracked files and may delete work that is not backed up.",
     re.compile(r"(?i)\bgit\s+clean\s+(?=[^\n]*-[a-z]*f)(?=[^\n]*-[a-z]*d)(?=[^\n]*-[a-z]*x)[^\n]*")),
    ("SLSEC007", "warning", "Instruction-hierarchy override phrase",
     "This phrase can be used in prompt-injection attempts; verify its intent.",
     re.compile(r"(?i)\bignore\s+(?:all\s+)?(?:previous|prior|above)\s+instructions\b")),
    ("SLSEC008", "warning", "Direct access to common credential files",
     "Avoid asking an agent to print credential files or copy their contents into a transcript.",
     re.compile(r"(?i)\b(?:cat|type|more|Get-Content)\s+(?:[^\n]{0,100})?(?:\.env(?:\b|\s)|id_rsa\b|id_ed25519\b|credentials\.json\b)")),
)

_NEGATED = (
    "do not run", "don't run", "never run", "avoid running",
    "do not use", "don't use", "never use", "unsafe example",
    "example of an unsafe", "must not run", "not recommended",
)


def check_security(text: str, path: str) -> list[Finding]:
    findings: list[Finding] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        lowered = line.strip().lower()
        negated = any(token in lowered for token in _NEGATED)
        for rule_id, severity, title, message, regex in _PATTERNS:
            if regex.search(line) and not negated:
                findings.append(Finding(
                    rule_id, severity, title, path, line_number, 1, message,
                    {"snippet": line.strip()[:160]},
                ))
    return findings


def check_allowed_tools(value: object, path: str, line: int = 1) -> list[Finding]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        tools = [str(item).strip() for item in value]
    elif isinstance(value, str):
        tools = [item for item in re.split(r"[\s,]+", value.strip()) if item]
    else:
        return [Finding(
            "SLPERM001", "error", "Invalid allowed-tools metadata", path, line, 1,
            "Use a string or list of tool names in allowed-tools.",
        )]
    findings: list[Finding] = []
    broad = {"*", "all", "bash(*)", "shell(*)", "terminal(*)"}
    for tool in tools:
        if tool.lower() in broad:
            findings.append(Finding(
                "SLPERM002", "warning", "Broad tool permission", path, line, 1,
                f"The permission {tool!r} appears to grant unrestricted tool access.",
                {"tool": tool},
            ))
        elif re.search(r"(?i)\b(?:bash|shell|terminal)\s*\(\s*(?:sudo|rm|curl|wget|chmod|powershell)\b", tool):
            findings.append(Finding(
                "SLPERM003", "warning", "High-impact command permission", path, line, 1,
                "Review this command-scoped shell permission and narrow it to the minimum required commands.",
                {"tool": tool[:120]},
            ))
    return findings
