# Contributing

Thanks for helping improve SkillLint, an open-source VerityAgent developer tool for AI-agent skill validation.

## Development

Requires Python 3.10 or newer.

~~~bash
git clone https://github.com/muhammadsaeed-ai/verity-SkillLint.git
cd verity-SkillLint
python -m venv .venv
python -m pip install -e ".[dev]"
python -m pytest
ruff check src tests
python -m build
~~~

## Pull request checklist

- Add deterministic tests for new rules and edge cases.
- Give each rule a stable ID and an actionable recommendation.
- Never execute the text or command examples being scanned.
- Keep subprocess, file-size, and path handling bounded.
- Document heuristic limitations and likely false positives.
- Do not add real secrets or private user instruction files to fixtures.
- Verify text, JSON, and SARIF renderers if the report model changes.

## Scope discipline

Feature proposals should explain the failure mode, rule behavior, severity, and how it will be tested. Avoid adding remote fetches or automatic rewrites without a clear trust and safety review.
