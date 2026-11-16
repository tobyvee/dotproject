---
name: project-doc
description: Create a planning doc (PRD, technical spec, ticket, review, reference note or decision) in the repo's .project/ folder with the required frontmatter and the matching template. Use when the user asks to write or start a PRD, spec, ticket, review or decision in a repo that uses .project/.
argument-hint: "<prd|spec|ticket|review|reference|decision> <title or feature>"
---

# New `.project/` doc

Create one doc in the current repo's `.project/`. `$ARGUMENTS` is
`<type> <title>`; ask for whatever is missing.

## Before writing

1. Find `.project/` at the repo root (`git rev-parse --show-toplevel`). If it is
   missing, run the `project-init` skill first.
2. Read `.project/STATUS.md` frontmatter for the canonical `project:` name. Never
   invent a new spelling.
3. Look at 1–2 existing docs of the same type in this repo. **Their structure and
   naming win over the templates below**: match file names, ID prefixes (e.g.
   `APP-ADDR-1.2`, `T-014`), headings and tags.
4. Read the repo's `CLAUDE.md`. If it defines a richer flow for this kind of doc
   (the `dps` plugin's `/plan-tickets` for build tickets, a repo's own
   `/plan-feature`), use that for whole features and this skill only for single
   docs. If it says `.project/` is committed, docs are committed with the work they
   describe; otherwise `.project/` is local and gitignored.

## Frontmatter (required on every doc)

```yaml
---
title: "<title>"
type: prd              # prd | spec | ticket | review | reference | status | decision
project: <project>     # from STATUS.md
status: todo           # tickets only: todo | doing | done | blocked
updated: YYYY-MM-DD    # today, `date +%F`
tags: [project, <project>, <type>]   # plus topic tags
---
```

Set `status` only where a real lifecycle exists (tickets). PRDs, specs, reviews,
references and decisions have none: an invented status makes the dashboard report
progress nobody measured. A ticket index (`tickets/INDEX.md`) is `type: reference`
with no `status`, so it isn't counted as a ticket. Put metadata in frontmatter, not
as `**Status:**` lines in the body. Cross-references (`prd_ref`, `spec_ref`) may go
in frontmatter as repo-relative paths.

## Locations and names

| Type | Folder | File name |
|------|--------|-----------|
| prd | `prd/` | `<slug>-prd.md` |
| spec | `spec/` | `<slug>-spec.md` |
| ticket | `tickets/` | `T-NNN-<slug>.md` (next free number), or the repo's existing scheme |
| review | `review/` | `<yyyy-mm-dd>-<slug>-review.md` |
| reference | `reference/` | `<slug>.md` |
| decision | `decisions/` | `<ticket-id>-<slug>.md`, or `general-<slug>.md` when no ticket owns it |

## Templates

Fill every section with real content from the conversation, the code and any
research; delete a section rather than leave a placeholder. Mark genuine unknowns
under **Open questions**, not inline.

**PRD**: `# <title>` · Problem · Goals · Non-goals · Users and use cases ·
Requirements (numbered, testable) · Success criteria · Open questions.

**Spec**: `# <title>` · Overview (link the PRD) · Architecture · Project structure
(which file owns what) · Data model / interfaces · Key decisions (with the
alternatives rejected) · Error handling · Testing strategy (a table of required test
cases per module) · Build plan (numbered milestones, each ending on a commit
message, plus a cut order if scope may shrink) · Rollout · Open questions.

The Project structure, Testing strategy table and Build plan are what the
spec-driven workflow plans from; include them whenever the spec will drive
`/plan-tickets`.

**Ticket**: `# <ID>: <title>` · Context (one paragraph, link spec section) ·
Scope · Acceptance criteria (`- [ ]` checklist, each verifiable) · Dependencies
(ticket IDs) · Notes. Split anything bigger than about a day of work. In a repo
using the spec-driven workflow, use `/plan-tickets` instead: its tickets also need
`priority`, `milestone`, `estimate`, `depends_on` and `touches`.

**Review**: `# Review: <subject>` · Summary verdict · Findings grouped by
severity (critical / major / minor), each with `file:line` and a fix · Follow-ups.

**Reference**: free-form, but start with one line on the source and date.

**Decision**: follow the template in the repo's `CLAUDE.md` → **Decision log** if
it has one. Otherwise: frontmatter adds `ticket:`, `decided_by:` and `supersedes:`;
body is `# <the decision, as a statement>` · Context · Decision · Alternatives ·
Consequences. A committed decision is never edited; supersede it with a new file.

## After writing

1. If the doc adds tickets or a feature, add it to `STATUS.md` (`## Planned` or
   `## In progress`, one `- [ ]` per ticket for a ticket set) and bump STATUS.md's
   `updated:`.
2. If tickets use a `tickets/INDEX.md`, add the new rows there too.
3. Tell the user the path. Only `git add` it if the repo's `CLAUDE.md` says
   `.project/` is committed, and then only as part of a commit the user asked for.
