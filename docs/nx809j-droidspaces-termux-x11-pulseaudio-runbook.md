# NX809J Droidspaces Termux:X11 and PulseAudio Runbook

This runbook records the manual recovery steps used on NX809J when Droidspaces
started a container but logged:

```text
Termux:X11: loader.apk not found. Is termux-x11 package installed?
PulseAudio: binary not found at /data/data/com.termux/files/usr/bin/pulseaudio.
Termux:X11: .X11-unix not found ... skipping socket bridge
PulseAudio: socket not found ... skipping socket bridge
```

## Diagnosis

Check installed Android packages:

```powershell
adb shell pm list packages | Select-String -Pattern 'termux|x11|droidspaces|pulse|pulseaudio' -CaseSensitive:$false
adb shell pm list packages -f | Select-String -Pattern 'termux|x11|droidspaces' -CaseSensitive:$false
```

Expected packages:

```text
package:com.termux
package:com.termux.x11
package:com.droidspaces.app
```

Check Termux-side binaries:

```powershell
adb shell su -c 'ls -la /data/data/com.termux/files/usr/bin/pulseaudio /data/data/com.termux/files/usr/bin/pactl /data/data/com.termux/files/usr/bin/termux-x11 2>/dev/null || true'
adb shell su -c 'find /data/data/com.termux/files/usr -maxdepth 6 -name loader.apk -print 2>/dev/null'
```

If `com.termux.x11` exists but `termux-x11` / `loader.apk` is missing, the APK is
installed but the Termux package is not. Droidspaces needs both.

## Fix Termux Repository Source

Some fresh Termux installs still pointed to the dead `https://termux.net`
repository. Replace it with the current package endpoint:

```powershell
@'
# The main termux repository
Components: main
Signed-By: /data/data/com.termux/files/usr/etc/apt/trusted.gpg.d/termux-packages.gpg
Suites: stable
Types: deb
URIs: https://packages.termux.dev/apt/termux-main
'@ | adb shell su -c 'tee /data/data/com.termux/files/usr/etc/apt/sources.list.d/termux.sources >/dev/null'

adb shell su -c 'chown u0_a526:u0_a526 /data/data/com.termux/files/usr/etc/apt/sources.list.d/termux.sources'
adb shell su -c 'cat /data/data/com.termux/files/usr/etc/apt/sources.list.d/termux.sources'
```

Replace `u0_a526` with the actual Termux app user if it changes:

```powershell
adb shell su -c 'ls -ld /data/data/com.termux'
```

## Offline Install When Termux DNS Fails Under KSU

On this device, running Termux tools through `su u0_a526 -c ...` could not
resolve DNS, even though root could. The workaround was to download `.deb`
packages on Windows, push them to the phone, then install with `dpkg` as the
Termux user.

Download dependencies locally:

```powershell
@'
import gzip, re, subprocess, urllib.request
from pathlib import Path

base = Path("C:/Users/adriano/Videos/WildKernel/termux_debs")
base.mkdir(parents=True, exist_ok=True)
indexes = {
    "main": "https://packages.termux.dev/apt/termux-main/dists/stable/main/binary-aarch64/Packages.gz",
    "x11": "https://packages.termux.dev/apt/termux-x11/dists/x11/main/binary-aarch64/Packages.gz",
}
repo_roots = {
    "main": "https://packages.termux.dev/apt/termux-main/",
    "x11": "https://packages.termux.dev/apt/termux-x11/",
}

def parse_packages(text, repo):
    pkgs = {}
    for block in text.strip().split("\n\n"):
        fields = {}
        last = None
        for line in block.splitlines():
            if line and line[0].isspace() and last:
                fields[last] += "\n" + line
            elif ":" in line:
                k, v = line.split(":", 1)
                fields[k] = v.strip()
                last = k
        if fields.get("Package"):
            fields["_repo"] = repo
            pkgs[fields["Package"]] = fields
    return pkgs

allpkgs = {}
for repo, url in indexes.items():
    raw = urllib.request.urlopen(url, timeout=60).read()
    text = gzip.decompress(raw).decode("utf-8", "replace")
    allpkgs.update(parse_packages(text, repo))

status = subprocess.check_output(
    ["adb", "shell", "su", "-c", "cat /data/data/com.termux/files/usr/var/lib/dpkg/status"],
    text=True,
    errors="replace",
)
installed = set(parse_packages(status, "installed").keys())

def dep_names(depstr):
    out = []
    for part in (depstr or "").replace("\n", " ").split(","):
        name = re.split(r"\s|\(", part.strip().split("|")[0].strip())[0]
        if name and not name.startswith("$"):
            out.append(name)
    return out

needed = []
seen = set(installed)

def add_pkg(name):
    if name in seen:
        return
    fields = allpkgs[name]
    seen.add(name)
    for dep in dep_names(fields.get("Pre-Depends", "")) + dep_names(fields.get("Depends", "")):
        add_pkg(dep)
    needed.append(name)

for name in ["pulseaudio", "termux-x11-nightly"]:
    add_pkg(name)

for name in needed:
    fields = allpkgs[name]
    url = repo_roots[fields["_repo"]] + fields["Filename"]
    out = base / Path(fields["Filename"]).name
    expected = int(fields.get("Size", "-1"))
    if not out.exists() or out.stat().st_size != expected:
        urllib.request.urlretrieve(url, out)

print(base)
'@ | python -
```

Push and install:

