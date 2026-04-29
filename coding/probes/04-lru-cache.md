# Probe 04: LRU Cache (Medium)

## Prompt to give the agent

> Implement an LRU (Least Recently Used) cache in Python.
>
> Requirements:
> - `LRUCache(capacity)` — initialize with a max capacity
> - `get(key)` — return the value if key exists, else -1. Marks as recently used.
> - `put(key, value)` — insert or update. If at capacity, evict the least recently used item first.
> - Both operations must be O(1) time.
>
> Write it from scratch — don't use `functools.lru_cache` or `OrderedDict`.

## What to evaluate

- Does it use a doubly-linked list + hashmap? (the O(1) requirement demands this)
- Are get and put actually O(1)?
- Does it handle: capacity=1, overwriting existing keys, get updating recency?
- Does it include a Node class or equivalent?
- Code quality: clean separation of concerns, no memory leaks (dangling refs)?

## Test cases

```python
cache = LRUCache(2)
cache.put(1, 1)
cache.put(2, 2)
assert cache.get(1) == 1       # returns 1, key 1 is now most recent
cache.put(3, 3)                 # evicts key 2
assert cache.get(2) == -1       # key 2 was evicted
cache.put(4, 4)                 # evicts key 1
assert cache.get(1) == -1       # key 1 was evicted
assert cache.get(3) == 3
assert cache.get(4) == 4
```

## Red flags
- Using OrderedDict (explicitly forbidden)
- O(n) eviction (scanning a list)
- Not handling "put updates existing key" case
- Over-engineering with threading, generics, etc.
