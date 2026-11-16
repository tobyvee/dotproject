---
title: "T-012: Card list with add and reorder"
type: ticket
project: example-app
status: done
priority: P0
milestone: 3
estimate: 20
depends_on: [T-005, T-008, T-010]
touches:
  - src/components/board/CardList.tsx
  - src/components/board/CardList.test.tsx
  - src/components/board/CardRow.tsx
cut_rank:
updated: 2026-11-12
tags: [project, example-app, ticket, ui]
---
# T-012: Card list with add and reorder

## Context
Build step 3 (spec → **UI → Card list**). This replaces the `CardList` stub from T-008. Cards are added inline and reordered within a column with Move up and Move down buttons; dragging between columns is out of scope for release 1 (PRD → **Later**). Order uses the position keys from T-010, and writes go through `createCard` and `moveCard` from T-005. Decisions: `T-005-actions-return-result-objects.md`, `T-010-position-keys-are-strings.md`.

## Scope
- `CardList({ boardId, column, cards })` renders `<ol aria-label="{column.name} cards">`, sorted by `position`.
- `CardRow({ card, isFirst, isLast, onMove })`: the title as a button that opens the card dialog (T-011), the assignee's initials, and Move up and Move down buttons (`aria-label="Move {title} up"` / `"down"`, disabled at the ends).
- **Add:** a "+ Add card" button that turns into a single-line input. Enter calls `createCard({ boardId, columnId, title })` and keeps the input open for the next card; Escape closes it. Empty titles aren't submitted.
- **Reorder:** `moveCard({ cardId, before, after })` with the neighbours' positions, shown immediately with `useOptimistic`.
- **Out of scope:** drag and drop; moving cards between columns; due-date badges (T-013).

## Acceptance criteria
- [x] Adding a card appends it to the column and keeps focus in the input.
- [x] Up and down reorder cards; the first card's Up and the last card's Down are disabled.
- [x] A move writes one row: `moveCard` is called once, with the neighbours' positions (spec test table, **CardList**).
- [x] If `moveCard` fails, the list returns to its previous order and says "Couldn't move card".
- [x] Every control is a real `<button>` or `<input>` with an accessible name; Tab reaches all of them.
- [x] Card titles render as text, never HTML.
- [x] `npm test`, `npx tsc --noEmit` and `npm run lint` pass.

## Dependencies
- T-005: `createCard` and `moveCard`, and their result objects.
- T-008: the `CardList` stub and its place in `Column`.
- T-010: `between(before, after)` for the optimistic position.

## Notes
- Actions return `{ ok: true, data } | { ok: false, error }` rather than throwing (`T-005-actions-return-result-objects.md`).
- Position keys are strings; compare them with `<`, never `localeCompare` (`T-010-position-keys-are-strings.md`).

## Outcome
- **Built:** the card list with inline add, up and down reordering with optimistic updates, and the failure message. 31 new tests; 214 pass in total, and `tsc` and lint are clean.
- **Review:** approved with two should-fixes, both fixed in `9b3e7d2` by the ticket implementer:
  - A failed move reloaded the board, which threw away a half-typed card title. It now rolls back the optimistic order instead ([`T-012-failed-move-rolls-back.md`](../decisions/T-012-failed-move-rolls-back.md), superseding [`T-012-failed-move-reloads-board.md`](../decisions/T-012-failed-move-reloads-board.md)).
  - Move buttons are described by the card's assignee, so two cards with the same title can be told apart.
- **Audits:** no trust boundary touched, so no security audit. No extra audit applies.

## Decisions
- [`T-012-failed-move-reloads-board.md`](../decisions/T-012-failed-move-reloads-board.md): a failed move reloads the board (superseded)
- [`T-012-failed-move-rolls-back.md`](../decisions/T-012-failed-move-rolls-back.md): a failed move rolls back the optimistic order and keeps the add-card input
