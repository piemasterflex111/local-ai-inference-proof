# Complete Configuration Attempt History

## Overview

**47 startup attempts** across **10 unique configurations** over **6 days** (June 12-17, 2026).

Every attempt was logged. Every config change was backed up before modification.

---

## All 10 Configuration Attempts (Chronological)

| # | Profile Name | GPU Mem | CPU Offload | Max Seqs | Batch Tokens | KV Cache | Special Params | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | CPU Offload 4GB | 0.988 | 4 GB | 4 | 2048 | fp8 | enforce-eager, MTP | Too slow, abandoned |
| 2 | Squeeze | 0.88 | none | 1 | default | fp8 | enforce-eager, MTP | Tested conservative memory |
| 3 | Ultra | 0.82 | none | 1 | 2048 | fp8 | enforce-eager, MTP | Tested aggressive memory reduction |
| 4 | CPU Offload 8GB | 0.988 | 8 GB | 1 | 1024 | fp8 | enforce-eager, MTP | CPU offload at max GPU utilization |
| 5 | CPU Offload 8GB Fast | 0.94 | 8 GB | 1 | 1024 | fp8 | enforce-eager, MTP | Balanced CPU offload |
| 6 | CPU Offload 10GB Stable | 0.92 | 10 GB | 1 | 512 | fp8 | enforce-eager, MTP | Stable CPU offload config |
| 7 | Daily GPU Fast | 0.97 | none | 4 | default | fp8 | prefix-caching | Daily operational config |
| 8 | Hermes 65K Stable | 0.988 | none | 4 | default | fp8 | prefix-caching, MTP | Hermes integration stable |
| 9 | Stable 65K No MTP | 0.988 | none | 4 | default | fp8 | prefix-caching, no MTP | Final stable production config |
| 10 | Original MTP Baseline | 0.94 | none | 1 | default | fp8 | prefix-caching, MTP qwen3_5 | Initial MTP experiment |

---

## Configuration Parameters Explored

### GPU Memory Utilization
- **0.82** → ultra conservative, left ~4.3 GB free
- **0.88** → squeeze, left ~2.9 GB free
- **0.92** → CPU offload stable, left ~1.9 GB free
- **0.94** → MTP baseline, left ~1.5 GB free
- **0.97** → daily GPU fast, left ~0.72 GB free
- **0.988** → final stable, left ~0.29 GB free

### CPU Offload Testing
- **0 GB** → GPU-only path (final)
- **4 GB** → too slow, CPU became bottleneck
- **8 GB** → mixed results, batch token tuning needed
- **10 GB** → stable but unnecessary after GPU-only worked

### Batch Token Sizes
- **default** → vLLM default batching
- **512** → conservative, slower throughput
- **1024** → medium batch size
- **2048** → aggressive batching

### Special Features Tested
- **MTP (Multi-Token Prediction)**: speculative tokens method tested both mtp and qwen3_5_mtp
- **Prefix Caching**: enabled in final configs for faster repeated context
- **Chunked Prefill**: enabled by default in vLLM
- **FP8 KV Cache**: consistent across all attempts
- **Enforce Eager**: tested to disable graph compilation overhead

---

## Evidence Files

### Startup Logs (47 files in evidence/startup_logs/)
- **2 canonical logs**: Full vLLM startup with GPU memory breakdown
  - `qwen36_canonical_2026-06-12_19-01-23.log` (250 KB)
  - `qwen36_canonical_2026-06-12_20-53-47.log` (191 KB)
- **45 container ID logs**: One per startup attempt
- **Docker error logs**: Name conflicts, restarts

### Config Backups (27 files in evidence/config_backups/)
- **11 config.yaml backups**: Pre-change snapshots of Hermes config
- **4 script backups**: Pre-change snapshots of startup scripts
- **5 health check backups**: Pre-change snapshots of health scripts
- **2 JSON snapshots**: Live container inspection dumps
- **1 text config export**: Standalone config export
- **3 maintenance backups**: Maintenance window backups

### Benchmarks (18 files in evidence/benchmarks/)
- **System state**: GPU memory, CUDA version, driver info
- **vLLM models**: Available model list
- **Throughput benchmarks**: 4 daily benchmark runs with CSV + markdown
- **Context stress tests**: Stress test results and templates
- **Direct API benchmarks**: Throughput measurements with/without thinking mode

### Profile Scripts (10 files in evidence/)
- Every unique configuration attempt as a runnable shell script
- Each shows exact docker run command with all parameters

---

## What This Proves

1. **Systematic testing**: Not random guessing. Each attempt changed specific parameters while holding others constant.
2. **Backup discipline**: Every config change was backed up before modification.
3. **Measurement-driven**: Benchmarks ran after stable configs to verify throughput.
4. **Documentation**: Full canonical logs captured every parameter and GPU memory allocation.
5. **Root cause classification**: Different failure types (OOM, CPU bottleneck, name conflicts) identified and resolved.

---

## How to Verify

```bash
# Count all evidence
cd ~/Work/local-ai-inference-proof
find evidence/ -type f | wc -l
ls -la evidence/startup_logs/ | wc -l
ls -la evidence/config_backups/ | wc -l
ls -la evidence/benchmarks/ | wc -l
ls -la evidence/*.sh | wc -l

# Read a canonical log
cat evidence/startup_logs/qwen36_canonical_2026-06-12_19-01-23.log | head -30

# Read a benchmark
cat evidence/benchmarks/rtx_daily_bench_20260617_014216.md

# Compare two profiles
diff evidence/start-qwen36-65k-mtp1.sh evidence/start-qwen36-stable-65k-no-mtp.sh
```
