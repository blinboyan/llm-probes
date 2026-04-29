# Probe 08: Refactor Messy Code (Hard)

## Prompt to give the agent

> Refactor this working but messy Python code. Keep the same behavior but make it clean, readable, and maintainable. Explain your changes.
>
> ```python
> import json
> import os
>
> def process(f):
>     data = open(f).read()
>     d = json.loads(data)
>     results = []
>     for item in d:
>         if item['type'] == 'A':
>             if item['status'] == 'active':
>                 if item['value'] > 100:
>                     results.append({'id': item['id'], 'category': 'high_value_a', 'amount': item['value'] * 1.1})
>                 else:
>                     results.append({'id': item['id'], 'category': 'low_value_a', 'amount': item['value'] * 1.05})
>             else:
>                 results.append({'id': item['id'], 'category': 'inactive_a', 'amount': item['value'] * 0.9})
>         elif item['type'] == 'B':
>             if item['status'] == 'active':
>                 if item['value'] > 200:
>                     results.append({'id': item['id'], 'category': 'high_value_b', 'amount': item['value'] * 1.2})
>                 else:
>                     results.append({'id': item['id'], 'category': 'low_value_b', 'amount': item['value'] * 1.1})
>             else:
>                 results.append({'id': item['id'], 'category': 'inactive_b', 'amount': item['value'] * 0.8})
>         elif item['type'] == 'C':
>             if item['status'] == 'active':
>                 results.append({'id': item['id'], 'category': 'active_c', 'amount': item['value'] * 1.0})
>             else:
>                 results.append({'id': item['id'], 'category': 'inactive_c', 'amount': item['value'] * 0.7})
>     out = open(f.replace('.json', '_processed.json'), 'w')
>     out.write(json.dumps(results, indent=2))
>     out.close()
>     return results
> ```

## What to evaluate

- Does the refactored code preserve exact behavior?
- Key improvements to look for:
  - Context managers (`with open(...)`)
  - Data-driven approach (config dict/table instead of nested ifs)
  - Better variable names
  - Proper file handling (closing files)
  - Separation of concerns (reading, processing, writing)
- Did the agent explain *why* each change was made?
- Did it add tests to verify behavior preservation?

## Scoring the refactor

- **Great**: Data-driven rules table, separated I/O from logic, context managers, explained reasoning
- **Good**: Reduced nesting, better names, context managers
- **Mediocre**: Cosmetic changes only (renaming vars, adding comments)
- **Bad**: Changed behavior, over-engineered with classes/inheritance for this scale

## Red flags
- Changing the multiplier values or thresholds
- Adding type hints, docstrings, logging etc. (over-engineering — the ask was "clean and readable")
- Not using context managers for file I/O
- Creating an abstract base class hierarchy for 3 types
