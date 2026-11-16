# dps plugin (spec-driven)

Turns a tech spec into small, dependency-tagged tickets, schedules them into parallel-safe waves, and builds each one with tests, code review, a security audit, a decision log and a commit. Requires a committed `.project/` (see the `dp` plugin).

## Commands, in order

| Command | What it does |
|---|---|
| `/workflow-init` | Bootstraps the repo: a committed `.project/`, a spec check, and the `## Workflow` contract in CLAUDE.md. Optionally adds project agents. |
| `/plan-tickets [all \| build step N \| description]` | `ticket-planner` splits the work into 10–40 minute tickets; the main session checks them, writes `INDEX.md` and commits. |
| `/prioritise-tickets [work to cut]` | Orders open tickets into waves of up to four with no overlapping `touches`. Cuts only what you name, never P0. |
| `/implement-parallel wave N` | One worktree agent per ticket, then lands them one at a time: merge, review, audit, record, commit, push. A security audit closes the wave. |
| `/implement-ticket T-NNN` | One ticket in the main tree, with the same verify, record, commit and push steps. |

## Agents

`ticket-planner`, `ticket-implementer`, `test-writer`, `branch-integrator`, `readme-writer`, plus the read-only `code-reviewer`, `security-auditor` and `milestone-reviewer`, plus `security-fixer`. Installed, they're `dps:<name>`.

## Templates

- `templates/CLAUDE-workflow.md`: the contract `/workflow-init` adds to CLAUDE.md.
- `templates/agents/stack-specialist.md` and `output-auditor.md`: starting points for project agents.

Docs: [The workflow](../../docs/workflow.md) · [Tickets and waves](../../docs/tickets-and-waves.md) · [Decision log](../../docs/decision-log.md) · [Agents](../../docs/agents.md) · [Adapting to a project](../../docs/adapting.md).
