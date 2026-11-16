# Example: an adapted repo

A worked example of what the `dps` plugin adds to a repo once it's set up. The project is fictional: a small task board for teams, built with Next.js on Postgres and deployed to Vercel, partway through its build. Nothing here is loaded by the plugins.

The plugin's commands and generic agents aren't copied here; they come from [`plugins/dps/`](../../plugins/dps/). A repo only adds its own contract, its project agents and its planning docs:

| Path | What it is |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | The repo's CLAUDE.md, with the `## Workflow` contract filled in from [the template](../../plugins/dps/templates/CLAUDE-workflow.md). |
| [`dot-claude/agents/`](dot-claude/agents/) | The repo's `.claude/agents/`, renamed so Claude Code doesn't load it from here: a stack specialist and an output auditor, each made from a [template](../../plugins/dps/templates/agents/). |
| [`project-samples/`](project-samples/) | A few `.project/` docs: `STATUS.md` midway through the build, the ticket `INDEX.md` with its waves, a finished ticket (`T-012`) and four decisions, one of which supersedes another. Links to docs that aren't included are written as plain file names. |

## How it maps to the contract

| In this example | Contract section |
|---|---|
| The spec's **Build plan**, **Unit tests** and **Project structure**; the PRD's **Release 1** | **Workflow → Sources of truth** |
| `npm test`, `npx tsc --noEmit`, `npm run lint` | **Workflow → Commands** |
| P0 = sign-in, boards, columns, cards; cut order filters → CSV export → digest email | **Workflow → Priorities and cuts** |
| `src/db/schema.ts` and `src/lib/actions.ts` as hotspots | **Workflow → Tickets** |
| "Every write goes through a server action that checks membership" | **Workflow → Architecture rules most often broken** |
| [`nextjs-specialist`](dot-claude/agents/nextjs-specialist.md) for `src/app/`, middleware, auth and `infra` | **Workflow → Implementers** |
| [`email-auditor`](dot-claude/agents/email-auditor.md) for `src/emails/` and `src/lib/digest.ts` | **Workflow → Extra audits** |
| Membership scoping, CSV formula escaping, the cron secret | **Workflow → Security** |
| [`general-push-after-each-ticket.md`](project-samples/decisions/general-push-after-each-ticket.md), deploy on push to `main` | **Workflow → Git and deploy** |
| [`general-time-budget-is-user-time.md`](project-samples/decisions/general-time-budget-is-user-time.md) | Built in: estimates are never a budget |
