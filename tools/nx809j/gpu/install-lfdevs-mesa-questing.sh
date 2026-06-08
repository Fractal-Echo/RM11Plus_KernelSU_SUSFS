#!/usr/bin/env sh
set -eu

PKG_NAME="mesa-for-android-container_26.2.0-devel-20260511_ubuntu_questing_arm64.tar.gz"
PKG_URL="https://github.com/lfdevs/mesa-for-android-container/releases/download/mesa-26.2.0-devel-20260511/${PKG_NAME}"
PKG_SHA256="f9848fdb3527c206a0937aa7b239b38e0eb81e2beec3f7df3453c99cb539dd68"
WORK_DIR="/root/lfdevs_mesa"
PKG_PATH="${WORK_DIR}/${PKG_NAME}"
BACKUP_PATH="${WORK_DIR}/mesa-ubuntu-original-$(date +%Y%m%d-%H%M%S).tar.gz"

if [ "$(id -u)" != "0" ]; then
  echo "Run this script as root inside the DroidSpaces Ubuntu container." >&2
  exit 1
fi

echo "WARNING: this Mesa build is experimental on NX809J DroidSpaces."
echo "It can make Termux:X11/Plasma turn black. Keep ADB root available for recovery."
echo "Press Ctrl+C within 8 seconds to stop."
sleep 8

. /etc/os-release
if [ "${ID:-}" != "ubuntu" ] || [ "${VERSION_CODENAME:-}" != "questing" ]; then
  echo "This package is only for Ubuntu questing arm64. Detected: ${PRETTY_NAME:-unknown}" >&2
  exit 1
fi

mkdir -p "$WORK_DIR"

if [ ! -f "$PKG_PATH" ]; then
  curl -L -o "$PKG_PATH" "$PKG_URL"
fi

echo "${PKG_SHA256}  ${PKG_PATH}" | sha256sum -c -

tar -czf "$BACKUP_PATH" \
  /usr/lib/aarch64-linux-gnu/libGLX_mesa.so* \
  /usr/lib/aarch64-linux-gnu/libEGL_mesa.so* \
  /usr/lib/aarch64-linux-gnu/libgbm.so* \
  /usr/lib/aarch64-linux-gnu/libgallium-* \
  /usr/lib/aarch64-linux-gnu/dri \
  /usr/lib/aarch64-linux-gnu/gbm \
  /usr/share/vulkan/icd.d \
  /usr/share/glvnd/egl_vendor.d

tar -xzf "$PKG_PATH" -C /
ldconfig

echo "Installed ${PKG_NAME}"
echo "Backup: ${BACKUP_PATH}"
echo "Restart DroidSpaces, then validate with: glxinfo -B"
