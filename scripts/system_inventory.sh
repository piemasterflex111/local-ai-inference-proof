#!/usr/bin/env bash
# Collect system inventory for evidence and documentation.
# Usage: ./scripts/system_inventory.sh [output_dir]
# Default output: evidence/system_inventory.txt

set -euo pipefail

OUTPUT_DIR="${1:-evidence}"
TIMESTAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUTPUT_FILE="${OUTPUT_DIR}/system_inventory_${TIMESTAMP}.txt"

mkdir -p "${OUTPUT_DIR}"

{
echo "=========================================="
echo "SYSTEM INVENTORY"
echo "Generated: ${TIMESTAMP}"
echo "=========================================="
echo ""

echo "=== OS ==="
cat /etc/os-release
echo ""

echo "=== Kernel ==="
uname -a
echo ""

echo "=== GPU ==="
nvidia-smi 2>/dev/null || echo "nvidia-smi not available"
echo ""

echo "=== GPU Details (CSV) ==="
nvidia-smi --query-gpu=name,driver_version,memory.used,memory.total,temperature.gpu --format=csv,noheader 2>/dev/null || echo "GPU query failed"
echo ""

echo "=== CUDA ==="
nvcc --version 2>/dev/null || echo "nvcc not in PATH"
echo ""

echo "=== Python ==="
python3 --version 2>/dev/null || echo "python3 not available"
python3 -c "import sys; print(sys.executable)" 2>/dev/null || true
pip3 list --format=columns 2>/dev/null | head -40 || echo "pip not available"
echo ""

echo "=== Docker ==="
docker --version 2>/dev/null || echo "docker not available"
echo ""

echo "=== Git ==="
git --version 2>/dev/null || echo "git not available"
echo ""

echo "=== systemctl ==="
systemctl --version 2>/dev/null | head -2 || echo "systemctl not available"
echo ""

echo "=== Service Status: local-ai ==="
systemctl is-active local-ai 2>/dev/null && echo "active" || echo "not found or inactive"
systemctl is-active qwen-governor 2>/dev/null && echo "active" || echo "not found or inactive"
echo ""

echo "=== VLLM Endpoint ==="
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8001/v1/models 2>/dev/null || echo "000")
echo "Status: ${HTTP_CODE}"
echo ""

echo "=== Governor Endpoint ==="
HTTP_CODE_G=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8003/v1/models 2>/dev/null || echo "000")
echo "Status: ${HTTP_CODE_G}"
echo ""

echo "=== Disk ==="
df -h / 2>/dev/null || echo "df not available"
echo ""

echo "=== Memory ==="
free -h 2>/dev/null || echo "free not available"
echo ""

echo "=== CPU ==="
nproc 2>/dev/null && echo "cores" || echo "nproc not available"
lscpu 2>/dev/null | head -12 || true
echo ""

echo "=== Docker Running Containers ==="
docker ps --format "table {{.ID}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}\t{{.Names}}" 2>/dev/null || echo "docker not running"
echo ""

echo "=== Directory Size ==="
du -sh "$PWD" 2>/dev/null || true
du -sh "$HOME/Work/local-ai-inference-proof/" 2>/dev/null || true
echo ""

echo "== END INVENTORY =="
} > "${OUTPUT_FILE}"

# Also write a symlinked current inventory for quick access
ln -sf "${OUTPUT_FILE}" "${OUTPUT_DIR}/system_inventory.txt"

echo "✓ Inventory saved to ${OUTPUT_FILE}"
cat "${OUTPUT_FILE}"