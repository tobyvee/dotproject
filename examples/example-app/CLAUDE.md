# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A small task board for teams: sign in by email, create boards, add columns and cards, set due dates and assignees, export a board as CSV, and get a daily digest email of what's due. It's a Next.js App Router app on Postgres (Drizzle), deployed to Vercel. This repo is the first release, built from the spec in `.project/spec/`.

## Commands

- `npm run dev`: local dev server at http://localhost:3000. Needs `DATABASE_URL` and `AUTH_SECRET` in `.env.local` (copy `.env.example`).
- `npm test`: runs `vitest run`. `npx vitest run src/lib/position.test.ts` runs one file; add `-t "<name>"` for one case.
- `npm run db:migrate`: applies Drizzle migrations to `DATABASE_URL`.
- `npm run build`: `next build`. CI runs tests, type-check and lint first.

## Architecture

- **`src/lib/schema.ts`:** Zod schemas for `Board`, `Column` and `Card`, the single source of truth for shapes. Database rows and form inputs are both parsed through them.
- **`src/db/`:** Drizzle tables (`schema.ts`) and the only code that queries Postgres (`queries.ts`).
- **`src/lib/actions.ts`:** every write is a server action here. Each one parses its input, checks the signed-in user is a member of the board, then calls a query.
- **`src/app/`:** routes. `/boards` lists boards, `/boards/[id]` is the board, `/api/boards/[id]/export` streams CSV, `/api/cron/digest` sends the digest.
- **`src/components/board/`:** the board UI. Components get data from server components and change it only through actions.
- **`src/emails/`:** React Email templates for the digest and invites. They render to static HTML and import nothing from the app.

## Workflow

This repo uses the dotproject spec-driven workflow (the `dps` plugin): `/plan-tickets` → `/prioritise-tickets` → `/implement-ticket` or `/implement-parallel`. The plugin's commands and agents read this section for everything project-specific.

### Sources of truth

- **Spec:** `.project/spec/example-app-tech-spec.md`, the source of truth for scope and build order.
  - **Milestones:** its **Build plan** section. Each numbered step is one milestone, with the commit message it ends on.
  - **Test cases:** its **Unit tests** section, a table of required cases per module.
  - **Cut order:** in **Build plan**; see **Priorities and cuts** below.
  - **Structure:** its **Project structure** section, which says which file owns what.
  - **README:** its **README contents** section (`readme-writer` follows it).
  - **Manual checks:** `.project/review/manual-checklist.md`. It covers what unit tests can't (drag on touch screens, the digest in real mail clients), and `test-writer` points skipped cases at it.
- **PRD:** `.project/prd/example-app-prd.md`. Only the **Release 1** section is in scope; **Later** (comments, attachments, SSO) is out of scope, and work that belongs to it is never ticketed without asking.
- **Design:** none. Build from the spec's **UI** section.

### Commands

| Purpose | Command |
|---|---|
| Install (when dependencies are missing) | `npm install` |
| Test (all) | `npm test` |
| Test (one file) | `npx vitest run path/to/file.test.ts` |
| Type-check | `npx tsc --noEmit` |
| Lint | `npm run lint` |
| Build | `npm run build` |

**Manifest:** `package.json`. Reviewers and specialists read the installed framework and language versions there and apply the practice for those versions.

Every ticket ends with test, type-check and lint passing.

### Priorities and cuts

- **P0:** sign-in, boards, columns, cards with reorder, and everything saved to the database. Never cut.
- **P1:** planned extras.
- **P2:** stretch, scheduled after the planned work like everything else.
- **cut:** set only when the user asks; the ticket keeps `status: todo`.
- **Cut order** (applied only when the user asks): 1 = filters, 2 = CSV export, 3 = digest email. A ticket for cuttable work carries `cut_rank: <its number in this list>`; P0 tickets never have one.
- Estimates size the work and plan the waves. They are never a budget: never shrink or drop work to fit a time estimate.

### Tickets

