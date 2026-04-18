#!/usr/bin/env sh
# Headless signaling server (e.g. Raspberry Pi). From this file's directory:
#   ./run_server.sh
# Logs go to ./.messenger/server.log (same as Python stderr if you redirect in systemd).

cd "$(dirname "$0")" || exit 1
exec python3 -m signaling_service "$@"
