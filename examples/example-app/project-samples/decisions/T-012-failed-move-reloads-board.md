---
title: "A failed card move reloads the board"
type: decision
project: example-app
ticket: T-012
decided_by: ticket-implementer
supersedes:
updated: 2026-11-12
tags: [project, example-app, decision, ui]
---
# A failed card move reloads the board

## Context
The spec says a move shows immediately (**UI → Card list**) but not what happens when `moveCard` returns `{ ok: false }`, e.g. when another member deleted the card or the session expired.

## Decision
On failure, call `router.refresh()` so the list shows the server's order, and show "Couldn't move card".

## Alternatives
- Roll back the optimistic order locally: needs the previous order kept per move, and can still disagree with the server if another member changed the column.
- Ignore the failure: the list would show an order the database doesn't have.

## Consequences
The board re-renders from the server after any failed move.
