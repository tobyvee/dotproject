#!/usr/bin/env python3
"""Generate Obsidian project-status notes from registered repos' .project/ folders.

Repos are the source of truth. The vault gets a derived, one-directional view:
one note per project plus a dashboard and a Base. Nothing here writes to the repos.

Progress uses a per-project adapter, because each project records completion
differently and a uniform rule reports confident nonsense (a backlog of unticked
checkboxes is not a progress record).

Configuration lives in ~/.config/dotproject/ (override with $DOTPROJECT_CONFIG_DIR):

  dashboard.json      code_root, vault_dir, optional require_mount and parent,
                      projects {name: repo path relative to code_root},
                      adapters {name: frontmatter_status | emoji_table | status_doc}
  project-next.json   per-project {status, next, why}, written by /project-status

Usage:  project-status.py [--json | --write | --dry-run | --init]
"""
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import date, datetime

CONFIG_DIR = os.path.expanduser(
    os.environ.get("DOTPROJECT_CONFIG_DIR", "~/.config/dotproject"))
CONFIG_FILE = os.path.join(CONFIG_DIR, "dashboard.json")
NEXT_FILE = os.path.join(CONFIG_DIR, "project-next.json")

EXAMPLE_CONFIG = {
    "code_root": "~/Code",
    "vault_dir": "~/Documents/Obsidian/Projects",
    "require_mount": None,
    "parent": None,
    "projects": {},
    "adapters": {},
}
EXAMPLE_NEXT = {
    "_comment": "Claude-authored per-project status label and next physical action. "
                "The generator merges this over the mechanical data. Refresh with "
                "/project-status. Everything else is derived from the repos.",
    "_status_vocab": ["active", "blocked", "stable", "ready", "parked"],
}


