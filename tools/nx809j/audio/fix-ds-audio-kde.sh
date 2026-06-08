#!/bin/sh
set -u

export DISPLAY="${DISPLAY:-:5}"
export PULSE_SERVER="${PULSE_SERVER:-tcp:172.28.0.1:4713}"
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/1000}"
export DBUS_SESSION_BUS_ADDRESS="${DBUS_SESSION_BUS_ADDRESS:-unix:path=/run/user/1000/bus}"

mkdir -p "$HOME/.config/pulse" "$HOME/.config/environment.d" "$HOME/.config/plasma-workspace/env"

cat > "$HOME/.config/pulse/client.conf" <<'EOF'
default-server = tcp:172.28.0.1:4713
autospawn = no
EOF

cat > "$HOME/.config/environment.d/99-droidspaces-audio.conf" <<'EOF'
PULSE_SERVER=tcp:172.28.0.1:4713
EOF

cat > "$HOME/.config/plasma-workspace/env/droidspaces-audio.sh" <<'EOF'
#!/bin/sh
export PULSE_SERVER=tcp:172.28.0.1:4713
EOF
chmod 755 "$HOME/.config/plasma-workspace/env/droidspaces-audio.sh"

systemctl --user stop pipewire-pulse.socket pipewire-pulse.service >/dev/null 2>&1 || true
systemctl --user mask pipewire-pulse.socket pipewire-pulse.service >/dev/null 2>&1 || true

pactl info
pactl list sinks short

pkill plasmashell >/dev/null 2>&1 || true
sleep 1
nohup plasmashell >/tmp/plasmashell-droidspaces-audio.log 2>&1 &

echo "DroidSpaces KDE audio bridge refreshed."
