# SkillLint architecture

![SkillLint architecture](../assets/readme/architecture.svg)

SkillLint is a static-analysis CLI. It reads UTF-8 instruction files as data and never interprets or executes the instructions inside them.

1. **Discovery** finds SKILL.md plus well-known coding-agent instruction files. Common generated/vendor directories are excluded by default.
2. **Frontmatter parsing** uses a conservative, non-executing parser for common YAML scalar, list, block-text, and shallow mapping forms.
3. **Rule engine** checks Agent Skill metadata, file budgets, relative links, risky shell patterns, permission scope, and explicit modal contradictions.
4. **Reporting** renders terminal text, stable JSON, or SARIF 2.1.0 for CI tooling.
5. **Policy** returns a non-zero exit code for errors; --strict also fails on warnings.

## Intentional boundaries

- Remote links are not crawled; no network access is required.
- YAML is not a full general-purpose YAML implementation. Unsupported syntax is reported instead of guessed.
- Contradiction detection is a deterministic lexical heuristic, not an LLM and not semantic entailment.
- Security patterns flag known risky forms but cannot prove that an instruction is safe.
- No skill, instruction, code block, or shell command is executed.

See [RULES.md](RULES.md) and [SECURITY.md](../SECURITY.md).
