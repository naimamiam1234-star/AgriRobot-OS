# Offline AI development ISO builder

The v0.3 recipe installs verified Qwen3, Whisper and YOLO11n weights, compiles pinned llama.cpp/whisper.cpp, exports ONNX vision, and installs Arabic eSpeak NG. See OFFLINE-AI-v0.3-ar.md for scope and commands. No trained crop/insect specialist, ROS, GUI, physical driver, disk installer or Secure Boot certification is claimed.

Use a disposable Ubuntu 24.04 amd64 build machine with mount/chroot/network-namespace capabilities and at least 40GB free disk. Network is required to build, not to run bundled inference. Building changes files under iso/work and dist; it never writes a disk device.

```sh
sudo apt-get update
sudo apt-get install debootstrap ubuntu-keyring squashfs-tools xorriso grub-pc-bin grub-efi-amd64-bin mtools dosfstools python3-venv qemu-system-x86 ovmf
python3 -m venv /tmp/agri-tests
/tmp/agri-tests/bin/pip install numpy==1.26.4
/tmp/agri-tests/bin/python -m unittest discover -v
sudo bash scripts/preflight.sh
sudo bash iso/build.sh --build
python3 tests/boot/run.py dist/AgriRobot-0.3-offline-ai-amd64.iso
```

The workflow performs these checks on GitHub Ubuntu runners. Read the exact run conclusion: an in-progress or failed run is not a completed release. Artifacts are retained 30 days, include checksums, asset manifest, rootfs inference report, boot catalog and BIOS/UEFI logs. Failed boot runs may upload diagnostic artifacts; inspect boot-validation.json before use.

The rootfs smoke gate runs actual inference in an isolated network namespace with loopback only. It checks Qwen response generation, Whisper's English JFK reference recording, general ONNX image inference and Arabic WAV generation. It does not measure field diagnosis accuracy, Arabic speech recognition accuracy or audible speech quality. QEMU BIOS/UEFI gates separately check the actual ISO's local API startup, 4GiB RAM, 2 CPUs, TCG, no NIC. They do not prove inference inside a booted guest or operation on physical hardware.

Build direct engine sources and original weights are pinned by SHA256 and byte count in config/assets.lock.json. Export/runtime Python direct versions are pinned, but transitive dependencies and wheel hashes are not fully locked; freeze manifests record what was resolved. This is not a fully reproducible binary build.

Do not enable physical irrigation from the Live image. Persistent storage, hardware identity, wiring, calibration and field acceptance remain required. Measure boot time, peak RAM and inference latency on the target hardware; LZ4 and on-demand language model startup do not guarantee a specific speed.
