#!/usr/bin/env sh
set -eu

if [ "$(id -u)" != "0" ]; then
  echo "Run this script as root inside the DroidSpaces Ubuntu container." >&2
  exit 1
fi

DISABLED_DIR="/root/lfdevs_mesa/disabled-icd"
mkdir -p "$DISABLED_DIR"

for icd in \
  /usr/share/vulkan/icd.d/freedreno_icd.aarch64.json \
  /usr/share/vulkan/icd.d/freedreno_icd.json
do
  if [ -e "$icd" ]; then
    mv "$icd" "$DISABLED_DIR/"
  fi
done

ldconfig

cat <<'EOF'
Freedreno Vulkan ICD files are disabled for the Ubuntu container.

Also keep the Android-side DroidSpaces container config in software mode:
  enable_gpu_mode=0
  enable_virgl=0

Restart DroidSpaces, then validate with:
  glxinfo -B

Expected stable renderer:
  OpenGL renderer string: llvmpipe
  Accelerated: no
EOF
