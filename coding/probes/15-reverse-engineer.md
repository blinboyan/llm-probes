# Probe 15: Reverse Engineer from Tests (Hard — Comprehension)

## Why this is hard
Instead of writing code from a spec, the agent must reverse-engineer the spec from
tests. This requires reading test assertions carefully, inferring the intended behavior,
and then implementing something that passes all tests. Distilled models are trained on
spec->code, not test->code.

## Prompt to give the agent

> These tests describe a `Scheduler` class. Implement the class so all tests pass. Do NOT modify the tests.
>
> ```python
> import pytest
> from scheduler import Scheduler
>
> def test_basic_scheduling():
>     s = Scheduler()
>     results = []
>     s.every(1).do(lambda: results.append("A"))
>     s.tick()
>     s.tick()
>     s.tick()
>     assert results == ["A", "A", "A"]
>
> def test_interval():
>     s = Scheduler()
>     results = []
>     s.every(3).do(lambda: results.append("B"))
>     for _ in range(7):
>         s.tick()
>     assert results == ["B", "B"]
>
> def test_multiple_jobs():
>     s = Scheduler()
>     results = []
>     s.every(1).do(lambda: results.append("X"))
>     s.every(2).do(lambda: results.append("Y"))
>     for _ in range(4):
>         s.tick()
>     assert results == ["X", "Y", "X", "X", "Y", "X"]
>
> def test_cancel():
>     s = Scheduler()
>     results = []
>     job = s.every(1).do(lambda: results.append("C"))
>     s.tick()
>     s.cancel(job)
>     s.tick()
>     assert results == ["C"]
>
> def test_once():
>     s = Scheduler()
>     results = []
>     s.once().do(lambda: results.append("D"))
>     s.tick()
>     s.tick()
>     s.tick()
>     assert results == ["D"]
>
> def test_chaining():
>     s = Scheduler()
>     results = []
>     s.every(2).times(3).do(lambda: results.append("E"))
>     for _ in range(10):
>         s.tick()
>     assert results == ["E", "E", "E"]
>
> def test_execution_order_within_tick():
>     s = Scheduler()
>     results = []
>     s.every(2).do(lambda: results.append("first"))
>     s.every(2).do(lambda: results.append("second"))
>     s.tick()  # tick 1 - nothing fires (interval=2, first fire at tick 2)
>     s.tick()  # tick 2 - both fire
>     assert results == ["first", "second"]
> ```

## What reveals genuine reasoning

- Must infer from `test_interval` that `every(3)` fires on tick 3 and tick 6 (not tick 1)
- Must infer from `test_multiple_jobs` that execution order is: jobs fire in registration order, but the *results* interleave based on which jobs fire on which tick
- Must figure out `test_execution_order_within_tick`: interval=2 means first fire at tick 2, not tick 1
- Must implement method chaining (`.every().do()`, `.every().times().do()`)
- Must handle `once()` as syntactic sugar for `every(1).times(1)` or equivalent

## Red flags
- Misreading the test assertions and getting the tick counting wrong
- Not understanding the execution order in test_multiple_jobs
- Implementing `.do()` as a separate call instead of chaining
