---
title: "A failed card move rolls back the optimistic order and keeps the add-card input"
type: decision
project: example-app
ticket: T-012
decided_by: main session
supersedes: T-012-failed-move-reloads-board.md
updated: 2026-11-12
tags: [project, example-app, decision, ui]
---
# A failed card move rolls back the optimistic order and keeps the add-card input

## Context
`code-reviewer` found that the refresh in `T-012-failed-move-reloads-board.md` remounts the column, which throws away whatever the user was typing in "+ Add card". `useOptimistic` already reverts to the server state when its transition ends, so the refresh isn't needed for the list to be right.

## Decision
On failure, let `useOptimistic` revert the order, show "Couldn't move card", and leave the add-card input as it was. `revalidatePath` in `moveCard` (T-005) still brings in other members' changes on the next successful write.

## Alternatives
- **Keep the refresh:** loses typed input, which the review rated should-fix.
- **Refresh but preserve the input in a ref:** more code for the same result.

## Consequences
Later tickets with optimistic writes (such as T-013's due date) follow the same pattern: revert locally, never refresh on failure. A test pins that a failed move keeps the input's value.
