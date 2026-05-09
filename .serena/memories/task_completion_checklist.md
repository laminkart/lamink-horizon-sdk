# Task Completion Checklist

Before finishing code changes:
- Check `git status --short` and distinguish own edits from pre-existing user edits. This repository is often used with uncommitted experiment/Docker changes, so avoid reverting unrelated changes.
- For Python package changes, run `colcon test --packages-select <package_name> --event-handlers console_direct+` from the workspace root when ROS dependencies are available. For narrow pure-Python logic, `python3 -m pytest -q <package>/test` can be useful after sourcing/installing dependencies.
- For C++/message package changes, run `colcon build --symlink-install --packages-select <package_name>` and then `colcon test --packages-select <package_name> --event-handlers console_direct+`.
- After `colcon test`, run `colcon test-result --verbose` if failures occur or to summarize results.
- If mission config, launch, or package data files change, verify they are included in the relevant `setup.py` `data_files` or CMake `install()` rules.
- If adding/changing console scripts, verify `setup.py` entry points and package dependencies in `package.xml`.
- For launch changes, at minimum run `python3 -m py_compile <launch_file.py>`; for YAML config changes, parse the touched YAML files with Python/YAML if available.
- For Dockerfile or Docker script changes, run `docker build --check` on the affected Dockerfile when possible. For `docker/dockerfile-suave`, use `--build-arg BASE_IMAGE=kasm-jammy:dev` if GHCR cannot authorize the default base.
- For shell script changes, run `bash -n <script>`.
- If touching MAVROS simulation wiring, preserve the working default `fcu_url` of `udp://0.0.0.0:14550@14555` unless intentionally changing the `sim_vehicle` port setup.
- If adding a new managing subsystem, verify ROS interface compatibility with `/diagnostics`, `/task/request`, `/task/cancel`, and the system_modes change mode services.
- Note any tests that could not be run because ROS/Gazebo/ArduSub/MAVROS/Docker dependencies are unavailable in the current environment.