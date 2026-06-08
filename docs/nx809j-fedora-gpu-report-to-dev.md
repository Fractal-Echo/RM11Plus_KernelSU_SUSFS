# RedMagic 11 Pro NX809J DroidSpaces Fedora GPU Report

## Summary

On RedMagic 11 Pro NX809J, the DroidSpaces Fedora 43 container is currently able to render with the Adreno 840 GPU. This Fedora container works better than the previous Ubuntu KDE/Plasma and Ubuntu XFCE tests for GPU acceleration.

The current working graphics stack is:

```text
OpenGL: freedreno via KGSL
Vulkan: Turnip
GPU: Adreno (TM) 840
Mesa: 26.2.0-devel
Acceleration: yes
```

## Device

```text
Device: RedMagic 11 Pro
Model: NX809J
SoC: SM8850
GPU: Qualcomm Adreno 840
Android kernel: 6.12.23-android16-OP-WILD
Architecture: aarch64 / arm64
```

## Current Container

```text
DroidSpaces container name: fedora
OS: Fedora Linux 43 (Container Image)
Desktop: KDE/Plasma X11
Display: Termux:X11 :5
```

Relevant DroidSpaces config:

```text
name=fedora
hostname=fedora
enable_hw_access=0
enable_gpu_mode=1
enable_termux_x11=1
enable_virgl=1
enable_pulseaudio=1
```

## OpenGL Result

Current OpenGL renderer:

```text
OpenGL vendor string: freedreno
OpenGL renderer string: Adreno (TM) 840
OpenGL core profile version string: 4.6 (Core Profile) Mesa 26.2.0-devel (git-3743cc80a8)
OpenGL version string: 4.6 (Compatibility Profile) Mesa 26.2.0-devel (git-3743cc80a8)
OpenGL ES profile version string: OpenGL ES 3.2 Mesa 26.2.0-devel (git-3743cc80a8)
Accelerated: yes
```

The command used:

```sh
glxinfo -B
```

The KGSL path also works when explicitly tested:

```sh
MESA_LOADER_DRIVER_OVERRIDE=kgsl TU_DEBUG=noconform glxinfo -B
```

This returns:

```text
OpenGL vendor string: freedreno
OpenGL renderer string: Adreno (TM) 840
Accelerated: yes
```

## Vulkan Result

Vulkan detects Turnip correctly:

```text
deviceName         = Adreno (TM) 840
driverID           = DRIVER_ID_MESA_TURNIP
driverName         = turnip Mesa driver
driverInfo         = Mesa 26.2.0-devel (git-3743cc80a8)
apiVersion         = 1.4.350
vendorID           = 0x5143
deviceID           = 0x44050a31
deviceType         = PHYSICAL_DEVICE_TYPE_INTEGRATED_GPU
```

The command used:

```sh
vulkaninfo --summary
```

## FPS Test

OpenGL test with KGSL/freedreno:

```sh
MESA_LOADER_DRIVER_OVERRIDE=kgsl TU_DEBUG=noconform glxgears -info
```

Observed:

```text
GL_RENDERER = Adreno (TM) 840
GL_VENDOR   = freedreno
303 frames in 5.0 seconds = 60.560 FPS
```

The result appears synchronized to display refresh, so 60 FPS is expected.

## Warnings Still Present

Even when GPU rendering works, Mesa still prints:

```text
MESA-LOADER: failed to retrieve device information
MESA: error: kgsl_pipe_get_param:103: invalid param id: 13
```

Despite this warning, OpenGL reports:

```text
OpenGL renderer string: Adreno (TM) 840
Accelerated: yes
```

## Networking Issue Found And Fixed Manually

The Fedora container initially had no internet because `eth0` was up but had no IP address and no default route.

Manual fix applied:

```sh
ip addr add 172.28.145.193/16 dev eth0
ip link set eth0 up
ip route add default via 172.28.0.1 dev eth0
```

After this:

```text
ping 1.1.1.1: OK
ping google.com: OK
curl https://github.com: HTTP/2 200
```

This may need to be made persistent in DroidSpaces startup/network setup.

## Comparison With Other Tested Containers

### Ubuntu 25.10 KDE/Plasma

The Ubuntu 25.10 KDE/Plasma container could detect Adreno 840 with Mesa/Turnip, but the desktop became unstable and produced black screen issues during real use.

Stable recovery mode there was software rendering:

```text
OpenGL renderer string: llvmpipe
Accelerated: no
```

### Ubuntu 24.04 XFCE

The XFCE container was lighter and more usable than KDE when using software rendering. Its config had GPU/VirGL enabled, but OpenGL hardware path failed with swapchain errors:

```text
MESA: error: CreateSwapchainKHR failed with VK_ERROR_INITIALIZATION_FAILED
MESA: error: zink: could not create swapchain
```

Forced software rendering worked:

```text
OpenGL renderer string: llvmpipe (LLVM 20.1.2, 128 bits)
Accelerated: no
```

### Fedora 43 KDE/Plasma

The Fedora container is the best current result. It renders with Adreno 840 using freedreno/KGSL for OpenGL and Turnip for Vulkan.

## Current Conclusion

Fedora 43 DroidSpaces container on RedMagic 11 Pro NX809J currently has the best GPU result:

```text
OpenGL: freedreno / KGSL / Adreno 840
Vulkan: Turnip / Adreno 840
Mesa: 26.2.0-devel
Acceleration: yes
```

The remaining issues to investigate are:

- Mesa KGSL warning: `kgsl_pipe_get_param: invalid param id: 13`
- Whether this remains stable in browser/video workloads
- Persistent network setup for Fedora container
- Whether `enable_hw_access=0` should be changed or documented for this GPU path
- Whether `MESA_LOADER_DRIVER_OVERRIDE=kgsl` and `TU_DEBUG=noconform` should be applied globally or only per app

## Suggested Developer Notes

Fedora 43 seems to be the most compatible rootfs for this device so far. Ubuntu KDE/Plasma and Ubuntu XFCE either fall back to software rendering or show swapchain/black-screen issues. Fedora 43 can render directly on Adreno 840 with Mesa 26.2.0-devel.
