# CLAUDE.md

## Build

- `go test ./...` runs the tests.
- `go build ./cmd/planner` builds the CLI.

## Conventions

- Wrap errors with `fmt.Errorf("...: %w", err)`.
