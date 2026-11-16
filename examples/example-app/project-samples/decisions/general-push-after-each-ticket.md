---
title: "Each finished ticket is committed and pushed before the next one lands"
type: decision
project: example-app
ticket: none
decided_by: user
supersedes:
updated: 2026-11-10
tags: [project, example-app, decision, workflow, git]
---
# Each finished ticket is committed and pushed before the next one lands

## Context
By default, commits stay local and the user pushes when they choose. The user wants every finished ticket on GitHub and on the live app as soon as it's done, so they can check the deployed app between waves.

## Decision
Set **Workflow → Git and deploy → Push after each ticket** to yes. `/implement-ticket` pushes once the ticket's code and records are committed. `/implement-parallel` lands a wave's tickets one at a time and pushes each before landing the next.

## Alternatives
- Commits stay local until the user pushes: nothing reaches the live app until they remember to.

## Consequences
- Every push to `main` deploys through Vercel, so each ticket deploys as it lands.
- Both commands check that the branch has an upstream and matches it before they start.
- Only the main session pushes. Agents never push, and nothing is force-pushed.
