---
title: "T-007: Token-bucket rate limiter"
type: ticket
project: ratelimit-proxy
status: doing
updated: 2026-10-01
tags: [project, ratelimit-proxy, ticket]
---
# T-007: Token-bucket rate limiter

## Context
Clients can currently flood the backend. See spec → Rate limiting.

## Scope
A per-client token bucket in `limiter.go`, applied before forwarding.

## Acceptance criteria
- [ ] Requests over the limit get a 429 with a `Retry-After` header
- [ ] The bucket refills at the configured rate (unit test)
- [ ] A load test in staging holds 2,000 requests per second

## Dependencies
- T-006

## Notes
