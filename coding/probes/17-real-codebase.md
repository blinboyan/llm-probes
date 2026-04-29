# Probe 17: Real Codebase Feature — amux pane output search (Comprehensive)

## Why this is hard
This requires navigating a real 500-commit Go codebase, understanding its architecture
(client-server, layout tree, PTY streams, command dispatch), and implementing a feature
that touches multiple packages correctly. Distilled models fail on real codebases because
they can't explore and reason about unfamiliar architecture.

## Prompt to give the agent

> The project at `~/Projects/amux` is a terminal multiplexer for human+agent workflows,
> written in Go. Read the CLAUDE.md and README.md to understand the architecture.
>
> Add an `amux grep <pattern>` CLI command that:
> 1. Searches visible pane content across all panes for a regex pattern
> 2. Returns results as JSON: `[{"pane": "pane-1", "line": 42, "text": "matched line", "match": "pattern"}]`
> 3. Accepts an optional `--pane <ref>` flag to search a single pane
> 4. Uses the existing capture infrastructure to get pane content
> 5. Include a unit test
>
> Do NOT modify the test harness or existing tests. Work in a new branch.

## What to evaluate

### Codebase navigation
- Did the agent read CLAUDE.md first?
- Did it find and understand the capture package?
- Did it understand the command dispatch pattern (how CLI commands are routed)?
- Did it find the right way to access pane content?

### Implementation quality
- Does it follow the project's patterns (one package per concern, dependency injection)?
- Does it use `Window.ResolvePane()` for pane references?
- Does it integrate with the existing CLI command dispatch?
- Is the regex compiled once, not per-line?

### Process
- How many files did it need to read before starting?
- Did it create a branch?
- Did the tests pass?
- How many iterations to get it working?

## Red flags
- Modifying existing test files
- Not reading CLAUDE.md
- Creating a new package when it should extend an existing one
- Not understanding the client-server protocol (trying to access PTYs directly from CLI)
