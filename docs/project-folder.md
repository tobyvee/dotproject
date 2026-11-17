# The `.project/` folder

Every project keeps its planning docs in `.project/` at the repo root.

```
.project/
├── STATUS.md    # current status; the first paragraph under `## Summary` feeds the dashboard
├── prd/         # product requirements
├── spec/        # technical specifications
├── tickets/     # engineering tickets (and INDEX.md, the run order)
├── decisions/   # one file per decision (when there are any)
├── review/      # code reviews and audits (when there are any)
└── reference/   # research and notes (when there are any)
```

`/project-init` creates it. Create `decisions/`, `review/` and `reference/` only when there's something to put in them.

## Local or committed

| | Local (default) | Committed |
|---|---|---|
| Set up with | `/project-init` | `/project-init --commit`, or `/workflow-init` |
| Git | `/.project/` in `.gitignore` | tracked like code |
| Good for | personal planning in any repo, including ones you don't own | the spec-driven workflow; teams; repos whose planning is part of the deliverable |
| Records | edited freely, never committed | committed with the work they record |

The spec-driven workflow requires **committed**: worktree agents branch from `HEAD` and read their ticket there. Committed also means public if the repo is public. Security tickets and decisions then describe the protection, never a working exploit.

A repo's CLAUDE.md says which mode it uses, and that overrides any global default.

## Frontmatter

Every doc starts with:

```yaml
---
title: "<title>"
type: prd              # prd | spec | ticket | review | reference | status | decision
project: <project>     # canonical name, from STATUS.md
status: todo           # tickets only: todo | doing | done | blocked
updated: YYYY-MM-DD
tags: [project, <project>, <type>]
---
```

- **`project`** is spelled exactly as in `STATUS.md`. It's the dashboard's key.
- **`status` only on tickets.** PRDs, specs, reviews, references, decisions and the status doc have no lifecycle. An invented status makes the dashboard report progress nobody measured. `tickets/INDEX.md` is `type: reference` with no `status`, so it isn't counted as a ticket.
- **`updated`** is bumped whenever the doc changes.
- Metadata goes in frontmatter, never as `**Status:**` lines in the body.

Spec-driven tickets add `priority`, `milestone`, `estimate`, `depends_on`, `touches` and `cut_rank`. Decisions add `ticket`, `decided_by` and `supersedes`. See [Tickets and waves](tickets-and-waves.md) and [Decision log](decision-log.md).

## Doc types and names

| Type | Folder | File name | Sections |
|---|---|---|---|
| prd | `prd/` | `<slug>-prd.md` | Problem · Goals · Non-goals · Users and use cases · Requirements (numbered, testable) · Success criteria · Open questions |
| spec | `spec/` | `<slug>-spec.md` | Overview · Architecture · Project structure · Data model / interfaces · Key decisions · Error handling · Testing strategy (case table) · Build plan (milestones, cut order) · Rollout · Open questions |
| ticket | `tickets/` | `T-NNN-<slug>.md` | Context · Scope · Acceptance criteria · Dependencies · Notes |
| review | `review/` | `<yyyy-mm-dd>-<slug>-review.md` | Summary verdict · Findings by severity, each with `file:line` and a fix · Follow-ups |
| reference | `reference/` | `<slug>.md` | free-form, starting with the source and date |
| decision | `decisions/` | `<ticket-id>-<slug>.md` or `general-<slug>.md` | Context · Decision · Alternatives · Consequences |

An existing repo's own naming and structure win over these defaults. `/project-doc` looks at existing docs of the same type first.

## `STATUS.md`

```markdown
---
title: "<project> — Status"
type: status
project: <project>
updated: YYYY-MM-DD
tags: [project, <project>, status]
---
# <project> — Status

## Summary

<Plain prose: what the project is and where it stands today.>

## In progress
## Outstanding
## Planned
## Completed
```

- **The Summary's first paragraph is quoted by the dashboard.** It must be prose. A paragraph that starts with a list, quote, table or heading is skipped.
- **Record facts:** dates, commit SHAs, what was verified, what's still broken. Never tick anything that wasn't finished and verified.
- **Blockers are explicit:** what's needed, and from whom. That's what makes a project show as blocked instead of silently stale. The blocked item keeps its line, with `— blocked: <what>, from <whom> (since <date>)` appended. The unblocking action goes under Outstanding, and the ticket gets `status: blocked` and a `## Blocked` section. There's no separate Blocked section in STATUS.md.
- **Planned → In progress → Completed:** one `- [ ] T-NNN: title` line per ticket, moved and ticked as work lands. Follow-ups go under Outstanding, one line each: what, where, and why it matters.

## Skills

| Skill | When |
|---|---|
| `/project-init [name] [--commit]` | A repo has no `.project/` yet |
| `/project-doc <type> <title>` | Write one PRD, spec, ticket, review, reference or decision |
| `/project-update [change]` | Record finished, changed or blocked work |
| `/project-status` | Refresh the dashboard across all registered repos ([Dashboard](dashboard.md)) |
