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
