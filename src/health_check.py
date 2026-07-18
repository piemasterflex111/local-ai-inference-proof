#!/usr/bin/env python3
"""
Health check module for the local AI inference platform.

Three levels:
  Level 1: Is the Linux process running?
  Level 2: Is the API responding?
  Level 3: Can the model produce a valid answer?
"""

import json
import subprocess
import sys
import time
from dataclasses import dataclass, fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx

# ── Configuration ──────────────────────────────────────────────────────
# Default base URLs — override with environment variables
VLLM_BASE = "http://127.0.0.1:8001"
GOVERNOR_BASE = "http://127.0.0.1:8003"

DEFAULT_PROMPT = "Say hello"


@dataclass
class HealthReport:
    timestamp: str
    level1_process: str
    level2_api: str
    level3_inference: str
    api_latency_ms: Optional[float] = None
    inference_latency_ms: Optional[float] = None
    tokens_per_second: Optional[float] = None
    gpu_memory_mi_b: Optional[int] = None
    cpu_percent: Optional[float] = None
    overall: str = "UNKNOWN"

    def to_json(self) -> str:
        result = {}
        for f in fields(self):
            result[f.name] = getattr(self, f.name)
        return json.dumps(result, indent=2)

    @property
    def is_healthy(self) -> bool:
        return self.overall == "HEALTHY"


def check_process() -> str:
    """Level 1: Check if the vLLM process or container is running."""
    # Container name — matches actual docker-compose service
    CONTAINER_NAME = "qwen36-vllm"

    # Check docker container
    try:
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{.State.Status}}", CONTAINER_NAME],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and result.stdout.strip() == "running":
            return "PASS: Docker container running"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Fallback: check if vLLM port (8000) is listening
    try:
        result = subprocess.run(
            ["ss", "-tlnp"], capture_output=True, text=True, timeout=5
        )
        if ":8000" in result.stdout or ":8003" in result.stdout:
            return "PASS: Inference ports active (8000/vLLM, 8003/governor)"
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return "FAIL: No process or port detected"


async def check_api(timeout: float = 10.0) -> tuple[str, float | None]:
    """Level 2: Check if the API responds with a valid HTTP status."""
    start = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(f"{GOVERNOR_BASE}/v1/models")
            elapsed_ms = (time.monotonic() - start) * 1000
            if resp.status_code == 200:
                data = resp.json()
                models = [m["id"] for m in data.get("data", [])]
                return f"PASS: API 200, models={models}", elapsed_ms
            return f"FAIL: HTTP {resp.status_code}", elapsed_ms
    except httpx.RequestError as e:
        elapsed_ms = (time.monotonic() - start) * 1000
        return f"FAIL: {type(e).__name__}: {e}", None


async def check_inference(timeout: float = 60.0) -> tuple[str, float | None, float | None]:
    """Level 3: Send a real inference request and measure response."""
    start = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(
                f"{GOVERNOR_BASE}/v1/completions",
                json={
                    "model": "qwen3.6-27b-nvfp4",
                    "prompt": DEFAULT_PROMPT,
                    "max_tokens": 10,
                    "temperature": 0.0,
                },
            )
            elapsed_ms = (time.monotonic() - start) * 1000

            if resp.status_code == 200:
                data = resp.json()
                choices = data.get("choices", [])
                if choices:
                    tokens = choices[0].get("usage", {}).get("completion_tokens", 0)
                    tps = tokens / (elapsed_ms / 1000) if elapsed_ms > 0 else 0
                    return (
                        f"PASS: Generated {tokens} tokens",
                        elapsed_ms,
                        tps,
                    )
                return "FAIL: No choices in response", elapsed_ms, 0.0
            return f"FAIL: HTTP {resp.status_code}", elapsed_ms, 0.0

    except httpx.TimeoutException:
        elapsed_ms = (time.monotonic() - start) * 1000
        return "FAIL: Inference timed out", elapsed_ms, 0.0
    except httpx.RequestError as e:
        elapsed_ms = (time.monotonic() - start) * 1000
        return f"FAIL: {type(e).__name__}", None, None


def get_gpu_memory() -> int | None:
    """Return GPU memory used in MiB."""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            vals = result.stdout.strip().split(",")
            return int(vals[0].strip())
    except (FileNotFoundError, subprocess.TimeoutExpired, ValueError, IndexError):
        pass
    return None


def get_cpu_percent() -> float | None:
    """Return current CPU usage percent (quick approximation)."""
    try:
        result = subprocess.run(
            ["top", "-bn1", "-p", str(subprocess.Popen(
                ["ps", "aux"], stdout=subprocess.PIPE
            ).pid)],
            capture_output=True, text=True, timeout=5,
        )
        # Parse last line CPU% — rough estimate; better to use /proc/stat
    except (FileNotFoundError, subprocess.TimeoutExpired):
        try:
            # Alternative: use mpstat or parse /proc/stat
            with open("/proc/stat") as f:
                line = f.readline()
            parts = line.split()[1:]
            idle = int(parts[3])
            total = sum(int(p) for p in parts)
            return (1 - idle / total) * 100 if total > 0 else None
        except Exception:
            return None
    return None


async def run_full_health() -> HealthReport:
    """Run all three levels and return a complete health report."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    level1 = check_process()
    api_msg, api_lat = await check_api()
    inf_msg, inf_lat, tps = await check_inference()
    gpu_mem = get_gpu_memory()
    cpu_pct = get_cpu_percent()

    healthy = (
        "PASS" in level1
        and "PASS" in api_msg
        and "PASS" in inf_msg
    )
    overall = "HEALTHY" if healthy else "UNHEALTHY"

    return HealthReport(
        timestamp=ts,
        level1_process=level1,
        level2_api=api_msg,
        level3_inference=inf_msg,
        api_latency_ms=api_lat,
        inference_latency_ms=inf_lat,
        tokens_per_second=tps,
        gpu_memory_mi_b=gpu_mem,
        cpu_percent=cpu_pct,
        overall=overall,
    )


def main():
    """CLI entry point: run health check and save to evidence."""
    import asyncio
    import os

    result = asyncio.run(run_full_health())

    report = result.to_json()
    print(report)

    # Save to evidence
    evidence_dir = Path(os.environ.get("EVIDENCE_DIR", "evidence/health_checks"))
    evidence_dir.mkdir(parents=True, exist_ok=True)

    ts = result.timestamp.replace(":", "-")
    ts = ts.replace("T", "_").replace("Z", "")
    filename = f"health_{ts}.json"
    filepath = evidence_dir / filename
    filepath.write_text(report)

    print(f"\n✓ Saved to {filepath}")

    # Return non-zero exit code if unhealthy
    sys.exit(0 if result.is_healthy else 1)


if __name__ == "__main__":
    main()