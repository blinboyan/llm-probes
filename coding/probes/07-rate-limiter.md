# Probe 07: Rate Limiter (Hard)

## Prompt to give the agent

> Implement a sliding window rate limiter in Python.
>
> Requirements:
> - `RateLimiter(max_requests, window_seconds)` — e.g., 100 requests per 60 seconds
> - `allow(client_id: str) -> bool` — returns True if the request is allowed, False if rate limited
> - `get_wait_time(client_id: str) -> float` — returns seconds until the client can make another request (0 if allowed now)
> - Uses a **sliding window** (not fixed window) — so the count is always for the last N seconds from *now*
> - Thread-safe
> - Memory-efficient: don't store timestamps forever, clean up old entries
>
> Include tests that verify:
> 1. Basic rate limiting works
> 2. Requests are allowed after the window passes
> 3. Different clients have independent limits
> 4. Thread safety under concurrent access

## What to evaluate

- Is it actually a sliding window? (not just fixed time buckets)
- Thread safety: does it use locks properly?
- Memory cleanup: does it prune old timestamps?
- Are the tests meaningful (do they use time mocking, or just sleep)?
- Does `get_wait_time` return accurate values?

## Architecture decisions to watch

- **Good**: deque of timestamps per client, bisect for cleanup, Lock per client or global
- **OK**: sorted list with binary search
- **Bad**: storing all timestamps forever, scanning full list on each call

## Red flags
- Fixed window implementation (resets at boundaries)
- No thread safety despite requirement
- Tests that `time.sleep(61)` — should mock time
- Unbounded memory growth
