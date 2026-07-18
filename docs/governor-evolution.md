# Request Governor Evolution

**Date:** 2026-06-26
**Source:** 12 governor backups + logs from ~/Work/local-ai-inference-proof
**Period:** June 19, 2026

---

## 1. Purpose

The `qwen-request-governor` sits between Hermes Desktop and vLLM, managing request routing, load balancing, and error handling for local inference. It proxies on port 8003.

```
Hermes Desktop :8080 → qwen-request-governor :8003 → vLLM :8001 → Qwen model → GPU
```

---

## 2. Architecture Timeline

### v0: Simple Forward Proxy (Before June 19)
**State:** Basic HTTP forwarding from port 8003 → 8001
**Problem:** No request queueing or error recovery. Governor crashes propagate to all Hermes requests.

### v1: Forward Patch (2026-06-19 00:26:12)
**File:** `governor.py.bak.forward_patch.20260619_002612`
**Change:** Added forward-path logic for routing requests through governor
**Status:** Interim patch, incomplete

### v2: Stream Broker (2026-06-19 13:37:50)
**File:** `governor.py.bak_stream_broker_20260619_133750`
**Change:** Introduced streaming broker for SSE (Server-Sent Events) passthrough
**Problem:** Stream handling introduced latency and complexity

### v3: Agent55 Broker v2 (2026-06-19 13:18:16)
**File:** `governor.py.bak_agent55_broker_v2_20260619_131816`
**Change:** Integrated with Agent55 sidecar for structured message handling
**Problem:** Over-engineered. Added more failure modes than it solved.

### v4: PASS Baseline (2026-06-19 20:35:05)
**File:** `qwen_request_governor_PASS_20260619_203505.jsonl`
**Change:** Simplified architecture with context budget guard
**Result:** **VERIFIED PASSING** — governor stable under sustained load
**Evidence:** `agent55_baselines/` contains both context budget guard and governor PASS logs

---

## 3. Change Analysis

| Version | Timestamp | Lines Changed | Architecture | Outcome |
|---------|-----------|---------------|-------------|---------|
| v0 | Pre-June 19 | N/A | Simple forward | Unstable |
| v1 | 00:26:12 | Patch | Forward + routing | Partial |
| v2 | 13:37:50 | Rewrite | Stream broker | Latency issues |
| v3 | 13:18:16 | Rewrite | Agent55 broker | Over-engineered |
| v4 | 20:35:05 | Simplify | Guard + budget | **PASS** |

---

## 4. Evolution Pattern

The governor followed a classic **complexity collapse** curve:

1. **Simple forward** — too naive, crashes propagate
2. **Added routing** — partial improvement
3. **Stream broker** — added latency
4. **Agent55 broker** — maximum complexity, still failing
5. **Simplified guard** — reduced to essential functionality, finally stable

**Key insight:** The governor failed when it tried to do too much. Stability arrived when it was reduced to its core function: request forwarding with error handling.

---

## 5. Final Stable Configuration

```
Hermes Desktop/CLI → :8003 (governor) → :8001 (vLLM) → Qwen3.6-27B → RTX PRO 4000
```

**Stable parameters:**
- Port 8003 for governor
- Port 8001 for vLLM text
- Context budget guard enabled
- Stream passthrough for SSE

**Verified at:** 2026-06-19 20:35:05
