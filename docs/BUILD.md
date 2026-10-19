# Development ISO builder

Status: recipe written; no ISO has been produced or boot-tested. This builds an Ubuntu development base with the local simulation API and reference library. It does NOT yet install ROS 2, AI engines/weights, visual UI, physical drivers or a disk installer. Secure Boot is not configured or tested. BIOS/UEFI boot has not been verified.

Use a disposable Ubuntu 24.04 amd64 VM or build machine with mount/chroot capabilities and at least 30GB free disk. The build creates files and mountpoints under iso/work; it does not write an ISO to a USB device or overwrite a system disk. The recipe has not been exercised end-to-end.

```bash
sudo apt-get update
sudo apt-get install debootstrap ubuntu-keyring squashfs-tools xorriso grub-pc-bin grub-efi-amd64-bin mtools dosfstools
python3 -m unittest discover -v
sudo bash scripts/preflight.sh
sudo bash iso/build.sh --build
```

The GitHub workflow offers the same build via workflow_dispatch after importing the source into a repository. Nothing has been pushed and no remote workflow has been run. Artifacts, if the workflow succeeds, are retained 7 days. A source ZIP is not an ISO.

## Required next validation

Install QEMU and OVMF on the build machine. Verify both BIOS and UEFI boot, offline startup, /health, /status, service failure/restart and persistence across reboot. Use software emulation if KVM is unavailable; lack of KVM alone is not proof that QEMU cannot run.

```bash
qemu-system-x86_64 -m 4096 -cdrom dist/AgriRobot-0.1-dev-amd64.iso -nic none
```

Do not use this development Live system for physical irrigation. Live storage may be temporary; no automatic repartitioning or persistence setup is supplied.

Measure cold-boot readiness, peak RAM and model response time on the actual target hardware. LZ4 and on-demand model loading are design choices, not proof of a particular startup speed. The current container has no effective mount/chroot capabilities and lacks image-building tools; this blocks the conventional build here.
