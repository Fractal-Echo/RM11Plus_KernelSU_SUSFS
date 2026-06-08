# RedMagic 11 Pro NX809J DroidSpaces GPU

This note documents the tested GPU path for RedMagic 11 Pro NX809J / Adreno 840 inside the DroidSpaces Ubuntu container.

## Tested Device State

- Device: RedMagic 11 Pro NX809J
- Android: 16
- Container: DroidSpaces Ubuntu 25.10 `questing` arm64
- Display: Termux:X11 `:5`
- GPU: Qualcomm Adreno 840
- Mesa package tested: `mesa-for-android-container_26.2.0-devel-20260511_ubuntu_questing_arm64.tar.gz`
- Package source: <https://github.com/lfdevs/mesa-for-android-container/releases/tag/mesa-26.2.0-devel-20260511>
- SHA256: `f9848fdb3527c206a0937aa7b239b38e0eb81e2beec3f7df3453c99cb539dd68`

The upstream release notes mention a fix for patched Turnip on Adreno 830/840. This is the first package that matched the device, the Ubuntu release, and the observed failure mode.

## Why This Was Needed

Ubuntu's stock Mesa 25.2.8 detected software rendering by default, and forcing KGSL globally made the Termux:X11 desktop turn black during browser/video use. After installing the lfdevs Mesa package, default GL changed to Zink over Turnip:

```text
OpenGL renderer string: zink Vulkan 1.4(Adreno (TM) 840 (MESA_TURNIP))
OpenGL version string: 4.6 Mesa 26.2.0-devel
```

Vulkan also detected Turnip:

```text
deviceName = Adreno (TM) 840
driverName = turnip Mesa driver
driverInfo = Mesa 26.2.0-devel
```

## Current Recommendation

Do not enable this package for the main Plasma session yet. On NX809J it passed `glxinfo`, `vulkaninfo`, and a short `glxgears` run, but the real Termux:X11 desktop later fell back to a black screen.

The device is currently kept in software rendering mode for stability.

The stable recovery state is:

- `enable_gpu_mode=0`
- `enable_virgl=0`
- Freedreno Vulkan ICD JSON files moved out of `/usr/share/vulkan/icd.d`
- OpenGL renderer: `llvmpipe`
- `Accelerated: no`

The current validation output should look like:

```text
OpenGL renderer string: llvmpipe (LLVM 20.1.8, 128 bits)
Accelerated: no
```

The package is still useful for isolated driver testing, but should not be used as the default browser/desktop path until the Termux:X11/Plasma crash is understood.

## Experimental Install

Run the helper from inside the DroidSpaces Ubuntu container as root only for isolated testing:

```sh
tools/nx809j/gpu/install-lfdevs-mesa-questing.sh
```

Or manually:

```sh
mkdir -p /root/lfdevs_mesa
curl -L -o /root/lfdevs_mesa/mesa-for-android-container_26.2.0-devel-20260511_ubuntu_questing_arm64.tar.gz \
  https://github.com/lfdevs/mesa-for-android-container/releases/download/mesa-26.2.0-devel-20260511/mesa-for-android-container_26.2.0-devel-20260511_ubuntu_questing_arm64.tar.gz
echo "f9848fdb3527c206a0937aa7b239b38e0eb81e2beec3f7df3453c99cb539dd68  /root/lfdevs_mesa/mesa-for-android-container_26.2.0-devel-20260511_ubuntu_questing_arm64.tar.gz" | sha256sum -c -
tar -czf /root/lfdevs_mesa/mesa-ubuntu-original-$(date +%Y%m%d-%H%M%S).tar.gz \
  /usr/lib/aarch64-linux-gnu/libGLX_mesa.so* \
  /usr/lib/aarch64-linux-gnu/libEGL_mesa.so* \
  /usr/lib/aarch64-linux-gnu/libgbm.so* \
  /usr/lib/aarch64-linux-gnu/libgallium-* \
  /usr/lib/aarch64-linux-gnu/dri \
  /usr/lib/aarch64-linux-gnu/gbm \
  /usr/share/vulkan/icd.d \
  /usr/share/glvnd/egl_vendor.d
tar -xzf /root/lfdevs_mesa/mesa-for-android-container_26.2.0-devel-20260511_ubuntu_questing_arm64.tar.gz -C /
ldconfig
```

Restart the DroidSpaces container after installation. Be ready to use the recovery section below if the screen turns black.

## Validate

Run from the Android host using the current `startplasma-x11` PID:

```sh
nsenter -t <startplasma_pid> -m -n -- env DISPLAY=:5 XDG_RUNTIME_DIR=/tmp/runtime-Gold glxinfo -B
```

Expected result:

```text
OpenGL renderer string: zink Vulkan 1.4(Adreno (TM) 840 (MESA_TURNIP))
Accelerated: yes
```

Optional short render test:

```sh
nsenter -t <startplasma_pid> -m -n -- env DISPLAY=:5 XDG_RUNTIME_DIR=/tmp/runtime-Gold timeout 6s glxgears -info
```

Observed result on NX809J:

```text
GL_RENDERER = zink Vulkan 1.4(Adreno (TM) 840 (MESA_TURNIP))
492 frames in 5.0 seconds = 98.251 FPS
```

## Browser Notes

The GPU stack is now active, but Firefox/YouTube can still crash if launched without browser-specific flags. Do not force `MESA_LOADER_DRIVER_OVERRIDE=kgsl` globally for Plasma or browsers. The direct KGSL path still prints:

```text
MESA-LOADER: failed to retrieve device information
MESA: error: kgsl_pipe_get_param:103: invalid param id: 13
```

Use software-rendered browser launchers for YouTube until the browser-specific EGL crash is solved. Do not use Zink/Turnip or direct KGSL as the default browser path.

## Recovery / Revert

Backups are stored under `/root/lfdevs_mesa/mesa-ubuntu-original-*.tar.gz`.

To recover a black screen:

```sh
mkdir -p /root/lfdevs_mesa/disabled-icd
mv /usr/share/vulkan/icd.d/freedreno_icd.aarch64.json /root/lfdevs_mesa/disabled-icd/ 2>/dev/null || true
mv /usr/share/vulkan/icd.d/freedreno_icd.json /root/lfdevs_mesa/disabled-icd/ 2>/dev/null || true
tar -xzf /root/lfdevs_mesa/mesa-ubuntu-original-YYYYMMDD-HHMMSS.tar.gz -C /
ldconfig
```

Also set the container config to software mode:

```text
enable_gpu_mode=0
enable_virgl=0
```

Restart the DroidSpaces container after changing these values.

The helper script `tools/nx809j/gpu/recover-software-rendering.sh` can be run inside the Ubuntu container to move the Freedreno ICD files out of the active Vulkan path and force Mesa's dynamic linker cache to refresh.