def init_config():
    """Write example config files, never overwriting existing ones."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    for path, body in ((CONFIG_FILE, EXAMPLE_CONFIG), (NEXT_FILE, EXAMPLE_NEXT)):
        if os.path.exists(path):
            print(f"exists, left alone: {path}")
            continue
        with open(path, "w", encoding="utf-8") as f:
            json.dump(body, f, indent=2)
            f.write("\n")
        print(f"wrote {path}")


def load_config():
    try:
        with open(CONFIG_FILE, encoding="utf-8") as f:
            cfg = json.load(f)
    except OSError:
        sys.exit(f"No dashboard config at {CONFIG_FILE}. "
                 f"Run with --init to create one, then add your projects.")
    except ValueError as e:
        sys.exit(f"{CONFIG_FILE} is not valid JSON: {e}")
    return cfg


CFG = {} if "--init" in sys.argv else load_config()
CODE = os.path.expanduser(CFG.get("code_root", "~/Code")).rstrip("/")
# The vault folder the notes are written into. Point it at the vault you actually
# open: a dashboard in a vault nobody opens is the failure this tool exists to fix.
VAULT = os.path.expanduser(CFG.get("vault_dir", ""))
OUT = os.path.join(VAULT, "Status")
# Optional mount point (an encrypted or network volume) that must be mounted
# before writing.
MOUNT = CFG.get("require_mount")

# canonical name -> repo path relative to CODE
PROJECTS = CFG.get("projects", {})
# Optional parent project whose sub-projects are rolled up on the dashboard.
PARENT = CFG.get("parent")
# Match on repo path, not project name: a child's name need not share the
# parent's prefix.
CHILDREN = [k for k, v in PROJECTS.items()
            if PARENT in PROJECTS and v.startswith(PROJECTS[PARENT] + "/")
            and k != PARENT]


def require_vault():
    """If a mount point is configured it must be present. Checking the directory
    is not enough: if it is unmounted, a write silently creates a plain folder
    that disappears on the next mount."""
    if not VAULT:
        sys.exit(f"Set vault_dir in {CONFIG_FILE}.")
    if not MOUNT:
        return
    try:
        out = subprocess.run(["mount"], capture_output=True, text=True).stdout
    except Exception:
        out = ""
    mp = os.path.expanduser(MOUNT).rstrip("/")
    if f" on {mp} " not in out:
        sys.exit(f"Vault not mounted at {mp}. Mount or unlock it first.")


def read(p):
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def frontmatter(text):
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}
    fm = {}
    for line in text[4:end].split("\n"):
        m = re.match(r"^([a-z_]+):\s*(.*)$", line)
        if m:
            fm[m.group(1)] = m.group(2).strip().strip('"')
    return fm


def git_last(repo):
    """Most recent commit date for the repo containing this path."""
    d = os.path.join(CODE, repo)
    while d.startswith(CODE):
        if os.path.isdir(os.path.join(d, ".git")):
            r = subprocess.run(
                ["git", "-C", d, "log", "-1", "--format=%cd", "--date=short"],
                capture_output=True, text=True)
            return r.stdout.strip() or None
        d = os.path.dirname(d)
    return None


def docs_of(proj):
    root = os.path.join(CODE, PROJECTS[proj], ".project")
    out = []
    for dirpath, _, files in os.walk(root):
        if "/assets" in dirpath:  # binary-heavy asset folders hold no docs
            continue
        out += [os.path.join(dirpath, f) for f in files if f.endswith(".md")]
    return out


# ---------------------------------------------------------------- adapters

def adapt_frontmatter_status(proj):
    """status: in ticket frontmatter (one file per ticket).

    Any non-empty status counts toward the total. Matching a fixed vocabulary
    would silently drop tickets whose status drifted (e.g. 'done-with-caveat'),
    and a ticket missing from the denominator is a worse lie than one in the
    wrong bucket. Anything starting with 'done' counts as done.
    """
    done = total = 0
    odd = []
    for f in docs_of(proj):
        if "/tickets/" not in f:
            continue
        st = (frontmatter(read(f)).get("status") or "").strip().lower()
        if not st:
            continue
        total += 1
        done += st.startswith("done")
        if st not in ("done", "todo", "doing", "blocked"):
            odd.append(st)
    note = f"{done}/{total} tickets done"
    if odd:
        note += f" ({', '.join(sorted(set(odd)))})"
    return done, total, note


def adapt_emoji(proj):
    """✅/🟡/⬜ status table in the ticket docs.

    Only table rows count. Per-ticket '**State:** ✅ done' lines restate a status
    already in the table, and counting both inflates the total.
    """
    done = blocked = deferred = 0
    for f in docs_of(proj):
        if "/tickets/" not in f:
            continue
        for ln in read(f).split("\n"):
            if not ln.lstrip().startswith("|"):
                continue
            done += "✅" in ln
            blocked += "🟡" in ln
            deferred += "⬜" in ln
    total = done + blocked + deferred
    bits = [f"{done}/{total} tickets done"]
    if blocked:
        bits.append(f"{blocked} blocked")
    if deferred:
        bits.append(f"{deferred} deferred")
    return done, total, ", ".join(bits)


def adapt_status_doc(proj):
    """No countable signal — the STATUS.md narrative carries it instead."""
    return None, None, ""


ADAPTER_FUNCS = {
    "frontmatter_status": adapt_frontmatter_status,
    "emoji_table": adapt_emoji,
    "status_doc": adapt_status_doc,
}


def resolve_adapters():
    out = {}
    for proj, name in CFG.get("adapters", {}).items():
        if name not in ADAPTER_FUNCS:
            sys.exit(f"Unknown adapter {name!r} for {proj} in {CONFIG_FILE}; "
                     f"use one of {', '.join(ADAPTER_FUNCS)}.")
        out[proj] = ADAPTER_FUNCS[name]
    return out


ADAPTERS = resolve_adapters()

# ---------------------------------------------------------------- gather


def status_doc(proj):
    p = os.path.join(CODE, PROJECTS[proj], ".project", "STATUS.md")
    return p if os.path.isfile(p) else None


def summary_of(text):
    """First substantive paragraph after the '## Summary' heading, else after H1."""
    m = re.search(r"^## Summary\s*$", text, re.M)
    chunk = text[m.end():] if m else re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S)
    for para in re.split(r"\n\s*\n", chunk):
        para = para.strip()
        if para and not para.startswith(("#", ">", "|", "-", "*")):
            return re.sub(r"\s+", " ", para)[:400]
    return ""


def days_since(d):
    if not d:
        return None
    try:
        return (date.today() - datetime.strptime(d, "%Y-%m-%d").date()).days
    except ValueError:
        return None


def gather():
    rows = []
    for proj in PROJECTS:
        sd = status_doc(proj)
        text = read(sd) if sd else ""
        fm = frontmatter(text)
        done, total, note = ADAPTERS.get(proj, adapt_status_doc)(proj)
        git = git_last(PROJECTS[proj])
        # mtimes are unreliable (a bulk rewrite reset them). Prefer git: it records
        # when work happened. STATUS.md's `updated:` records when someone edited the
        # doc, which is not the same thing and inflates freshness if the doc is
        # touched without the code moving. Fall back to it only when there is no
        # git history at all.
        stated = fm.get("updated")
        last = git or stated
        last_src = "git" if git else ("doc" if stated else None)
        rows.append({
            "project": proj,
            "path": os.path.join(CODE, PROJECTS[proj], ".project"),
            "has_status_doc": bool(sd),
            "status_updated": stated,
            "git_last": git,
            "last_activity": last,
            "stale_days": days_since(last),
            "last_src": last_src,
            "done": done, "total": total,
            "percent": (round(100 * done / total) if total else None),
            "progress_note": note,
            "docs": len(docs_of(proj)),
            "summary": summary_of(text) if text else "",
            "is_parent": proj == PARENT,
        })
    return rows


# ---------------------------------------------------------------- render

# status -> (callout type, sort rank). Blocked sorts first: it is the one state
# that needs a human decision before anything else can move.
CALLOUT = {
    "blocked": ("danger", 0),
    "active": ("tip", 1),
    "ready": ("success", 2),
    "stable": ("note", 3),
    "parked": ("abstract", 4),
}
STALE_AFTER = 14  # days


def merge_next(rows):
    try:
        with open(NEXT_FILE, encoding="utf-8") as f:
            extra = json.load(f)
    except (OSError, ValueError):
        extra = {}
    for r in rows:
        e = extra.get(r["project"], {})
        r["status"] = e.get("status", "active")
        r["next"] = e.get("next", "")
        r["why"] = e.get("why", "")
    return rows


def bar(pct, width=10):
    if pct is None:
        return ""
    filled = round(pct * width / 100)
    return "▓" * filled + "░" * (width - filled)


def stale_note(d, status="active", src="git"):
    """Staleness is only a warning for work that is supposed to be moving.
    A stable or shipped project sitting untouched is not a problem."""
    if d is None:
        return "no recorded activity"
    if src == "doc":
        # No commits exist; this is a doc-edit date, so say so rather than
        # implying the code moved.
        when = "today" if d == 0 else f"{d}d ago"
        return f"no commits yet (doc updated {when})"
    if d == 0:
        return "active today"
    label = "1 day ago" if d == 1 else f"{d} days ago"
    warn = d >= STALE_AFTER and status in ("active", "blocked")
    return label + ("  ⚠️" if warn else "")


def note_body(r):
    """One project note. Frontmatter drives the Base; the body is for reading."""
    fm = {
        "title": json.dumps(r["project"], ensure_ascii=False),
        "type": "project-status",
        "project": r["project"],
        "status": r["status"],
        "docs": r["docs"],
        "last_activity": r["last_activity"] or "",
        "stale_days": "" if r["stale_days"] is None else r["stale_days"],
        "percent": "" if r["percent"] is None else r["percent"],
        "generated": "true",
        "tags": "[project, project-status]",
    }
    if r["total"]:
        fm["done"] = r["done"]
        fm["total"] = r["total"]
    out = ["---"] + [f"{k}: {v}" for k, v in fm.items()] + ["---", ""]
    kind, _ = CALLOUT.get(r["status"], ("note", 3))
    out += [f"> [!{kind}] {r['project']} — {r['status']}"]
    if r["percent"] is not None:
        out.append(f"> `{bar(r['percent'])}` **{r['percent']}%** — {r['progress_note']}")
    elif r["progress_note"]:
        out.append(f"> {r['progress_note']}")
    if r["next"]:
        out.append("> ")
        out.append(f"> **Next:** {r['next']}")
    out += ["", f"*Last activity: {stale_note(r['stale_days'], r['status'], r['last_src'])}"
                f"{' · ' + r['last_activity'] if r['last_activity'] else ''} · "
                f"{r['docs']} docs*", ""]
    if r["why"]:
        out += [f"**Why this next:** {r['why']}", ""]
    if r["summary"]:
        out += ["## Status", "", r["summary"], ""]
    out += ["## Source", "",
            f"Docs live in the repo, not here: `{r['path']}`", "",
            "> [!warning] Generated file",
            "> Rewritten by `/project-status`. Edits here are lost — "
            "change the repo's `.project/STATUS.md` instead.", ""]
    return "\n".join(out)


def dashboard(rows):
    order = sorted(rows, key=lambda r: (CALLOUT.get(r["status"], ("", 9))[1],
                                        -(r["stale_days"] or 0)))
    out = ["---", 'title: "Projects Dashboard"', "type: dashboard",
           "generated: true", "tags: [project, dashboard]", "---", "",
           "# Projects", "",
           f"*{len(rows)} projects · regenerate with `/project-status`*", ""]
    for r in order:
        if r["is_parent"]:
            continue
        kind, _ = CALLOUT.get(r["status"], ("note", 3))
        head = f"> [!{kind}] [[{r['project']}]] — {r['status']}"
        out.append(head)
        if r["percent"] is not None:
            out.append(f"> `{bar(r['percent'])}` **{r['percent']}%** · {r['progress_note']}")
        elif r["progress_note"]:
            out.append(f"> {r['progress_note']}")
        if r["next"]:
            out.append(f"> **Next:** {r['next']}")
        out.append(f"> *{stale_note(r['stale_days'], r['status'], r['last_src'])}*")
        out.append("")
    parent = next((r for r in rows if r["is_parent"]), None)
    if parent:
        kids = ", ".join(f"[[{k}]]" for k in CHILDREN)
        out += ["---", "", f"### {parent['project']} (roll-up)", "",
                f"Sub-projects: {kids}", ""]
    return "\n".join(out)


BASE = """filters:
  and:
    - 'type == "project-status"'
