# Local AI Inference Validation Record

## Overview

This document records the validation of a local AI inference stack: Qwen3.6-27B NVFP4 served through vLLM on RTX PRO 4000 Blackwell hardware. It captures 8 days of debugging, configuration changes, and failure classification. The system went from unstable startup behavior to a verified, measurable runtime baseline.

The goal was not to build a production system. The goal was to debug an inference stack, understand its failure modes, and preserve the evidence of what happened.

## Project Timeline

| Date | Event |
|---|---|
| 2026-06-07 | Project initiation; vLLM launch failures begin |
| 2026-06-08 | Request governor design; first revision |
| 2026-06-09 | Hermes proxy misrouting debug |
| 2026-06-10 | Proxy routing confirmed |
| 2026-06-11 | Context budget guard implementation |
| 2026-06-12 | Governor revisions; OpenShift manifests |
| 2026-06-13 | Benchmark execution |
| 2026-06-14 | Docker inspect baseline capture |
| 2026-06-15 | Failure taxonomy documentation |

## Evidence Inventory

The `analysis/evidence_index.csv` file contains 164 indexed evidence items across 9 categories.

### Key Evidence Artifacts

| Artifact | File | Status | Significance |
|---|---|---|---|
| Qwen3.6-27B full Docker inspect | `evidence/config_backups/qwen36-current-full-inspect-20260614_093751.json` | VERIFIED_BASELINE | Container state, GPU, model params |
| Direct vLLM benchmark | `evidence/benchmarks/direct_vllm_bench.txt` | VERIFIED | 27.77 tok/s at low context |
| Context stress benchmarks | `evidence/benchmarks/context_stress_bench.txt` | VERIFIED | Throughput vs. context length |
| Startup launch scripts | `evidence/automation/qwen3.6-launcher.sh` | VERIFIED | Repeatable launch workflow |
| Governor revisions | `evidence/governor_revisions/` | VERIFIED | Request governance evolution |
| Context guard logic | `src/api/context_guard.py` | VERIFIED | Context budget validation |
| Proxy port mapping | `evidence/proxy/hermes-proxy-map.txt` | VERIFIED | Port debug evidence |

## Request Governor Architecture

The request governor is a FastAPI service that sits between the user and the vLLM backend. Its purpose is to validate requests before they reach the model.

### Request flow

```
User request → Hermes API (:8003) → Request Governor → vLLM Backend (:8001)
```

### Core components

* **Context Budget Guard** — validates that `input_tokens + requested_output_tokens <= context_window_limit`. Rejects oversized requests before they hit vLLM.
* **Classifier** — categorizes requests (chat, code, context_stress, unknown) to apply different governance rules.
* **Input validation** — type checking, empty input rejection, parameter bounds.
* **Request routing** — direct pass-through for valid requests; structured rejection for invalid ones.

### Key implementation details

* The context guard (`src/api/context_guard.py`) loads model configuration (max_model_length, token estimation) and performs budget checks before forwarding to vLLM.
* The governor revision history is preserved in `evidence/governor_revisions/`, showing 12 iterations of context guard logic improvements.
* Input validation checks for empty inputs, missing parameters, and type mismatches.

## Failure Taxonomy

Six failure modes were identified and classified:

| ID | Name | Category | Severity | Detection | Fix |
|---|---|---|---|---|---|
| F1 | GPU OOM | Hardware | High | docker logs OOMKilled=true | Reduce context, reduce batch size |
| CUDA launch | GPU | Critical | docker logs | Rebuild container, check GPU memory |
| F3 | Context overflow | Config | Medium | HTTP 500, 422 | Enforce context budget, add guards |
| F4 | Proxy port mismatch | Config | High | Connection refused | Map correct host port |
| F5 | Config drift | Config | Low | Intermittent failures | Version control config |
| F6 | MTP instability | Runtime | Medium | vLLM errors | Disable MTP, use standard mode |

## Benchmark Results

### Direct vLLM benchmark

| Run | Tokens | Time (s) | tok/s | Notes |
|---|---|---|---|---|
| 1 | 300 | 10.80 | 27.77 | 29 input tokens |
| 2 | 300 | 10.82 | 27.72 | 29 input tokens |

### Context stress benchmarks

| Context Length | tok/s | Notes |
|---|---|---|
| 29 tokens | 27.77 | Baseline |
| 1,452 tokens | 28.79 | Similar to baseline |
| 14,052 tokens | 15.72 | ~44% drop from baseline |
| 56,052 tokens | 4.88 | ~82% drop from baseline |

**Throughput degrades approximately linearly with context length.** At near-max context (56k/65k), throughput drops to ~17% of baseline.

## Verified Runtime Baseline

The Docker inspect file (`evidence/config_backups/qwen36-current-full-inspect-20260614_093751.json`) captures a verified running state. This represents the "known good" configuration that the debugging process arrived at.

The container shows:
* `OOMKilled: false` — no GPU memory exhaustion
* `ExitCode: 0` — clean exit (no crash)
* `State: running` — active inference serving
* `65,536` — full context length enabled
* `kv-cache-dtype: fp8` — FP8 KV cache in use
* `quantization: modelopt` — modelopt quantization active
* `prefix-caching` — prefix caching enabled

## Working Configuration Parameters

The verified baseline uses these vLLM parameters:

```json
{
  "max-model-len": 65536,
  "quantization": "modelopt",
  "kv-cache-dtype": "fp8",
  "enable-prefix-caching": true,
  "port": 8001
}
```

These parameters were arrived at through iterative debugging. Earlier configurations that caused failures are preserved in the config backups for reference.

## Quick Start

```bash
cd local-ai-inference-proof
python -m pip install -e '.[dev]'
make verify
```

Run API:

```bash
make run-api
```

Test endpoints:

```bash
curl -s http://127.0.0.1:8060/health | jq .
curl -s http://127.0.0.1:8060/sample/classify | jq .
```

Docker:

```bash
make docker-build
make docker-run
```

## Lessons

* GPU memory is the hard constraint. 24 GB limits what model/quantization/context combinations fit.
* Context budget validation in the governor prevents the backend from receiving requests that will crash it.
* Docker inspect is the authoritative baseline — not logs, not memory. The JSON state is verifiable.
* Benchmark results show throughput is context-dependent. The `27.77 tok/s` number is only valid at low context.
* Proxy misrouting was a configuration error, not a code error. Port mapping is easy to get wrong.
* Preserving failure evidence (bad configs, error logs) is as valuable as preserving the working state.
