# Development status — 2026-10-19

| Item | Evidence/status |
|---|---|
| SQLite events, dose IDs, restart refusal, stop | Implemented, unit tested, simulation only |
| JSON API authentication, request bounds, loopback transport | Implemented and tested; development HTTP server |
| Local AI integration | Qwen3 GGUF, Whisper tiny, YOLO11n ONNX and eSpeak NG integrated in ISO recipe |
| Full offline asset downloads | Successful GitHub resource run 39192823835, SHA256/size verified |
| Actual rootfs inference | Qwen, Whisper, ONNX and eSpeak passed in build run 39192878940, network-isolated namespace |
| Actual ISO BIOS/UEFI boot | Both passed in exact-artifact validation run 39193640954, no NIC, 70.01s per mode on TCG |
| Source tests | 51 unit tests passed locally and on the current GitHub test job |
| PlantDoc | All 2578 source images downloaded, matched to source Git blobs; archive bundled by recipe |
| Reference catalog | 28 plant-leaf and 5 insect photos, individual attribution and SHA256 verified |
| IP102 | 102 reference class names only; restricted dataset photos not bundled |
| Agricultural diagnosis model | Not trained or field evaluated; generic YOLO is explicitly not a crop diagnosis |
| Controller self-description | Read-only host registry, bounded CRC codec, replay CLI and authenticated context implemented/tested; live transport/firmware pending |
| Physical movement and water/fertilizer actuation | Not implemented, no physical driver exposed |
| ROS and graphical operator UI | Planned, not implemented |
| Internet/cloud/weather sync | Local operation works independently of internet; cloud integrations not implemented |
| Target hardware startup/RAM/accuracy | Not measured; QEMU/rootfs results do not replace hardware tests |
| Persistent Live storage | Operator must prepare/verify; no automatic partitioning or disk installer |

The resource artifact contains original weights, engine source archives and PlantDoc, not installed compiled engines. The ISO recipe builds/install engines separately; only a successful exact ISO build/inference/boot run demonstrates that result.

Resource run: https://github.com/naimamiam1234-star/AgriRobot-OS/actions/runs/39192823835

Resource artifact (1,527,472,678 bytes; expires 2027-01-17): https://github.com/naimamiam1234-star/AgriRobot-OS/actions/runs/39192823835/artifacts/12160243295

Current ISO attempt: https://github.com/naimamiam1234-star/AgriRobot-OS/actions/runs/39192878940

## Review and limits

Fresh review identified bundled CLI engine discovery and stale boot log defects. Both were reproduced and fixed with RED→GREEN regressions. Runtime status now checks all selected model/runtime categories without claiming presence proves healthy inference.

Direct model/source artifacts have fixed sizes and SHA256. Python direct versions are pinned, but transitive dependencies and wheel hashes are not fully locked. Freeze manifests document resolution; fully reproducible binaries remain deferred. The QEMU gate covers guest API readiness only; actual inference is tested separately inside the rootfs without an external network. Arabic transcription accuracy, audible voice quality and field diagnosis remain unevaluated.

The preflight unit fixture assumes an unprivileged/unprovisioned initial test host. Running that particular test on a fully provisioned privileged host may require fixture isolation; the builder's actual preflight should succeed there.

CPU profile: x86_64, SSE4.2/AVX/AVX2/F16C/FMA/BMI2. GGML_NATIVE=OFF does not disable these backend defaults. Check target CPU; this is not a baseline-only amd64 build.

Robotics skills: 22 upstream developer/test skills plus one AgriRobot integration skill; see ROBOTICS-SKILLS-ar.md. Existing ISO artifact 12161056066 was independently checksum/boot-validated; skills are included in future builds.
