# Probe 16: Performance Trap (Hard — Engineering Judgment)

## Why this is hard
The naive solution works but is O(n^2). The "clever" solution most models jump to
(sorting + two pointers) doesn't work due to a subtle constraint. Only careful
reasoning reveals the correct O(n) approach.

## Prompt to give the agent

> Given an array of integers and a target sum, find all pairs of *indices* (i, j) where
> i < j and `arr[i] + arr[j] == target`. Return them sorted by (i, j).
>
> Constraints:
> - Array can have duplicate values
> - You must return INDICES, not values
> - Must handle arrays up to 10^6 elements efficiently
> - Multiple pairs can share an index (e.g., arr[0] can appear in multiple pairs)
>
> Example:
> ```python
> find_pairs([1, 2, 3, 2, 1], 3)
> # Returns: [(0, 1), (0, 3), (1, 4), (3, 4)]
> # Because: arr[0]+arr[1]=3, arr[0]+arr[3]=3, arr[1]+arr[4]=3, arr[3]+arr[4]=3
> ```
>
> Write the function and include tests that verify correctness AND that it handles
> 10^5 elements in under 1 second.

## The trap

1. **Naive O(n^2)**: Two nested loops. Works but too slow for 10^6.
2. **Sort + two pointers**: Classic approach for pair sum, but DESTROYS index information.
   To recover indices you need to carry them along, and with duplicates this gets messy.
3. **Hash map approach**: Group indices by value. For each value v, look up (target - v).
   But must carefully handle the case where v == target - v (same value group, need combinations).

The correct approach is a defaultdict(list) mapping value -> list of indices, then
for each value, find the complement and enumerate pairs. Sorting the output is
the final step.

## What reveals genuine reasoning

- Immediately spots the "indices not values" constraint that kills sort+two-pointers
- Uses the hash map approach with proper duplicate handling
- Handles the v == target/2 case (pairs within the same value group)
- Performance test actually generates large input and asserts timing

## Red flags
- Sorting the array and losing indices
- O(n^2) brute force for a 10^6 constraint
- Not handling duplicates properly
- Performance "test" that doesn't actually measure time
