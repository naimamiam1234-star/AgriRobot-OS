# Controller host implementation — approved self-description design

Continue the controller self-description design approved by the user's repeated instruction to complete development. Implement the host-side read-only subsystem first; no firmware/physical acceptance claim.

1. Add a bounded 768-byte, UTF-8 JSON frame codec with CRC32, duplicate-key/nonfinite rejection and protocol/type validation. CRC is transport integrity, not authentication.
2. Add assembly validation, host-owned sessions, ordered frames, firmware conflict detection, heartbeats and expiring component observations. Board declarations are never promoted to verified identity by the board itself.
3. Add a bounded replay CLI and read-only authenticated context endpoint; never connect this evidence layer to actuation. Include an explicitly fictional example assembly with logical port names, not invented physical wiring.
4. Verify corrupt/oversize/replay/old-session/unknown-component/pin-conflict/stale-evidence behavior and preserve existing suite. Record current limitations and publish sources.

Later independent tasks: transport/firmware builds on actual supported boards, identification-probe allowlists, physical tests, UI, crop-specific model training. No automatic arbitrary port probing.
