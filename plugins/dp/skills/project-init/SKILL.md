---
name: project-init
description: Set up the .project/ planning folder (prd/, spec/, tickets/, STATUS.md) in the current repo, either local and gitignored (the default) or committed, document it in the repo's CLAUDE.md, and register the repo with the optional /project-status dashboard. Use when starting planning in a repo that has no .project/ yet, or when the user asks to "set up .project" or "add PM docs" to a project.
argument-hint: "[project-name] [--commit]"
---

# Initialise `.project/`

Bootstrap the `.project/` workflow in the current repo. `$ARGUMENTS` is an
optional canonical project name, plus `--commit` to keep `.project/` in git
instead of gitignoring it.

**Local or committed?**

- **Local (default):** `.project/` is gitignored personal planning. Nothing in it
  reaches the remote.
- **Committed (`--commit`):** `.project/` is part of the repo and records move
  with the code they describe. The spec-driven workflow (`/dps:workflow-init`)
  needs this, because its worktree agents read tickets from `HEAD`. If the repo is
  public, so is everything in `.project/`; say so before choosing it.

Run every step; each is idempotent, so re-running on a half-set-up repo fills the
gaps without clobbering anything. Never overwrite an existing doc: report it and
move on.

## 1. Resolve the project

1. Repo root: `git rev-parse --show-toplevel`. If the directory is not a git repo,
   ask whether to continue (the gitignore step is then skipped).
2. If the repo sits inside a workspace that already uses `.project/` (an ancestor
   has a `.project/` folder or a CLAUDE.md that describes the workflow), follow
   that workspace's conventions where they differ from these. Its CLAUDE.md wins.
3. Canonical name (`project:` in frontmatter, and the dashboard key). If
   `.project/STATUS.md` already exists, its `project:` value wins, even over a
   different package name. Existing docs and the dashboard already use it, and
   renaming would split the project in two. Otherwise use `$ARGUMENTS`,
   else the module/package name (`go.mod` last path segment, `package.json`
   `name` without scope, `Cargo.toml`, `pyproject.toml`), else the repo directory
   name. Lowercase, kebab-case or dotted (`docs.example.io`). Confirm it with the
   user only if the sources disagree.

## 2. Create the folder

```
.project/
├── STATUS.md        # current status; the dashboard reads this
├── prd/             # product requirements
├── spec/            # technical specifications
└── tickets/         # engineering tickets (incl. cross-project integration tickets)
```

Create `review/` (code reviews and audits), `reference/` (research, notes) and
`decisions/` (decision log) only when there is something to put in them. Add a
`.gitkeep` to each empty folder so the structure survives being copied.

If the repo already has planning docs elsewhere (`docs/prd`, `planning/`, `PRD.md`,
`TODO.md`, `specs/` that are plans rather than published docs), list them and
**ask** before moving them in. In local mode, moving a committed file into a
gitignored folder deletes it from the repo going forward, so say so. Add
frontmatter to anything moved (step 4).

## 3. Git

**Local mode.** Check with `git check-ignore -q .project/STATUS.md`; if it isn't
ignored, append to the repo's `.gitignore`:

```
# Local planning docs (PRDs, specs, tickets, status); see CLAUDE.md
/.project/
```

If `.project/` files are already tracked (`git ls-files .project`), stop and ask:
untracking them (`git rm -r --cached .project`) removes them from the remote for
everyone else.

**Committed mode.** If `git check-ignore -q .project/STATUS.md` says it's ignored,
show the rule that ignores it (`git check-ignore -v`) and ask before removing it.
Don't commit; say the folder is ready to commit.

## 4. Write `STATUS.md`

Only if it doesn't exist. Use today's date (`date +%F`):

```markdown
---
title: "<project> — Status"
type: status
project: <project>
updated: YYYY-MM-DD
tags: [project, <project>, status]
---
# <project> — Status

> PM docs: this repo's `.project/` (`prd/`, `spec/`, `tickets/`, this file). <Gitignored. | Committed with the repo.>

## Summary

<One or two sentences of plain prose: what the project is and where it stands
today. The dashboard quotes this paragraph, so it must be prose. A paragraph
that starts with a list, quote, table or heading is skipped.>

## In progress

## Outstanding

## Planned

## Completed
```

Write the Summary from what you can see (README, recent `git log`, open
branches). Don't leave the placeholder. Omit `status:`: a status doc has no
lifecycle status of its own.

## 5. Document it in the repo's CLAUDE.md

Add this section to the repo-root `CLAUDE.md` (create the file with a one-line
`# CLAUDE.md — <project>` heading if there is none). Skip if a section that
describes `.project/` already exists; update it instead if it is missing the
frontmatter or skills lines.

```markdown
## Project Management (`.project/`)

Planning docs live in a <**local, gitignored** | **committed**> `.project/` folder:

- `.project/prd/`: product requirements documents
- `.project/spec/`: technical specifications
- `.project/tickets/`: engineering tickets
- `.project/STATUS.md`: current status (the dashboard quotes the first paragraph under `## Summary`)

Every doc starts with YAML frontmatter (`title`, `type`, `project: <project>`,
`updated`, `tags`; `status` on tickets only). Create docs with `/project-doc`;
after finishing work, record it with `/project-update`: tick the ticket, update
`STATUS.md`, bump `updated:`. <Never commit `.project/`. | Commit doc changes in
the same commit as the work they record.>
```

Don't commit the CLAUDE.md change unless asked; say it's ready to commit.

## 6. Register with the dashboard (optional)

The `/project-status` skill builds an Obsidian dashboard from every registered
repo. It's configured in `~/.config/dotproject/dashboard.json`. If that file
doesn't exist, skip this step and mention `/project-status` can be set up later.
If it does:

1. Add `"<project>": "<repo path relative to code_root>"` under `projects`,
   keeping the existing ordering. Repos outside `code_root` can't be registered;
   say so.
2. If tickets will be one file per ticket with a `status:` field (the default
   from `/project-doc` and the spec-driven workflow), add
   `"<project>": "frontmatter_status"` under `adapters` so the dashboard counts
   progress. Leave narrative-only projects out of `adapters`.
3. Add an entry to `~/.config/dotproject/project-next.json`:
   `"<project>": {"status": "active", "next": "<one concrete action>", "why": ""}`.
   `next` must be a physical action someone could start now (a file, ticket or
   command), not "continue work".
4. Run `python3 ${CLAUDE_PLUGIN_ROOT}/skills/project-status/scripts/project-status.py --json`
   and confirm the project appears with `has_status_doc: true`. If it exits
   because the vault isn't mounted, that's fine: registration is done; mention it.

## 7. Report

Print what was created, what already existed, what was skipped and why, and the
suggested next step: usually `/project-doc prd <feature>`, or
`/dps:workflow-init` once a spec exists and the user wants the ticket
workflow.
