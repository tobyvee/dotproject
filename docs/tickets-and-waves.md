# Tickets and waves

In the spec-driven workflow, a ticket is a 10–40 minute unit of work that one agent can build in an isolated worktree from the ticket and the spec alone. A wave is a set of up to four tickets that can be built at the same time without touching the same files.

## Ticket format

`ticket-planner` writes tickets as `.project/tickets/T-NNN-<slug>.md`:

```markdown
---
title: "T-012: Card list with add and reorder"
type: ticket
project: <project>
status: todo            # todo | doing | done | blocked
priority: P0            # P0 | P1 | P2 | cut, as defined in CLAUDE.md → Workflow → Priorities and cuts
milestone: 3            # the spec's build-plan step
estimate: 20            # minutes
depends_on: [T-003, T-008]
touches:                # every file or directory this ticket creates or edits
  - src/components/board/CardList.tsx
  - src/components/board/CardList.test.tsx
cut_rank:               # its place in the spec's cut order, only for cuttable work
updated: YYYY-MM-DD
tags: [project, <project>, ticket, ui]
---
# T-012: Card list with add and reorder

## Context       one paragraph, linking the spec section, the design artboard and the decisions that shape it
## Scope         what to build, naming files, functions and props; plus what's out of scope
## Acceptance criteria   - [ ] verifiable items: a test case, a visible behaviour, a rule from CLAUDE.md
## Dependencies  why each depends_on entry is needed
## Notes         the spec detail the implementer needs, quoted or summarised
```

When the ticket lands, the main session adds:

- `## Outcome`: what was built, the review and audit results, and the fixes made.
- `## Decisions`: links to every decision file naming the ticket.

A finished example is [`examples/example-app/project-samples/tickets/T-012-card-list.md`](../examples/example-app/project-samples/tickets/T-012-card-list.md).

## The fields that matter

**`touches`** is what makes parallel work safe. Agents edit only the files listed there; directories overlap with every file inside them. If an agent needs another file, it stops and reports it, and doesn't edit it. Two tickets may list the same file only if one depends on the other, directly or indirectly.

**`depends_on`** is minimal and real. A false dependency serialises work for no reason; a missing one breaks the build when parallel work merges.

**`priority`:**

| Priority | Meaning |
|---|---|
| P0 | The minimum the product must ship. Never cut. |
| P1 | Planned extras. |
| P2 | Stretch. Still scheduled, after the planned work. |
| cut | Cut at the user's request. `status` stays `todo` so it still shows as unbuilt, and a `## Cut` note gives the reason. |

**`estimate`** sizes the work and plans the waves. It's never checked against a time budget, so nothing is shrunk or dropped to fit.

## How the planner splits work

- **One ticket owns a set of files.** Two tickets that would edit the same file are combined, or one depends on the other.
- **Shared foundations come first and alone:** scaffold, schema, store. They stay small, because everything depends on them.
- **Hotspots get one owner.** If several later tickets need new store actions, one foundation ticket adds them all up front. If parts must be registered in a router or index file, the foundation ticket creates every slot with stubs, or the wiring gets its own ticket after the parts.
- **Dependencies go in the scaffold** wherever possible, so later tickets don't each touch the manifest and lockfile.
- **Pure modules are separate from UI.**
- **Tests are in the same ticket as their module,** from the spec's case table.
- **Trust boundaries are tagged `security`,** with an acceptance criterion for the specific threat (e.g. "a `javascript:` URL is rejected by the schema (test)").
- **A security finding becomes one P0 ticket** whose first criterion is the finding's regression test.

## Waves

`/prioritise-tickets` turns open tickets into waves, written to `tickets/INDEX.md`:

1. A ticket is **ready** when all its dependencies are done or scheduled in an earlier wave.
2. Each wave is filled greedily from ready tickets, sorted by priority, then how many tickets transitively depend on it, then milestone, then estimate (shortest first).
3. **Two tickets share a wave only if their `touches` don't overlap.** Manifest and lockfile changes all count as overlapping.
4. **At most four tickets per wave.** Past that, merge conflicts and review cost outweigh the gain.
5. A wave's length is its longest estimate, and the sum of wave lengths is the critical path.

Overrides of these rules, such as pulling a ticket forward, are logged as decisions.

## How a ticket lands

```
todo ──► doing ──► built (agent commit, in a worktree) ──► merged ──► reviewed ──► done (record commit, push)
                                                    └──► blocked (blocked/<id> branch, reason in Notes)
```

1. **Preflight:** clean tree; the branch matches its upstream (if pushing after each ticket); every dependency is done; no `touches` overlap in the wave.
2. **Build:** the implementer from **Workflow → Implementers** builds the ticket with its tests, runs the configured checks, and commits. It never pushes.
3. **Merge** (parallel only): `branch-integrator` rebases onto the current branch and fast-forwards, keeping history linear.
4. **Verify:**
   - `code-reviewer`: must-fix findings are fixed until the verdict clears.
   - Extra auditors run on their paths.
   - `security-auditor` runs on trust boundaries. Critical and high findings are fixed, each with a regression test. Medium ones are fixed if small, otherwise become a follow-up ticket. Low ones go in the ticket's notes.
5. **Record:** decisions, `status: done`, ticked criteria, `STATUS.md`, `INDEX.md`. When the ticket closes a milestone, `milestone-reviewer` runs first and supplies the commit message.
6. **Commit and push**, before the next ticket starts landing. A rejected push stops the run. Nothing is force-pushed, and nothing is rebased over a rejection.

A must-fix, critical or high finding that can't be resolved means the ticket isn't pushed. Its work is kept on `blocked/<id>`, the branch resets to before it, and the ticket is recorded as `blocked`.

## Commit messages

- Code: describe the change and end with the ticket ID, e.g. `Card list with add and reorder (T-012)`.
- Records: `Record card list as done (T-012)`.
- Security fixes: one commit per finding, describing the protection (`Reject javascript: URLs in image sources`), never the exploit, with no per-report finding IDs.
- Milestones close on the spec's commit message for that step, adjusted to what was actually built.
