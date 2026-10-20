# Security policy

## Threat model

SkillLint treats skill files and agent instruction files as untrusted text. The scanner never executes their commands, imports their code, follows remote links, or sends content to a hosted service.

The explicit checks are designed to help reviewers spot common packaging and risk signals:
- risky download-to-shell and destructive shell patterns;
- broad or high-impact allowed-tools declarations;
- broken local references and paths that escape the scanned scope;
- suspicious instruction-hierarchy override phrases;
- repeated modal statements that may conflict.

## Limitations

These checks are static heuristics. They do not prove that a skill is safe, do not understand every natural-language instruction, and may produce false positives. A clean report is not a security certification. Secret patterns are incomplete. Review permissions and execution steps with a human before installing or using an unfamiliar skill.

The frontmatter parser handles a documented subset of YAML; unsupported constructs result in diagnostics instead of executing tags or loading arbitrary objects.

## Reporting a vulnerability

Do not include real credentials, private skills, or confidential customer instructions in public reports. Contact the repository owner through the GitHub profile with a minimal sanitized reproduction, the affected version, and the expected impact. Response time is not guaranteed for this early-stage project.