views:
  - type: cards
    name: Cards
    order:
      - status
      - percent
      - stale_days
    sort:
      - property: stale_days
        direction: DESC
  - type: table
    name: Table
    order:
      - file.name
      - status
      - percent
      - stale_days
      - last_activity
"""


def write_all(rows, dry):
    files = {os.path.join(OUT, f"{r['project']}.md"): note_body(r) for r in rows}
    files[os.path.join(VAULT, "Projects Dashboard.md")] = dashboard(rows)
    files[os.path.join(VAULT, "Projects.base")] = BASE
    if dry:
        for p in sorted(files):
            print(f"  would write {p}")
        return files
    os.makedirs(OUT, exist_ok=True)
    for p, body in files.items():
        with open(p, "w", encoding="utf-8") as f:
            f.write(body)
    return files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write", action="store_true", help="write notes into the vault")
    ap.add_argument("--init", action="store_true",
                    help=f"create example config files in {CONFIG_DIR}")
    args = ap.parse_args()
    if args.init:
        init_config()
        return
    if not PROJECTS:
        sys.exit(f"No projects registered in {CONFIG_FILE}.")
    require_vault()
    rows = merge_next(gather())
    if args.json:
        print(json.dumps(rows, indent=2))
        return
    if args.write or args.dry_run:
        files = write_all(rows, args.dry_run)
        print(f"{'would write' if args.dry_run else 'wrote'} {len(files)} files to "
              f"{VAULT}")
        if not args.dry_run:
            return
    hdr = f"{'project':17} {'docs':>5} {'progress':>10} {'%':>4}  {'last':10} {'stale':>6}  note"
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        prog = f"{r['done']}/{r['total']}" if r["total"] else "—"
        pct = f"{r['percent']}%" if r["percent"] is not None else "—"
        # 0 is a real staleness value ("today"), so test for None explicitly
        stale = "—" if r["stale_days"] is None else str(r["stale_days"])
        print(f"{r['project']:17} {r['docs']:5} {prog:>10} {pct:>4}  "
              f"{r['last_activity'] or '—':10} {stale:>6}  {r['progress_note']}")


if __name__ == "__main__":
    main()
