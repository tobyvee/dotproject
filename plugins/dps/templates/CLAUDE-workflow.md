<!--
The section `/workflow-init` adds to a repo's CLAUDE.md. Every command and agent in
the `dps` plugin reads it for anything project-specific, so they never
hard-code paths, commands or rules. Replace each <placeholder>, delete the
optional subsections you don't need, and keep the headings: the agents look them
up by name (e.g. "CLAUDE.md → Workflow → Commands").
-->

## Workflow

This repo uses the dotproject spec-driven workflow (the `dps` plugin): `/plan-tickets` → `/prioritise-tickets` → `/implement-ticket` or `/implement-parallel`. The plugin's commands and agents read this section for everything project-specific.

### Sources of truth

- **Spec:** `.project/spec/<spec file>.md`, the source of truth for scope and build order.
  - **Milestones:** its `<Build plan>` section. Each numbered step is one milestone, with the commit message it ends on.
  - **Test cases:** its `<Unit tests>` section, a table of required cases per module.
  - **Cut order:** in `<Build plan>`; see **Priorities and cuts** below.
  - **Structure:** its `<Project structure>` section, which says which file owns what.
  - **README:** its `<README contents>` section, if the final milestone writes the README (`readme-writer` follows it).
  - **Manual checks:** `<a manual or real-device checklist, e.g. .project/review/device-checklist.md, or "none">`. It covers what unit tests can't (layout, devices, uploads), and `test-writer` points skipped cases at it.
- **PRD:** `.project/prd/<prd file>.md`. Only `<the MVP / Phase 0 section>` is in scope; `<later sections>` are out of scope, and work that belongs to them is never ticketed without asking.
- **Design (optional):** `<URL or path, or "none">`. How to read it: `<e.g. Artifact tool: list files, then read one artboard per call by path; never WebFetch>`. Which artboard covers what:

  | Artboard | Covers |
  |---|---|
  | `<Main>` | `<the main screen>` |

  If the design can't be read, build from the spec alone and say so in the report.

### Commands

| Purpose | Command |
|---|---|
| Install (when dependencies are missing) | `<npm install>` |
| Test (all) | `<npm test>` |
| Test (one file) | `<npx vitest run path/to/file.test.ts>` |
| Type-check | `<npx tsc --noEmit>` |
| Lint (if it exists) | `<npm run lint>` |
| Build | `<npm run build>` |

**Manifest:** `<package.json>`. Reviewers and specialists read the installed framework and language versions there and apply the practice for those versions.

Every ticket ends with test, type-check and lint passing. A row that's deleted or says "none" is skipped, not treated as a failure.

### Priorities and cuts

- **P0:** `<the minimum the product must ship, e.g. the brief's minimum, persistence, export>`. Never cut.
- **P1:** planned extras.
- **P2:** stretch, scheduled after the planned work like everything else.
- **cut:** set only when the user asks; the ticket keeps `status: todo`.
- **Cut order** (applied only when the user asks): 1 = `<first to go>`, 2 = `<next>`, … A ticket for cuttable work carries `cut_rank: <its number in this list>`; P0 tickets never have one.
- Estimates size the work and plan the waves. They are never a budget: never shrink or drop work to fit a time estimate.

### Tickets

- **ID scheme:** `T-NNN`, file `.project/tickets/T-NNN-<slug>.md`.
- **Area tags:** `<schema | store | ui | lib | api | infra | docs>`.
- **Hotspot files** that later tickets must not all edit (give them to one foundation ticket, or have it create stubs): `<e.g. src/lib/store.ts, src/app/layout.tsx, package.json>`.

### Architecture rules most often broken

Implementers follow these, and reviewers check them:

- `<e.g. UI components change state only through store actions>`
- `<e.g. the renderer has no framework imports>`

### Implementers

| Ticket touches | Implemented by |
|---|---|
| `<src/app/, framework config, tag infra>` | `<a project specialist agent, e.g. nextjs-specialist>` |
| Everything else | `dps:ticket-implementer` |

The first matching row wins. The same agent fixes `code-reviewer` findings in its area. Project agents live in `.claude/agents/`; the plugin's agents are named `dps:<name>`.

### Extra audits (optional)

| Ticket touches | Run | Fix with |
|---|---|---|
| `<src/renderer/, src/lib/export.ts>` | `<a project auditor, e.g. output-auditor>` | the implementer for those paths (**Implementers**) |

### Security

