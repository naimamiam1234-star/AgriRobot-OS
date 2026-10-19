# AgriRobot development

Read skills/agrirobot-robotics/SKILL.md for the robotics skill map, then the relevant upstream skill via its wrapper. Pinned sources and SHA256 values are in config/robotics-skills.lock.json. Imported examples require validation against actual dependencies; they are not implemented AgriRobot features.

Use ROS2 guidance for a new middleware integration, but check the actual installed distro before code changes. ROS is currently not implemented in the runtime. The selected SkiROS2 master documents ROS1/catkin; its name is not proof of ROS2/Jazzy compatibility. ASPIRE/ManiSkill require separate simulation/training environments. Furhat examples require their SDK. Robot Framework skills govern tests, not physical robot actuation.

Preserve the fail-disabled physical boundary and distinguish declared wiring from observed identity/evidence. A language model must not authorize direct actuator commands. Keep simulation, rootfs inference, ISO boot and physical field tests separate. See docs/STATUS.md and docs/release-validation-v0.3.md; verify exact current evidence before claims.

Run source tests with python3 -m unittest discover -v (NumPy 1.26.4 required for vision tests). Run bash -n iso/build.sh scripts/*.sh for build script changes. Keep large models/datasets out of Git and preserve pinned downloads and licenses. The skills folder is lightweight documentation/resources copied by subsequent ISO builds; adding skills does not install their framework dependencies or retrain models.
