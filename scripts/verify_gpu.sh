#!/usr/bin/env bash
# Verify GPU availability and NVIDIA stack.
# Usage: ./scripts/verify_gpu.sh
set -euo pipefail

log() { echo "[gpu-verify] $*"; }
FAIL_COUNT=0

check() {
    if "$@" > /dev/null 2>&1; then
        log "✓ $*"
    else
        log "✗ $*"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
}

echo "=== GPU Verification ==="

# 1. Check nvidia-smi access
check nvidia-smi

# 2. Check device access
if [[ -e /dev/nvidia0 ]]; then
    log "✓ /dev/nvidia0 exists"
else
    log "✗ /dev/nvidia0 missing"
    FAIL_COUNT=$((FAIL_COUNT + 1))
fi

# 3. Check NVIDIA driver module
if modinfo nvidia >/dev/null 2>&1; then
    log "✓ NVIDIA kernel module loaded"
else
    log "✗ NVIDIA kernel module not found"
    FAIL_COUNT=$((FAIL_COUNT + 1))
fi

# 4. GPU details
echo ""
echo "=== GPU Details ==="
nvidia-smi --query-gpu=name,driver_version,memory.used,memory.total --format=csv 2>/dev/null || \
    echo "nvidia-smi query failed"

# 5. CUDA toolkit
if command -v nvcc >/dev/null 2>&1; then
    NVCC_VER=$(nvcc --version | grep -oP 'release \K[0-9.]+')
    log "✓ CUDA ${NVCC_VER} available"
else
    log "WARNING: nvcc not in PATH"
fi

echo ""
if [[ $FAIL_COUNT -eq 0 ]]; then
    log "GPU verification: ALL CHECKS PASSED"
    exit 0
else
    log "GPU verification: ${FAIL_COUNT} CHECK(S) FAILED"
    exit 1
fi