- **Trust boundaries:** a ticket that touches any of these gets a `security-auditor` run: `<src/lib/schema.ts, src/app/api/, package.json, .gitignore, .github/workflows/, …>`.
- **Runtime:** `<where server code runs and what that implies, e.g. "serverless isolates: module memory isn't a cache, response cache headers aren't honoured at the edge, secrets come from the platform's secret store">`.
- **Untrusted inputs:** `<user content, uploads, request bodies, third-party API responses, npm dependencies>`.
- **Project checklist:** `<the project-specific checks the auditor adds to its generic list, e.g. "every URL rendered into href/src passes the schema's allowlist">`.
- **Public repo:** `<yes | no>`. If yes, security commits, tickets and decisions describe the protection, never a working exploit.

### Git and deploy

- **Push after each ticket:** `<yes | no>`. If yes, `/implement-ticket` and `/implement-parallel` push the current branch once each ticket is reviewed, recorded and committed, and need an upstream that matches `HEAD` before they start. If no, commits stay local and the user pushes when they choose.
- **Deploy:** `<e.g. every push to main deploys through .github/workflows/deploy.yml | none>`.
- Commit subjects describe the change and end with the ticket ID, e.g. `Card list with add and reorder (T-012)`. One commit per milestone closes with the spec's message for that step.
- Only the main session pushes. Agents never push, and nothing is force-pushed.

## Project Management (`.project/`)

Planning docs live in `.project/`, which **is committed with this repo**: worktree agents read tickets from `HEAD`, and records move with the code they describe.

- `.project/prd/`: product requirements
- `.project/spec/`: technical specifications
- `.project/tickets/`: engineering tickets, plus `INDEX.md` (the run order)
- `.project/decisions/`: one file per decision (see **Decision log**)
- `.project/review/`: audits with findings
- `.project/STATUS.md`: current status (the dashboard quotes the first paragraph under `## Summary`)

Every doc starts with YAML frontmatter (`title`, `type`, `project: <project>`, `updated`, `tags`; `status` on tickets only). Create single docs with `/project-doc`; record finished work with `/project-update`. Commit doc changes in the same commit as the work they record.

### Decision log (`.project/decisions/`)

**Every decision an agent or session makes on a ticket gets its own file in `.project/decisions/`**, committed with the work it shaped.

**What counts:** a choice between real alternatives that the spec, the design and the ticket don't already settle: interpreting an ambiguous requirement, departing from the spec, choosing a library, API or pattern, changing a ticket's scope, `touches` or dependencies, splitting or merging tickets, cutting or deferring work, fixing versus deferring a finding, resolving a non-mechanical merge, and any answer the user gives to a `needs decision`. Following the spec as written, naming and formatting aren't decisions. If in doubt, log it.

**File name:** `<ticket-id>-<slug>.md`, or `general-<slug>.md` when no single ticket owns it. Never number decisions globally: parallel worktrees would collide. A committed decision file is never edited; to change course, write a new one that sets `supersedes:`.

```markdown
---
title: "<the decision, as a statement>"
type: decision
project: <project>
ticket: T-012            # or a list, or "none"
decided_by: ticket-implementer   # agent name, "main session", or "user"
supersedes:              # earlier decision file name, if any
updated: YYYY-MM-DD
tags: [project, <project>, decision, <area>]
---
# <the decision, as a statement>

## Context
What forced a choice, linked to the spec section or finding.

## Decision
What was chosen, in one or two sentences.

## Alternatives
Each option rejected, and why in one line.

## Consequences
What this commits later tickets to, or what it costs.
```

**Who writes what:** code-writing agents write their own decision files and list them in their report. Read-only agents (reviewers, auditors) can't write; when their result forces a choice, the calling session logs it. When recording a ticket, the main session adds a `## Decisions` list to the ticket linking its decision files. Only the main session edits tickets, `INDEX.md` and `STATUS.md`.

### Reading the log

**Before acting on a ticket, a review or a question, check `.project/decisions/`.**

1. **Find candidates:** every `general-*.md`; every file whose `ticket:` names your ticket, one in its `depends_on`, or one that owns a file you'll touch (`grep -l "T-012" .project/decisions/*.md`); any file whose title or tags match your area (`grep -il "<keyword>" .project/decisions/*.md`).
2. **Drop superseded files:** a file named in another's `supersedes:` no longer applies.
3. **Precedence:** a decision overrides the spec or PRD text it departs from, and a `decided_by: user` decision overrides an agent's. If a decision conflicts with the spec and neither says which wins, or two live decisions conflict, don't pick: report the conflict.
4. **Cite them:** name the decision files that shaped your work in your report. To depart from one, log a new decision with `supersedes:`; read-only agents recommend this instead.
