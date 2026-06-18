#!/usr/bin/env python3
"""Package the vendored Droidspaces boot module for KernelSU/Magisk/APatch."""

from __future__ import annotations

import argparse
import hashlib
import os
import stat
import zipfile
from pathlib import Path


CUSTOMIZE_SH = """#!/system/bin/sh
DROIDSPACE_DIR=/data/local/Droidspaces

ui_print "- Droidspaces Daemon & Init module"
ui_print "- Installing vendored Droidspaces payload"

mkdir -p "$DROIDSPACE_DIR/bin" "$DROIDSPACE_DIR/Logs" "$DROIDSPACE_DIR/Containers" 2>/dev/null

for file in droidspaces busybox magiskpolicy; do
  if [ -f "$MODPATH/bin/$file" ]; then
    cp -f "$MODPATH/bin/$file" "$DROIDSPACE_DIR/bin/$file" 2>/dev/null
  fi
done

chmod 755 "$DROIDSPACE_DIR/bin/droidspaces" "$DROIDSPACE_DIR/bin/busybox" "$DROIDSPACE_DIR/bin/magiskpolicy" 2>/dev/null
chown root:root "$DROIDSPACE_DIR/bin/droidspaces" "$DROIDSPACE_DIR/bin/busybox" "$DROIDSPACE_DIR/bin/magiskpolicy" 2>/dev/null
chcon u:object_r:droidspacesd_exec:s0 "$DROIDSPACE_DIR/bin/droidspaces" 2>/dev/null

set_perm "$MODPATH/post-fs-data.sh" 0 0 0755
set_perm "$MODPATH/service.sh" 0 0 0755
set_perm_recursive "$MODPATH/bin" 0 0 0755 0755

ui_print "- Droidspaces payload installed to /data/local/Droidspaces"
"""


EXECUTABLES = {
    "customize.sh",
    "post-fs-data.sh",
    "service.sh",
    "bin/busybox",
    "bin/droidspaces",
    "bin/magiskpolicy",
}

REQUIRED = {
    "module.prop",
    "post-fs-data.sh",
    "service.sh",
    "sepolicy.rule",
    "bin/busybox",
    "bin/droidspaces",
    "bin/magiskpolicy",
}


def add_bytes(zout: zipfile.ZipFile, arcname: str, data: bytes, mode: int) -> None:
    info = zipfile.ZipInfo(arcname)
    info.external_attr = (mode & 0xFFFF) << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    zout.writestr(info, data)


def add_file(zout: zipfile.ZipFile, root: Path, file_path: Path) -> None:
    arcname = file_path.relative_to(root).as_posix()
    mode = 0o755 if arcname in EXECUTABLES else 0o644
    info = zipfile.ZipInfo(arcname)
    info.external_attr = (stat.S_IFREG | mode) << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    with file_path.open("rb") as src:
        zout.writestr(info, src.read())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as src:
        for chunk in iter(lambda: src.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--module-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    module_dir = args.module_dir.resolve()
    output = args.output.resolve()

    missing = [name for name in sorted(REQUIRED) if not (module_dir / name).is_file()]
    if missing:
        raise SystemExit(f"Missing required Droidspaces module files: {', '.join(missing)}")

    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()

    with zipfile.ZipFile(output, "w") as zout:
        add_bytes(zout, "customize.sh", CUSTOMIZE_SH.encode("utf-8"), stat.S_IFREG | 0o755)
        for base, _, files in os.walk(module_dir):
            for name in sorted(files):
                add_file(zout, module_dir, Path(base) / name)

    print(f"module_zip={output.name}")
    print(f"module_sha256={sha256(output)}")
    print(f"module_size={output.stat().st_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
