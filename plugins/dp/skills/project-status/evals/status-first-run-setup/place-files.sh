#!/usr/bin/env bash
set -eu
cp -R "$(dirname "$0")/files/." .
# Fixture dotfiles are stored without the dot, so they don't act on the repo that holds the evals.
[ -f gitignore ] && mv gitignore .gitignore
[ -d github ] && mv github .github
commit_on() { (cd "$1" && git init -q -b main && git add -A && GIT_AUTHOR_DATE="$2T12:00:00" GIT_COMMITTER_DATE="$2T12:00:00" git -c user.name=Eval -c user.email=eval@example.com commit -qm "Initial commit"); }
commit_on code/shop-frontend 2026-11-12
commit_on code/infra-notes 2026-10-02
commit_on code/no-project 2026-09-20
