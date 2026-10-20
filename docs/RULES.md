# Rule catalogue

SkillLint emits stable rule IDs so teams can review findings and build CI policy around them. Severity reflects the default impact estimate; static checks can produce false positives and must be reviewed in context.

| Rule family | Meaning |
| --- | --- |
| SL001–SL005 | Missing or malformed frontmatter, unsupported syntax, duplicate keys |
| SL006–SL017 | Required metadata, name format, directory match, description quality, compatibility, empty or very short body |
| SLFILE001–SLFILE004 | File size, line budget, or input-size guardrails |
| SLFILE005–SLFILE006 | Symlink target escapes the scan root or a symlinked instruction file is skipped |
| SLLINK001–SLLINK003 | Broken local links, links escaping the scan scope, insecure HTTP links |
| SLSEC001–SLSEC008 | High-risk shell patterns and suspicious instruction-hierarchy language |
| SLPERM001–SLPERM003 | Invalid, overly broad, or high-impact allowed-tools permissions |
| SLCONF001 | Potentially conflicting modal instructions |

## Severity

- **error** — a structural failure, broken local dependency, or high-impact command pattern that should be fixed before relying on the instruction.
- **warning** — a likely quality/security problem or heuristic signal that needs human review.
- **info** — reserved for informational findings that do not fail normal runs.

The conflict detector only matches equivalent normalized action phrases with opposite modal polarity; it is not semantic reasoning. Secret scanning is not a guarantee. Remote links are not fetched, and SkillLint does not run instructions or commands from the target.
