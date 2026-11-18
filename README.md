# dotproject

A Claude Code plugin marketplace for the `.project/` workflow. Planning docs live in the repo next to the code. When you want it, a spec-driven ticket workflow turns a tech spec into small tickets and builds them with subagents. Each ticket is tested, reviewed, audited, recorded and committed.

## What's in it

| Plugin | What you get | Use it when |
|---|---|---|
| [`dp`](plugins/dp/) | `/project-init`, `/project-doc`, `/project-update` | Any repo where you want PRDs, specs, tickets and a `STATUS.md` that Claude reads first and keeps current |
| [`dps`](plugins/dps/) | `/workflow-init`, `/plan-tickets`, `/prioritise-tickets`, `/implement-ticket`, `/implement-parallel`, and nine agents | A repo with a tech spec you want built ticket by ticket, in parallel where it's safe, with a reviewable commit history |

`dps` builds on `dp`'s folder and conventions. Install both.

**Companion app:** [Brief](https://github.com/tobyvee/brief) is a native macOS app for reading and editing `.project/` docs. Point it at a folder such as `~/Code` and it finds every `.project/` beneath it, showing each project's status, PRDs, specs, tickets and reviews, kept up to date as agents change them.

## Install

```
/plugin marketplace add tobyvee/dotproject
/plugin install dp@dotproject
/plugin install dps@dotproject
```

Plugin skills and commands are namespaced (`/dp:project-init`, `/dps:plan-tickets`), and the short form works when nothing else claims the name. Plugin agents are named `dps:<agent>`.

## Quick start

**Just the planning docs:**

```
/project-init                        # .project/ with STATUS.md, gitignored by default
/project-doc prd "Guest checkout"
/project-doc spec "Guest checkout"
# ...work...
/project-update "T-003 done"
```

**The full spec-driven workflow:**

```
/project-init --commit               # the workflow needs .project/ in git
/project-doc spec "MVP"              # needs a build plan (milestones) and a test-case table
/workflow-init                       # adds the Workflow contract to CLAUDE.md
/plan-tickets all                    # spec → tickets in .project/tickets/
/prioritise-tickets                  # tickets → parallel-safe waves in INDEX.md
/implement-parallel wave 1           # one worktree agent per ticket, landed one at a time
/implement-ticket T-007              # or one ticket in place
```

## Documentation

| Doc | Covers |
|---|---|
| [The workflow](docs/workflow.md) | The whole loop from PRD to deployed milestone, and the principles behind it |
| [The `.project/` folder](docs/project-folder.md) | Layout, frontmatter, doc types, `STATUS.md`, local versus committed |
| [Tickets and waves](docs/tickets-and-waves.md) | Ticket format, `touches`, priorities, waves, and how a ticket lands |
| [Decision log](docs/decision-log.md) | What counts as a decision, the file format, who writes, how agents read it |
| [Agents](docs/agents.md) | Each agent's job, what it may write, and who calls it |
| [Adapting to a project](docs/adapting.md) | The `## Workflow` contract in CLAUDE.md, project specialists and auditors |

## Repository layout

```
.claude-plugin/marketplace.json     the marketplace manifest
plugins/
  dp/                               .project/ docs plugin
    skills/project-{init,doc,update}/
  dps/                              ticket workflow plugin
    commands/                       plan-tickets, prioritise-tickets, implement-ticket, implement-parallel
    agents/                         ticket-planner, ticket-implementer, test-writer, code-reviewer,
                                    security-auditor, security-fixer, branch-integrator,
                                    milestone-reviewer, readme-writer
    skills/workflow-init/           bootstraps a repo for the workflow
    templates/                      the CLAUDE.md Workflow contract, plus project agent templates
docs/                               the documentation above
examples/example-app/               a worked example of an adapted repo (fictional)
```

## Global instructions (optional)

To make every session look in `.project/` first, add this to `~/.claude/CLAUDE.md`:

```markdown
## Project planning docs (`.project/`)

Every project keeps its planning docs in a `.project/` folder at its repo root
(`STATUS.md`, `prd/`, `spec/`, `tickets/`, and `review/`, `reference/`,
`decisions/` when needed). It's gitignored unless the repo's CLAUDE.md says it's
committed.

- **Look there first.** Read `.project/STATUS.md` for where things stand, and
  check `.project/tickets/` before planning anything. A repo's own `CLAUDE.md`
  overrides these defaults.
- **Put plans there**, never in the repo root, `docs/` or `.claude/`.
- **Frontmatter on every doc:** `title`, `type`, `project`, `updated`
  (`YYYY-MM-DD`) and `tags`; `status` (`todo | doing | done | blocked`) on
  tickets only.
- **Keep it current.** After finishing a ticket or feature, or hitting a blocker,
  run `/project-update` before reporting done.
```

## Licence

[MIT](LICENSE)
