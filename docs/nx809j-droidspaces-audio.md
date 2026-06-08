# RedMagic 11 Pro NX809J DroidSpaces Audio

This note documents the audio path that was tested on the RedMagic 11 Pro NX809J with the DroidSpaces KernelSU module.

## What Works

The working route is:

```text
DroidSpaces Ubuntu app
  -> PulseAudio client in the container
  -> Termux PulseAudio over TCP
  -> module-aaudio-sink
  -> Android AAudio
  -> phone speaker
```

The TCP bridge is preferred over a bind-mounted Unix socket because it survives PulseAudio restarts more reliably inside DroidSpaces NAT networking.

## Confirmed Device State

The tested container was `Ubuntu`, with DroidSpaces NAT networking enabled. The container had IP `172.28.251.97` and used the Android side gateway `172.28.0.1`.

In Termux, PulseAudio exposed the Android speaker as:

```text
Default Sink: AAudio_sink
Default Source: AAudio_sink.monitor
```

In the Ubuntu container, this worked:

```sh
PULSE_SERVER=tcp:172.28.0.1:4713 pactl info
PULSE_SERVER=tcp:172.28.0.1:4713 paplay /usr/share/sounds/freedesktop/stereo/audio-test-signal.oga
```

The user confirmed that the test sound played from the phone speaker.

## Install Termux Dependencies

Copy `tools/nx809j/audio/install-termux-audio-deps.sh` and `tools/nx809j/audio/start-ds-pulseaudio.sh` to Termux home, then run:

```sh
bash ~/install-termux-audio-deps.sh
bash ~/start-ds-pulseaudio.sh
```

The startup script loads both:

- `module-native-protocol-unix` at `$PREFIX/tmp/.pulse-socket`
- `module-native-protocol-tcp` at `tcp:172.28.0.1:4713`

It also loads `module-aaudio-sink` when needed and sets the default sink to `AAudio_sink`.

## Configure KDE Inside DroidSpaces Ubuntu

Copy `tools/nx809j/audio/fix-ds-audio-kde.sh` into the Ubuntu container and run it as the desktop user:

```sh
sh ./fix-ds-audio-kde.sh
```

The script writes:

```text
~/.config/pulse/client.conf
~/.config/environment.d/99-droidspaces-audio.conf
~/.config/plasma-workspace/env/droidspaces-audio.sh
```

It sets:

```text
PULSE_SERVER=tcp:172.28.0.1:4713
```

It also masks the user `pipewire-pulse` service so KDE applications use the Termux PulseAudio server instead of trying to use a broken local sound service.

## About The KDE Warning

KDE may still show messages such as:

```text
No output or input devices found
Connection to the sound service lost, retrying
```

That message comes from KDE/PipeWire expecting a local sound service inside the container. In the working setup, the actual audio output is external: applications send sound to Termux PulseAudio over TCP. So the warning can appear even when playback works.

Use these commands to verify the real audio path:

```sh
PULSE_SERVER=tcp:172.28.0.1:4713 pactl info
PULSE_SERVER=tcp:172.28.0.1:4713 pactl list sinks short
PULSE_SERVER=tcp:172.28.0.1:4713 paplay /usr/share/sounds/freedesktop/stereo/audio-test-signal.oga
```

On the Termux side, this shows active playback streams:

```sh
pactl list sink-inputs short
```

## Notes

- This fixes output playback through the Android speaker.
- Microphone/input capture is separate and was not confirmed.
- The issue is not a RedMagic kernel audio driver failure when the `paplay` test works. It is a userspace audio routing problem between DroidSpaces, KDE/PipeWire, Termux PulseAudio, and Android AAudio.
