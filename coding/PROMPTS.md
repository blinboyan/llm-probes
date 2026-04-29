# Copy-Paste Prompts

Ready to send to the other agent. Each is self-contained.

---

## 01 — FizzBuzz Variant (Simple)

Write a Python function `fizzbuzz_custom(n, rules)` that generalizes FizzBuzz. `n`: print results for 1 through n. `rules`: a list of `(divisor, word)` tuples, e.g. `[(3, "Fizz"), (5, "Buzz")]`. For each number, concatenate all matching words in the order given. If no rules match, print the number. Return a list of strings. Example: `fizzbuzz_custom(15, [(3, "Fizz"), (5, "Buzz")])` should return the classic FizzBuzz output.

---

## 02 — Bug Fix (Simple)

This Python function is supposed to find the first duplicate in a list, but it has bugs. Fix it.

```python
def first_duplicate(arr):
    """Return the first element that appears more than once. Return -1 if no duplicates."""
    seen = {}
    for i in range(len(arr)):
        if arr[i] in seen:
            seen[arr[i]] = seen[arr[i]] + 1
        else:
            seen[arr[i]] = 1

    for key in seen:
        if seen[key] > 1:
            return key

    return -1
```

Bug: `first_duplicate([1, 2, 3, 2, 1])` should return `2` (first element to repeat), but this can return `1` or `2` depending on dict ordering. Fix it so it always returns the element whose *second* occurrence comes first.

---

## 03 — String Transform (Simple)

Write a Python function `snake_to_camel(s)` that converts a snake_case string to camelCase. Examples: `"hello_world"` -> `"helloWorld"`, `"already"` -> `"already"`, `"__leading_underscores"` -> `"__leadingUnderscores"`, `"trailing__"` -> `"trailing__"`, `""` -> `""`.

---

## 04 — LRU Cache (Medium)

Implement an LRU (Least Recently Used) cache in Python. `LRUCache(capacity)` — initialize with a max capacity. `get(key)` — return the value if key exists, else -1. Marks as recently used. `put(key, value)` — insert or update. If at capacity, evict the least recently used item first. Both operations must be O(1) time. Write it from scratch — don't use `functools.lru_cache` or `OrderedDict`.

---

## 05 — CSV Pipeline (Medium)

Write a Python script that reads a CSV file, processes it, and outputs a summary. Input CSV (`sales.csv`):
```
date,product,quantity,unit_price
2024-01-15,Widget A,10,29.99
2024-01-15,Widget B,5,49.99
2024-01-16,Widget A,3,29.99
2024-01-16,Widget C,8,19.99
2024-02-01,Widget B,12,49.99
2024-02-01,Widget A,7,29.99
```

Output a JSON file (`summary.json`) with: 1) Total revenue (quantity * unit_price, summed), 2) Revenue per product (sorted descending by revenue), 3) Revenue per month (YYYY-MM format), 4) Best selling product by quantity. Use only the standard library.

---

## 06 — Async Retry Decorator (Medium)

Write a Python async retry decorator with exponential backoff. `@retry(max_attempts=3, base_delay=1.0, backoff_factor=2.0, exceptions=(Exception,))`. Retries on specified exceptions only. Delay doubles each attempt: 1s, 2s, 4s. Add jitter (random 0-25% of delay) to prevent thundering herd. Log each retry attempt (use `logging` module). Raise the last exception if all attempts fail. Include a usage example and a simple test.

---

## 07 — Rate Limiter (Hard)

Implement a sliding window rate limiter in Python. `RateLimiter(max_requests, window_seconds)` — e.g., 100 requests per 60 seconds. `allow(client_id: str) -> bool` — returns True if the request is allowed, False if rate limited. `get_wait_time(client_id: str) -> float` — returns seconds until the client can make another request. Uses a sliding window (not fixed window). Thread-safe. Memory-efficient: clean up old entries. Include tests that verify: basic rate limiting, requests allowed after window passes, independent client limits, thread safety under concurrent access.

---

## 08 — Refactor (Hard)

Refactor this working but messy Python code. Keep the same behavior but make it clean, readable, and maintainable. Explain your changes.

```python
import json
import os

def process(f):
    data = open(f).read()
    d = json.loads(data)
    results = []
    for item in d:
        if item['type'] == 'A':
            if item['status'] == 'active':
                if item['value'] > 100:
                    results.append({'id': item['id'], 'category': 'high_value_a', 'amount': item['value'] * 1.1})
                else:
                    results.append({'id': item['id'], 'category': 'low_value_a', 'amount': item['value'] * 1.05})
            else:
                results.append({'id': item['id'], 'category': 'inactive_a', 'amount': item['value'] * 0.9})
        elif item['type'] == 'B':
            if item['status'] == 'active':
                if item['value'] > 200:
                    results.append({'id': item['id'], 'category': 'high_value_b', 'amount': item['value'] * 1.2})
                else:
                    results.append({'id': item['id'], 'category': 'low_value_b', 'amount': item['value'] * 1.1})
            else:
                results.append({'id': item['id'], 'category': 'inactive_b', 'amount': item['value'] * 0.8})
        elif item['type'] == 'C':
            if item['status'] == 'active':
                results.append({'id': item['id'], 'category': 'active_c', 'amount': item['value'] * 1.0})
            else:
                results.append({'id': item['id'], 'category': 'inactive_c', 'amount': item['value'] * 0.7})
    out = open(f.replace('.json', '_processed.json'), 'w')
    out.write(json.dumps(results, indent=2))
    out.close()
    return results
```

---

## 09 — REST API (Comprehensive)

Build a simple URL shortener API using Python and Flask (or FastAPI — your choice). Endpoints: `POST /shorten` — accepts `{"url": "https://example.com"}`, returns `{"short_url": "http://localhost:5000/abc123", "id": "abc123"}`. `GET /<id>` — redirects to the original URL (302). `GET /stats/<id>` — returns `{"id": "abc123", "url": "...", "clicks": 42, "created_at": "..."}`. Use an in-memory store. Short IDs: 6 chars alphanumeric. Validate URL input. Return appropriate HTTP status codes (201, 302, 404, 400). Include tests using pytest covering all endpoints and error cases. Create a complete runnable project with requirements.txt.

---

## 10 — CLI Note System (Comprehensive)

Build a CLI note-taking app in Python that stores notes as Markdown files. Commands: `notes add "Title" --tags tag1,tag2` — creates a timestamped .md file in `./notes/` with YAML frontmatter (title, date, tags), content from `--body "text"`. `notes list` — lists all notes in a table, with `--tag filter` and `--sort date|title`. `notes search "query"` — full-text search with matching snippets. `notes export --format json` — export all notes as JSON. Use `argparse` or `click` for CLI. Store as individual .md files with YAML frontmatter. Use only standard library (except click/pyyaml if chosen). Include at least 5 tests. Handle errors gracefully. Create a proper project structure.
