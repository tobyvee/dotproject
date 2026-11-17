#!/usr/bin/env bash
set -eu
cp -R "$(dirname "$0")/files/." .
# Fixture dotfiles are stored without the dot, so they don't act on the repo that holds the evals.
[ -f gitignore ] && mv gitignore .gitignore
[ -d github ] && mv github .github
commit_on() { (cd "$1" && git init -q -b main && git add -A && GIT_AUTHOR_DATE="$2T12:00:00" GIT_COMMITTER_DATE="$2T12:00:00" git -c user.name=Eval -c user.email=eval@example.com commit -qm "Initial commit"); }
commit_on code/alpha 2026-11-10
commit_on code/beta 2026-11-06
mkdir -p dotproject-config
cat > dotproject-config/dashboard.json <<EOF
{
  "code_root": "$PWD/code",
  "vault_dir": "$PWD/vault",
  "require_mount": null,
  "parent": null,
  "projects": { "alpha-api": "alpha", "beta-site": "beta" },
  "adapters": { "alpha-api": "frontmatter_status" }
}
EOF
cat > dotproject-config/project-next.json <<EOF
{
  "_comment": "Claude-authored per-project status label and next physical action.",
  "_status_vocab": ["active", "blocked", "stable", "ready", "parked"]
}
EOF
