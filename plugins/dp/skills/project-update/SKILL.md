---
name: project-update
description: Record finished or changed work in the repo's .project/ docs. Sets ticket status, ticks STATUS.md checklists, rewrites the Summary, moves items between In progress / Outstanding / Completed, bumps updated dates and fixes frontmatter. Use after completing a ticket or feature, when work gets blocked, or when the user says "update STATUS" or "update the project docs".
argument-hint: "[what changed, e.g. 'T-007 done' or 'blocked on API keys']"
---

# Update `.project/`

Bring `.project/` in line with what actually happened. `$ARGUMENTS` describes the
change; if empty, work it out from this conversation and `git log` since
STATUS.md's `updated:` date.

The docs are the resumption point for the next session and the source for the
`/project-status` dashboard, so record **facts**: commit SHAs, dates, what was
verified, what is still broken. Never tick something that wasn't finished and
verified.

## 1. Tickets

For each ticket the work touched:

- Set frontmatter `status:` (`todo` → `doing` → `done`, or `blocked`) and bump
  its `updated:`.
- Tick acceptance-criteria boxes that were met; leave the rest unticked and say
  why in **Notes**.
- If the repo keeps a decision log (`.project/decisions/`), add or extend the
  ticket's `## Decisions` list with a link to every decision file naming it.
- In a one-file-per-feature ticket doc, set the doc's `status: done` only when
  every ticket in it is done.
- Update `tickets/INDEX.md` (or the repo's equivalent) if present.

## 2. STATUS.md

- **`## Summary`**: rewrite the first paragraph so it is true today. The
  dashboard quotes it: plain prose, one or two sentences, no leading list, quote
  or table.
- Tick the matching `- [ ]` boxes; move finished features to **Completed** with
  the date and commit SHAs; list follow-ups under **Outstanding** (one line each:
  what, where, why it matters).
- Record blockers explicitly: what is needed, from whom. That's what makes a
  project show as `blocked` instead of silently stale.
- Bump `updated:` to today (`date +%F`).

## 3. Roll-ups

- If the repo is part of a workspace with a parent `.project/STATUS.md` (e.g. a
  monorepo root), update its row or summary for this project too.
- If the repo's `CLAUDE.md` has a status table or checklist mirroring STATUS.md,
  update it to match, and mention that the CLAUDE.md change needs committing.
- If the dashboard is set up (`~/.config/dotproject/project-next.json` exists) and
  the work changed what to do next, update the project's entry there (`status`
  and one concrete `next` action). Don't run `/project-status` unless asked.

## 4. Frontmatter check

For every `.project/` doc you touched (or all of them, if the user asks for a
check), confirm the frontmatter has `title`, `type`, `project` (matching
STATUS.md), `updated` (`YYYY-MM-DD`) and `tags`, and that `status` appears only on
tickets, with a value from `todo | doing | done | blocked`. Fix what's wrong;
report anything you couldn't infer.

## 5. Report

List each file changed and the one-line change. If the repo's `CLAUDE.md` says
`.project/` is committed, these changes belong in the same commit as the work they
record: say so, and commit only if asked or if the calling command commits.
Otherwise `.project/` is gitignored; never `git add` it.
