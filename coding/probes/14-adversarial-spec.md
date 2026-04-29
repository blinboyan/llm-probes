# Probe 14: Adversarial Spec — Contradictory Requirements (Hard — Judgment)

## Why this is hard
The spec has a hidden contradiction. A distilled model will just implement what's
asked. A reasoning model should spot the contradiction, flag it, and propose a resolution.

## Prompt to give the agent

> Implement a Python `CircularBuffer` with these requirements:
>
> 1. `CircularBuffer(size)` — fixed-size buffer
> 2. `write(data: bytes)` — write data to the buffer. If the data exceeds remaining space, overwrite the oldest data.
> 3. `read(n: int) -> bytes` — read n bytes from the buffer. Raises `BufferError` if fewer than n bytes available.
> 4. `peek(n: int) -> bytes` — like read but doesn't consume the data
> 5. The buffer must maintain FIFO ordering
> 6. `write()` must be atomic — either all data is written or none (no partial writes)
> 7. Maximum write size is `size` bytes
>
> Include tests.

## The contradiction

Requirements 2 and 6 contradict each other:
- Req 2: "overwrite the oldest data" (implies partial old data can be lost)
- Req 6: "atomic — either all data is written or none" (implies no partial state change)

If you write 5 bytes to a buffer with 3 bytes free and 7 total capacity, do you:
- (a) Overwrite old data to make room, writing all 5 (satisfies req 2, sort-of satisfies 6)
- (b) Reject the write entirely (satisfies req 6 strictly, violates req 2)
- (c) The "atomic" applies to the data being written, not the existing data (req 2 + 6 compatible)

## What reveals genuine reasoning

- The agent should explicitly identify the tension between req 2 and req 6
- It should propose an interpretation and explain why
- Interpretation (c) is the most reasonable: "atomic" means the new data is fully written or not at all, but old data can be overwritten to make room
- The agent should still handle the case where `len(data) > size` (impossible to write even with overwriting)

## Red flags
- Implementing without noticing the contradiction
- Asking "which one do you want?" without analyzing the options
- Only implementing one behavior and ignoring the conflict