- **ID scheme:** `T-NNN`, file `.project/tickets/T-NNN-<slug>.md`.
- **Area tags:** `schema | db | auth | ui | api | email | infra | docs`.
- **Hotspot files** that later tickets must not all edit: `src/db/schema.ts`, `src/lib/actions.ts`, `src/app/(app)/layout.tsx`, `package.json`. The foundation ticket for each creates every table, action or slot later tickets need.

### Architecture rules most often broken

Implementers follow these, and reviewers check them:

- Every write goes through a server action in `src/lib/actions.ts` that parses its input with `src/lib/schema.ts` and checks board membership before any query.
- Components never import from `src/db/`.
- Card and column order is a fractional `position` key on the row. A move updates one row; never renumber a whole list.
- Dates are stored in UTC and formatted in the viewer's time zone only when rendered.
- `src/emails/` imports nothing from the app, and uses tables and inline styles only.

### Implementers

| Ticket touches | Implemented by |
|---|---|
| `src/app/`, `next.config.ts`, `middleware.ts`, `src/auth.ts`, tag `infra` | `nextjs-specialist` |
| Everything else | `dps:ticket-implementer` |

The first matching row wins. The same agent fixes `code-reviewer` findings in its area. Project agents live in `.claude/agents/`; the plugin's agents are named `dps:<name>`.

### Extra audits

| Ticket touches | Run | Fix with |
|---|---|---|
| `src/emails/`, `src/lib/digest.ts` | `email-auditor` | the implementer for those paths (**Implementers**) |

### Security

- **Trust boundaries:** a ticket that touches any of these gets a `security-auditor` run: `src/lib/schema.ts`, `src/lib/actions.ts`, `src/db/queries.ts`, `src/auth.ts`, `middleware.ts`, `src/app/api/`, `src/lib/csv.ts`, `src/emails/`, `package.json`, `.gitignore`, `.github/workflows/`.
- **Runtime:** Vercel serverless functions. Module memory isn't a cache, and secrets come from the project's environment variables, never the repo.
- **Untrusted inputs:** board, column and card text; invite email addresses; request bodies and query strings; the cron request; npm dependencies.
- **Project checklist:**
  - Every query that reads or writes a board is scoped to a board the signed-in user belongs to.
  - CSV cells that start with `=`, `+`, `-`, `@`, a tab or a carriage return are prefixed with `'`.
  - Card text is never rendered as HTML, in the app or in email.
  - `/api/cron/digest` rejects requests without the `CRON_SECRET` bearer token.
  - Invite links are single-use and expire after 7 days.
- **Public repo:** yes. Security commits, tickets and decisions describe the protection, never a working exploit.

### Git and deploy

- **Push after each ticket:** yes. `/implement-ticket` and `/implement-parallel` push the current branch once each ticket is reviewed, recorded and committed, and need an upstream that matches `HEAD` before they start.
- **Deploy:** every push to `main` deploys through Vercel's Git integration.
- Commit subjects describe the change and end with the ticket ID, e.g. `Card list with add and reorder (T-012)`. One commit per milestone closes with the spec's message for that step.
- Only the main session pushes. Agents never push, and nothing is force-pushed.

## Project Management (`.project/`)

Planning docs live in `.project/`, which **is committed with this repo**: worktree agents read tickets from `HEAD`, and records move with the code they describe.

- `.project/prd/`: product requirements
- `.project/spec/`: technical specifications
- `.project/tickets/`: engineering tickets, plus `INDEX.md` (the run order)
- `.project/decisions/`: one file per decision (see **Decision log**)
- `.project/review/`: audits with findings, and the manual checklist
- `.project/STATUS.md`: current status (the first paragraph under `## Summary` is the project's summary)

Every doc starts with YAML frontmatter (`title`, `type`, `project: example-app`, `updated`, `tags`; `status` on tickets only). Create single docs with `/project-doc`; record finished work with `/project-update`. Commit doc changes in the same commit as the work they record.

<!--
The **Decision log** and **Reading the log** subsections follow here in a real repo.
`/workflow-init` copies them unchanged from plugins/dps/templates/CLAUDE-workflow.md,
with `<project>` replaced by `example-app`, so they're left out of this example.
-->
