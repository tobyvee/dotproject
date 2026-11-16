---
title: "Estimates size the work; they aren't a time budget and don't drive cuts"
type: decision
project: example-app
ticket: none
decided_by: user
supersedes:
updated: 2026-11-10
tags: [project, example-app, decision, planning]
---
# Estimates size the work; they aren't a time budget and don't drive cuts

## Context
The spec gives each build step a rough time, and `/plan-tickets` reported 325 minutes of ticket estimates against them. The user clarified that the times describe their own effort. Agents running in parallel don't use that time up, because the user does other things while they run.

## Decision
Ticket estimates aren't a planning constraint. Don't cut, defer or shrink work to fit them, and don't report ticket totals or critical paths against the spec's step times. Cut work only when the user asks.

## Alternatives
- Plan to the spec's step times and cut in the spec's order when over: treats agent run time as the user's time.

## Consequences
- Estimates stay as sizing for splits and waves.
- `cut_rank` stays as the order to cut in if the user asks for cuts.
- P2 work is scheduled after the planned work like everything else, not only "if there's time".
