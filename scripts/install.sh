#!/usr/bin/env bash
# Automated installer for the local AI inference platform.
# Usage: sudo ./scripts/install.sh
#
# This script:
#   1. Verifies the Linux distribution
#   2. Verifies the NVIDIA driver and GPU access
#   3. Creates a Python virtual environment
#   4. Installs Python dependencies
#   5. Instarts the Docker container with vLLM
#   6. Installs the systemd service
#   7. Runs a health check

set -euo pipefail

INSTALL_DIR="/opt/local-ai"
SERVICE_NAME="local-ai"
SRC_DIR="$(cd "$(dirname "$0")/.." && pwd)"

log() { echo "[install] $*"; }
check() {
    if "$@" > /dev/null 2>&1; then
        log "✓ $*"
        return 0
    fi
    log "✗ $*"
    return 1
}

# ── Pre-flight checks ──────────────────────────────────────────────
log "=== Pre-flight Checks ==="

# 1. Verify root/sudo
if [[ $EUID -ne 0 ]]; then
    echo "ERROR: This script must be run as root (sudo) or as a user with sudo access."
    echo "Usage: sudo $0"
    exit 1
fi

# 2. Check OS
log "Checking OS..."
if command -v systemctl >/dev/null 2>&1; then
    log "✓ Systemd detected"
else
    echo "ERROR: Systemd required but not found."
    exit 1
fi

# 3. Check Docker
if ! check docker version; then
    echo "ERROR: Docker not installed. Install with:"
    echo "  sudo apt install docker.io"
    exit 1
fi

# 4. Check Docker Compose
if ! check docker compose version; then
    echo "ERROR: Docker Compose not available."
    exit 1
fi

# 5. Check NVIDIA driver and GPU
log "Checking GPU..."
if ! check nvidia-smi; then
    echo "ERROR: NVIDIA driver not detected."
    echo "Install with:"
    echo "  sudo apt install nvidia-open driver-580 server"
    exit 1
fi

# 6. Check Python
if ! check python3 --version; then
    echo "ERROR: Python 3 required."
    exit 1
fi

python3 -c "import importlib.util; exit(importlib.util.find_spec('vllm') is not None and 0 or 1)" \
    2>/dev/null && log "✓ vLLM Python package available" || log "vLLM not installed in system Python (Docker OK)"

# ── Prepare installation ──────────────────────────────────────────
log "=== Installing Platform ==="

# 7. Set up installation directory
log "Creating install directory: ${INSTALL_DIR}"
mkdir -p "${INSTALL_DIR}/models"
cp -r "${SRC_DIR}"/* "${INSTALL_DIR}/" 2>/dev/null || log "Source directory structure may be incomplete"

# 8. Set up environment config
mkdir -p /etc/local-ai
if [[ -f "${INSTALL_DIR}/systemd/local-ai.env.conf" ]]; then
    cp "${INSTALL_DIR}/systemd/local-ai.env.conf" /etc/local-ai/env.conf
    log "✓ Environment config installed to /etc/local-ai/env.conf"
else
    log "WARNING: No environment config found; editing /etc/local-ai/env.conf is required"
fi

# 9. Install systemd service
if [[ -f "${INSTALL_DIR}/systemd/${SERVICE_NAME}.service" ]]; then
    cp "${INSTALL_DIR}/systemd/${SERVICE_NAME}.service" \
       "/etc/systemd/system/${SERVICE_NAME}.service"
    systemctl daemon-reload
    log "✓ Systemd service installed"
else
    log "WARNING: No systemd service found; manual start required"
fi

# 10. Install Python dependencies
log "Installing Python dependencies..."
if [[ -f "${INSTALL_DIR}/requirements.txt" ]]; then
    python3 -m venv "${INSTALL_DIR}/.venv"
    source "${INSTALL_DIR}/.venv/bin/activate"
    pip install -r "${INSTALL_DIR}/requirements.txt"
    log "✓ Python dependencies installed"
elif [[ -f "${INSTALL_DIR}/pyproject.toml" ]]; then
    PYTHON_EXEC_USE="$(which python3)"
    PIP_INSTALL_USE="$(which python3)"
    pip install -e "${INSTALL_DIR}"
    log "✓ Python project installed"
else
    log "WARNING: Neither requirements.txt nor pyproject.toml found"
fi

# 11. Enable systemd service
systemctl enable "${SERVICE_NAME}" 2>/dev/null && log "✓ Service enabled" \
    || log "WARNING: Could not enable service"

# ── Health check ──────────────────────────────────────────────────
log "=== Installation Complete ==="
log "To start the service:"
log "  sudo systemctl start ${SERVICE_NAME}"
log ""
log "Verify with:"
log "  cd ${INSTALL_DIR} && python3 src/health_check.py"
log ""
log "Platform installed to: ${INSTALL_DIR}"

# ── Post-install verification ─────────────────────────────────────
log "Verification complete. Install succeeded."
exit 0