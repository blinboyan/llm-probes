# Probe 01: FizzBuzz Variant (Simple)

## Prompt to give the agent

> Write a Python function `fizzbuzz_custom(n, rules)` that generalizes FizzBuzz.
>
> - `n`: print results for 1 through n
> - `rules`: a list of `(divisor, word)` tuples, e.g. `[(3, "Fizz"), (5, "Buzz")]`
> - For each number, concatenate all matching words in the order given. If no rules match, print the number.
> - Return a list of strings.
>
> Example: `fizzbuzz_custom(15, [(3, "Fizz"), (5, "Buzz")])` should return the classic FizzBuzz output.

## What to evaluate

- Does it handle overlapping rules (e.g. 15 -> "FizzBuzz")?
- Does it handle an empty rules list (just numbers)?
- Does it handle rules with divisor=1 (everything matches)?
- Is it a clean, Pythonic implementation?
- Did it go straight to code or ask unnecessary questions?

## Expected solution (reference)

```python
def fizzbuzz_custom(n, rules):
    result = []
    for i in range(1, n + 1):
        words = ''.join(word for divisor, word in rules if i % divisor == 0)
        result.append(words or str(i))
    return result
```

## Red flags
- Over-engineering (classes, type checking, etc.)
- Asking "what language?" when Python was specified
- Not returning a list (printing instead)
