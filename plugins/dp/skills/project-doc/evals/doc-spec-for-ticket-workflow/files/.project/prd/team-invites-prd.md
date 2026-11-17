---
title: "Team invites"
type: prd
project: teamspace
updated: 2026-11-01
tags: [project, teamspace, prd, invites]
---
# Team invites

## Problem
Team owners can't add anyone: new members have to be added in the database by hand.

## Goals
- An owner can invite someone by email and they can join in one click.

## Non-goals
- Single sign-on, domain-based auto-join.

## Requirements
1. An owner can invite one or more email addresses to their team.
2. The invitee gets an email with a link that works once and expires after 7 days.
3. Opening the link signs the invitee in (or up) and adds them to the team.
4. An owner can see pending invites and revoke one before it's used.
5. Inviting someone already in the team shows an error rather than sending an email.

## Success criteria
- 90% of invites sent are accepted within 7 days.
