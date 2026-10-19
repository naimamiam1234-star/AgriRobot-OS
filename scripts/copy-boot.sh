#!/usr/bin/env bash
set -Eeuo pipefail
rootfs=${1:?rootfs required}
destination=${2:?destination required}
kernel=$(find "$rootfs/boot" -maxdepth 1 -type f -name 'vmlinuz-*-generic' -printf '%f\n' | sort -V | tail -n 1)
if [ -z "$kernel" ]; then echo 'No versioned generic kernel in rootfs/boot' >&2; exit 1; fi
version=${kernel#vmlinuz-}
initrd="$rootfs/boot/initrd.img-$version"
if [ ! -f "$initrd" ]; then echo "Missing initrd for kernel $version" >&2; exit 1; fi
mkdir -p "$destination"
cp "$rootfs/boot/$kernel" "$destination/vmlinuz"
cp "$initrd" "$destination/initrd"
