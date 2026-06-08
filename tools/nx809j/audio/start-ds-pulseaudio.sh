#!/data/data/com.termux/files/usr/bin/bash
set -u

PREFIX="${PREFIX:-/data/data/com.termux/files/usr}"
HOME="${HOME:-/data/data/com.termux/files/home}"
PATH="$PREFIX/bin:/system/bin:/system/xbin:$PATH"
SOCKET="$PREFIX/tmp/.pulse-socket"

mkdir -p "$PREFIX/tmp" "$HOME/.config/pulse"
rm -f "$SOCKET"

pulseaudio -k >/dev/null 2>&1 || true
sleep 0.5

pulseaudio --start \
  --load="module-native-protocol-unix socket=$SOCKET auth-anonymous=1" \
  --load="module-native-protocol-tcp auth-ip-acl=127.0.0.1;172.28.0.0/16 auth-anonymous=1 port=4713" \
  --exit-idle-time=-1 \
  --disallow-exit

sleep 1

if ! pactl info >/dev/null 2>&1; then
  echo "PulseAudio did not start"
  exit 1
fi

if ! pactl list modules short | grep -q module-aaudio-sink; then
  pacmd load-module module-aaudio-sink >/dev/null 2>&1 || true
fi

sink="$(pactl list sinks short | awk '/aaudio/ {print $2; exit}')"
if [ -n "$sink" ]; then
  pactl set-default-sink "$sink" >/dev/null 2>&1 || true
  echo "AAudio sink ready: $sink"
else
  echo "AAudio sink not found"
  pactl list sinks short || true
  exit 1
fi

echo "Pulse socket: $SOCKET"
echo "Pulse TCP: tcp:172.28.0.1:4713"
