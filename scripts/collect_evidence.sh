#!/usr/bin/env bash
# Collect evidence: run system inventory, health check, and quick benchmark.
# Usage: ./scripts/collect_evidence.sh
set -euo pipefail

SRC_DIR="$(cd "$(dirname "$0")/.." && pwd)"
EVIDENCE_DIR="${SRC_DIR}/evidence"
mkdir -p "${EVIDENCE_DIR}"

echo "=== Collecting Evidence ==="

# 1. System inventory
echo ""
echo "--- System Inventory ---"
bash "${SRC_DIR}/scripts/system_inventory.sh" "${EVIDENCE_DIR}"

# 2. GPU verification
echo ""
echo "--- GPU Verification ---"
bash "${SRC_DIR}/scripts/verify_gpu.sh" || echo "GPU verification had warnings"

# 3. Health check (requires running service)
echo ""
echo "--- Health Check ---"
cd "${SRC_DIR}"
python3 src/health_check.py || echo "Health check failed (service may be down)"

# 4. Benchmark (optional, only if service is up)
echo ""
echo "--- Benchmark (3 requests) ---"
python3 src/benchmark.py --n 3 --max-tokens 20 || echo "Benchmark failed (service may be down)"

echo ""
echo "=== Evidence Collection Complete ==="
echo "Evidence directory: ${EVIDENCE_DIR}"