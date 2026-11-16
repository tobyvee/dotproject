# Agents

The `dps` plugin ships nine generic agents. Installed, they're named `dps:<agent>`. Each reads the repo's CLAUDE.md (the `## Workflow` contract and the decision log rules), the spec, and the relevant decisions before acting. The commands delegate heavy work to them, and you can also call any of them directly.

Two rules apply to all of them:

- **`.project/` is read-only for agents,** except for adding new files to `.project/decisions/`. Only the main session edits tickets, `INDEX.md` and `STATUS.md`.
- **Agents never push.** Only the main session pushes, and only a reviewed, recorded ticket.

## Planning

| Agent | Job | Writes | Called by |
|---|---|---|---|
| [`ticket-planner`](../plugins/dps/agents/ticket-planner.md) | Splits the spec's build plan, or a described piece of work, into 10–40 minute tickets with `priority`, `milestone`, `estimate`, `depends_on` and `touches`. Checks there are no cycles, no shared `touches` without a dependency, and nothing in scope left uncovered. | Ticket files, decision files | `/plan-tickets` |

## Building

| Agent | Job | Writes | Called by |
|---|---|---|---|
| [`ticket-implementer`](../plugins/dps/agents/ticket-implementer.md) | Builds exactly one ticket with its tests, inside its `touches`. Runs the configured checks, then commits. Returns `done`, `partial` or `blocked`, plus what later tickets will rely on. | Code, tests, decision files | `/implement-parallel` (one per worktree), `/implement-ticket` |
| [`test-writer`](../plugins/dps/agents/test-writer.md) | Writes a module's tests from the spec's case table and runs them. If the module is wrong, it leaves the test failing and reports the bug, without changing the module. | Tests, decision files | `/implement-ticket`, or directly after writing a module |
| [`branch-integrator`](../plugins/dps/agents/branch-integrator.md) | Rebases a wave's ticket branches onto the current branch one at a time and runs tests after each. Fixes only mechanical conflicts (imports, barrel files, lockfiles, list entries) and blocks everything else. | Integration fixes, decision files | `/implement-parallel` |
| [`readme-writer`](../plugins/dps/agents/readme-writer.md) | Writes the README from what actually shipped: how it maps to the brief, the key decisions, what was cut, and the path to production. | `README.md` | The final milestone |

## Reviewing (read-only)

| Agent | Checks | Called by |
|---|---|---|
| [`code-reviewer`](../plugins/dps/agents/code-reviewer.md) | Correctness, completeness, concision, readability, and practice for the installed versions of the stack. Returns must-fix, should-fix and nit findings with a verdict: approve, approve with should-fixes, or changes required. | `/implement-ticket`, `/implement-parallel` |
| [`security-auditor`](../plugins/dps/agents/security-auditor.md) | A diff or the whole repo, against a generic checklist plus the project's own. Covers output injection, URL allowlists, secrets, uploads, persisted state, API routes and SSRF, CI triggers and permissions, secret history and dependencies. Each finding has an exploit, a fix and a regression test, ranked critical to low. | `/implement-ticket` (trust-boundary tickets), `/implement-parallel` (each ticket and each wave), before the final deploy (`full`) |
| [`milestone-reviewer`](../plugins/dps/agents/milestone-reviewer.md) | A finished milestone against the spec as amended by the decision log, and against the design. Runs the checks, flags scope creep, and suggests the commit message. | When a ticket closes a milestone |

## Fixing

| Agent | Job | Writes | Called by |
|---|---|---|---|
| [`security-fixer`](../plugins/dps/agents/security-fixer.md) | Fixes the findings it's given. Each fix starts with a regression test that must fail, and is committed separately when asked. Returns `fixed`, `not reproduced`, or `needs decision` when the fix would remove something a customer can do. | Code, tests, decision files | `/implement-ticket`, `/implement-parallel` |

## Project agents

Generic agents can't know your stack's sharp edges or your output's hard constraints. `/workflow-init` offers two kinds of project agent, created in the repo's `.claude/agents/` from templates in [`plugins/dps/templates/agents/`](../plugins/dps/templates/agents/):

| Template | For | Registered in | Example |
|---|---|---|---|
| [`stack-specialist.md`](../plugins/dps/templates/agents/stack-specialist.md) | A framework that's easy to get wrong across versions (scaffold, routing, config, hydration, build). It implements those tickets and fixes review findings in its area, checking the installed version's docs. | **Workflow → Implementers** | [`nextjs-specialist`](../examples/example-app/dot-claude/agents/nextjs-specialist.md) |
| [`output-auditor.md`](../plugins/dps/templates/agents/output-auditor.md) | Output with strict external constraints: a page for a restricted WebView, an email, an exported file, a public API contract. It's read-only. | **Workflow → Extra audits** | [`email-auditor`](../examples/example-app/dot-claude/agents/email-auditor.md) |

## Who runs what, per ticket

```
/implement-ticket T-NNN                     /implement-parallel wave N
──────────────────────                      ──────────────────────────
implementer (or main session)               implementer × up to 4, in worktrees
  └ test-writer                             for each ticket, in order:
code-reviewer ⇄ implementer (fixes)           branch-integrator
extra auditors ⇄ their fixer                  code-reviewer ⇄ implementer
security-auditor ⇄ security-fixer             extra auditors ⇄ their fixer
milestone-reviewer (if it closes one)         security-auditor ⇄ security-fixer
record, commit, push                          milestone-reviewer (if it closes one)
                                              record, commit, push
                                            security-auditor over the whole wave
```
