# Development status — 2026-10-19

| Item | Status |
|---|---|
| SQLite events/dose IDs/restart refusal | Implemented and unit-tested, simulation only |
| JSON API, authentication, size bounds, local default | Implemented and tested on loopback |
| Optional local AI/camera/audio adapters | Implemented; missing-dependency and local HTTP integration tests only |
| Real language/vision/audio inference | NOT RUN; weights and engines not bundled |
| Offline catalog and photo SHA256 integrity | Implemented and tested |
| Reference photos | 28 plant-leaf photos plus 5 insect photos; source labels, not expert re-verified diagnoses |
| PlantDoc wider source URL index | Created; additional images NOT downloaded |
| 102 IP102 category names | Reference list included; IP102 photos NOT bundled |
| External disease knowledge | Source links and license notes; no full third-party corpus mirrored |
| Ubuntu ISO recipe and GitHub workflow | Written; shell syntax/preflight/unmount regression tested |
| Actual ISO file and BIOS/UEFI boot | NOT PRODUCED / NOT RUN |
| Startup speed and RAM benchmarks | NOT RUN on target hardware |
| ROS 2 integration and GUI | Planned, not implemented |
| STM32 serial protocol / firmware / real movement | Planned, not implemented |
| Physical water/fertilizer control | Not implemented; all actuation remains absent |
| Cloud inference/weather/synchronization | Planned; no provider keys or cloud calls included |

Limits: unit tests do not certify field safety or a plant diagnosis. The API uses a token and rejects browser mutations but is a development server, not an Internet-facing production service. Persistent=True in simulation is not an inspection of actual Live USB durability.

Review: a fresh read-only reviewer found a recursive-unmount problem in the initial builder; fixed with a RED-to-GREEN regression. Loopback AI transport was hardened to reject redirects and ignore proxies, tested with an actual local HTTP fixture. No second review was claimed.

Deferred test limitation: the preflight unit test currently expects an unprovisioned/unprivileged host, as in this environment and the workflow's initial test job. On a fully provisioned privileged machine it must be adapted to use isolated prerequisite fixtures. The builder's own preflight is separate and is intended to succeed on such a machine. Missing-dependency adapter tests do not prove runtime memory behavior, timeouts or real inference.
