---
description: Order the open tickets into parallel-safe waves by priority and dependencies, and cut only the work the user asks to cut
argument-hint: "[work the user wants cut: ticket IDs or cut-order items, e.g. T-031 T-032]"
---

# Prioritise tickets

Read every ticket in `.project/tickets/` and produce the run order that `/dps:implement-parallel` will follow. `$ARGUMENTS` optionally names work the user wants cut.

Read the repo's `CLAUDE.md` first. If it has no `## Workflow` section, stop and suggest `/dps:workflow-init`.

Estimates size the work; they are never a budget. Never cut work to fit a time estimate (CLAUDE.md → **Workflow → Priorities and cuts**).

## 1. Load and validate

- Parse each ticket's frontmatter: `status`, `priority`, `milestone`, `estimate`, `depends_on`, `touches`, `cut_rank`.
- Report problems before scheduling anything:
  - A dependency that doesn't exist, or a dependency cycle.
  - A `todo` ticket with no `touches` or no `estimate`.
  - A ticket that depends on one with `priority: cut`.
- Check `status` against the code. If `git log` or the files show a `todo` ticket is actually built, say so; don't silently change it.
- Read the decision log (CLAUDE.md → **Reading the log**). A live decision can change an ordering, a dependency or a cut.

## 2. Build the waves

Consider only `todo` and `blocked` tickets that aren't cut.

1. A ticket is **ready** when all its `depends_on` are `done`, or are scheduled in an earlier wave.
2. Fill each wave greedily from the ready tickets, sorted by:
   1. Priority (P0, then P1, then P2).
   2. How many tickets transitively depend on it (unblock the most first).
   3. Milestone number.
   4. Estimate (shortest first).
3. **Two tickets can share a wave only if their `touches` don't overlap.** Directories overlap with every file inside them, and dependency-manifest and lockfile changes (e.g. `package.json` and `package-lock.json`) count as overlapping with each other. If two tickets clash, put the lower-ranked one in the next wave.
4. Cap each wave at **4 tickets**. Past that, merge conflicts and review cost outweigh the gain.
5. A wave's length is its longest estimate. Add up the wave lengths to get the critical-path time.

## 3. Cut only what the user asks for

Cut only work the user named, in `$ARGUMENTS` or the conversation. A cut-order item maps to its tickets by `cut_rank`, using the cut order in CLAUDE.md → **Workflow → Priorities and cuts**.

**Never cut P0.** If the user names a P0 ticket, say so and leave it in. For each cut, set `priority: cut` and keep `status: todo`, so it still shows as unbuilt. Also add a `## Cut` note giving the reason, so the README can say what was cut and why.

Log each cut as a decision in `.project/decisions/` (`<ticket-id>-cut.md`, `decided_by: user`), following CLAUDE.md's **Decision log**. Give the user's reason as context and keeping the ticket as the alternative. Whenever you override the wave-ordering rules in step 2, e.g. to pull a lower-priority ticket forward, log that too (`decided_by: main session`).

## 4. Write it down

- Rewrite `.project/tickets/INDEX.md` (keep its frontmatter, with no `status:`) with:
  - A **Waves** section: one table per wave with ID, title, priority, estimate and touches.
  - A **Cut** list.
  - A **Problems** list from step 1.
  - The ticket table, re-sorted into run order.
- Update `STATUS.md`:
  - Wave 1 tickets go under `## Outstanding`.
  - Cut tickets go under `## Planned` with "(cut)" appended.
  - Bump the `updated:` dates.
- Commit the ticket, decision, `INDEX.md` and `STATUS.md` changes together, e.g. `Prioritise tickets into waves`, ending with the attribution trailer Claude Code currently specifies. `/dps:implement-parallel` needs a clean tree, and its worktrees read the waves from `HEAD`.
- Report the waves as a compact list, the critical-path time, and any cuts. Then suggest the exact next command: `/dps:implement-parallel wave 1`, or `/dps:implement-ticket T-NNN` if the next wave has only one ticket.
