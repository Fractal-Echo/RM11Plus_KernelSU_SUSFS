#!/usr/bin/env python3
"""Package Droidspaces Daemon & Init as a KernelSU/Magisk module zip."""

from __future__ import annotations

import argparse
import hashlib
import os
import stat
import zipfile
from pathlib import Path


EXECUTABLES = {
    "customize.sh",
    "post-fs-data.sh",
    "service.sh",
    "uninstall.sh",
    "bin/busybox",
    "bin/droidspaces",
    "bin/magiskpolicy",
}


CUSTOMIZE_SH = """#!/system/bin/sh

SKIPUNZIP=0
DROIDSPACE_DIR=/data/local/Droidspaces

ui_print "- Droidspaces Daemon & Init module"
ui_print "- Preparing /data/local/Droidspaces"

mkdir -p "$DROIDSPACE_DIR/bin" "$DROIDSPACE_DIR/Logs" "$DROIDSPACE_DIR/Containers" 2>/dev/null

if [ -d "$MODPATH/bin" ]; then
  cp -f "$MODPATH/bin/droidspaces" "$DROIDSPACE_DIR/bin/droidspaces" 2>/dev/null
  cp -f "$MODPATH/bin/busybox" "$DROIDSPACE_DIR/bin/busybox" 2>/dev/null
  cp -f "$MODPATH/bin/magiskpolicy" "$DROIDSPACE_DIR/bin/magiskpolicy" 2>/dev/null
fi

chmod 755 "$DROIDSPACE_DIR/bin" 2>/dev/null
chmod 755 "$DROIDSPACE_DIR/bin/droidspaces" "$DROIDSPACE_DIR/bin/busybox" "$DROIDSPACE_DIR/bin/magiskpolicy" 2>/dev/null
chown root:root "$DROIDSPACE_DIR/bin/droidspaces" "$DROIDSPACE_DIR/bin/busybox" "$DROIDSPACE_DIR/bin/magiskpolicy" 2>/dev/null

echo 1 > "$DROIDSPACE_DIR/.daemon_mode" 2>/dev/null
chmod 644 "$DROIDSPACE_DIR/.daemon_mode" 2>/dev/null
chcon u:object_r:droidspacesd_exec:s0 "$DROIDSPACE_DIR/bin/droidspaces" 2>/dev/null

set_perm_recursive "$MODPATH" 0 0 0755 0644
set_perm "$MODPATH/post-fs-data.sh" 0 0 0755
set_perm "$MODPATH/service.sh" 0 0 0755
set_perm "$MODPATH/bin/droidspaces" 0 0 0755
set_perm "$MODPATH/bin/busybox" 0 0 0755
set_perm "$MODPATH/bin/magiskpolicy" 0 0 0755

ui_print "- Done. Reboot after installing."
"""

UNINSTALL_SH = """#!/system/bin/sh

pkill -f "droidspaces daemon" 2>/dev/null
rm -f /data/local/Droidspaces/.dmesg_pid 2>/dev/null
"""


ENSURE_PAYLOAD_SH = r"""

# NX809J payload guard: keep /data/local/Droidspaces populated even if the
# installer hook did not run or the directory was removed between boots.
MODDIR="${0%/*}"
DROIDSPACE_DIR=/data/local/Droidspaces
DROIDSPACE_LOG="$DROIDSPACE_DIR/Logs/module-setup.log"

mkdir -p "$DROIDSPACE_DIR/bin" "$DROIDSPACE_DIR/Logs" "$DROIDSPACE_DIR/Containers" 2>/dev/null

log_droidspaces_setup() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') $*" >> "$DROIDSPACE_LOG" 2>/dev/null
}

ensure_droidspaces_payload() {
  for name in droidspaces busybox magiskpolicy; do
    if [ -f "$MODDIR/bin/$name" ]; then
      cp -f "$MODDIR/bin/$name" "$DROIDSPACE_DIR/bin/$name" 2>/dev/null
      chmod 755 "$DROIDSPACE_DIR/bin/$name" 2>/dev/null
      chown root:root "$DROIDSPACE_DIR/bin/$name" 2>/dev/null
    else
      log_droidspaces_setup "missing module payload: $MODDIR/bin/$name"
    fi
  done

  chmod 755 "$DROIDSPACE_DIR" "$DROIDSPACE_DIR/bin" "$DROIDSPACE_DIR/Logs" "$DROIDSPACE_DIR/Containers" 2>/dev/null
  echo 1 > "$DROIDSPACE_DIR/.daemon_mode" 2>/dev/null
  chmod 644 "$DROIDSPACE_DIR/.daemon_mode" 2>/dev/null
  chcon u:object_r:droidspacesd_exec:s0 "$DROIDSPACE_DIR/bin/droidspaces" 2>/dev/null

  if [ -x "$DROIDSPACE_DIR/bin/droidspaces" ]; then
    log_droidspaces_setup "payload ready"
  else
    log_droidspaces_setup "payload not executable after setup"
  fi
}

ensure_droidspaces_payload
"""


def inject_after_shebang(data: bytes, injection: bytes) -> bytes:
    if data.startswith(b"#!"):
        first_newline = data.find(b"\n")
        if first_newline != -1:
            return data[: first_newline + 1] + injection + data[first_newline + 1 :]
    return injection + data


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def add_file(zout: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.create_system = 3
    mode = stat.S_IFREG | (0o755 if name in EXECUTABLES else 0o644)
    info.external_attr = (mode & 0xFFFF) << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    zout.writestr(info, data)


def add_dir(zout: zipfile.ZipFile, name: str) -> None:
    info = zipfile.ZipInfo(name.rstrip("/") + "/", date_time=(1980, 1, 1, 0, 0, 0))
    info.create_system = 3
    info.external_attr = ((stat.S_IFDIR | 0o755) & 0xFFFF) << 16
    zout.writestr(info, b"")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--boot-module-dir", required=True, type=Path)
    parser.add_argument("--payload-bin-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    required = ["module.prop", "post-fs-data.sh", "service.sh", "sepolicy.rule"]
    payload = ["busybox", "droidspaces", "magiskpolicy"]
    args.output.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(args.output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zout:
        add_file(zout, "customize.sh", CUSTOMIZE_SH.encode())
        for filename in required:
            data = (args.boot_module_dir / filename).read_bytes()
            if filename == "post-fs-data.sh":
                data = inject_after_shebang(data, ENSURE_PAYLOAD_SH.encode())
            elif filename == "service.sh":
                data += ENSURE_PAYLOAD_SH.encode()
            add_file(zout, filename, data)
        add_file(zout, "uninstall.sh", UNINSTALL_SH.encode())
        add_dir(zout, "bin")
        for filename in payload:
            add_file(zout, f"bin/{filename}", (args.payload_bin_dir / filename).read_bytes())

    print(f"zip={args.output}")
    print(f"zip_size={args.output.stat().st_size}")
    print(f"zip_sha256={sha256(args.output)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
