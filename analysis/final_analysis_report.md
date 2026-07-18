## What Is the Strongest Technical Explanation?

### 30-Second Version

"I built a local AI inference stack on RTX PRO 4000 Blackwell, going through 47 startup attempts to find a stable configuration. I classified 6 failure modes, built a request governor, and landed at 27 tok/s sustained throughput. I treated it like hardware validation — measure, fail, classify, fix, repeat."

### 2-Minute Version

"I treated local AI inference as a validation problem. I started with naive vLLM configs that kept hitting GPU OOM — memory fraction set too high. I systematically reduced it from 0.988 down to 0.85, disabled MTP decoding which was causing instability, and landed on a stable 65k context configuration. Along the way, I built a request governor that went through 12 revisions before it was stable. The pattern is identical to manufacturing test: you have hardware constraints, you hit them, you classify the failure, you tune parameters until you're in the operating envelope. The result is 27 tok/s sustained throughput with a verified passing baseline."

---

## Evidence File Inventory

| Category | File Count | Sample Files |
|----------|-----------|-------------|
| startup_log | 47 | `qwen36_start_2026-06-12_19-01-23.log` |
| workflow_script | 40 | `start-qwen`, `qwen-health`, `qwen-bench4` |
| config_backup | 27 | `config.json.bak.TIMESTAMP` |
| project_meta | 25 | `pyproject.toml`, `README.md` |
| benchmark | 18 | `rtx_daily_bench_*.md` |
| profile_script | 15 | `start-qwen36-stable-65k-no-mtp.sh` |
| documentation | 13 | `docs/ARCHITECTURE.md` |
| source_code | 10 | `src/local_ai_stack_proof/api.py` |
| archive | 7 | `vllm_troubleshooting_runbook.txt` |
| Other | 26 | Various supporting files |

---

## Conclusion

This repository documents 8 days of systematic local AI inference debugging, resulting in a verified stable stack. The evidence corpus demonstrates GPU memory management, proxy architecture evolution, configuration discipline, performance benchmarking, failure taxonomy, and shell automation.

**Highest-value finding:** The repo documents methodology over outcome. The 47 startup logs with 10 unique configs show systematic debugging. The 12 governor revisions show architectural iteration. The 27 config backups show engineering discipline. This is not just a working system — it's the complete evidence trail of how the system was engineered to work.

---

## Key Engineering Pattern: Complexity Collapse

The evidence shows the same pattern across both the governor and vLLM configuration work.

Initial attempts added capability quickly: larger context, more routing logic, more request handling, more aggressive serving settings.

Failures exposed the unstable parts of the system.

The stable path came from reducing complexity, isolating one variable at a time, and preserving only the controls required for reliable operation.

This is visible in two places:

- Governor evolution: simple → complex → simpler → stable
- vLLM configuration: aggressive → reduced → stable

The engineering lesson is that local AI serving reliability depends on controlled operating envelopes, not maximum feature enablement.

### Verified vLLM Serving Baseline

One Docker inspect capture shows the Qwen3.6-27B NVFP4 MTP vLLM container in a running state.

The baseline is valuable because it captures the full launch envelope:

- vLLM OpenAI-compatible server
- CUDA 13 runtime container
- modelopt quantization
- FP8 KV cache
- 65,536 max model length
- max 4 sequences
- prefix caching enabled
- reasoning parser set to Qwen3
- tool parser set to Qwen3 Coder
- host port 8001 mapped to container port 8000
- Docker GPU device request enabled
- OOMKilled false
- ExitCode 0

This is a known-good serving-state artifact. It should be referenced publicly as a summarized baseline, not published as raw inspect JSON.