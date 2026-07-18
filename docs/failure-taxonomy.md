# Failure Taxonomy: Local vLLM + Qwen Inference Stack

**Date:** 2026-06-26
**Source:** 189 evidence files from ~/Work/local-ai-inference-proof
**Period:** June 12-19, 2026

---

## 1. Classification Framework

Failures are classified along two axes:

| Axis | Dimensions |
|------|-----------|
| **Layer** | GPU driver, CUDA/cuDNN, vLLM, Governor, Hermes proxy |
| **Severity** | Critical (complete failure), Degraded (reduced performance), Warning (operational risk) |

---

## 2. Failure Modes

### F1: GPU OOM (Out of Memory)
**Layer:** vLLM + CUDA
**Frequency:** Most common in early attempts (Configs #1-#3)
**Root Cause:** GPU memory fraction set too high (0.988) leaving no room for CUDA context initialization. Model weights exceed available VRAM after CUDA allocator overhead.
**Symptoms:**
```
RuntimeError: CUDA error: out of memory
```
**Fix:** Reduce `--gpu-memory-fraction` from 0.988 → 0.95, then further to 0.85 for stability.
**Evidence:** `evidence/startup_logs/qwen36_canonical_2026-06-12_19-01-23.log`

### F2: MTP (Multi-Token Prediction) Instability
**Layer:** vLLM speculative decoding
**Frequency:** High in Configs #4-#5
**Root Cause:** MTP draft stages enabled but draft model compatibility issues with Qwen3.6 architecture cause decoding failures under load.
**Symptoms:**
```
Speculative decoding mismatch
Sequence generation failure after 50+ tokens
```
**Fix:** Disable MTP entirely (`--num-mt-prefill-sequences 0`). Stable config achieved at Config #6.
**Evidence:** `evidence/config_backups/`, startup logs with MTP flags

### F3: Request Governor Forwarding Failure
**Layer:** qwen-request-governor
**Frequency:** Critical in June 19 session
**Root Cause:** Governor proxy process crashed or became unresponsive, causing all downstream Hermes requests to fail. Multiple architecture changes attempted (stream broker → agent55 broker v2).
**Symptoms:**
```
ConnectionRefusedError: Connection refused
HTTP 502/504 from governor endpoint
```
**Fix:** Simplify governor architecture. Final stable config verified at 20:35:05 on June 19.
**Evidence:** `evidence/home_root/governor/`, `evidence/home_root/governor_logs/`

### F4: Configuration Drift
**Layer:** Multiple (shell profiles, config.yaml, governor)
**Frequency:** Moderate
**Root Cause:** Running live config changes without backup discipline leads to inconsistent state across related files (config.yaml, start scripts, hermes settings).
**Symptoms:**
```
Hermes can't reach model endpoint
Model starts but Hermes uses wrong port
Port conflicts between text/vision models
```
**Fix:** "Backup before change" discipline. Every modification preceded by `.bak.TIMESTAMP` copy.
**Evidence:** 27 config backups show backup-before-change pattern

### F5: Port Conflict (8001/8003/8080)
**Layer:** Hermes proxy + vLLM + governor
**Frequency:** Recurring
**Root Cause:** Multiple services competing for same ports during text/vision model swaps. Text on :8001, governor on :8003, Hermes UI on :8080.
**Symptoms:**
```
Address already in use
EADDRINUSE on bind()
```
**Fix:** Port assignment discipline documented in launch scripts. Text on 8001, vision on 8002, governor on 8003.
**Evidence:** Profile scripts in `evidence/*.sh`

### F6: Thermal Throttling
**Layer:** GPU hardware
**Frequency:** Observed during extended benchmark sessions
**Root Cause:** Sustained high-load inference pushes GPU past thermal limits, causing clock throttling.
**Symptoms:**
```
Tokens/sec drops from 27.77 → 15-20 tok/s during extended runs
GPU temp > 80°C
```
**Fix:** Monitor with `qwen-bench4`, limit sustained benchmark length. Accept throttling as GPU limitation.
**Evidence:** `evidence/benchmarks/rtx_daily_bench_*.md`

---

## 3. Severity Matrix

| Mode | Critical | Degraded | Warning |
|------|----------|----------|---------|
| F1: GPU OOM | ✓ | | |
| F2: MTP Instability | ✓ | ✓ | |
| F3: Governor Failure | ✓ | | |
| F4: Config Drift | | ✓ | ✓ |
| F5: Port Conflict | ✓ | | |
| F6: Thermal Throttle | | ✓ | ✓ |

---

## 4. Resolution Rate

| Failure Mode | Attempts to Fix | Resolution Method | Final Status |
|-------------|-----------------|-------------------|-------------|
| F1: GPU OOM | 3 configs | Memory fraction tuning | RESOLVED |
| F2: MTP Instability | 2 configs | Disable MTP | RESOLVED |
| F3: Governor Failure | 12 backups | Architecture simplification | RESOLVED |
| F4: Config Drift | Ongoing | Backup discipline | MITIGATED |
| F5: Port Conflict | Multiple | Port discipline | MITIGATED |
| F6: Thermal Throttle | N/A | Accept limitation | ACCEPTED |

---

## 5. Lessons Learned

1. **MTP is not worth the complexity.** Disabled in favor of stable single-stage decoding.
2. **Governor architecture must be simple.** Multiple rewrites (stream broker → agent55 broker) succeeded only after simplification.
3. **Backup discipline prevents config drift.** 27 backups → zero unrecoverable state.
4. **GPU memory fraction has diminishing returns.** 0.988 → OOM; 0.85 → stable. Lower is more reliable.
5. **Thermal throttling is inevitable on laptop GPU.** Benchmark against it; don't try to eliminate it.