```powershell
adb shell su -c 'rm -rf /data/local/tmp/termux_debs; mkdir -p /data/local/tmp/termux_debs; chmod 755 /data/local/tmp/termux_debs'
adb push C:\Users\adriano\Videos\WildKernel\termux_debs /data/local/tmp/
adb shell su -c 'chown -R u0_a526:u0_a526 /data/local/tmp/termux_debs'

adb shell su u0_a526 -c env `
  HOME=/data/data/com.termux/files/home `
  PREFIX=/data/data/com.termux/files/usr `
  TMPDIR=/data/data/com.termux/files/usr/tmp `
  PATH=/data/data/com.termux/files/usr/bin:/system/bin:/system/xbin `
  LD_LIBRARY_PATH=/data/data/com.termux/files/usr/lib `
  /data/data/com.termux/files/usr/bin/dpkg -i /data/local/tmp/termux_debs/*.deb
```

Expected installed packages include:

```text
pulseaudio
termux-x11-nightly
xkeyboard-config
```

## Start PulseAudio

Use the repo helper, but convert CRLF to LF after pushing from Windows:

```powershell
adb push C:\Users\adriano\Videos\WildKernel\OnePlus_KernelSU_SUSFS\tools\nx809j\audio\start-ds-pulseaudio.sh /data/local/tmp/start-ds-pulseaudio.sh
adb shell su -c 'cp /data/local/tmp/start-ds-pulseaudio.sh /data/data/com.termux/files/home/start-ds-pulseaudio.sh'
adb shell su -c 'chown u0_a526:u0_a526 /data/data/com.termux/files/home/start-ds-pulseaudio.sh'
adb shell su -c 'chmod 700 /data/data/com.termux/files/home/start-ds-pulseaudio.sh'

adb shell su u0_a526 -c env `
  HOME=/data/data/com.termux/files/home `
  PREFIX=/data/data/com.termux/files/usr `
  TMPDIR=/data/data/com.termux/files/usr/tmp `
  PATH=/data/data/com.termux/files/usr/bin:/system/bin:/system/xbin `
  LD_LIBRARY_PATH=/data/data/com.termux/files/usr/lib `
  dos2unix /data/data/com.termux/files/home/start-ds-pulseaudio.sh

adb shell su u0_a526 -c env `
  HOME=/data/data/com.termux/files/home `
  PREFIX=/data/data/com.termux/files/usr `
  TMPDIR=/data/data/com.termux/files/usr/tmp `
  PATH=/data/data/com.termux/files/usr/bin:/system/bin:/system/xbin `
  LD_LIBRARY_PATH=/data/data/com.termux/files/usr/lib `
  /data/data/com.termux/files/usr/bin/bash /data/data/com.termux/files/home/start-ds-pulseaudio.sh
```

Expected output:

```text
AAudio sink ready: AAudio_sink
Pulse socket: /data/data/com.termux/files/usr/tmp/.pulse-socket
Pulse TCP: tcp:172.28.0.1:4713
```

Validate:

```powershell
adb shell su -c 'ls -la /data/data/com.termux/files/usr/tmp/.pulse-socket'
adb shell ps -A -o USER,PID,PPID,NAME,ARGS | Select-String -Pattern 'pulse' -CaseSensitive:$false
```

## Start Termux:X11

Start the X11 loader as the Termux user:

```powershell
adb shell su u0_a526 -c env `
  HOME=/data/data/com.termux/files/home `
  PREFIX=/data/data/com.termux/files/usr `
  TMPDIR=/data/data/com.termux/files/usr/tmp `
  PATH=/data/data/com.termux/files/usr/bin:/system/bin:/system/xbin `
  LD_LIBRARY_PATH=/data/data/com.termux/files/usr/lib `
  termux-x11 :0 -ac
```

This command can remain in the foreground. If the shell times out, check whether
the loader stayed alive:

```powershell
adb shell ps -A -o USER,PID,PPID,NAME,ARGS | Select-String -Pattern 'termux.x11|x11' -CaseSensitive:$false
adb shell su -c 'ls -la /data/data/com.termux/files/usr/tmp/.X11-unix /data/data/com.termux/files/usr/tmp/.X11-unix/X0 2>/dev/null || true'
```

Expected:

```text
app_process ... com.termux.x11.Loader :0 -ac
/data/data/com.termux/files/usr/tmp/.X11-unix/X0
```

## Validate Droidspaces

Restart the container with direct `su -c` invocation. Avoid wrapping the whole
command in another remote shell string because quoting can cause false
`Permission denied` or `inaccessible or not found` errors.

```powershell
adb shell su -c /data/local/Droidspaces/bin/droidspaces --name linux stop
adb shell su -c /data/local/Droidspaces/bin/droidspaces --name linux start
adb shell su -c /data/local/Droidspaces/bin/droidspaces --name linux show
```

Successful startup should include:

```text
Termux:X11: daemon pid=... launched
PulseAudio: daemon pid=... launched
Termux:X11: display is :5 (X5 bind mount)
PulseAudio: socket bind-mounted into container
Termux-X11: enabled
PulseAudio: enabled
```

Check recent Droidspaces log:

```powershell
adb shell su -c 'tail -200 /data/local/Droidspaces/Logs/linux/log'
```

## Notes

- The Android `com.termux.x11` APK alone is not enough. Droidspaces also needs
  the Termux package `termux-x11-nightly` because it provides the loader used
  from the Termux prefix.
- The package previously called `termux-x11` may appear as
  `termux-x11-nightly` in the current Termux X11 repo.
- PulseAudio must run from Termux and expose both Unix socket and TCP
  `tcp:172.28.0.1:4713`.
- If commands executed through `su u0_a526 -c` cannot resolve DNS, prefer the
  offline `.deb` flow above instead of fighting Android resolver context.
- If a copied shell script fails with `$'\r': command not found`, run `dos2unix`
  on it inside Termux.
