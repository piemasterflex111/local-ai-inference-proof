"""
Tests for the local AI inference platform.

Run with: pytest tests/ -v
"""

import json
from pathlib import Path

# ── System inventory tests ──────────────────────────────────────────────


def test_system_inventory_script_exists():
    """Verify the system inventory script exists and is executable."""
    script = Path("scripts/system_inventory.sh")
    assert script.exists(), "system_inventory.sh not found"
    # Check it starts with shebang and has content
    content = script.read_text()
    assert content.startswith("#!"), "Missing shebang in system_inventory.sh"
    assert len(content) > 100, "system_inventory.sh too short"


# ── Benchmark module tests ──────────────────────────────────────────────


def test_benchmark_module_imports():
    """Verify benchmark module can be imported."""
    import src.benchmark as bench
    assert hasattr(bench, "run_benchmark")
    assert hasattr(bench, "BenchResult")
    assert hasattr(bench, "get_gpu_stats")


def test_benchresult_serialization():
    """BenchResult can be serialized to JSON and parsed back."""
    import src.benchmark as bench

    result = bench.BenchResult(
        timestamp="2026-07-17T00:00:00Z",
        endpoint="http://127.0.0.1:8003/v1/completions",
        prompt_length=5,
        max_tokens=50,
        requests=10,
        successes=10,
        failures=0,
        success_rate=1.0,
        first_latency_ms=1500.0,
        total_latency_ms=15000.0,
        tokens_per_second=33.3,
        gpu_memory_used_mib=15000,
        gpu_memory_free_mib=8000,
        gpu_memory_total_mib=24000,
    )

    json_str = result.to_json()
    parsed = json.loads(json_str)
    assert parsed["success_rate"] == 1.0
    assert parsed["successes"] == 10
    assert parsed["tokens_per_second"] == 33.3


def test_benchresult_summary_output():
    """Summary returns readable text with expected fields."""
    import src.benchmark as bench

    result = bench.BenchResult(
        timestamp="2026-07-17T00:00:00Z",
        endpoint="http://127.0.0.1:8003/v1/completions",
        prompt_length=5,
        max_tokens=50,
        requests=3,
        successes=2,
        failures=1,
        success_rate=2 / 3,
        first_latency_ms=1000.0,
        total_latency_ms=4000.0,
        tokens_per_second=37.5,
        gpu_memory_used_mib=15000,
        gpu_memory_total_mib=24000,
    )

    summary = result.summary()
    assert "BENCHMARK SUMMARY" in summary
    assert "37.5" in summary
    assert "15000" in summary


# ── Health check module tests ───────────────────────────────────────────


def test_health_module_imports():
    """Verify health check module can be imported."""
    import src.health_check as hc
    assert hasattr(hc, "run_full_health")
    assert hasattr(hc, "HealthReport")
    assert hasattr(hc, "check_process")


def test_healthreport_serialization():
    """HealthReport serializes to JSON and parses back."""
    import src.health_check as hc

    report = hc.HealthReport(
        timestamp="2026-07-17T00:00:00Z",
        level1_process="PASS: Docker container running",
        level2_api="PASS: API 200, models=['qwen']",
        level3_inference="PASS: Generated 10 tokens",
        api_latency_ms=100.0,
        inference_latency_ms=1500.0,
        tokens_per_second=6.67,
        gpu_memory_mi_b=15000,
        overall="HEALTHY",
    )

    json_str = report.to_json()
    parsed = json.loads(json_str)
    assert parsed["overall"] == "HEALTHY"
    assert parsed["tokens_per_second"] == 6.67


# ── Scripts existence tests ─────────────────────────────────────────────


def test_install_script_exists():
    """Install script exists and has proper structure."""
    script = Path("scripts/install.sh")
    assert script.exists(), "install.sh not found"
    content = script.read_text()
    assert "Pre-flight" in content, "Missing pre-flight section"
    assert "systemd" in content, "Missing systemd installation"


def test_verify_gpu_script_exists():
    """GPU verification script exists."""
    script = Path("scripts/verify_gpu.sh")
    assert script.exists()
    content = script.read_text()
    assert "nvidia-smi" in content


def test_collect_evidence_script_exists():
    """Evidence collection script exists."""
    script = Path("scripts/collect_evidence.sh")
    assert script.exists()
    content = script.read_text()
    assert "health_check" in content
    assert "benchmark" in content