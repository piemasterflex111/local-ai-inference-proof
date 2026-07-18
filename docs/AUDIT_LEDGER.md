# vLLM / Qwen3.6 Local Inference Audit Ledger

**Author:** REDACTED_USER REDACTED_USER
**Date:** June 26, 2026
**Purpose:** Record of the debugging and stabilization process for a local Qwen3.6-27B NVFP4 inference stack on RTX PRO 4000 Blackwell hardware. Documents failure modes, configuration evolution, and verified baselines.

---

## 1. System Under Test

| Parameter | Value |
|---|---|
| GPU | NVIDIA RTX PRO 4000 Blackwell (24 GB VRAM, 145 W power limit) |
| Driver | 580.159.03 |
| Persistence mode | Enabled |
| Performance state | P1 |
| Host OS | Ubuntu Linux (kernel 7.0.0-22-generic) |
| CPU | Ryzen 7 9700X |
| RAM | 64 GB |
| Container runtime | Docker |
| Serving framework | vLLM 0.19.2rc1.dev134+gfe9c3d6c5 |
| Base image | vllm/vllm-openai:cu130-nightly |
| Model | sakamakismile/Qwen3.6-27B-Text-NVFP4-MTP |
| Quantization | ModelOpt NVFP4 |
| Host port | 8001 (container port 8000) |
| Container name | qwen36-vllm |
| Uptime | 10+ days (continuous) |

---

## 2. Active Launch Configuration (HERMES STABLE 65K)

**Source file:** `Work/ai/models/profiles/start-qwen36-hermes-65k-stable.sh`

```
--model sakamakismile/Qwen3.6-27B-Text-NVFP4-MTP
--served-model-name qwen3.6-27b-nvfp4-mtp
--trust-remote-code
--quantization modelopt
--safetensors-load-strategy prefetch
--language-model-only
--max-model-len 64000
--max-num-seqs 2
--max-num-batched-tokens 4096
--enable-chunked-prefill
--kv-cache-dtype fp8
--gpu-memory-utilization 0.980
--enable-prefix-caching
--enable-auto-tool-choice
--tool-call-parser qwen3_xml
--reasoning-parser qwen3
--default-chat-template-kwargs {"enable_thinking": false}
--generation-config vllm
```

**Key trade-offs in this config:**
- `max-model-len 64000` (vs 65536): Slightly shorter context to leave headroom for KV cache on 24 GB VRAM
- `max-num-seqs 2`: Two concurrent requests to balance throughput vs latency
- `max-num-batched-tokens 4096`: Limits burst token batches to prevent OOM
- `gpu-memory-utilization 0.980`: Reserve ~2% VRAM for CUDA graphs, driver overhead, and host buffers
- `--enable-chunked-prefill`: Break long prompts into chunks to avoid VRAM spikes during prompt processing
- `--enable-prefix-caching`: Reuse KV cache for repeated prefixes (28.6% hit rate observed in steady state)
- No speculative decoding on the active config (MTP was tested in separate profiles)

---

## 3. GPU Memory Breakdown (from startup logs)

| Component | Size |
|---|---|
| Model weights (NVFP4) | 17.62 GiB |
| CUDA graphs | 0.43 GiB |
| KV cache (FP8, 2 seqs) | 2.65 GiB |
| **Total allocated** | **~20.7 GiB** |
| **GPU VRAM available** | **24 GiB** |
| **Headroom** | **~3.3 GiB** |

Source: vLLM startup log lines (Docker container `qwen36-vllm`)

---

## 4. Benchmark Evidence

### 4.1. Direct vLLM throughput test

**Test:** Single completion request, 300 token response, no thinking mode
**Script:** `Work/ai/benchmarks/direct_vllm_template_no_think.py`

| Metric | Value |
|---|---|
| Elapsed | 10.80 seconds |
| Prompt tokens | 29 |
| Completion tokens | 300 |
| Total tokens | 329 |
| **Throughput** | **27.77 tok/s** |

### 4.2. Steady-state throughput (from Docker logs)

Observed ranges during active use over 10 days:
- Average generation throughput: 13.2 to 56.8 tok/s (varies by request length and concurrency)
- GPU KV cache usage: 38.9% to 42.6%
- Prefix cache hit rate: 25.9% to 28.6%
- Concurrent requests: 1-2 running, 0-1 queued

---

## 5. Failure Taxonomy (Observed Errors)

### 5.1. Context length overflow

```
This model's maximum context length is 64000 tokens. However, you requested 8192 output tokens.
```
**Cause:** Client requested `max_tokens` that exceeded the model's remaining context budget (max_model_len minus existing context).
**Fix:** Client-side validation: reject requests where `max_tokens > (max_model_len - context_length)`.
**Trade-off:** Could raise `max-model-len` but would reduce available KV cache capacity.

### 5.2. Multimodal rejection on text-only model

```
ValueError: At most 0 image(s) may be provided in one prompt.
```
**Cause:** Client sent image data to a text-only model (`--language-model-only` flag).
**Fix:** Proxy layer must inspect `modalities` field and reject image payloads before they reach vLLM.
**Lesson:** Model capability enforcement belongs at the gateway/proxy layer, not the model server.

### 5.3. Model-not-found errors

```
Error with model error=ErrorInfo(message='The model `qwen2.5-vl-7b` does not exist.', type='NotFoundError', param='model', code=404)
```
**Cause:** Client referenced a model not loaded on this instance.
**Fix:** Model name validation at the API gateway level. Return 404 with list of available models.
**Lesson:** Single-model instances need strict model name enforcement.

