# Triage Labels

The five canonical triage roles map directly to the local tracker's `Status:` values.

| Canonical role | Local status | Meaning |
| --- | --- | --- |
| `needs-triage` | `needs-triage` | Maintainer needs to evaluate the issue |
| `needs-info` | `needs-info` | Waiting on the reporter for more information |
| `ready-for-agent` | `ready-for-agent` | Fully specified, ready for an AFK agent |
| `ready-for-human` | `ready-for-human` | Requires human implementation |
| `wontfix` | `wontfix` | Will not be actioned |

When a skill mentions a triage role, set the issue's `Status:` line to the corresponding local status.

Wayfinder lifecycle statuses are defined in [issue-tracker.md](issue-tracker.md).

Edit the Local status column to change the vocabulary used by this repo.
