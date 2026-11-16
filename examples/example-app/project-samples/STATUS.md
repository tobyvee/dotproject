---
title: "example-app — Status"
type: status
project: example-app
updated: 2026-11-12
tags: [project, example-app, status]
---
# example-app — Status

> PM docs: this repo's `.project/` (`prd/`, `spec/`, `tickets/`, `decisions/`, this file). Committed with the repo.

## Summary

The task board's core is built and deployed: email sign-in, boards, columns, cards with add, edit and reorder, all saved to Postgres. Waves 1 to 5 are done (12 of 18 tickets). Milestones 1 and 3 are closed, and milestone 2 closes when invites (`T-007`) land. Every ticket was reviewed, and the five that crossed a trust boundary were security-audited; the wave audits found one medium, which was fixed in wave 4. 214 tests pass. Wave 6 (invites, due dates, CSV export and the digest query) is next, and needs `CRON_SECRET` set in Vercel before `T-016` lands.

## In progress

## Outstanding

Questions waiting on the user:
- [ ] Should the digest go out at 08:00 in each member's own time zone, or at one fixed time for everyone? The spec doesn't say; `T-016` needs the answer.

Setup the user needs to do:
- [ ] Add `CRON_SECRET` to the Vercel project's environment variables before wave 6.

## Planned

- [ ] Wave 6: `T-007` invites, `T-013` due dates, `T-015` CSV export, `T-016` digest query and job
- [ ] Wave 7: `T-014` filters, `T-017` digest email template
- [ ] Wave 8: `T-018` README and final deploy

## Completed

- [x] Repo created, `.project/` set up and committed (2026-11-09)
- [x] PRD and tech spec written and reviewed (2026-11-09)
- [x] Build planned and prioritised: 18 tickets in 8 waves (2026-11-10)
- [x] T-001: Scaffold the Next.js app with Vitest, lint and the CI workflow (2026-11-10)
- [x] T-002: Zod schemas for boards, columns and cards (2026-11-10)
- [x] T-010: Fractional position keys (2026-11-10)
- [x] T-003: Drizzle tables, migrations and query helpers (2026-11-10)
- [x] T-004: Email sign-in with Auth.js and the session guard (2026-11-10)
- [x] Milestone 1 closed: scaffold, schema and database (2026-11-10)
- [x] Wave 3 closed; wave-wide security audit found nothing (2026-11-10)
- [x] T-005: Server actions with input parsing and membership checks (2026-11-11)
- [x] T-008: Board page shell with column slots (2026-11-11)
- [x] Wave 4 closed; wave-wide security audit found one medium (a column could be moved to another board), fixed in `4f2a9c1` (2026-11-11)
- [x] T-006: Boards page: list, create and rename (2026-11-11)
- [x] T-009: Columns: create, rename and reorder (2026-11-12)
- [x] T-011: Card dialog: title, description and assignee (2026-11-12)
- [x] T-012: Card list with add and reorder (2026-11-12)
- [x] Milestone 3 closed: columns and cards (2026-11-12)
- [x] Wave 5 closed; wave-wide security audit found nothing (2026-11-12)
