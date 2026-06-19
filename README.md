<div align="center">

# 🔥 Wild Kernels for OnePlus (Oppo/Realme)

[![KernelSU](https://img.shields.io/badge/KernelSU-Supported-green)](https://kernelsu.org/)
[![KernelSU-Next](https://img.shields.io/badge/KernelSU-Supported-green)](https://kernelsu-next.github.io/webpage/)
[![SUSFS](https://img.shields.io/badge/SUSFS-Integrated-orange)](https://gitlab.com/simonpunk/susfs4ksu)
[![KernelSU](https://img.shields.io/badge/KernelSU-Supported-green)](https://kernelsu.org/)
[![OnePlusOSS Tracking Status](https://img.shields.io/badge/OnePlusOSS--Tracker-active-green)](https://github.com/WildKernels/OnePlus_KernelSU_SUSFS/blob/status-page/README.md)

</div>

---

## ⚠️ Disclaimer

Flashing this kernel will not void your warranty, but there is always a risk of bricking your device. Please make sure to:
- 💾 Back up your data
- 🧠 Understand the risks before proceeding

- I am **not responsible** for bricked devices, damaged hardware, or any issues that arise from using this kernel.

- **Please** do thorough research and fully understand the features added in this kernel before flashing it!

- By flashing this kernel, **YOU** are choosing to make these modifications. If something goes wrong, **do not blame me**!

<div align="center">
  
# **🚨 Proceed at your own risk!**

</div>

---

## 🔧 Available Kernels

<div align="center">

| Kernel | Repository | Status |
|--------|------------|--------|
| 🏗️ **GKI** | [GKI_KernelSU_SUSFS](https://github.com/WildKernels/GKI_KernelSU_SUSFS) | ✅ Active |
| 👑 **Sultan** | [Sultan_KernelSU_SUSFS](https://github.com/WildKernels/Sultan_KernelSU_SUSFS) | ✅ Active |
| 📱 **OnePlus/Oppo/Realme** | [OnePlus_KernelSU_SUSFS](https://github.com/WildKernels/OnePlus_KernelSU_SUSFS) | ✅ Active |
| 📱 **Samsung** | [Samsung_KernelSU_SUSFS](https://github.com/WildKernels/Samsung_KernelSU_SUSFS) | ✅ Active |
</div>

---

## 🔗 Additional Resources

- 🩹 [Kernel Patches](https://github.com/WildKernels/kernel_patches)
- ⚡ [Kernel Flasher](https://github.com/fatalcoder524/KernelFlasher)

---

## 📱 Device Compatibility

- Please verify the device compatibility before flashing here: [Compatibility_Info](https://github.com/WildKernels/OnePlus_KernelSU_SUSFS/blob/main/compatibility.md). 

---

## 📱 OnePlusOSS Repositories Tracking

- 📊 **Live Dashboard**: [OnePlus Repos Tracking & Changes](https://github.com/WildKernels/OnePlus_KernelSU_SUSFS/blob/status-page/README.md)
- ⏱️ **Update Frequency**: Every 2 hours (Automated)
---

## ✨ Features

- 🔐 **KernelSU / KernelSU-Next**: A root solution for Android GKI devices that works in kernel mode and grants root permission to userspace applications directly in kernel space
- 🔥 **WildKSU Manager Support**: Support for the Root Manager developed by our team with lots of customisations
- 🥷 **SUSFS**: An addon root hiding kernel patches and userspace module for KernelSU
- 🛡️ **BBG**: LSM-based Baseband Guard security to protect critical device partitions
- 🛠️ **HMBIRD SCX**: Scheduler extensions for SM8750/MT6991 devices
- 🖧 **BBRv1**: Improved TCP congestion control
- ✅ **LTO**: Link Time Optimisation enabled
- 🚀 **Optimisation patches**: Memory, I/O, CPU scheduler, network and other general tunings
- 🌐 **TTL Target Support**: Network packet manipulation
- 🧱 **IP Set & IPv6 NAT Support**: Advanced firewall capabilities and IPv6 NAT Support
- ⚡️ **TMPFS XATTR / POSIX ACL**: Extended TMPFS support for meta modules and Mountify
- </> **Unicode Bypass Fix**: Prevent path traversal and other detections using non-printable Unicode codepoints [Experimental]
- 🖥️ **Droidspaces Support**: Support Portable Linux containers to run full Linux environments.
- 🔃 **NTSync**: Provide high-performance, low-latency synchronization primitives compatible with the Windows NT kernel API

---

## 📋 Installation Instructions

For GKI installation, please follow the official guide:

📖 **[KernelSU Installation Guide](https://kernelsu.org/guide/installation.html)**

You can also find Installation instructions in the release notes.

---

## OP15 OOS16 AnyKernel Build Notes

This section documents what was required to recover a bootable OP15 AnyKernel
after test builds started bootlooping.

### Known Good Target

- Device target: `OP15`
- OS target: `OOS16`
- Kernel version: `android16-6.12.23`
- KernelSU type: `KSUN`
- Known working KernelSU Next ref:
  `f1b64f440f3cd170e2a86d7816bef26fbdee1caa`
- Known working SUSFS ref:
  `7b3e90160043ffe844f3db34d8c7c57ff4789f53`
- Expected KSUN version in the ZIP name/logs: `33169`

### What Broke Boot

The failed AnyKernel builds were not caused by module signature changes.
The likely bootloop cause was that Droidspaces/RedMagic container configs were
added globally to `gki_defconfig`, so they were also applied to OP15.

These configs changed the OP15 kernel `Image` size and produced non-booting
AnyKernel ZIPs:

```text
CONFIG_NAMESPACES=y
CONFIG_IPC_NS=y
CONFIG_UTS_NS=y
CONFIG_USER_NS=y
CONFIG_DEVTMPFS_MOUNT=y
CONFIG_CGROUPS=y
CONFIG_CGROUP_DEVICE=y
CONFIG_CGROUP_PIDS=y
CONFIG_MEMCG=y
```

Do not apply those container/Droidspaces configs globally for OP15. If they are
needed later, gate them per-device and test with `fastboot boot` before
publishing a flashable release.

### What Was Needed For The Functional AnyKernel

- Restored the OP15 kernel patch flow to match the previously boot-tested
  WildKernels path.
- Removed dynamic KernelSU/SUSFS source edits that changed the final kernel
  `Image`.
- Removed the global Droidspaces/namespace/cgroup config injection from OP15.
- Kept automatic release publishing enabled.
- Kept the Droidspaces daemon/init as a separate KernelSU module ZIP.
- Kept the Droidspaces module files vendored locally under:
  `vendor/droidspaces-module`

The Droidspaces module must remain separate from the AnyKernel boot image. It
should be installed only after the OP15 kernel boots successfully.

### How To Trigger The OP15 Build

Use the workflow manually with:

```powershell
gh workflow run build-kernel-release.yml `
  --repo Coding-BR/OnePlus_KernelSU_SUSFS `
  --ref main `
  -f make_release=true `
  -f op_model=OP15
```

The workflow defaults are pinned to the known working KSUN and SUSFS refs above.
Do not pass malformed JSON through PowerShell for `ksu_options`; if custom JSON
is required, verify the run reaches the matrix generation step successfully.

### Validation Checklist Before Flashing

After the Action finishes:

- Confirm the release contains an `AK3_OP15_OOS16_android16-6.12.23_KSUN_33169`
  ZIP.
- Confirm the release also contains the separate
  `Droidspaces_Daemon_Init_KernelSU_OP15_OOS16_android16-6.12.23_KSUN_33169`
  ZIP when Droidspaces packaging is enabled.
- Extract the AK3 ZIP and compare the internal `Image` size with the known-good
  OP15 build. The recovered functional-size target was:

```text
Image size: 40974848 bytes
```

- A bad bootlooping build had a larger `Image`, around:

```text
41044480 bytes
41048576 bytes
```

- Flash/test the AK3 first.
- Install the Droidspaces KernelSU module only after Android boots.

### Unsigned `.ko` Driver Policy

Android GKI can load unsigned `.ko` modules only when signature enforcement is
not active and the module uses allowed KMI symbols. Unsigned support is not the
same thing as "load any driver".

For OP15 `android16-6.12.23`, the workflow now disables `MODULE_SIG_FORCE` and
`MODULE_SIG_ALL` before `olddefconfig`, then validates the final `.config` and
fails the build if unsafe enforcement is found:

```text
CONFIG_MODULE_SIG_FORCE=y
CONFIG_MODULE_SIG_ALL=y
module.sig_enforce=1
```

`CONFIG_MODULE_SIG=y` may still exist. That only enables module signature
support. It does not by itself force signed-only loading. The dangerous setting
for unsigned modules is `CONFIG_MODULE_SIG_FORCE=y` or the boot parameter
`module.sig_enforce=1`.

Before testing an external driver on the phone:

```sh
zcat /proc/config.gz | grep MODULE_SIG
cat /proc/cmdline
modinfo driver.ko
insmod driver.ko
dmesg | tail -n 80
```

If loading fails, read `dmesg` first:

- signature/enforcement error: check `CONFIG_MODULE_SIG_FORCE` and
  `module.sig_enforce=1`.
- `vermagic` error: rebuild the module for the exact running kernel.
- unknown symbol/KMI error: the driver uses symbols not exported through the
  allowed KMI surface and must be fixed or rebuilt against allowed symbols.

### Latest Recovery Reference

The recovery build that removed the global Droidspaces configs was generated
from:

```text
Commit: 2ed51cf fix(op15): stop applying droidspaces configs globally
Run:    27830882926
AK3:    AK3_OP15_OOS16_android16-6.12.23_KSUN_33169_SuSFS_v2.1.0.zip
SHA256: 021403fb5254f41c69a9c0a4ca868051c23ecc9e181f68840924bafe5b6d5984
Module: Droidspaces_Daemon_Init_KernelSU_OP15_OOS16_android16-6.12.23_KSUN_33169.zip
SHA256: 4446e5db99964e626a7d038eb35b7e65ba5a3cb5ac8c7805b5b3d6517d4f7a49
```

---

## 🌟 Special Thanks

**These amazing people help make this project possible! ❤️**

<div align="center">


| 🔧 **Project** | 👨‍💻 **Developer** | 🔗 **Link** |
|:---------------:|:----------------:|:-----------:|
| **KernelSU** | tiann | [![GitHub](https://img.shields.io/badge/GitHub-tiann-blue?style=flat-square&logo=github)](https://github.com/tiann/KernelSU) |
| **KernelSU-Next** | rifsxd | [![GitHub](https://img.shields.io/badge/GitHub-rifsxd-blue?style=flat-square&logo=github)](https://github.com/KernelSU-Next/KernelSU-Next) |
| **Magic-KSU** | 5ec1cff | [![GitHub](https://img.shields.io/badge/GitHub-5ec1cff-blue?style=flat-square&logo=github)](https://github.com/5ec1cff/KernelSU) |
| **SUSFS** | simonpunk | [![GitLab](https://img.shields.io/badge/GitLab-simonpunk-orange?style=flat-square&logo=gitlab)](https://gitlab.com/simonpunk/susfs4ksu.git) |
| **SUSFS Module** | sidex15 | [![GitHub](https://img.shields.io/badge/GitHub-sidex15-blue?style=flat-square&logo=github)](https://github.com/sidex15) |
| **Sultan Kernels** | kerneltoast | [![GitHub](https://img.shields.io/badge/GitHub-kerneltoast-blue?style=flat-square&logo=github)](https://github.com/kerneltoast) |
| **Baseband Guard** | vc-teahouse | [![GitHub](https://img.shields.io/badge/GitHub-vc--teahouse-blue?style=flat-square&logo=github)](https://github.com/vc-teahouse/Baseband-guard.git) |
| **Droidspaces** | ravindu644 | [![GitHub](https://img.shields.io/badge/GitHub-ravindu644-blue?style=flat-square&logo=github)](https://github.com/ravindu644/Droidspaces-OSS.git) |

</div>

*If you have contributed and are not listed here, please remind me!* 🙏

---

## 💬 Support

If you encounter any issues or need help, feel free to:
- 🐛 Open an issue in this repository
- 💬 Reach out to me directly

---

## 📱 Connect With Us

<div align="center">
  
[![Telegram](https://img.shields.io/badge/Telegram-fatalcoder524-blue?logo=telegram)](https://t.me/anonymous_yolo)
[![Telegram Group](https://img.shields.io/badge/Telegram-WildKernels-blue?logo=telegram)](https://t.me/WildKernelsTG)

</div>

---

## 💝 Donations

Any and all donations are appreciated!

PayPal: [paypal.me/fatalcoder524](https://paypal.me/fatalcoder524)

DM on Telegram for UPI donations!

