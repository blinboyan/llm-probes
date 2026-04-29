# Probe 06: Async Retry Decorator (Medium)

## Prompt to give the agent

> Write a Python async retry decorator with exponential backoff.
>
> Requirements:
> - `@retry(max_attempts=3, base_delay=1.0, backoff_factor=2.0, exceptions=(Exception,))`
> - Retries on specified exceptions only
> - Delay doubles each attempt: 1s, 2s, 4s, ...
> - Add jitter (random 0-25% of delay) to prevent thundering herd
> - Log each retry attempt (use `logging` module)
> - Raise the last exception if all attempts fail
> - Must work with both async and sync functions (or clearly document it's async-only)
>
> Include a usage example and a simple test.

## What to evaluate

- Does the decorator actually work with `async def` functions?
- Is exponential backoff implemented correctly (base * factor^attempt)?
- Is jitter added?
- Does it catch only the specified exceptions?
- Does the test actually verify retry behavior (mock the function to fail N times then succeed)?
- Process: did the agent write the test unprompted, or only after being asked?

## Tricky bits

- Preserving the function signature (`@functools.wraps`)
- Jitter should be additive, not replacing the delay
- Should the decorator itself be usable with or without parentheses? (`@retry` vs `@retry()`)

## Red flags
- Using `time.sleep` instead of `asyncio.sleep` for async version
- No jitter
- Test that doesn't actually test retry behavior
- Not preserving function metadata
