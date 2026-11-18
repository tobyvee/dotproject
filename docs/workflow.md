# The workflow

dotproject is two layers. The first is a convention: planning docs live in `.project/` at the repo root, every doc has frontmatter, and `STATUS.md` always says where things stand. The second is a build workflow on top of it: a tech spec becomes tickets, tickets become waves, and each ticket is built, verified, recorded and committed by subagents under one main session.

You can use the first layer on its own. The second needs the first.

## Layer 1: planning docs

```
.project/
├── STATUS.md      # where things stand; read first, kept current
├── prd/           # what and why
├── spec/          # how, and in what order
├── tickets/       # units of work
├── decisions/     # one file per decision (spec-driven)
├── review/        # audits and reviews with findings
└── reference/     # research and notes
```

The loop is simple:

1. **Start a session by reading `STATUS.md`** and checking `tickets/` before planning anything.
2. **Write plans into `.project/`**, never into the repo root, `docs/` or `.claude/` (`/project-doc`).
3. **Record what happened** after finishing or blocking on work (`/project-update`): ticket status, ticked criteria, a Summary that's true today, commit SHAs.

The `STATUS.md` Summary is the resumption point: the next session, or the next person, starts there. [Brief](https://github.com/tobyvee/brief) shows it for every repo at once.

Details: [The `.project/` folder](project-folder.md).

## Layer 2: spec-driven build

```
 PRD ──► spec ──► /plan-tickets ──► /prioritise-tickets ──► /implement-parallel wave N ─┐
                     │                    │                  /implement-ticket T-NNN    │
                     ▼                    ▼                                             │
              tickets/T-NNN-*.md    tickets/INDEX.md (waves)                            │
                                                                                        ▼
      ┌──────────── for each ticket, one at a time ─────────────────────────────────────┐
      │ build (worktree agent) → merge → test → code review → audits → fix → record →   │
      │ commit → push                                                                   │
      └─────────────────────────────────────────────────────────────────────────────────┘
                                                                                        │
                       milestone closed? ──► milestone-reviewer ──► spec's commit message
```

### 1. Write the PRD and the spec

The PRD says what to build and for whom; the spec says how. The workflow plans from the spec, so it needs:

- **A build plan:** numbered milestones in order, each one ending on a commit message, and ordered so stopping at any milestone still leaves something working.
- **A test-case table:** the required cases per module. Agents write tests from it rather than from "add tests".
- **A project structure:** which file owns what. Ticket ownership (`touches`) comes from here.
- **A cut order**, if scope may shrink: what goes first. It's applied only when the user asks.

### 2. Bootstrap the repo: `/workflow-init`

It makes `.project/` committed (worktree agents read tickets from `HEAD`), checks the spec has what the workflow needs, and adds a `## Workflow` section to the repo's CLAUDE.md. That section is the contract: the spec's path, the test and type-check commands, what P0 means, which agent builds which tickets, the trust boundaries, and whether to push after each ticket. The plugin's commands and agents read it and hard-code nothing. See [Adapting to a project](adapting.md).

### 3. Plan: `/plan-tickets`

`ticket-planner` splits the build plan into 10–40 minute tickets. Each ticket owns a set of files (`touches`), names its dependencies, and carries a priority, a milestone and an estimate. Shared foundations (scaffold, schema, store) come first and alone. Hotspot files are given to one ticket, which creates stubs for the others. The main session spot-checks the result, writes `INDEX.md` and commits. See [Tickets and waves](tickets-and-waves.md).

### 4. Schedule: `/prioritise-tickets`

Tickets are packed greedily into **waves** of up to four. A ticket is ready when its dependencies are done or scheduled earlier. Two tickets share a wave only if their `touches` don't overlap. The order within a wave is priority, then how much the ticket unblocks, then milestone, then estimate. Nothing is cut unless the user names it, and P0 is never cut.

### 5. Build: `/implement-parallel wave N` or `/implement-ticket T-NNN`

`/implement-parallel` launches one agent per ticket, each in its own git worktree, in a single message. Then it **lands them one at a time**:

1. `branch-integrator` rebases the ticket's branch onto the current branch, fast-forwards, and runs the tests. It fixes only mechanical conflicts and blocks the rest.
2. `code-reviewer` reviews the diff. Must-fix findings are fixed and re-reviewed until the verdict clears.
3. Extra auditors run on the paths they own (for example, an auditor for email templates), and `security-auditor` runs on tickets that cross a trust boundary. `security-fixer` fixes critical and high findings, each with a regression test that fails first.
4. The main session records the ticket: status, ticked criteria, decision links, `STATUS.md`, `INDEX.md`. It commits and pushes before the next ticket starts landing.

Each push is therefore one ticket, reviewed and recorded. A ticket that can't be fixed is parked on a `blocked/<id>` branch, and the current branch resets to before it. After the wave, `security-auditor` reviews the whole wave's diff, because tickets that are each safe can combine into a hole.

`/implement-ticket` runs the same verify-record-commit steps for one ticket in the main tree.

### 6. Close milestones

When the last ticket of a milestone lands, `milestone-reviewer` checks the milestone against the spec (as amended by the decision log) and the design. Its suggested commit message, normally the spec's, closes the milestone. The final milestone gets a full-repo security audit, and `readme-writer` writes a README that describes what actually shipped.

## Principles

These come from running the workflow on a real project, and most rules in the commands exist to enforce one of them.

- **The spec is the source of truth, and the decision log amends it.** Anything the spec doesn't settle becomes a decision file, and agents read the log before acting. See [Decision log](decision-log.md).
- **File ownership makes parallelism safe.** Agents in separate worktrees can't see each other. `touches` is the contract that lets their work merge, so agents never edit outside it.
- **Only the main session writes the record.** Agents may only add decision files under `.project/`. Tickets, `INDEX.md` and `STATUS.md` are edited by one writer, so parallel branches never conflict on them.
- **Records move with the code.** Ticket status, decisions and `STATUS.md` are committed in the same commit as the work they describe.
- **History is part of the deliverable.** History stays linear, with one ticket per landing and one commit per security fix. Commit messages describe what changed and end with the ticket ID. Nothing is force-pushed, and agents never push.
- **Reviewers can't write; writers don't review themselves.** Reviewers and auditors are read-only. When their findings force a choice, the calling session logs it.
- **Estimates size work; they are not a budget.** Nothing is shrunk or dropped to fit a time estimate. Work is cut only when the user names it, and P0 never.
- **Tests come with the module,** from the spec's case table, in the same ticket.
- **Never tick what wasn't verified.** An unmet acceptance criterion stays unticked, with the reason in the ticket's notes.
