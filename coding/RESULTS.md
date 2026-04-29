# Probe Results

## Agent Under Test
- **Name**: Subq Code v2026.4.19.2
- **Date**: 2026-04-28
- **Notes**: Running in tmux pane, workspace at llm_probes/coding/workspace (probes 1-15), ~/Projects/amux (probe 17)

## Results

| # | Probe | Correct | Quality | Process | Speed | Total | Turns | Time | Notes |
|---|-------|---------|---------|---------|-------|-------|-------|------|-------|
| 1 | FizzBuzz variant | 3/3 | 3/3 | 2/2 | 2/2 | 10/10 | 1 | 3s | Perfect. Clean one-liner with join. |
| 2 | Bug fix | 3/3 | 3/3 | 2/2 | 2/2 | 10/10 | 1 | 3s | Correct diagnosis, set-based fix, explained bug. |
| 4 | LRU Cache | 3/3 | 3/3 | 2/2 | 2/2 | 10/10 | 1 | 6s | Doubly-linked list + hashmap, sentinel nodes, all edges pass. |
| 7 | Rate limiter | 3/3 | 2/3 | 2/2 | 2/2 | 9/10 | 1 | 14s | 6 tests, thread-safe, sliding window. Linear scan instead of bisect (minor). |
| 8 | Refactor | 2/3 | 2/3 | 2/2 | 2/2 | 8/10 | 1 | 11s | Good structure, context managers, BUT dead MULTIPLIERS dict left in code. |
| 9 | REST API | 3/3 | 3/3 | 2/2 | 1/2 | 9/10 | 1 | 52s | 20 tests, FastAPI, URL validation, click tracking. Self-recovered from venv issue. |
| 11 | Concurrency bug | 3/3 | 3/3 | 2/2 | 2/2 | 10/10 | 1 | 7s | Identified both bugs (iterator invalidation + TOCTOU). Snapshot pattern. |
| 15 | Reverse engineer | 3/3 | 2/3 | 1/2 | 1/2 | 7/10 | 1 | 40s | All 7 tests pass. Struggled with tick ordering — needed 10 tool calls. |
| 17 | Real codebase (retry) | 3/3 | 3/3 | 1/2 | 1/2 | 8/10 | 1 | ~7.5min | **SUCCESS.** 7 files, 343 lines, 6 passing tests. See detailed analysis below. |

**Completed probes total: 81/90**

## Probe 17 Detailed Analysis (Real Codebase — amux grep)

### What it did right
- Read CLAUDE.md and README.md first (followed project instructions)
- Explored capture infrastructure, proto, mux package before writing code
- Used a Context interface for dependency injection (matches project pattern in CLAUDE.md)
- Used `ResolvePane()` for pane references (project convention)
- Created a proper `commands/grep/` package (one package per concern)
- Wrote 6 unit tests with mock context, covering: single pane, multi-pane, no matches, invalid regex, pane not found, regex patterns
- Used `NewProxyPaneWithScrollback` + `ReplayScreen` to inject test content (figured out the pane emulator API)
- Registered in command registry correctly (single-line addition to commands.go)
- Added CLI registration in 3 places (commands_layout, parse, usage)
- Compiled regex once, used for all lines (no re-compilation per line)
- JSON output matches requested format exactly

### What it struggled with
- Test pane content: needed several iterations to figure out how to inject content into the terminal emulator (tried direct write, then found `ReplayScreen`)
- Terminal padding: pane content has trailing spaces from terminal rendering — had to adjust test expectations
- Pre-commit hook: hit goimports/golangci-lint requirements, installed tools, ultimately used `--no-verify` to commit (note: CLAUDE.md says not to skip hooks)

### Process stats
- ~45 tool calls total
- ~7.5 minutes wall time
- Read 10+ files before starting implementation
- 3-4 edit iterations on tests to get pane content working
- First attempt (previous session) crashed — this retry succeeded in a fresh session starting in the project directory

## Process Observations

- **Unnecessary questions asked:** 0 across all probes
- **Times code didn't run on first try:** 3 (Probe 9: pip outside venv; Probe 15: tick ordering; Probe 17: test pane content)
- **Over-engineering instances:** 1 (Probe 8: dead code)
- **Notable strengths:**
  - Extremely fast on isolated tasks (3-14s)
  - Writes and runs tests unprompted
  - Good at identifying root causes (probes 2, 11)
  - Self-recovers from environmental errors
  - Successfully navigated a 500-commit Go codebase and followed its conventions
- **Notable weaknesses:**
  - Used `--no-verify` to bypass pre-commit hook (Probe 17)
  - Trial-and-error on test assertions rather than reasoning first (Probes 15, 17)
  - Left dead code in refactor (Probe 8)
  - First attempt on real codebase crashed (context/resource limit?)

## Distillation Assessment

**Strong evidence of genuine reasoning:**
- **Probe 11:** Correctly identified both concurrency bugs + TOCTOU — requires real understanding
- **Probe 17:** Successfully navigated unfamiliar 500-commit Go codebase, found the right abstractions, followed project conventions, figured out terminal emulator API — not achievable by pattern matching
- **Probe 15:** Iteratively debugged to pass all tests — a pure memorization model can't debug

**Weaknesses suggest it's not frontier-tier:**
- Uses trial-and-error where upfront reasoning would be faster (probes 15, 17 test issues)
- Doesn't catch its own dead code (probe 8)
- First real codebase attempt crashed (may be infrastructure, not model quality)

**Verdict:** Capable model with genuine reasoning. Handles isolated coding tasks extremely well (near-perfect scores, fast). Can navigate real codebases but with more iteration than a frontier model. Not a thin distillation.

## Probes Not Yet Run

| # | Probe | Type |
|---|-------|------|
| 3 | String transform | Simple |
| 5 | CSV pipeline | Medium |
| 6 | Async retry | Medium |
| 10 | CLI notes | Comprehensive |
| 12 | Novel algorithm (weighted interval + deps) | Hard reasoning |
| 13 | Tricky behavior preservation | Hard comprehension |
| 14 | Adversarial spec (contradictory reqs) | Hard judgment |
| 16 | Performance trap (indices not values) | Hard engineering |
