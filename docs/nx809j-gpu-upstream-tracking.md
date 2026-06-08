# RedMagic 11 Pro NX809J GPU Upstream Tracking

This note lists the projects to follow for Adreno 840 GPU acceleration inside Android Linux containers such as DroidSpaces, Termux:X11, PRoot, chroot, and LXC.

## Current Local Status

The tested RedMagic 11 Pro NX809J container currently runs in software rendering mode:

```text
OpenGL renderer string: llvmpipe (LLVM 20.1.8, 128 bits)
Accelerated: no
```

The Adreno 840 hardware path is detected by Mesa/Turnip, but it is not stable enough for the full Plasma + Termux:X11 desktop yet. It passed short synthetic tests, then caused a black screen during real desktop/browser use.

## Follow In This Order

### 1. lfdevs/mesa-for-android-container

Repository: <https://github.com/lfdevs/mesa-for-android-container>

Releases: <https://github.com/lfdevs/mesa-for-android-container/releases>

This is the first project to watch for NX809J container use. It packages Mesa, Freedreno, Turnip, Zink, and KGSL/Termux:X11-related patches for Android-hosted Linux containers.

Watch for packages matching the container distribution:

```text
ubuntu_questing_arm64
```

Relevant package families:

```text
mesa-for-android-container_*_ubuntu_questing_arm64.tar.gz
turnip_*_ubuntu_questing_arm64.tar.gz
turnip-weekly
```

### 2. Mesa Upstream: Freedreno, Turnip, Zink

Mesa GitLab: <https://gitlab.freedesktop.org/mesa/mesa>

Freedreno docs: <https://docs.mesa3d.org/drivers/freedreno.html>

This is where the core open-source Adreno driver work lands.

- Freedreno: OpenGL/OpenGL ES for Adreno
- Turnip: Vulkan for Adreno
- Zink: OpenGL over Vulkan

Adreno 840 support is part of the newer Mesa 26.x development work, so fixes may appear here before they are packaged for Android containers.

### 3. Termux:X11

Repository: <https://github.com/termux/termux-x11>

Issues: <https://github.com/termux/termux-x11/issues>

Termux:X11 is important because the observed failure is a black screen in the X11 desktop session. DRI3, buffer handling, window presentation, and X server compatibility issues can be fixed here even when Mesa itself detects the GPU correctly.

### 4. Termux Packages

Repository: <https://github.com/termux/termux-packages>

This project packages Termux-side Mesa, Vulkan loader, VirGL, Turnip, and related graphics dependencies. It matters when testing native Termux graphics or the host-side pieces used by DroidSpaces.

### 5. DroidSpaces OSS

Repository: <https://github.com/ravindu644/Droidspaces-OSS>

DroidSpaces controls the container lifecycle, mounts, hardware access, Termux:X11 integration, VirGL startup, PulseAudio, and access to Android GPU devices such as KGSL. Container-side bugs or environment choices can affect whether Mesa uses a stable path.

## Practical Rule

For NX809J, do not assume a driver is stable just because these checks pass:

```text
vulkaninfo
glxinfo -B
glxgears
```

The current failure only appeared after using the real desktop/browser session. A release should be considered usable only after it passes:

- `vulkaninfo`
- `glxinfo -B`
- short OpenGL render test
- Plasma/KWin session stability
- browser startup
- YouTube/video page stability
- touch interaction inside Termux:X11 without black screen

## Current Recommendation

Stay on software rendering for daily use:

```text
enable_gpu_mode=0
enable_virgl=0
```

Keep Freedreno Vulkan ICD files disabled inside the Ubuntu container until a newer Mesa/Termux:X11/DroidSpaces combination proves stable.
