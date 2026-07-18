# Evidence Index

## Evidence Summary

| Category | Count | Location |
|---|---|---|
| Startup logs | 47 | `evidence/startup_logs/` |
| Config backups | 27 | `evidence/config_backups/` |
| Benchmarks | 18 | `evidence/benchmarks/` |
| Profile scripts | 10 | `evidence/*.sh` |
| Benchmark scripts | 17 | `evidence/bin_ai/` |
| Governance artifacts | 9 | `evidence/governance/`, `evidence/governance_logs/` |
| Audit records | 5 | `evidence/` |
| Agent55 baselines | 2 | `evidence/agent55_baselines/` |

## How to Find What You Need

### Evidence index CSV (machine-readable)
```bash
cat analysis/evidence_index.csv
```

### Raw startup logs
```bash
ls evidence/startup_logs/
head -30 evidence/startup_logs/qwen36_canonical_2026-06-12_19-01-23.log
```

### Benchmarks
```bash
cat evidence/benchmarks/rtx_daily_bench_20260617_014216.md
```

### Config backups
```bash
cat evidence/config_backups/config.yaml.before_text_switch_20260613_152955
```

### Compare two startup profiles
```bash
diff evidence/start-qwen36-65k-mtp1.sh evidence/start-qwen36-stable-65k-no-mtp.sh
```

### Governance evidence
```bash
cat evidence/governance_logs/qwen_request_governor_sample.jsonl
cat evidence/governance/governor.py
```

---

## Proof of Process

This evidence base shows:
1. **Systematic testing** — parameters changed methodically, not randomly
2. **Backup discipline** — every config change backed up first
3. **Measurement** — benchmarks captured after stable configs
4. **Documentation** — full startup logs captured
5. **Verification** — scripts to validate health
6. **Governance** — request governor with context budget management
7. **Workflow automation** — complete AI tooling script library
