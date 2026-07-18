# Local vLLM Runtime Log Artifact

## Purpose

This artifact documents one local vLLM API server log excerpt and ties the raw log lines back to observable system behavior.

It is intended to support the visual post artifact: **raw logs -> interpretation -> documented evidence -> easier repeat check**.

## Source

- Uploaded log file: `Pasted text(423).txt`
- Parsed APIServer log lines: **71**
- Successful API responses: **16**
- Qwen3XMLToolParser load lines: **28**
- Periodic engine metric snapshots: **27**
- Metric window: **00:58:33 to 01:02:53** (260 seconds)

## What the log directly shows

| Evidence in log | Direct interpretation |
|---|---|
| `POST /v1/chat/completions HTTP/1.1" 200 OK` | A chat-completions API request completed successfully. |
| `vLLM Successfully import tool parser Qwen3XMLToolParser` | The Qwen XML tool parser was loaded. This does not prove a tool call executed. |
| `Avg prompt throughput` | Input-token processing rate during the reporting window. |
| `Avg generation throughput` | Output-token generation rate during the reporting window. |
| `Running: X reqs` | Requests currently in model execution batches. |
| `Waiting: X reqs` | Requests waiting to be scheduled or processed. |
| `GPU KV cache usage` | Percent of allocated KV cache capacity occupied. This is not total GPU memory usage. |
| `Prefix cache hit rate` | How often cached prompt prefixes were reused instead of recomputed. |

## Metric summary from the parsed log

| Metric | Min | Max | Mean |
|---|---:|---:|---:|
| Avg prompt throughput, tokens/s | 0.0 | 4976.5 | 1097.6 |
| Avg generation throughput, tokens/s | 0.0 | 56.0 | 32.7 |
| Running requests | 1.0 | 2.0 | 1.9 |
| Waiting requests | 0.0 | 2.0 | 1.3 |
| GPU KV cache usage, percent | 9.3 | 90.7 | 61.3 |
| Prefix cache hit rate, percent | 9.4 | 21.9 | 17.0 |

## Selected timeline samples

| Time | Log values | Interpretation |
|---|---|---|
| 00:58:29 | `POST /v1/chat/completions ... 200 OK` | A request completed successfully. |
| 00:58:33 | Prompt 1651.8 tok/s, Gen 25.9 tok/s, Running 2, Waiting 1, KV 50.0% | Input processing was active, two requests were running, and one request was waiting. |
| 00:59:33 | Prompt 0.0 tok/s, Gen 0.7 tok/s, Running 2, Waiting 2, KV 90.7% | High KV cache occupancy with queued work. This means capacity pressure, not automatic out-of-memory. |
| 01:01:23 | Prompt 0.0 tok/s, Gen 26.3 tok/s, Running 1, Waiting 1, KV 9.3% | KV cache occupancy dropped after earlier active context was released or completed. |
| 01:01:43 | Prompt 4976.5 tok/s, Gen 0.3 tok/s, Running 2, Waiting 1, KV 90.7% | Large input-token processing window with very low output-token generation in that reporting interval. |

## Corrected wording used in the visual

- **Periodic Engine Metrics** instead of implying a fixed exact 10-second guarantee.
- **GPU KV cache usage** means allocated KV cache capacity occupied, not total GPU memory.
- **Running requests** means requests currently in model execution batches.
- **Waiting requests** means requests waiting to be scheduled or processed.
- **High KV cache usage** means capacity pressure, longer queues, or possible preemption depending on configuration. It does not automatically mean out-of-memory.
- **Tool parser loaded** means the parser was available. It does not prove a tool/function call occurred.
- **Throughput** is measured over the current reporting window and can change depending on prompt length, output length, batching, cache state, and queue state.

## What this artifact does not prove by itself

The log excerpt alone does not prove:

- model quality
- correctness of generated output
- full GPU memory usage
- exact GPU model
- full Docker/container configuration
- full launch command
- latency distribution
- production deployment

For a stronger audit package, attach:

- exact vLLM launch command
- Docker inspect output
- `nvidia-smi` snapshot
- benchmark script
- request payload examples
- response samples
- hardware inventory
- environment variables
- git commit hash

## Short LinkedIn caption

Real vLLM run, shown from logs to machine behavior.

Requests, speed, GPU cache usage, and queueing in one view.
