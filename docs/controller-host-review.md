# Controller host review — 2026-10-19

Fresh independent read-only review of the controller host implementation: no Critical or Important findings within its bounded read-only scope; acceptable for that scope. Reviewer ran 17 registry/service tests and additional parser probes. Author full suite: 51 tests passed locally and GitHub source test job.

Deferred Minor findings:

1. decode_frame accepts a complete multiline JSON envelope under 768 bytes, while the replay tool splits on physical newline. Future decoder hardening should reject interior literal newlines to align the JSONL contract. encode_frame emits single-line frames; a multiline replay is rejected rather than interpreted as valid hardware evidence.
2. Assembly file CLI loaders use json.loads and silently select the last duplicate JSON key. Expected local configuration remains ambiguous in that case. Use the strict duplicate-rejecting parser for future configuration hardening. This is operator-controlled local input; no HTTP write or live transport exists.

Decisions reaffirmed: CRC is not authentication; session replay state is process-local; the 64-session budget requires reinitialization; file replay timestamps are receipt times, not historical reconstruction. These limits are documented and the module must not serve as physical motion authorization or a deadman controller. Missing firmware/live transport/identification probes/assistant-context integration remain explicit subsequent tasks, not features established by these tests.

ISO inference/boot evidence must be read from its exact CI run separately. No physical hardware acceptance claimed.
