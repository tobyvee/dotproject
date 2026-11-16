---
title: "example-app — Ticket index"
type: reference
project: example-app
updated: 2026-11-12
tags: [project, example-app, reference, tickets]
---
# example-app — Ticket index

The run order for `/implement-parallel`: 18 tickets in 8 waves. Estimates add up to 325 minutes of agent work. The critical path, the sum of each wave's longest ticket, is 150 minutes before merging and review. Estimates size the work; they aren't a budget ([`general-time-budget-is-user-time.md`](../decisions/general-time-budget-is-user-time.md)).

Waves follow the greedy rules in `/prioritise-tickets`, with one override: `T-018` (README and final deploy) runs alone, last. Each ticket is pushed as it lands ([`general-push-after-each-ticket.md`](../decisions/general-push-after-each-ticket.md)).

## Waves

### Wave 1 (25 min)

| ID | Title | Priority | Estimate | Touches |
|---|---|---|---|---|
| T-001 | Scaffold the Next.js app with Vitest, lint and the CI workflow | P0 | 25 | `package.json`, `package-lock.json`, `tsconfig.json`, `next.config.ts`, `eslint.config.mjs`, `vitest.config.ts`, `.env.example`, `.gitignore`, `.github/workflows/ci.yml`, `src/app/layout.tsx`, `src/app/page.tsx` |

### Wave 2 (15 min)

| ID | Title | Priority | Estimate | Touches |
|---|---|---|---|---|
| T-002 | Zod schemas for boards, columns and cards | P0 | 15 | `src/lib/schema.ts`, `src/lib/schema.test.ts` |
| T-010 | Fractional position keys | P0 | 10 | `src/lib/position.ts`, `src/lib/position.test.ts` |

### Wave 3 (25 min)

| ID | Title | Priority | Estimate | Touches |
|---|---|---|---|---|
| T-003 | Drizzle tables, migrations and query helpers | P0 | 25 | `src/db/schema.ts`, `src/db/queries.ts`, `src/db/queries.test.ts`, `drizzle.config.ts`, `drizzle/` |
| T-004 | Email sign-in with Auth.js and the session guard | P0 | 25 | `src/auth.ts`, `src/db/auth-schema.ts`, `middleware.ts`, `src/app/api/auth/[...nextauth]/route.ts`, `src/app/page.tsx` |

### Wave 4 (20 min)

| ID | Title | Priority | Estimate | Touches |
|---|---|---|---|---|
| T-005 | Server actions with input parsing and membership checks | P0 | 20 | `src/lib/actions.ts`, `src/lib/actions.test.ts` |
| T-008 | Board page shell with column slots | P0 | 20 | `src/app/(app)/layout.tsx`, `src/app/(app)/boards/[id]/page.tsx`, `src/components/board/Board.tsx`, `src/components/board/Column.tsx`, `src/components/board/CardList.tsx`, `src/components/board/CardDialog.tsx` |

### Wave 5 (20 min)

| ID | Title | Priority | Estimate | Touches |
|---|---|---|---|---|
| T-006 | Boards page: list, create and rename | P0 | 15 | `src/app/(app)/boards/page.tsx`, `src/components/boards/BoardList.tsx`, `src/components/boards/BoardList.test.tsx` |
| T-009 | Columns: create, rename and reorder | P0 | 15 | `src/components/board/Column.tsx`, `src/components/board/Column.test.tsx` |
| T-011 | Card dialog: title, description and assignee | P0 | 20 | `src/components/board/CardDialog.tsx`, `src/components/board/CardDialog.test.tsx` |
| [T-012](T-012-card-list.md) | Card list with add and reorder | P0 | 20 | `src/components/board/CardList.tsx`, `src/components/board/CardList.test.tsx`, `src/components/board/CardRow.tsx` |

### Wave 6 (20 min)

| ID | Title | Priority | Estimate | Touches |
|---|---|---|---|---|
| T-016 | Digest query and scheduled job | P2 | 20 | `src/lib/digest.ts`, `src/lib/digest.test.ts`, `src/app/api/cron/digest/route.ts`, `vercel.json` |
| T-007 | Invite a teammate by email | P1 | 20 | `src/app/invite/[token]/page.tsx`, `src/emails/Invite.tsx`, `src/components/board/InviteForm.tsx` |
| T-015 | CSV export with formula escaping | P1 | 20 | `src/lib/csv.ts`, `src/lib/csv.test.ts`, `src/app/api/boards/[id]/export/route.ts` |
| T-013 | Due dates with an overdue badge | P1 | 15 | `src/components/board/DueBadge.tsx`, `src/components/board/DueBadge.test.tsx`, `src/lib/dates.ts` |

### Wave 7 (15 min)

| ID | Title | Priority | Estimate | Touches |
|---|---|---|---|---|
| T-014 | Filters by assignee and due date | P1 | 15 | `src/components/board/Filters.tsx`, `src/components/board/Filters.test.tsx` |
| T-017 | Digest email template | P2 | 15 | `src/emails/Digest.tsx`, `src/emails/Digest.test.tsx` |

### Wave 8 (10 min)

| ID | Title | Priority | Estimate | Touches |
|---|---|---|---|---|
| T-018 | README and final deploy | P1 | 10 | `README.md` |

## All tickets

| Wave | ID | Title | Priority | Milestone | Estimate | Depends on | Status |
|---|---|---|---|---|---|---|---|
| 1 | T-001 | Scaffold the Next.js app with Vitest, lint and the CI workflow | P0 | 1 | 25 | — | done |
| 2 | T-002 | Zod schemas for boards, columns and cards | P0 | 1 | 15 | T-001 | done |
| 2 | T-010 | Fractional position keys | P0 | 3 | 10 | T-001 | done |
| 3 | T-003 | Drizzle tables, migrations and query helpers | P0 | 1 | 25 | T-002 | done |
| 3 | T-004 | Email sign-in with Auth.js and the session guard | P0 | 2 | 25 | T-001 | done |
| 4 | T-005 | Server actions with input parsing and membership checks | P0 | 2 | 20 | T-003, T-004, T-010 | done |
| 4 | T-008 | Board page shell with column slots | P0 | 3 | 20 | T-003, T-004 | done |
| 5 | T-006 | Boards page: list, create and rename | P0 | 2 | 15 | T-005 | done |
| 5 | T-009 | Columns: create, rename and reorder | P0 | 3 | 15 | T-005, T-008 | done |
| 5 | T-011 | Card dialog: title, description and assignee | P0 | 3 | 20 | T-005, T-008 | done |
| 5 | [T-012](T-012-card-list.md) | Card list with add and reorder | P0 | 3 | 20 | T-005, T-008, T-010 | done |
| 6 | T-016 | Digest query and scheduled job | P2 | 6 | 20 | T-003 | todo |
| 6 | T-007 | Invite a teammate by email | P1 | 2 | 20 | T-005 | todo |
| 6 | T-015 | CSV export with formula escaping | P1 | 5 | 20 | T-003, T-005 | todo |
| 6 | T-013 | Due dates with an overdue badge | P1 | 4 | 15 | T-011 | todo |
| 7 | T-014 | Filters by assignee and due date | P1 | 4 | 15 | T-012, T-013 | todo |
| 7 | T-017 | Digest email template | P2 | 6 | 15 | T-016 | todo |
| 8 | T-018 | README and final deploy | P1 | 7 | 10 | all | todo |
