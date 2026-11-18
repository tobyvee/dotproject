---
name: workflow-init
description: Bootstrap the spec-driven ticket workflow in the current repo. Makes sure a committed .project/ (STATUS.md, prd/, spec/, tickets/, decisions/) and a spec with milestones exist, adds the Workflow, Project Management and Decision log sections to the repo's CLAUDE.md, offers project-specific specialist and auditor agents, and creates the ticket index. Use when a repo should start using /plan-tickets, /prioritise-tickets, /implement-ticket or /implement-parallel, or when one of those commands reports there is no Workflow section.
argument-hint: "[project-name]"
---

# Initialise the spec-driven workflow

Set up the current repo so the `dps` plugin's commands and agents can run. `$ARGUMENTS` is an optional canonical project name.

Run every step. Each is idempotent: re-running on a half-set-up repo fills the gaps without clobbering anything. Never overwrite an existing doc or section; report it and move on, or merge into it where a step says so.

**Plugin files.** This skill reads templates from `${CLAUDE_PLUGIN_ROOT}/templates/`. If `${CLAUDE_PLUGIN_ROOT}` isn't expanded in this session, find the plugin with Glob for `**/dps/templates/CLAUDE-workflow.md` under `~/.claude/plugins`, and use that folder.

## 1. Resolve the repo and project

1. Repo root: `git rev-parse --show-toplevel`. This workflow needs git (worktrees, per-ticket commits). If the directory isn't a git repo, stop and say so; offer `git init`, but don't run it unasked.
2. Canonical name (`project:` in frontmatter): an existing `.project/STATUS.md`'s `project:` wins. Otherwise `$ARGUMENTS`, else the package name (`package.json` `name` without scope, `go.mod` last path segment, `Cargo.toml`, `pyproject.toml`), else the repo directory name. Lowercase, kebab-case or dotted. Confirm it only if the sources disagree.

## 2. Make sure `.project/` exists and is committed

1. If `.project/` is missing, run the `dp:project-init` skill with the project name, if it's installed. Otherwise create it yourself:
   - `.project/prd/`, `.project/spec/`, `.project/tickets/` (with a `.gitkeep` while empty).
   - `.project/STATUS.md`, with today's date (`date +%F`):

     ```markdown
     ---
     title: "<project> — Status"
     type: status
     project: <project>
     updated: YYYY-MM-DD
     tags: [project, <project>, status]
     ---
     # <project> — Status

     > PM docs: this repo's `.project/` (`prd/`, `spec/`, `tickets/`, `decisions/`, this file). Committed with the repo.

     ## Summary

     <One or two sentences of plain prose: what the project is and where it stands today, written from the README and git log. It's the project's summary, so it must not start with a list, quote, table or heading.>

     ## In progress

     ## Outstanding

     ## Planned

     ## Completed
     ```
2. Create `.project/decisions/` (with a `.gitkeep`) if it's missing. `review/` is created when the first audit with findings is saved.
3. **This workflow needs `.project/` committed**, unlike the dotproject default of a local, gitignored folder. Worktree agents read their ticket from `HEAD`, and each ticket's records are committed with its code. Check with `git check-ignore -q .project/STATUS.md`. If it's ignored:
   - Explain why the workflow needs it committed, and that committing it publishes every planning doc wherever the repo is pushed (all of it, if the repo is public).
   - Ask before changing anything. On yes, remove the `/.project/` rule from `.gitignore` (or add `!/.project/` if the rule comes from elsewhere) and update the "Gitignored" line in `STATUS.md`. On no, stop: the commands can't run against an ignored `.project/`.

## 3. Require a spec

The workflow plans from a tech spec. Look in `.project/spec/` for one that has:

- **Milestones (required):** a build plan, i.e. a numbered list of steps that each end in a working, testable state, ideally each with the commit message it ends on.
- **Test cases (strongly recommended):** a table of required test cases per module. Implementers and `dps:test-writer` write tests from it rather than "add tests".
- **Project structure (recommended):** which file owns what. The planner uses it to assign `touches`.
- **Cut order (optional):** what goes first if the user asks to cut.

If there's no spec, or it has no milestones, stop after step 2. Say which sections are missing and suggest `/dp:project-doc spec <title>` to write one (or adding the missing sections to the existing spec), then re-running this skill. If several specs exist, ask which one drives the workflow.

## 4. Add the contract to CLAUDE.md

Read `${CLAUDE_PLUGIN_ROOT}/templates/CLAUDE-workflow.md`. It holds two top-level sections, `## Workflow` and `## Project Management (.project/)`, and the second contains `### Decision log` and `### Reading the log`. Strip its leading HTML comment.

1. Open the repo-root `CLAUDE.md`, creating it with a `# CLAUDE.md` heading if there is none.
2. For each of those sections (including the two `###` subsections):
   - **Missing:** add it, filled in.
   - **Present:** keep the repo's text. Add only the subsections and lines the template has and it lacks (e.g. a missing **Reading the log**, or a gitignored `.project/` description that must now say committed). Say what you merged.
