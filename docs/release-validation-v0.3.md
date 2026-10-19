# Validation evidence — v0.3 integration

The release consists of separate layers; do not promote a result from one layer to another.

1. Source regression suite: 39 tests, local and current GitHub test job passed. Includes durable simulation controls, authenticated API, local-only transport, verified downloads, image catalog, ONNX postprocessing, bundled CLI discovery and fresh boot evidence.
2. Resource bundle: run 39192823835 passed. Three original weights (Qwen3, Whisper, YOLO11n), two fixed engine source archives and PlantDoc full image archive hash/byte counts checked.
3. Target engine compilation and isolated inference: latest ISO run 39192878940 pending at report preparation. Report is generated only if real Qwen/Whisper/ONNX/eSpeak checks pass.
4. Actual ISO boot: BIOS and UEFI QEMU gates pending at report preparation. Each boots actual ISO with no NIC, 4GiB RAM and two emulated CPU cores. Serial logs are deleted before each fresh boot to reject stale markers.
5. Physical hardware and field acceptance: not run. No physical driver, crop-specific trained model, calibrated movement/irrigation or embedded firmware is certified by these tests.

Earlier build run 39192331936 compiled llama.cpp successfully and failed configuring whisper.cpp because target Git was absent. The Ubuntu package list now includes Git. Earlier resource run 39192595086 failed because NumPy was not installed before vision tests; dependency setup is now explicit and the replacement resource run passed.

Architecture decisions and residual issues are recorded in progress.md. Further acceptance needs actual CPU/RAM, controller models, motor drivers, pump specifications, sensors, wiring and persistent storage configuration. Until those are known and tested, all actuation remains simulation only.
