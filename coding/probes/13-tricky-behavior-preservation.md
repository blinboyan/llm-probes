# Probe 13: Tricky Behavior Preservation (Hard — Comprehension)

## Why this is hard
The code has intentional "quirks" that look like bugs but are load-bearing behavior.
A distilled model will "fix" them, breaking the contract. This tests whether the
agent can distinguish bugs from intentional behavior by reasoning about usage patterns.

## Prompt to give the agent

> This class is used in production and has tests that depend on its exact behavior.
> The team wants to add type hints and clean up the code, but they're worried about
> breaking things. Review this code, identify which behaviors are intentional vs
> accidental, and add type hints WITHOUT changing any behavior.
>
> ```python
> class TokenBucket:
>     def __init__(self, rate, capacity):
>         self.rate = rate
>         self.capacity = capacity
>         self._tokens = capacity  # start full
>         self._last_refill = None  # intentionally None, not time.time()
>
>     def _refill(self):
>         import time
>         now = time.time()
>         if self._last_refill is None:
>             self._last_refill = now
>             return  # no refill on first call — burst budget is the initial capacity
>         elapsed = now - self._last_refill
>         self._last_refill = now
>         self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
>
>     def consume(self, tokens=1):
>         self._refill()
>         if self._tokens >= tokens:
>             self._tokens -= tokens
>             return True
>         return False  # does NOT partially consume
>
>     def peek(self):
>         # deliberately does NOT call _refill
>         return self._tokens
>
>     @property
>     def tokens(self):
>         self._refill()
>         return self._tokens
>
>     def force_consume(self, tokens=1):
>         self._refill()
>         self._tokens -= tokens  # can go negative — this is intentional
>         return self._tokens
> ```
>
> Questions:
> 1. Why does `_last_refill` start as None instead of `time.time()`?
> 2. Why does `peek()` NOT call `_refill()`?
> 3. Is the negative token balance in `force_consume` a bug or a feature?
> 4. Add type hints to all methods without changing any behavior.

## What reveals genuine reasoning

1. **None initialization**: The agent should reason that this means the first call to consume/tokens gets the full initial capacity without any time-based refill — it's a "cold start" optimization. If it were `time.time()`, the first call might have 0 elapsed time (same effect) OR a small elapsed time that adds unexpected tokens beyond capacity... actually no, it's min'd. The real reason is: if `time.time()` is called at init time but `consume()` is called much later, you'd get a huge refill. Setting None defers the baseline.
2. **peek() skips refill**: This gives a snapshot of "committed" tokens without advancing the refill clock. Useful for monitoring without side effects.
3. **Negative tokens**: This is a deliberate "debt" mechanism — future refills must pay back the debt before new tokens are available.

## Red flags
- "Fixing" the None initialization to `time.time()`
- Making peek() call _refill()
- Adding a `max(0, ...)` guard to force_consume
- Not explaining the reasoning behind each design choice
