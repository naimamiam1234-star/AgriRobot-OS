#!/usr/bin/env bash
set -eu
for attempt in $(seq 1 90); do
    if curl --noproxy '*' -fsS http://127.0.0.1:8080/health >/dev/null; then
        echo 'AGRIROBOT_BOOT_READY local_api=ok physical_control=disabled' > /dev/ttyS0
        exit 0
    fi
    sleep 1
done
echo 'AGRIROBOT_BOOT_FAILED local_api=unavailable' > /dev/ttyS0
exit 1