3. **Fill every placeholder from the repo**, without asking:
   - **Sources of truth:** the spec and PRD paths, and the spec's actual headings for the build plan, test cases and project structure. A design source only if the repo or spec names one (a URL, a Figma link, a design artifact); otherwise write "none" and drop the artboard table.
   - **Commands:** from the manifest's scripts (`package.json`, `Makefile`, `justfile`, `pyproject.toml`, `Cargo.toml`, `go.mod`) and the test runner's config. Leave a row out rather than invent a command.
   - **Tickets:** area tags from the spec's project structure; hotspot files (the store, the root layout or router, the dependency manifest) from the structure and the code.
   - **Architecture rules most often broken:** from the spec's architecture section and the existing CLAUDE.md. Pick the rules a parallel implementer would most easily break; three to six.
   - **Security:** trust boundaries from the code and spec (schemas and validators, API routes, upload handling, persistence, rendered output, the dependency manifest, `.gitignore`, CI workflows). Untrusted inputs from the spec.
   - **Git and deploy:** the deploy from the CI files (`.github/workflows/`, etc.) and any deploy script.
   - **Project Management / Decision log:** the project name in `project:` and `tags`.
4. **Ask the user only what can't be inferred**, in one AskUserQuestion call with at most four questions, each standing on its own:
   - What counts as **P0**, the minimum that's never cut (suggest one from the spec's scope).
   - The **cut order**, if the spec doesn't give one (or "none").
   - **Push after each ticket?** Recommend yes when the repo has an upstream and CI; say that with a deploy-on-push workflow every ticket then deploys.
   - **Is the repo public?** Skip it if `gh repo view --json visibility` answers it.

   Skip any question the spec or repo already answers.
5. Don't touch the rest of CLAUDE.md.

## 5. Offer project agents

The plugin's agents are generic. Some projects need a specialist that knows their stack, or an auditor for output with hard constraints. Decide from the stack and the spec whether either is warranted:

- **A stack specialist** when the framework or its build is easy to get wrong across versions (e.g. a Next.js, Rails or Django specialist for the scaffold, routing, config and hydration). Template: `${CLAUDE_PLUGIN_ROOT}/templates/agents/stack-specialist.md`.
- **An output auditor** when the product emits something with strict external constraints (pages for a restricted WebView, emails, exported files, a public API contract). Template: `${CLAUDE_PLUGIN_ROOT}/templates/agents/output-auditor.md`.

Offer each one you think is warranted, with a one-line reason; skip this step if neither is. For each the user accepts:

1. Create `.claude/agents/<name>.md` from the template, filled in for this repo, with the template's leading HTML comment removed so the file starts with the `---` frontmatter (never overwrite an existing agent; report it instead).
2. Register it in CLAUDE.md: a specialist in **Workflow → Implementers** (with the paths and tags it owns), an auditor in **Workflow → Extra audits** (with the paths that trigger it and who fixes its failures).

## 6. Create the ticket index

If `.project/tickets/INDEX.md` doesn't exist, create it with **no `status:`** in its frontmatter, so it isn't counted as a ticket:

```markdown
---
title: "<project> — Ticket index"
type: reference
project: <project>
updated: YYYY-MM-DD
tags: [project, <project>, reference, tickets]
---
# <project> — Ticket index

The run order for `/dps:implement-parallel`. `/dps:plan-tickets` adds tickets here, and `/dps:prioritise-tickets` orders them into waves.

## Waves

## Tickets

| ID | Title | Priority | Milestone | Estimate | Depends on | Status |
|---|---|---|---|---|---|---|
```

## 7. Log the adoption

If `.project/decisions/general-adopt-spec-driven-workflow.md` doesn't exist, write it in the template's decision format:

- `title`: "This repo uses the spec-driven ticket workflow".
- `ticket: none`, `decided_by: user` (the user asked for the workflow and answered step 4's questions).
- **Context:** why the repo adopted it; the spec it plans from.
- **Decision:** the workflow, with the user's answers: the P0 definition, the cut order, push after each ticket, and `.project/` committed (and whether that changed a gitignore rule).
- **Alternatives:** working without tickets; keeping `.project/` local (incompatible with worktree agents).
- **Consequences:** `.project/` is committed and visible wherever the repo is pushed; only the main session edits tickets, `INDEX.md` and `STATUS.md`; and, if pushing after each ticket, every landed ticket is pushed (and deployed, where pushes deploy).

## 8. Report

- What was created, what already existed, what was merged and what was skipped, and why.
- The answers recorded, and any placeholder you couldn't fill (left as `<…>` in CLAUDE.md, listed here so the user can fill it).
- What's ready to commit: `CLAUDE.md`, `.gitignore` if it changed, `.project/` and any new `.claude/agents/` files. Don't commit unless asked; suggest a message like `Adopt the spec-driven workflow`.
- The next step: `/dps:plan-tickets all`.
