# Probe 11: Subtle Concurrency Bug (Hard — Reasoning)

## Why this is hard
The bug is NOT a classic race condition. It requires understanding Python's GIL,
reference counting, and how `dict.items()` works during iteration. A distilled
model will likely suggest adding locks or using `threading.Lock`, which misses the point.

## Prompt to give the agent

> This code has a subtle bug that only manifests under specific conditions. Find it and explain exactly when and why it fails. Don't just add locks — explain the root cause.
>
> ```python
> import threading
> import time
>
> class EventBus:
>     def __init__(self):
>         self._handlers = {}  # event_name -> [handler_functions]
>
>     def subscribe(self, event, handler):
>         if event not in self._handlers:
>             self._handlers[event] = []
>         self._handlers[event].append(handler)
>
>     def unsubscribe(self, event, handler):
>         if event in self._handlers:
>             self._handlers[event].remove(handler)
>             if not self._handlers[event]:
>                 del self._handlers[event]
>
>     def emit(self, event, *args, **kwargs):
>         if event in self._handlers:
>             for handler in self._handlers[event]:
>                 handler(*args, **kwargs)
> ```
>
> Scenario: Multiple threads call `subscribe`, `unsubscribe`, and `emit` concurrently.
> One thread is emitting events while another thread unsubscribes a handler.

## What reveals genuine reasoning

1. The agent should identify that `emit()` iterates over the list while `unsubscribe()` mutates it (RuntimeError: list changed size during iteration)
2. The agent should also identify that `del self._handlers[event]` during `emit()`'s `if event in self._handlers` check can cause KeyError
3. A sophisticated agent will note that even with the GIL, bytecode boundaries create windows where the list can be modified between iteration steps
4. The fix should involve iterating over a snapshot (`list(self._handlers[event])`) AND a lock, not just one or the other

## Red flags
- Only suggesting "add a threading.Lock" without explaining the iteration mutation issue
- Not mentioning the snapshot pattern
- Claiming the GIL makes this safe
- Only fixing one of the two bugs (list mutation AND dict key deletion)
