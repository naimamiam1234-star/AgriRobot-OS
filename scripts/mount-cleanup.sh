#!/usr/bin/env bash
# Source from build.sh. Failure must prevent filesystem packaging.
cleanup_mounts() {
    local failed=0
    local i
    for ((i=${#mounts[@]}-1;i>=0;i--)); do
        umount --recursive "${mounts[i]}" || failed=1
    done
    return "$failed"
}
