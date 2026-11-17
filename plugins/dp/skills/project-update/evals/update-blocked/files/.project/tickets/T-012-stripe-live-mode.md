---
title: "T-012: Switch payments to Stripe live mode"
type: ticket
project: billing-portal
status: doing
updated: 2026-11-02
tags: [project, billing-portal, ticket, payments]
---
# T-012: Switch payments to Stripe live mode

## Acceptance criteria
- [ ] Live keys are read from the environment, never the repo
- [ ] A real £1 payment succeeds and is refunded
- [ ] Webhooks are verified with the live signing secret

## Notes
The code path is ready behind `STRIPE_MODE=live`.
