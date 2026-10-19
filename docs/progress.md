# Execution ledger — AgriRobot-ISO-Implementation-Plan.md

2026-10-19: User requested creation of project folder and disease/insect resources and instructed development to start. Plan accepted through this instruction; native execution.

Isolation: new project repository on develop, no prior main branch or user changes.

Pre-flight interfaces: Controller/Store consumed by service; JSON status consumed by CLI and later UI. AI has no Controller reference. Builder copies tested runtime.

Ruling: implement an honest command-line/JSON-service development release first; visual UI, hardware drivers, trained crop models and boot validation remain explicit release blockers, not simulated completions. Unknown hardware makes actuating drivers speculative.

Ruling: include redistributable reference images with attribution; IP102 is indexed as academic-use only and is not bundled into the OS. No claim of globally exhaustive insect/disease coverage.

Task 1: development subset complete — Store/Controller simulation tests RED (missing modules) → GREEN, restart/duplicate/pending/invalid volumes and approval checks exercised. No physical control implemented.

Task 2: development subset complete — loopback JSON API tests RED → GREEN, real local HTTP requests test auth, browser mutation rejection, size limits, simulation and unknown hardware endpoints. Cloud/sync/weather deferred and marked not implemented.

Task 3: partial — adapters and missing-dependency tests RED → GREEN; actual language/vision/audio inference NOT RUN, no engines or weights downloaded. Additional real loopback transport fixture tests successful content, malformed JSON and redirect rejection.

Task 4: partial — offline photo catalog and source handbook implemented; GUI deferred. 33 real reference images verified by Pillow and SHA256; original labels not revalidated diagnoses. Source URL index contains 2578 PlantDoc entries; these are not downloaded assets. IP102 list has 102 categories; its dataset photos not bundled.

Task 5: partial — ISO recipe/workflow written, shell syntax and fail-closed preflight checked. Actual build blocked in current environment by missing tools and CAP_SYS_ADMIN/CAP_SYS_CHROOT; no image produced. Source workflow not pushed or run remotely.

Task 6: blocked — no ISO exists for BIOS/UEFI testing; no target CPU available for performance claims.

Final review: fresh read-only reviewer checked core/ISO and ran 20 tests. Important recursive-bind cleanup defect reproduced in test then fixed; packaging aborts on unmount failure. Local-only AI transport also hardened and tested RED → GREEN. Final suite expanded to 25 tests.

Final: minor (deferred): preflight test expects an underprivileged/unprovisioned environment, and needs isolated prerequisite fixtures before use on a fully provisioned privileged build host. README/build guide must not imply the test validates all build environments.

Final: minor (deferred): real inference, timeout/memory-pressure and device tests remain unrun; adapter missing-dependency test does not exercise a subprocess. Simulation persistent=True is a test-mode flag, not a Live-storage guarantee.

Ruling: ship a development source archive and separate reference-photo archive now; do not invent a completed ISO or a trained disease model. Cost: another build/test phase is required before a bootable or field-capable release.

GitHub integration: uploaded 74 files preserving the user's initial commit and README, then started run 39189185620. Its test job passed; ISO build reached kernel installation and failed because root-level /vmlinuz is absent (Ubuntu kernel links are inside /boot). Added a version-paired /boot discovery/copy helper and regression fixture. This fixes the observed failure; subsequent build result must be checked separately.

## Offline inference integration — 2026-10-19
Resuming approved ISO plan tasks 3, 5 and 6 under executing-plans.
Ruling: compile pinned llama.cpp b6000 and whisper.cpp v1.7.5 inside target rootfs; preserve verified source archives in ISO. Generic CPU build, no GPU required. Cost: lower performance than per-device tuning.
Added real network-isolated inference gate before ISO packaging (Qwen Arabic response, Whisper English reference recording). Arabic transcription accuracy and agronomic accuracy remain not evaluated.
Readiness now distinguishes installed files from healthy inference; 33 unit tests pass locally. ISO/inference build result pending.

Ruling: export generic YOLO11n to ONNX; install ONNX Runtime and OpenCV without PyTorch in target. Cost: custom postprocessing needs validation; two overlap/low-confidence regression tests added.
Ruling: use explicit eSpeak NG Arabic formant voice instead of redistributing unclear Piper voice dataset. Cost: less natural speech. 36 unit tests pass after preserving the existing models_bundled API key with evidence-based value.
Added actual ISO BIOS/UEFI boot gate, no NIC, serial API readiness marker; tests pending on build runner. No physical control or crop-trained model claim.

Final review: fresh reviewer found two Important defects: bundled STT not discovered by documented CLI, stale QEMU READY logs. Both reproduced RED→GREEN with CLI sanitized-PATH and preseeded-log regression tests.
Final: regraded incomplete models_bundled evidence as Important; readiness now includes ONNX model/runtime and speech output. Regression covers absent runtime with present model.
Final: fixed missing NumPy setup in resource workflow, as demonstrated by failed run 39192595086. Build guide updated to avoid obsolete commands.
Final: minor (deferred): transitive Python dependency/wheel hashes are not fully locked; freeze records installed versions but does not guarantee reproducible resolution.
Final: minor (deferred): boot marker checks guest API only, not guest inference/authenticated status; report now explicitly states that scope. Rootfs inference is tested separately.
