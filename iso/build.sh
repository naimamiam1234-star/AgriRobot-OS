#!/usr/bin/env bash
# Development base-image recipe. Not yet boot-validated; no trained models/ROS included.
set -Eeuo pipefail
if [ "${1:-}" != --build ]; then
    echo 'Usage: sudo bash iso/build.sh --build'
    echo 'Creates a development Live ISO; does not write a disk. See docs/BUILD.md.'
    exit 2
fi
project_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
cd "$project_dir"
bash scripts/preflight.sh
work="$project_dir/iso/work"
rootfs="$work/rootfs"
image="$work/image"
if [ -e "$work" ]; then
    echo 'Build directory exists. Inspect it and unmount any mounts before moving it aside.' >&2
    exit 2
fi
mkdir -p "$rootfs" "$image/casper" "$image/boot/grub" "$project_dir/dist"
mounts=()
source scripts/mount-cleanup.sh
trap cleanup_mounts EXIT
debootstrap --arch=amd64 --variant=minbase --include=ca-certificates --components=main,universe \
    --keyring=/usr/share/keyrings/ubuntu-archive-keyring.gpg \
    noble "$rootfs" https://archive.ubuntu.com/ubuntu/
cat > "$rootfs/etc/apt/sources.list" <<'APT'
deb https://archive.ubuntu.com/ubuntu noble main universe
deb https://archive.ubuntu.com/ubuntu noble-updates main universe
deb https://security.ubuntu.com/ubuntu noble-security main universe
APT
cp --dereference /etc/resolv.conf "$rootfs/etc/resolv.conf"
for item in dev proc sys; do
    mount --rbind "/$item" "$rootfs/$item"
    mounts+=("$rootfs/$item")
    mount --make-rslave "$rootfs/$item"
done
printf '#!/bin/sh\nexit 101\n' > "$rootfs/usr/sbin/policy-rc.d"
chmod 755 "$rootfs/usr/sbin/policy-rc.d"
chroot "$rootfs" apt-get update
mapfile -t packages < iso/packages.list
chroot "$rootfs" env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends "${packages[@]}"
mkdir -p "$rootfs/opt/agrirobot" "$rootfs/etc/systemd/system" "$rootfs/var/lib/agrirobot"
cp -a app config docs data "$rootfs/opt/agrirobot/"
chroot "$rootfs" useradd --system --home-dir /var/lib/agrirobot --shell /usr/sbin/nologin agrirobot
chroot "$rootfs" chown agrirobot:agrirobot /var/lib/agrirobot
cp iso/agrirobot.service "$rootfs/etc/systemd/system/"
mkdir -p "$rootfs/etc/systemd/system/multi-user.target.wants"
ln -s /etc/systemd/system/agrirobot.service "$rootfs/etc/systemd/system/multi-user.target.wants/agrirobot.service"
echo agrirobot > "$rootfs/etc/hostname"
printf '127.0.0.1 localhost\n127.0.1.1 agrirobot\n' > "$rootfs/etc/hosts"
printf 'LANG=C.UTF-8\n' > "$rootfs/etc/default/locale"
chroot "$rootfs" update-initramfs -u -k all
chroot "$rootfs" dpkg-query -W --showformat='${Package} ${Version}\n' > "$image/casper/filesystem.manifest"
cp "$image/casper/filesystem.manifest" "$image/casper/filesystem.manifest-desktop"
bash scripts/copy-boot.sh "$rootfs" "$image/casper"
chroot "$rootfs" apt-get clean
rm -f "$rootfs/usr/sbin/policy-rc.d" "$rootfs/etc/machine-id"
touch "$rootfs/etc/machine-id"
cleanup_mounts || { echo 'Unmount failed: refusing to package rootfs' >&2; exit 1; }
mounts=()
du -sx --block-size=1 "$rootfs" | cut -f1 > "$image/casper/filesystem.size"
mksquashfs "$rootfs" "$image/casper/filesystem.squashfs" -noappend -comp lz4
cp iso/grub.cfg "$image/boot/grub/grub.cfg"
printf 'AgriRobot 0.1 development\n' > "$image/README.diskdefines"
grub-mkrescue -o "$project_dir/dist/AgriRobot-0.1-dev-amd64.iso" "$image"
sha256sum dist/AgriRobot-0.1-dev-amd64.iso > dist/SHA256SUMS
xorriso -indev dist/AgriRobot-0.1-dev-amd64.iso -report_el_torito plain 2>&1 | tee dist/boot-catalog.txt
echo 'ISO created; QEMU BIOS/UEFI tests still required. Not a complete offline AI release.'