### 5.4. ASGI validation errors

```
RuntimeWarning: Enable tracemalloc to get the object allocation traceback
RuntimeWarning: coroutine 'AsyncLLMEngine.step' was never awaited
```
**Cause:** Internal async lifecycle issues in vLLM nightly builds (unawaited coroutines during engine shutdown or reconfiguration).
**Status:** Non-critical; no user-facing impact observed during 10-day continuous run.
**Mitigation:** Nightly build instability is accepted risk. Would pin to release tag for production.

### 5.5. Nightly build warnings

```
Warning: Prefix caching in Mamba cache 'align' mode is currently enabled for SSM models by default.
```
**Cause:** vLLM nightly enables Mamba SSM state caching by default for Qwen3 architecture.
**Impact:** Informational; no observed functional impact on throughput or accuracy.

---

## 6. Configuration Comparison Matrix

| Parameter | HERMES STABLE | NO MTP | SQUEEZE | ULTRA |
|---|---|---|---|---|
| max-model-len | 64000 | 65536 | 65536 | 65536 |
| max-num-seqs | 2 | 4 | 1 | 1 |
| max-num-batched-tokens | 4096 | (default) | (default) | 2048 |
| gpu-memory-utilization | 0.980 | 0.988 | 0.88 | 0.82 |
| speculative decoding | OFF | OFF | MTP=1 | MTP=1 |
| enforce-eager | OFF | OFF | ON | ON |
| enable-chunked-prefill | ON | OFF | OFF | OFF |
| enable-prefix-caching | ON | ON | OFF | OFF |
| --shm-size | (default) | (default) | 32g | 32g |
| PYTORCH_CUDA_ALLOC_CONF | (default) | (default) | expandable_segments | expandable_segments |
| use-case | Daily Hermese use | Max concurrency | Memory-constrained test | Extreme memory test |

**Lessons learned from 10-profile comparison:**
- `gpu-memory-utilization > 0.95`: Safe if `--enable-chunked-prefill` is active; dangerous without it
- `max-num-seqs 1` + `--enforce-eager`: Most stable but lowest throughput
- MTP=1 speculative decoding: Marginal benefit on NVFP4 quantized models; adds complexity
- `expandable_segments:True`: Required for MTP/ultra profiles to avoid CUDA allocation fragmentation
- 65536 context length requires `gpu-memory-utilization <= 0.88` for single-seq safety

---

## 7. GPU Power and Thermal Profile

| Metric | Value |
|---|---|
| Power draw (average) | 144.93 W |
| Power limit | 145.00 W |
| Temperature | 65 C |
| Fan speed | 50% |
| Performance state | P1 (max performance) |
| Power cap | Active (software) |
| HW slowdown | Not active |
| HW thermal slow down | Not active |

**Observation:** The GPU runs near its power cap (99.96% of 145 W limit) during sustained generation. Thermal headroom is excellent at 65C with 50% fan. No throttling observed in 10+ days of continuous operation.

---

## 8. Container Health and Lifecycle

| Parameter | Value |
|---|---|
| Container status | Running |
| Container age | 10+ days |
| Image size | 30.8 GB (downloaded: 8.02 GB delta) |
| EngineCore process CPU | 35.3% (one core, async event loop) |
| API server process CPU | 0.2% (FastAPI/Starlette async server) |
| vLLM version | 0.19.2rc1.dev134+gfe9c3d6c5 |
| Initialization time | 73.84 seconds (compilation: 31.94s, KV cache warmup: 41.9s) |
| Model loading | Prefetch strategy (no zero-copy; loads through CPU first) |

---

## 9. What This Demonstrates

1. **Containerized model serving:** Full Docker-based deployment lifecycle (image selection, volume mounts, GPU passthrough, health monitoring, log collection, crash recovery).

2. **Performance tuning:** 10 distinct configurations tested across memory utilization, concurrency, context length, speculative decoding, and eager vs graph modes. Selection criteria: throughput vs stability vs memory safety.

3. **Failure classification:** 5 distinct error categories identified from logs with root causes, fixes, and gateway-level enforcement strategies.

4. **Resource accounting:** Precise GPU memory accounting (weights, CUDA graphs, KV cache, headroom) validated against 24 GB VRAM constraint.

5. **Production-grade observability:** Docker logs, nvidia-smi telemetry, benchmark scripts, and persistent configuration management.

6. **Trade-off reasoning:** Every parameter choice has a documented trade-off (e.g., higher context length vs KV cache capacity, speculative decoding complexity vs marginal throughput gain).

---

## 10. Artifacts Referenced

| Artifact | Path |
|---|---|
| Active launch script | `Work/ai/models/profiles/start-qwen36-hermes-65k-stable.sh` |
| All launch profiles | `Work/ai/models/profiles/` (10 scripts) |
| Benchmark script | `Work/ai/benchmarks/direct_vllm_template_no_think.py` |
| Benchmark results | `Work/ai/benchmarks/direct_vllm_no_think_bench.txt` |
| vLLM error log | `Work/local-ai-inference-proof/sample_data/vllm_errors.log` |
| Docker container logs | `docker logs qwen36-vllm` |
| GPU health | `nvidia-smi --query-gpu=...` (see Section 7) |
| Audit ledger (this file) | `Work/local-ai-inference-proof/docs/AUDIT_LEDGER.md` |

---

*End of audit ledger. All data sourced from live system observation on 2026-06-26.*
