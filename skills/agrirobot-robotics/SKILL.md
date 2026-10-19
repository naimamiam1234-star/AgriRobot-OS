---
name: agrirobot-robotics
description: Develop, review and validate AgriRobot OS and offline agricultural robot software. Use for ROS integration, perception, controller identity, motion/irrigation boundaries, robotics testing, ISO evidence, or selecting ASPIRE, ManiSkill, SkiROS2 and Furhat references.
---

# AgriRobot robotics integration

Read the project's AGENTS.md, current implementation and validation reports first. Preserve its existing interfaces and confirmed hardware information. Use the skill map below to load only the instructions needed for the task; load upstream content through each skill's references/upstream/SKILL.md.

| Task | Skills |
|---|---|
| ROS 2 nodes, QoS, lifecycle, launch | ros2; use actual installed distro/API |
| Legacy migration | ros1; never assume ROS1 examples work under ROS2 |
| Architecture, hardware adapters, state machines | robotics-software-principles, robotics-design-patterns |
| Cameras, calibration, fusion, latency | robot-perception |
| Services, deterministic device names, heartbeat | robot-bringup |
| Device/network boundaries and credentials | robotics-security |
| Regression, integration, simulation, HIL | robotics-testing |
| Browser/ROS bridges and telemetry | ros2-web-integration |
| Container-based development | docker-ros2-development |
| Robot Framework test code | rf-language, rf-python-library, rf-libdoc |
| HTTP contract tests | rf-requests or rf-restinstance |
| Browser/mobile/desktop tests | rf-browser or rf-selenium; rf-appium; rf-platynui |
| Test environment, CLI and reports | rf-setup, rf-robotcode, rf-results |

Robot Framework is a test framework, not robot motion middleware. Read [framework-specific guidance](references/frameworks.md) before choosing ASPIRE, ManiSkill, SkiROS2 or Furhat. These references do not install their frameworks or provide policies trained for the agricultural robot.

Apply these project rules:

1. Separate perception, planning, deterministic control and hardware interfaces. Keep language models outside the actuation authorization path.
2. Represent controller identity, declared wiring and observed evidence separately. Include units, timestamps, session IDs and expiry. Never infer arbitrary connected parts from a GPIO value or I2C address alone.
3. Keep startup/reconnection outputs disabled. Require explicit supported hardware configuration and physical calibration before enabling actuators. Test disconnect/restart/duplicate/stale-command behavior.
4. Start the status service without waiting for network or model loading. Keep inference local by default; report missing dependencies explicitly. Load models on demand on weak machines.
5. Distinguish generic object detection from plant/insect diagnosis. Record dataset provenance, splits, metrics and unknown cases before making crop-specific claims.
6. Verify source tests, engine/model inference, actual ISO boot and physical robot behavior separately. Record exact artifact checksum, CPU/RAM, connectivity and limits. Never promote simulation or file presence into physical success.
7. Use upstream commands as references; check versions and project constraints before execution. Preserve attribution and pinned source revisions. Avoid copying illustrative code as production code without tests.

Adding these instructions does not train model weights or create consciousness. The integration persists developer workflows and references; runtime policies require separate implementation and evaluation.
