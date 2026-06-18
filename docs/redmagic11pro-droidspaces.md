# RedMagic 11 Pro / Droidspaces Notes

This fork keeps the WildKernels OP15 kernel as the base for NX809J / RedMagic 11 Pro:

- SoC: SM8850 / canoe
- KMI target: android16-6.12.23
- WildKernels features kept: KernelSU-Next, SUSFS, NTSync, Droidspaces, BBR, TTL, IP_SET, BBG

Useful references:

- Official fork upstream: https://github.com/WildKernels/OnePlus_KernelSU_SUSFS
- Droidspaces kernel package reference: https://github.com/Goldzxcbug/Droidspaces-kernel
- Droidspaces patch reference: https://github.com/Goldzxcbug/Droidspaces_Kernel_patch

Changes adopted from the Droidspaces references:

- Ensure AnyKernel accepts 6.12 kernels before packaging.
- Ensure AnyKernel tools are executable before flashing:
  - `sync`
  - `sleep 0.5`
  - `chmod -R 755 "${AKHOME}/tools"`
- Extend Droidspaces build configs with IPC, PID, UTS, devtmpfs mount, and cgroup support. Keep user namespaces disabled by default unless a tested rootfs proves it needs them; Droidspaces v6.3.0 reports `CONFIG_USER_NS disabled` as a hardening-positive state on NX809J.

The Goldzxcbug 6.12.23 images are useful as Droidspaces/NTSync references, but they are not used as the base here because the WildKernels OP15 image already carries KernelSU-Next and SUSFS.

Packaging and release reproduction notes:

- [RedMagic 11 Pro NX809J Packaging Guide](nx809j-packaging.md)
- [RedMagic 11 Pro NX809J DroidSpaces Audio](nx809j-droidspaces-audio.md)
