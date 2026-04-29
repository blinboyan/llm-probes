# Probe 12: Novel Algorithm — Weighted Interval Scheduling with Dependencies (Hard)

## Why this is hard
This is NOT a standard interval scheduling problem. The dependency constraint
makes greedy approaches incorrect. It requires genuine dynamic programming reasoning
with topological ordering. Unlike standard DP problems that are heavily represented
in training data (knapsack, LIS, etc.), this combination is uncommon.

## Prompt to give the agent

> You have N tasks. Each task i has:
> - `start[i]`, `end[i]`: time interval (half-open, [start, end))
> - `profit[i]`: reward for completing the task
> - `deps[i]`: list of task indices that must be completed before task i can start
>
> A valid schedule:
> 1. No two selected tasks overlap in time
> 2. If task i is selected and has dependencies, ALL dependencies must also be selected
> 3. A dependency must end before its dependent task starts (this is guaranteed by the input)
>
> Find the maximum total profit from any valid schedule.
>
> Write a Python function `max_profit(tasks)` where each task is a dict:
> `{"start": int, "end": int, "profit": int, "deps": list[int]}`
>
> Example:
> ```python
> tasks = [
>     {"start": 0, "end": 3, "profit": 5, "deps": []},      # task 0
>     {"start": 2, "end": 5, "profit": 6, "deps": []},      # task 1
>     {"start": 4, "end": 7, "profit": 8, "deps": [0]},     # task 2 (depends on 0)
>     {"start": 6, "end": 9, "profit": 4, "deps": [1]},     # task 3 (depends on 1)
> ]
> # Answer: 13 (select tasks 0 and 2: 5+8=13)
> # Can't pick 1+2 because 1 and 2 overlap
> # Can't pick 0+1 because they overlap
> # 0+2 is valid: 0 ends at 3, 2 starts at 4, and 0 is dep of 2
> ```

## What reveals genuine reasoning

- Recognizes this needs bitmask DP or subset enumeration for small N
- Correctly handles the constraint propagation (selecting task forces deps)
- Uses topological ordering to resolve dependency chains
- For larger N, discusses the NP-hard nature and approximation tradeoffs
- Tests with cases where the greedy choice (highest profit first) gives wrong answer

## Red flags
- Treating it as standard weighted interval scheduling (ignoring deps)
- Greedy approach without acknowledging it doesn't work
- Not handling transitive dependencies (if A deps B deps C, selecting A requires B and C)
