#!/usr/bin/env bash
set -eu
cp -R "$(dirname "$0")/files/." .
# Fixture dotfiles are stored without the dot, so they don't act on the repo that holds the evals.
[ -f gitignore ] && mv gitignore .gitignore
[ -d github ] && mv github .github
git init -q -b main
git add -A
git -c user.name=Eval -c user.email=eval@example.com commit -qm "Initial commit"
