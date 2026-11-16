# Dashboard

`/project-status` builds an Obsidian dashboard from every registered repo's `.project/`. It writes one note per project, a dashboard note sorted with blocked projects first, and an Obsidian Base for card and table views. It's optional: nothing else in dotproject depends on it.

The repos are the source of truth. The vault holds a one-directional view that's rewritten on every run. To change a project's status, edit its `STATUS.md`, never the note.

## Set up

```
/project-status --init
```

This runs `project-status.py --init`, which writes two files to `~/.config/dotproject/` (or `$DOTPROJECT_CONFIG_DIR`), never overwriting existing ones. The skill then asks for your paths and registers your repos.

**`dashboard.json`:**

```json
{
  "code_root": "~/Code",
  "vault_dir": "~/Documents/Obsidian/Projects",
  "require_mount": null,
  "parent": null,
  "projects": {
    "shop": "shop",
    "shop-api": "shop/api"
  },
  "adapters": {
    "shop": "frontmatter_status"
  }
}
```

| Key | Meaning |
|---|---|
| `code_root` | Where your repos live. Project paths are relative to it. |
| `vault_dir` | The folder in the vault you actually open. A dashboard in a vault nobody opens defeats the purpose. |
| `require_mount` | Optional mount point (an encrypted or network volume). If it's set and not mounted, the script refuses to write, rather than silently creating a plain folder that disappears on the next mount. |
| `parent` | Optional project whose repo contains other registered repos. The dashboard rolls them up under it. |
| `projects` | `name → path`. The name is the `project:` value from that repo's `STATUS.md`. |
| `adapters` | How to count progress per project (below). Leave narrative-only projects out. |

**`project-next.json`:** the judgement fields Claude maintains: `{"<project>": {"status": "active", "next": "...", "why": ""}}`.

## Progress adapters

Projects record completion differently, and a uniform rule reports confident nonsense. A backlog of unticked checkboxes isn't a progress record.

| Adapter | Counts |
|---|---|
| `frontmatter_status` | `status:` in each ticket file's frontmatter. Any non-empty status counts toward the total, and anything starting with `done` counts as done. Unusual values are listed in the note rather than dropped. Use it for `/project-doc` and spec-driven tickets. |
| `emoji_table` | ✅ / 🟡 / ⬜ in table rows of ticket docs, table rows only, so per-ticket status lines don't double-count. |
| `status_doc` (default) | No count. The `STATUS.md` narrative carries progress. |

## What a run does

1. `--json` gathers the mechanical data: progress from the adapter, the last commit date, `STATUS.md`'s `updated:`, the doc count, and the Summary's first prose paragraph.
2. Claude reads each `STATUS.md` (and open tickets where it's thin), then sets `status` (`active | blocked | stable | ready | parked`) and `next` in `project-next.json`. `next` is one physical action you could start now, naming a file, ticket or command, with no counts.
3. `--write` writes the notes. `--dry-run` lists them instead.
4. Claude reports what moved, what's newly blocked, and what's stale.

**Staleness** comes from git commit dates, falling back to `STATUS.md`'s `updated:` for repos with no commits, and never from file mtimes, which bulk edits reset. ⚠️ appears after 14 days, but only for `active` and `blocked` projects. A stable project sitting untouched is fine.

## Migrating

If you ran an earlier version of the script from `~/.claude/scripts/`:

1. Run `/project-status --init`.
2. Copy the old script's `CODE`, `VAULT`, `PROJECTS`, `PARENT` and `ADAPTERS` values into `dashboard.json`. Adapter functions become names: `adapt_frontmatter_status` is `frontmatter_status`, and `adapt_emoji` is `emoji_table`. Project-specific adapters have no generic equivalent; those projects fall back to `status_doc`.
3. If the vault is on an encrypted volume, set `require_mount` to its mount point.
4. Move `~/.claude/scripts/project-next.json` to `~/.config/dotproject/project-next.json`.
5. Remove `~/.claude/commands/project-status.md` so the old command doesn't shadow the skill.
