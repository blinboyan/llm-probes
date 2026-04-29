# Probe 03: String Transform (Simple)

## Prompt to give the agent

> Write a Python function `snake_to_camel(s)` that converts a snake_case string to camelCase.
>
> Examples:
> - `"hello_world"` -> `"helloWorld"`
> - `"already"` -> `"already"`
> - `"__leading_underscores"` -> `"__leadingUnderscores"`
> - `"trailing__"` -> `"trailing__"`
> - `""` -> `""`

## What to evaluate

- Does it handle leading/trailing underscores (tricky edge case)?
- Does it handle consecutive underscores?
- Is the implementation clean (not regex soup)?
- Did the agent handle the edge cases shown, or only the happy path?

## Expected behavior on tricky inputs

```
"a_b_c"          -> "aBC"
"__private"      -> "__private"  (leading underscores preserved)
"hello___world"  -> "hello__World"  (extra underscores preserved)
"ALL_CAPS"       -> "aLLCAPS"  or  "allCaps" (either is reasonable, but should be consistent)
```

## Red flags
- Ignoring the leading/trailing underscore examples entirely
- Using only `.split('_')` without handling consecutive underscores
- Asking for clarification on cases that were already specified in the examples
