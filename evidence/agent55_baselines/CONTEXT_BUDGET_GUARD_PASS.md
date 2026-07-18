# Agent55 Context Budget Guard — Verified Pass

## Result

The context budget guard is working.

## Verified behavior

- 98,870-token payload compacted to 34,678 tokens.
- Request returned 200 OK.
- 49,488-token payload passed without compaction.
- Normal requests passed without unnecessary compaction.
- Guard preserved max_tokens at 4,096 when compaction made the request safe.

## Fixed failure mode

Previous failure:

    59,905 input tokens + 4,096 output tokens = 64,001 > 64,000

vLLM rejected the request with a context-length 400.

Current behavior:

    Governor intercepts oversized context
    Compacts stale assistant/tool/log state
    Preserves hot messages
    Forwards valid request to vLLM

## Engineering value

This turns Hermes long-running Desktop tasks from fragile chat-history sessions into recoverable, budget-aware agent runs.
