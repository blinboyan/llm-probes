# LLM Coding Agent Probes

A structured set of coding tasks to evaluate coding agents on **quality**, **speed**, and **process efficiency**.

## Dimensions Measured

| Dimension | What it captures |
|-----------|-----------------|
| **Correctness** | Does the code work? Edge cases handled? |
| **Speed** | Wall-clock time from prompt to working solution |
| **Process** | Straight-to-code vs unnecessary back-and-forth |
| **Code Quality** | Idiomatic, clean, no over-engineering |
| **Edge Cases** | Handles boundaries without being told |
| **Debugging** | Can it fix broken code efficiently? |
| **Architecture** | Good structure for larger tasks |

## Scoring

See `SCORING.md` for the rubric applied to each probe.

## Probes

| # | Tier | Probe | File | Expected Time |
|---|------|-------|------|---------------|
| 1 | Simple | FizzBuzz variant | `probes/01-fizzbuzz-variant.md` | < 2 min |
| 2 | Simple | Bug fix | `probes/02-bug-fix.md` | < 3 min |
| 3 | Simple | String transform | `probes/03-string-transform.md` | < 3 min |
| 4 | Medium | LRU Cache | `probes/04-lru-cache.md` | 5-10 min |
| 5 | Medium | CSV pipeline | `probes/05-csv-pipeline.md` | 5-10 min |
| 6 | Medium | Async retry | `probes/06-async-retry.md` | 5-10 min |
| 7 | Hard | Rate limiter | `probes/07-rate-limiter.md` | 10-20 min |
| 8 | Hard | Refactor messy code | `probes/08-refactor.md` | 10-20 min |
| 9 | Comprehensive | REST API with tests | `probes/09-rest-api.md` | 20-40 min |
| 10 | Comprehensive | Multi-file feature | `probes/10-multi-file-feature.md` | 20-40 min |
