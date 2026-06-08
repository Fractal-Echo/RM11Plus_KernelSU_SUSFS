#!/data/data/com.termux/files/usr/bin/bash
set -e

pkg update
pkg install -y x11-repo
pkg install -y pulseaudio termux-x11

echo "Dependencies installed. Run: bash ~/start-ds-pulseaudio.sh"
