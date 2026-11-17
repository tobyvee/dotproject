---
title: "Taskboard tech spec"
type: spec
project: taskboard
updated: 2026-11-10
tags: [project, taskboard, spec]
---
# Taskboard tech spec

## Overview
A small team task board: email sign-in, boards, columns and cards. PRD: `.project/prd/taskboard-prd.md`.

## Architecture
- Next.js App Router on Vercel, Postgres through Drizzle.
- Every write is a server action in `src/lib/actions.ts` that parses its input with the Zod schemas in `src/lib/schema.ts` and checks board membership before any query.
- Components never import from `src/db/`.
- Card order is a fractional `position` key; a move updates one row.

## Project structure
| File | Owns |
|---|---|
| `src/lib/schema.ts` | Zod schemas for boards, columns and cards |
| `src/db/schema.ts` | Drizzle tables |
| `src/db/queries.ts` | Every database query |
| `src/lib/actions.ts` | Server actions (all writes) |
| `src/auth.ts` | Auth.js email sign-in |
| `src/app/` | Routes and layouts |
| `src/components/board/` | Board UI |

## Unit tests
| Module | Required cases |
|---|---|
| `schema` | rejects an empty card title; rejects a title over 200 characters |
| `actions` | a non-member can't move a card; moving a card updates one row |
| `position` | a key between two neighbours sorts between them |

## Build plan
1. Scaffold, schema and database. Commit: `Scaffold app, schema and database`
2. Sign-in and boards. Commit: `Email sign-in and boards`
3. Columns and cards with reorder. Commit: `Columns and cards`
4. Filters by assignee. Commit: `Filters`
5. CSV export. Commit: `CSV export`
6. README and deploy. Commit: `README and deploy`

**Cut order** (only if asked): 1 = filters, 2 = CSV export.
