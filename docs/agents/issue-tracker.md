# Issue tracker: Local Markdown

Issues and specs for this repo live as Markdown files in `.scratch/`.

## Conventions

- One feature per directory: `.scratch/<feature-slug>/`.
- The spec is `.scratch/<feature-slug>/spec.md`.
- Implementation issues use one file per ticket at `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01`.
- Give every issue a descriptive title as its first heading. Refer to maps and tickets by linked titles in human-facing output.
- Triage state is recorded as a `Status:` line near the top of ordinary issue files; use the role strings in [triage-labels.md](triage-labels.md).
- Append comments and conversation history under a `## Comments` heading.

## When a skill says "publish to the issue tracker"

Create a file at the appropriate path above, creating its directory if needed.

## When a skill says "fetch the relevant ticket"

Read the file at the referenced path. Resolve a ticket number within its feature directory; numbers are not unique across features.

## Wayfinding operations

Used by `/wayfinder`. The map is a file with one child file per decision ticket. Wayfinder tickets use the lifecycle statuses below instead of ordinary triage statuses.

- **Map**: `.scratch/<effort>/map.md`, with `Labels: wayfinder:map` and the Destination, Notes, Decisions so far, Not yet specified, and Out of scope sections. Keep open tickets in child files; the map indexes resolved decisions by title and link.
- **Child ticket**: `.scratch/<effort>/issues/<NN>-<slug>.md`, numbered from `01`. The directory establishes parentage. Include a title, `Type:` (`research`, `prototype`, `grilling`, or `task`), matching `Labels: wayfinder:<type>`, `Status: open`, an initially empty `Assignee:`, and a `## Question` body.
- **Blocking**: a `Blocked by: NN, NN` line near the top references tickets in the same effort. A ticket is unblocked when every listed blocker has `Status: resolved`. Missing blockers remain unresolved.
- **Frontier**: scan the effort's child files for `Status: open`, no assignee, and no unresolved blockers. First by number wins.
- **Claim**: re-read the ticket, record the driving developer in `Assignee:`, set `Status: claimed`, and save before starting work. Skip tickets already claimed by another session.
- **Resolve**: append the answer under `## Comments` as a `### Resolution` entry, set `Status: resolved`, and append a gist plus a title link to the map's Decisions so far. Keep the detailed answer in the ticket.
- **Out of scope**: append the reason as a comment, set `Status: resolved` to close the ticket, and link it from the map's Out of scope section.

Re-read affected files before updating them to preserve other sessions' changes.
