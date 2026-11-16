# Adapting to a project

The plugin's commands and agents are generic. Everything project-specific lives in two sections of the repo's CLAUDE.md, which `/workflow-init` writes from [`plugins/dps/templates/CLAUDE-workflow.md`](../plugins/dps/templates/CLAUDE-workflow.md):

- **`## Workflow`:** the contract the commands and agents read.
- **`## Project Management (.project/)`:** the folder, plus the **Decision log** and **Reading the log** rules that every agent follows.

Agents look up subsections by name, e.g. "CLAUDE.md → **Workflow → Commands**", so keep the headings even when you rewrite the content.

## The `## Workflow` contract

| Subsection | What it holds | Who reads it |
|---|---|---|
| **Sources of truth** | The spec's path and the sections that hold the milestones, test cases, cut order, structure and README contents. The PRD and which parts are out of scope. The design and how to read it, with an artboard table. A manual checklist. | everyone |
| **Commands** | Install, test (all and one file), type-check, lint, build. The manifest that pins framework versions. A deleted row is skipped. | implementers, `test-writer`, `branch-integrator`, reviewers |
| **Priorities and cuts** | What P0 means, P1 and P2, and the numbered cut order for `cut_rank`. Estimates are never a budget. | `ticket-planner`, `/prioritise-tickets` |
| **Tickets** | The ID scheme, area tags, and hotspot files that need a single owner. | `ticket-planner` |
| **Architecture rules most often broken** | The handful of rules agents tend to break. | implementers, `code-reviewer`, `milestone-reviewer` |
| **Implementers** | Which agent builds which tickets, by path or tag. The first matching row wins, and the same agent fixes review findings in its area. | `/implement-ticket`, `/implement-parallel` |
| **Extra audits** | Project auditors, the paths that trigger them, and who fixes their failures. | `/implement-ticket`, `/implement-parallel` |
| **Security** | Trust boundaries (paths that trigger an audit), runtime, untrusted inputs, a project-specific checklist, and whether the repo is public. | `security-auditor`, `security-fixer`, `ticket-planner` |
| **Git and deploy** | Whether to push after each ticket, what a push deploys, and commit message rules. | `/implement-ticket`, `/implement-parallel` |

### What good entries look like

From the example repo, a task board on Next.js and Postgres:

- **Architecture rules:** "Every write goes through a server action that parses its input and checks board membership." "Components never import from `src/db/`." "Order is a position key on the row; a move updates one row." Four or five rules like these catch most drift. Don't restate the whole spec.
- **Hotspot files:** `src/db/schema.ts`, `src/lib/actions.ts`, the app layout, `package.json`. The planner gives each one to a single foundation ticket, which creates everything later tickets need from it.
- **Trust boundaries:** the schema, the server actions and queries, auth and middleware, API routes, the CSV and email output, the manifest, `.gitignore`, and CI workflows.
- **Project security checklist:** "every query that reads or writes a board is scoped to a board the signed-in user belongs to"; "CSV cells that start with `=`, `+`, `-` or `@` are prefixed with `'`".
- **Implementers:** `src/app/`, middleware, the auth config and the tag `infra` go to `nextjs-specialist`; everything else goes to `dps:ticket-implementer`.
- **Extra audits:** `src/emails/` and `src/lib/digest.ts` trigger `email-auditor`.

The whole example, with its CLAUDE.md, project agents and `.project/` samples, is in [`examples/example-app/`](../examples/example-app/).

## Writing a spec the workflow can use

`/workflow-init` checks for these, and `/plan-tickets` depends on them:

1. **Build plan:** numbered milestones in build order, each with a one-line scope and a commit message. Order them so stopping after any milestone still leaves something working, and put the product's minimum first.
2. **Test-case table:** one row per module, with concrete cases ("rejects a `javascript:` URL", "20 updates 100ms apart make one undo step") rather than "add tests".
3. **Project structure:** the file tree, with one line per file saying what it owns.
4. **Cut order** (optional): the features to drop first, applied only when you ask.
5. **README contents** (optional): what the final README must cover.

## Project agents

When the generic implementer isn't enough, add a project agent to `.claude/agents/` and register it in the contract:

- **A stack specialist** ([template](../plugins/dps/templates/agents/stack-specialist.md)): an expert in the framework that reads the installed version's docs before using any API. Register it under **Implementers** with the paths and tags it owns.
- **An output auditor** ([template](../plugins/dps/templates/agents/output-auditor.md)): a read-only checklist for output with hard external constraints. Register it under **Extra audits** with its trigger paths and fixer.

A project agent follows the same rules as the plugin's agents: read the contract and the decision log first, stay inside `touches`, write only decision files under `.project/`, and never push. Copy those sections from the templates.

## Overriding a plugin agent

To change a plugin agent's behaviour for one repo, prefer adding a rule to the contract (an architecture rule, a security checklist item, a decision). If you need a different agent, create one in `.claude/agents/` under a new name and point **Implementers** or **Extra audits** at it. Don't copy a plugin agent under the same name: the copy stops getting plugin updates.
