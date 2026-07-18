#!/usr/bin/env python3
"""
Performance benchmark for the local AI inference platform.

Measures:
  - Model startup time
  - GPU memory consumption
  - First-response latency (time to first token)
  - Token generation speed (tokens/second)
  - Successful request percentage
  - GPU memory after load

Usage:
  python3 src/benchmark.py
  python3 src/benchmark.py --url http://127.0.0.1:8003/v1/completions
  python3 src/benchmark.py --n 10 --max-tokens 100
"""

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass, fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

# ── Configuration ──────────────────────────────────────────────────────
DEFAULT_URL = "http://127.0.0.1:8003/v1/completions"
REQUESTS = 5
MAX_TOKENS = 50
PROMPT = "Explain what a CPU is in one sentence."


@dataclass
class BenchResult:
    timestamp: str
    endpoint: str
    prompt_length: int
    max_tokens: int
    requests: int
    successes: int
    failures: int
    success_rate: float
    first_latency_ms: float
    total_latency_ms: float
    tokens_per_second: float
    gpu_memory_used_mib: int | None = None
    gpu_memory_free_mib: int | None = None
    gpu_memory_total_mib: int | None = None
    params: dict[str, Any] | None = None
    errors: list[str] | None = None

    def to_json(self) -> str:
        result = {}
        for f in fields(self):
            val = getattr(self, f.name)
            if val is not None:
                result[f.name] = val
        return json.dumps(result, indent=2)

    def summary(self) -> str:
        lines = [
            "=== BENCHMARK SUMMARY ===",
            f"Endpoint: {self.endpoint}",
            f"Prompt length: {self.prompt_length} tokens",
            f"Max tokens: {self.max_tokens}",
            f"Requests: {self.requests}",
            f"Successes: {self.successes}/{self.requests} ({self.success_rate:.1%})",
            f"First latency: {self.first_latency_ms:.1f} ms",
            f"Total latency: {self.total_latency_ms:.1f} ms",
            f"Throughput: {self.tokens_per_second:.2f} tokens/sec",
        ]
        if self.gpu_memory_used_mib is not None:
            lines.append(
                f"GPU memory: {self.gpu_memory_used_mib} MiB / {self.gpu_memory_total_mib} MiB"
            )
        return "\n".join(lines)


def get_gpu_stats():
    """Query NVIDIA GPU memory usage."""
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=memory.used,memory.free,memory.total",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            vals = result.stdout.strip().split(",")
            return {
                "used": int(vals[0].strip()),
                "free": int(vals[1].strip()),
                "total": int(vals[2].strip()),
            }
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return {"used": None, "free": None, "total": None}


async def run_benchmark(
    url: str = DEFAULT_URL,
    n: int = REQUESTS,
    max_tokens: int = MAX_TOKENS,
) -> BenchResult:
    """Run a series of inference requests and collect metrics."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    gpu_before = get_gpu_stats()
    MODEL = "qwen3.6-27b-nvfp4"
    payload = {
        "model": MODEL,
        "prompt": PROMPT,
        "max_tokens": max_tokens,
        "temperature": 0.0,
    }

    success_latencies = []
    errors = []

    async with httpx.AsyncClient(timeout=120.0) as client:
        for i in range(n):
            start = time.monotonic()
            try:
                resp = await client.post(url, json=payload)
                elapsed = (time.monotonic() - start) * 1000

                if resp.status_code == 200:
                    success_latencies.append(elapsed)
                else:
                    errors.append(
                        f"Request {i}: HTTP {resp.status_code}"
                    )
            except Exception as e:
                errors.append(f"Request {i}: {type(e).__name__}: {e}")

    gpu_after = get_gpu_stats()
    successes = len(success_latencies)
    total_latency = sum(success_latencies) if success_latencies else 0.0
    first_latency = min(success_latencies) if success_latencies else 0.0
    tps = (successes * max_tokens) / (total_latency / 1000) if total_latency > 0 else 0.0

    return BenchResult(
        timestamp=ts,
        endpoint=url,
        prompt_length=len(PROMPT.split()),
        max_tokens=max_tokens,
        requests=n,
        successes=successes,
        failures=n - successes,
        success_rate=successes / n if n > 0 else 0.0,
        first_latency_ms=first_latency,
        total_latency_ms=total_latency,
        tokens_per_second=tps,
        gpu_memory_used_mib=gpu_after.get("used"),
        gpu_memory_free_mib=gpu_after.get("free"),
        gpu_memory_total_mib=gpu_after.get("total"),
        params=payload,
        errors=errors if errors else None,
    )


def main():
    import asyncio

    parser = argparse.ArgumentParser(description="Benchmark local AI inference")
    parser.add_argument(
        "--url", default=DEFAULT_URL, help="API endpoint URL"
    )
    parser.add_argument(
        "--n", type=int, default=REQUESTS, help="Number of requests"
    )
    parser.add_argument(
        "--max-tokens", type=int, default=MAX_TOKENS, help="Max tokens per request"
    )
    args = parser.parse_args()

    result = asyncio.run(
        run_benchmark(url=args.url, n=args.n, max_tokens=args.max_tokens)
    )

    print(result.summary())
    print()
    print(result.to_json())

    # Save to evidence
    import os as _os
    evidence_dir = Path(_os.environ.get("EVIDENCE_DIR", "benchmarks"))
    evidence_dir.mkdir(parents=True, exist_ok=True)

    ts = result.timestamp.replace(":", "-").replace("T", "_").replace("Z", "")
    filepath = evidence_dir / f"benchmark_{ts}.json"
    filepath.write_text(result.to_json())

    print(f"\n✓ Saved to {filepath}")
    sys.exit(0)


if __name__ == "__main__":
    main()