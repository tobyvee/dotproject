# Decision log

The spec says what to build. The decision log records every choice the spec didn't settle, so the next agent builds to it instead of silently redoing or contradicting it. On a real build of about 50 tickets, agents wrote more than 250 decision files. They covered everything from "a failed move rolls back instead of reloading" to "estimates aren't a budget", and agents read them before every ticket.

## What counts as a decision

A choice between real alternatives that the spec, the design and the ticket don't already settle:

- interpreting an ambiguous requirement
- departing from the spec
- choosing a library, API or pattern
- changing a ticket's scope, `touches` or dependencies
- splitting or merging tickets
- cutting or deferring work
- fixing versus deferring a review or security finding
- resolving a non-mechanical merge
- any answer the user gives to a `needs decision`

Following the spec as written isn't a decision, and neither are naming and formatting. If in doubt, log it.

## File format

One file per decision in `.project/decisions/`, named `<ticket-id>-<slug>.md`, or `general-<slug>.md` when no single ticket owns it. Decisions are **never numbered globally**: agents in parallel worktrees would collide.

```markdown
---
title: "Each finished ticket is committed and pushed before the next one lands"
type: decision
project: <project>
ticket: none             # a ticket ID, a list, or "none"
decided_by: user         # an agent name, "main session", or "user"
supersedes:              # an earlier decision file name, if any
updated: YYYY-MM-DD
tags: [project, <project>, decision, workflow]
---
# Each finished ticket is committed and pushed before the next one lands

## Context
What forced a choice, linked to the spec section or finding.

## Decision
What was chosen, in one or two sentences.

## Alternatives
Each option rejected, and why in one line.

## Consequences
What this commits later tickets to, or what it costs.
```

See [`examples/example-app/project-samples/decisions/`](../examples/example-app/project-samples/decisions/) for examples, including one that supersedes another.

**A committed decision is never edited.** To change course, write a new file that sets `supersedes:` to the old file's name.

## Who writes

| Writer | Writes |
|---|---|
| Code-writing agents (`ticket-implementer`, `test-writer`, `security-fixer`, `branch-integrator`, project specialists) | their own decision files, committed with the change and listed in their report |
| `ticket-planner` | planning decisions: interpretations, non-obvious splits, who owns a shared file |
| Read-only agents (reviewers, auditors) | nothing. When their result forces a choice, the calling session logs it. |
| The main session | choices the commands force: a deferred finding, an unmet criterion, a file added to `touches`, a blocked ticket, a wave override. It also logs the user's answers, as `decided_by: user`. |

When the main session records a ticket, it adds a `## Decisions` list to the ticket linking every decision file that names it. It finds them with `git diff --name-only --diff-filter=A <pre>..HEAD -- .project/decisions/`.

## How agents read it

Before acting on a ticket, a review or a question:

1. **Find candidates:**
   - every `general-*.md`;
   - every file whose `ticket:` names your ticket, one of its dependencies, or a ticket that owns a file you'll touch (`grep -l "T-012" .project/decisions/*.md`);
   - any file whose title or tags match your area (`grep -il "export" .project/decisions/*.md`).
2. **Drop superseded files.** A file named in another's `supersedes:` no longer applies; follow the chain to the newest.
3. **Precedence.** A decision overrides the spec or PRD text it departs from. A `decided_by: user` decision overrides an agent's. If a decision conflicts with the spec and neither says which wins, or two live decisions conflict, don't pick: report the conflict.
4. **Cite them.** Name the decision files that shaped the work. To depart from one, log a new decision with `supersedes:`. Read-only agents recommend this instead. An implementer that would have to override a `decided_by: user` decision returns `blocked`.

Reviewers use the log too. A deliberate, logged choice isn't a defect. Code that contradicts a live decision is a must-fix, and so is a choice that should have been logged but wasn't.

## Public repos

If the repo is public, so are its decisions. Security decisions describe the protection chosen, never a working exploit.
