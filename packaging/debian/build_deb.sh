#!/usr/bin/env bash
# Build a Debian package for the local AI inference platform.
# Usage: cd packaging && bash build_deb.sh
set -euo pipefail

PACKAGE="local-ai-platform"
VERSION="0.1.0"
ARCH="amd64"
BUILD_DIR="build/${PACKAGE}_${VERSION}_${ARCH}"
INSTALL_DIR="${BUILD_DIR}/opt/local-ai"
SRC_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Building ${PACKAGE}_${VERSION}_${ARCH}.deb ==="

# Clean previous build
rm -rf "${BUILD_DIR}"
rm -f ../${PACKAGE}_${VERSION}_${ARCH}.deb

# Create package directory structure
mkdir -p "${INSTALL_DIR}"
mkdir -p "${BUILD_DIR}/etc/local-ai"
mkdir -p "${BUILD_DIR}/etc/systemd/system"
mkdir -p "${BUILD_DIR}/usr/bin"

# Copy application files
cp -r "${SRC_DIR}/src" "${INSTALL_DIR}/"
cp -r "${SRC_DIR}/scripts" "${INSTALL_DIR}/"
cp "${SRC_DIR}/pyproject.toml" "${INSTALL_DIR}/"
cp "${SRC_DIR}/requirements.txt" "${INSTALL_DIR}/"
cp "${SRC_DIR}/docker-compose.yml" "${INSTALL_DIR}/"
cp "${SRC_DIR}/Dockerfile" "${INSTALL_DIR}/" 2>/dev/null || true
cp "${SRC_DIR}/README.md" "${INSTALL_DIR}/"

# Copy systemd files
cp "${SRC_DIR}/systemd/local-ai.service" \
   "${BUILD_DIR}/etc/systemd/system/"
cp "${SRC_DIR}/systemd/local-ai.env.conf" \
   "${BUILD_DIR}/etc/local-ai/env.conf"

# Create wrapper scripts
cat > "${BUILD_DIR}/usr/bin/local-ai-health" << 'WRAPPER'
#!/usr/bin/env bash
exec python3 /opt/local-ai/src/health_check.py "$@"
WRAPPER
chmod +x "${BUILD_DIR}/usr/bin/local-ai-health"

cat > "${BUILD_DIR}/usr/bin/local-ai-benchmark" << 'WRAPPER'
#!/usr/bin/env bash
exec python3 /opt/local-ai/src/benchmark.py "$@"
WRAPPER
chmod +x "${BUILD_DIR}/usr/bin/local-ai-benchmark"

# Create post-install script
mkdir -p "${BUILD_DIR}/DEBIAN"
cat > "${BUILD_DIR}/DEBIAN/postinst" << 'POSTINST'
#!/bin/bash
systemctl daemon-reload
systemctl enable local-ai.service 2>/dev/null || true
echo "local-ai-platform ${VERSION} installed."
echo "Start the service with: sudo systemctl start local-ai"
POSTINST
chmod +x "${BUILD_DIR}/DEBIAN/postinst"

# Create post-remove script
cat > "${BUILD_DIR}/DEBIAN/postrm" << 'POSTRM'
#!/bin/bash
systemctl daemon-reload
echo "local-ai-platform removed."
POSTRM
chmod +x "${BUILD_DIR}/DEBIAN/postrm"

# Create control file
cat > "${BUILD_DIR}/DEBIAN/control" << CONTROL
Package: ${PACKAGE}
Version: ${VERSION}
Section: science
Priority: optional
Architecture: ${ARCH}
Depends: python3-all, python3-httpx, docker.io, nvidia-driver
Maintainer: Payam Adloo <payam.adloo@example.com>
Description: Local AI Inference Platform
 Deploy and operate a local LLM inference service on Linux
 using vLLM and Qwen models on NVIDIA GPU hardware.
 Includes health checks, benchmarks, and automated testing.
CONTROL

# Build the .deb package
echo "Creating .deb package..."
dpkg-deb --build --root-owner-group "${BUILD_DIR}" \
    "../${PACKAGE}_${VERSION}_${ARCH}.deb"

echo ""
echo "Build complete: ${SRC_DIR}/${PACKAGE}_${VERSION}_${ARCH}.deb"
echo ""
echo "Install with:"
echo "  sudo apt install ../${PACKAGE}_${VERSION}_${ARCH}.deb"
echo ""
echo "Uninstall with:"
echo "  sudo apt remove ${PACKAGE}"