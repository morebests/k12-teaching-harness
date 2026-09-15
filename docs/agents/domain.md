# Domain Docs

This repo uses a single context: a root `CONTEXT.md` glossary and `docs/adr/` for architectural decisions.

## Before exploring

Read the root `CONTEXT.md` and any ADRs in `docs/adr/` relevant to the area being explored.

If they do not exist, proceed silently. The `domain-modeling` skill creates the glossary when terms are resolved, and ADRs when a decision warrants one.

## File structure

```text
/
├── CONTEXT.md
└── docs/
    └── adr/
```

These paths describe the layout; setup does not create placeholder domain content.

## Use the glossary's vocabulary

Use the terms defined in `CONTEXT.md` when naming domain concepts in issues, proposals, hypotheses, and tests.

If a needed concept is absent, reconsider the terminology or note the gap for `domain-modeling`.

## Flag ADR conflicts

Explicitly identify any ADR contradicted by a proposal, and explain why the decision may need to be revisited.
