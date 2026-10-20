# Changelog

## 1.0.0 — Initial public implementation

- Add a Python CLI for static AI-agent skill and instruction-file checks.
- Validate common Skill frontmatter fields, name conventions, directory agreement, and instruction budgets.
- Check local Markdown/HTML references, out-of-scope links, risky shell patterns, broad tool permissions, and explicit modal conflicts.
- Produce text, stable JSON, and SARIF 2.1.0 reports with source locations and recommendations.
- Add deterministic test coverage, a reference skill, Python-version CI, and reproducible animated README visuals.
- Explicitly avoid running instructions or commands, calling tools, crawling external links, or uploading scan contents.
