# Validation evidence — v0.3 integration

The release consists of separate layers; do not promote a result from one layer to another.

1. Source regression suite: 39 tests, local and current GitHub test job passed. Includes durable simulation controls, authenticated API, local-only transport, verified downloads, image catalog, ONNX postprocessing, bundled CLI discovery and fresh boot evidence.
2. Resource bundle: run 39192823835 passed. Three original weights (Qwen3, Whisper, YOLO11n), two fixed engine source archives and PlantDoc full image archive hash/byte counts checked.
3. Target engine compilation and isolated inference: latest ISO run 39192878940 pending at report preparation. Report is generated only if real Qwen/Whisper/ONNX/eSpeak checks pass.
4. Actual ISO boot: BIOS and UEFI QEMU gates pending at report preparation. Each boots actual ISO with no NIC, 4GiB RAM and two emulated CPU cores. Serial logs are deleted before each fresh boot to reject stale markers.
5. Physical hardware and field acceptance: not run. No physical driver, crop-specific trained model, calibrated movement/irrigation or embedded firmware is certified by these tests.

Earlier build run 39192331936 compiled llama.cpp successfully and failed configuring whisper.cpp because target Git was absent. The Ubuntu package list now includes Git. Earlier resource run 39192595086 failed because NumPy was not installed before vision tests; dependency setup is now explicit and the replacement resource run passed.

Architecture decisions and residual issues are recorded in progress.md. Further acceptance needs actual CPU/RAM, controller models, motor drivers, pump specifications, sensors, wiring and persistent storage configuration. Until those are known and tested, all actuation remains simulation only.

## Completed evidence

Rootfs build run 39192878940 successfully compiled both engines and passed Qwen Arabic response generation, Whisper reference transcription, ONNX general image inference and eSpeak Arabic WAV generation in a loopback-only network namespace. Original artifact 12161056066 contains the built ISO and reports; ZIP size 3,301,800,581 bytes.

Independent validation run 39193640954 downloaded that exact artifact and verified ISO SHA256SUMS. BIOS and UEFI each reached local API readiness in 70.01 seconds with no NIC, QEMU TCG, 4GiB RAM and two vCPUs. Validation artifact 12161600154 contains serial logs, checksum and reports. Guest model inference was not tested; rootfs inference evidence is separate. The original build job's overall failure was a log-directory ownership issue before QEMU boot, corrected by independent validation and the future workflow.

Skill integration commit adds developer guidance/resources for subsequent builds; the existing v0.3 ISO bytes are unchanged.
