# dp plugin (dotproject)

Planning docs in a `.project/` folder at the repo root, with frontmatter conventions Claude reads first and keeps current.

| Skill | What it does |
|---|---|
| `/project-init [name] [--commit]` | Creates `.project/` (`STATUS.md`, `prd/`, `spec/`, `tickets/`), gitignored by default or committed with `--commit`. Documents it in CLAUDE.md. |
| `/project-doc <type> <title>` | Writes one PRD, spec, ticket, review, reference or decision with the right frontmatter and template, matching the repo's existing docs. |
| `/project-update [change]` | Records finished, changed or blocked work: ticket status, ticked criteria, the `STATUS.md` Summary and checklists, and `updated:` dates. |

Docs: [The `.project/` folder](../../docs/project-folder.md). To browse the docs across all your repos, use [Brief](https://github.com/tobyvee/brief).
