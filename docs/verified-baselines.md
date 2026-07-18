# Verified Baselines

This document records the known-good state of the local inference stack. These baselines represent configurations that were verified to work — not theoretical or aspirational settings.

## Docker Inspect Baseline

**File:** `evidence/config_backups/qwen36-current-full-inspect-20260614_093751.json`

Docker inspect of the Qwen3.6-27B NVFP4 vLLM container:

| Parameter | Value | Meaning |
|---|---|---|
| Model | Qwen3.6-27B NVFP4 MTP | Quantized model serving |
| Container State | Running | Active inference serving |
| OOMKilled | `false` | No GPU memory exhaustion |
| ExitCode | `0` | Clean exit |
| max-model-len | `65,536` | Full context length enabled |
| kv-cache-dtype | `fp8` | FP8 KV cache |
| Quantization | `modelopt` | modelopt quantization |
| Prefix Caching | `true` | Prefix caching enabled |
| GPU Runtime | NVIDIA CUDA | Hardware-accelerated inference |
| Host Port | `8001` | External API port |

## vLLM Startup Baseline

The model serves successfully through vLLM with the following startup command parameters:

```bash
vllm serve Qwen/Qwen3.6-27B-NVFP4-MTP \
  --max-model-len 65536 \
  --quantization modelopt \
  --kv-cache-dtype fp8 \
  --enable-prefix-caching \
  --port 8001
```

## Benchmark Baseline

**File:** `evidence/benchmarks/direct_vllm_bench.txt`

Low-context throughput measurement:

| Run | Input Tokens | Output Tokens | Time (s) | tok/s |
|---|---|---|---|---|
| 1 | 29 | 300 | 10.80 | 27.77 |
| 2 | 29 | 300 | 10.82 | 27.72 |

**Average: ~27.7 tok/s at low context (29 input tokens).**

Context stress benchmark (`evidence/benchmarks/context_stress_bench.txt`):

| Context Length | tok/s | % of baseline |
|---|---|---|
| 29 tokens | 27.77 | 100% |
| 1,452 tokens | 28.79 | 104% |
| 14,052 tokens | 15.72 | 57% |
| 56,052 tokens | 4.88 | 18% |

## Verified Configuration Files

| File | Purpose | Status |
|---|---|---|
| `evidence/automation/qwen3.6-launcher.sh` | Launch script | VERIFIED |
| `src/api/context_guard.py` | Context budget guard | VERIFIED |
| `src/api/governor.py` | Request governor | VERIFIED |
| `evidence/config_backups/` | Config history | ARCHIVED |
| `evidence/governor_revisions/` | Governor evolution | ARCHIVED |

## Verification Commands

To reproduce baseline verification:

```bash
# Check Docker container state
docker inspect <container_id> --format='{{.State.Status}}'

# Verify model serving
curl -s http://127.0.0.1:8001/v1/models | jq .

# Run throughput benchmark
python scripts/run_benchmark.py --input-tokens 29 --output-tokens 300
```

## Baseline Notes

* Benchmarks were run on the local workstation (Ryzen 7 9700X, RTX PRO 4000 Blackwell, 64 GB RAM). Results will differ on other hardware.
* The `27.77 tok/s` number is valid only at low context. Throughput drops as context length increases.
* Docker inspect was captured on 2026-06-14. The container was running at that time.
* Config backups include both working and failed configurations. Not all files in `config_backups/` represent verified states.
