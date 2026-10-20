---
name: changelog-auditor
description: "Review a repository's user-visible changes and produce an evidence-backed changelog draft, grouped by user impact and release risk."
license: MIT
compatibility: "Works with coding agents that can read repository files and inspect version-control history."
allowed-tools:
  - Read
  - Grep
  - Glob
metadata:
  author: VerityAgent
  version: "1.0.0"
---

# Changelog Auditor

Use this skill when preparing a release note, reviewing a pull request for user-facing impact, or checking whether a proposed changelog is supported by the repository.

## Procedure

1. Read the current changelog, release metadata, and relevant repository guidance.
2. Inspect the supplied diff or commit range. Do not infer changes from branch names alone.
3. Group changes as Added, Changed, Fixed, Deprecated, or Security when the evidence supports those categories.
4. Cite the relevant file paths or commits beside each draft item.
5. Mark unclear or unverified claims as questions instead of presenting them as facts.
6. Separate internal refactors from changes that materially affect users.
7. Return a proposed changelog and a short list of evidence gaps.

## Constraints

- Do not invent behavior that is not supported by the diff or source.
- Do not expose tokens, credentials, private customer information, or unredacted environment values.
- Do not run destructive commands or publish a release without explicit human approval.
- Keep the draft concise, specific, and suitable for a changelog rather than a commit-by-commit transcript.

For the review structure, use the [release checklist](references/release-checklist.md).
