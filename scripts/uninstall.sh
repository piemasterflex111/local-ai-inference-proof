#!/usr/bin/env bash
# Uninstall the local AI inference platform.
# Usage: sudo ./scripts/uninstall.sh
set -euo pipefail

SERVICE_NAME="local-ai"
INSTALL_DIR="/opt/local-ai"

log() { echo "[uninstall] $*"; }

log "Stopping and disabling ${SERVICE_NAME}..."
systemctl stop "${SERVICE_NAME}" 2>/dev/null || log "Service not running"
systemctl disable "${SERVICE_NAME}" 2>/dev/null || log "Service not enabled"
rm -f "/etc/systemd/system/${SERVICE_NAME}.service"
systemctl daemon-reload

log "Removing environment config..."
rm -rf /etc/local-ai

log "Removing install directory..."
rm -rf "${INSTALL_DIR}"

log "Uninstall complete."