---
name: project-status
description: Refresh the Obsidian project dashboard from the .project/ folders of every registered repo. Reads each STATUS.md, sets each project's status and one concrete next action, then writes a dashboard note, one note per project and an Obsidian Base. Use when the user asks for the project dashboard, "what's the status across my projects", or "refresh project status".
argument-hint: "[--init]"
---

# Refresh the project dashboard

The script is `${CLAUDE_PLUGIN_ROOT}/skills/project-status/scripts/project-status.py`
(if the variable isn't expanded, use `${CLAUDE_SKILL_DIR}/scripts/project-status.py`,
or Glob for `**/dp/skills/project-status/scripts/project-status.py` under
`~/.claude/plugins`). Call it `$SCRIPT` below.

## 0. First run (or `$ARGUMENTS` is `--init`)

Configuration lives in `~/.config/dotproject/` (override with
`$DOTPROJECT_CONFIG_DIR`). If `dashboard.json` is missing:

1. Run `python3 $SCRIPT --init`. It writes example `dashboard.json` and
   `project-next.json` and never overwrites existing files.
2. Ask the user for `code_root` (where their repos live, default `~/Code`) and
   `vault_dir` (the Obsidian vault folder they actually open). If the vault is on
   an encrypted or network volume, set `require_mount` to its mount point so the
   script refuses to write while it's unmounted.
3. Register projects: find repos with a `.project/STATUS.md` under `code_root`
   (`find <code_root> -maxdepth 4 -path '*/.project/STATUS.md' -not -path '*/node_modules/*'`),
   show the list, and add the ones the user wants under `projects` as
   `"<project name from STATUS.md frontmatter>": "<path relative to code_root>"`.
   Under `adapters`, set `frontmatter_status` for repos with one ticket file per
   ticket carrying `status:`, or `emoji_table` for repos tracking tickets in a
   ✅/🟡/⬜ table; leave narrative-only repos out.

## 1. Gather the mechanical data

```
python3 $SCRIPT --json
```

This walks every registered repo's `.project/` and derives progress through the
project's adapter, staleness from git commit dates, and a summary from each
`STATUS.md`. If it exits saying the vault isn't mounted, tell the user to mount
or unlock it and stop.

## 2. Refresh the judgement fields

The script can't derive `status` or `next`: they are the point of the dashboard
and need reading comprehension. For each project, read its `.project/STATUS.md`
(and its open tickets where the status doc is thin), then update
`~/.config/dotproject/project-next.json`:

- `status`: one of `active`, `blocked`, `stable`, `ready`, `parked`. Use
  `blocked` only when something external is required before work can resume;
  that state sorts to the top of the dashboard.
- `next`: **one concrete physical action** the user could start right now. Name
  the file, ticket or command. "Wire the Overview page to the live API" beats
  "continue frontend work". This field removes the "what was I even doing" cost
  of reopening a project, so make it resumable without rereading anything.
- `why`: one sentence on why this is the next thing. Optional; leave `""` if it
  adds nothing.

Don't put counts (`10 of 23 tickets`) in `next`: they go stale between runs and
the script already reports them.

## 3. Write the notes

```
python3 $SCRIPT --write
```

This writes `Projects Dashboard.md`, one note per project under `Status/`, and
`Projects.base` into `vault_dir`. Use `--dry-run` to list the files without
writing.

## 4. Report

What changed since last time: projects that moved, anything newly blocked, and
anything now stale (⚠️ appears at 14+ days, but only for `active` and `blocked`
projects; a `stable` project sitting untouched is fine).

## Notes

- **The repos are the source of truth.** The notes are a derived, one-directional
  view. Never edit the vault notes to change a status: edit the repo's
  `.project/STATUS.md`, then re-run this skill.
- **Progress uses per-project adapters** because projects record completion
  differently, and a uniform rule reports confident nonsense. A backlog of
  unticked checkboxes is not a progress record; never count one.
  - `frontmatter_status`: `status:` in ticket frontmatter. Any non-empty status
    counts toward the total; anything starting with `done` counts as done.
  - `emoji_table`: ✅/🟡/⬜ rows in ticket tables, table rows only.
  - default (`status_doc`): no count; the `STATUS.md` narrative carries it.
- **File mtimes are not a staleness signal**: a bulk frontmatter rewrite resets
  them all. Staleness comes from git commit dates, falling back to `STATUS.md`'s
  `updated:` when a repo has no commits.
- **Parent roll-up:** set `parent` in `dashboard.json` to a project whose repo
  contains other registered repos, and the dashboard lists them under it.
