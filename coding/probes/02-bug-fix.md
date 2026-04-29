# Probe 02: Bug Fix (Simple)

## Prompt to give the agent

> This Python function is supposed to find the first duplicate in a list, but it has bugs. Fix it.
>
> ```python
> def first_duplicate(arr):
>     """Return the first element that appears more than once. Return -1 if no duplicates."""
>     seen = {}
>     for i in range(len(arr)):
>         if arr[i] in seen:
>             seen[arr[i]] = seen[arr[i]] + 1
>         else:
>             seen[arr[i]] = 1
>
>     for key in seen:
>         if seen[key] > 1:
>             return key
>
>     return -1
> ```
>
> Bug: `first_duplicate([1, 2, 3, 2, 1])` should return `2` (first element to repeat), but this can return `1` or `2` depending on dict ordering. Fix it so it always returns the element whose *second* occurrence comes first.

## What to evaluate

- Does the agent correctly identify the bug? (iterating dict keys doesn't preserve insertion order of *second* occurrence)
- Does the fix use a set for O(n) time?
- Does it handle: empty list, no duplicates, all duplicates?
- Process: did it explain the bug before fixing, or just silently rewrite?

## Expected solution (reference)

```python
def first_duplicate(arr):
    seen = set()
    for x in arr:
        if x in seen:
            return x
        seen.add(x)
    return -1
```

## Red flags
- Saying "dict preserves insertion order in Python 3.7+" and missing the actual bug
- Adding unnecessary complexity (sorting, Counter, etc.)
- Not explaining what was wrong
