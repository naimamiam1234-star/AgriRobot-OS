## ASPIRE

Source: https://github.com/NVlabs/ASPIRE/tree/fa00f0ef2bc1d91d594b9aa502c22133c9f538f7

Research workspace: preserve development, validation and held-out seed boundaries; evaluate terminal physical outcomes, not prose reports. Its language-generated Python trials are not a sandbox. Keep simulation separate from device control and use its calibrated robot runbooks only for the specified robot. It is not a pre-trained agricultural policy.

## ManiSkill

Source: https://github.com/mani-skill/ManiSkill/tree/62ff3a5896b4d5b4cf0ac4c8d79afe600c9404a3

Simulation/training framework based on SAPIEN. Record robot embodiment, task, seed, simulator/version, sensors and success criterion. Verify Vulkan/rendering and actual CPU/GPU capability before choosing workloads. Dataset/assets licenses differ from code licenses (README specifies non-commercial assets). Simulation success does not validate real-world irrigation.

## SkiROS2

Source: https://github.com/RobotLabLTH/SkiROS2/tree/c4438e71a25978b14c30191539e4de68943fe863

Model a skill using preconditions, invariants/hold conditions and postconditions. Use a world model with provenance and freshness; behavior-tree failure must lead to explicit recovery. Despite its name, the selected master README documents ROS1/catkin and describes a ROS2 port as work in progress; do not assume Jazzy compatibility. License metadata was unclassified; inspect LICENSE.md before copying code.

## Furhat

Source: https://github.com/FurhatRobotics/example-skills/tree/59b4b4e9ec86f00f9051d7e668b01b04546fd6f7

Social interaction examples require the Furhat SDK/robot, usually Kotlin/Gradle. Reuse interaction-state and ASR recovery concepts through project-specific code; do not import SDK-dependent executables into AgriRobot. A spoken acknowledgment is not proof of actuator execution. Repository reports MIT; verify SDK's separate terms before use.
