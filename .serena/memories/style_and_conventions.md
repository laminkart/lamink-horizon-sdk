# Style and Conventions

General:
- Keep edits scoped to individual ROS packages and preserve existing launch/config installation patterns.
- The repo uses Apache-2.0 headers in many files; new substantive files should follow nearby package headers and licensing style.
- Prefer ASCII unless touching files that already require non-ASCII.

Python:
- Packages are ROS 2 `ament_python` packages using `setuptools.setup` and console script entry points.
- Use `extras_require={'test': ['pytest']}` for pytest metadata; avoid reintroducing deprecated `tests_require`.
- Code is mostly plain Python without type hints. Follow existing style unless introducing type hints locally adds clear value.
- ROS nodes subclass `rclpy.node.Node`, declare/read ROS parameters in `__init__`, use `create_publisher`, `create_subscription`, `create_service`, `create_client`, and expose a module-level `main()` for console scripts.
- Existing style uses snake_case for functions, methods, variables, ROS parameters, and file names; PascalCase for classes.
- String formatting often uses `.format(...)`; f-strings are acceptable if they do not make surrounding style inconsistent.
- Lint tests use `ament_flake8` and `ament_pep257`. Keep imports PEP8-compatible, avoid trailing whitespace, and add docstrings where pep257 would require them in new public modules/classes/functions.
- Tests are pytest-based. `suave_runner/test/test_suave_runner.py` exercises runner behavior with `rclpy.init()`/`rclpy.shutdown()` and temporary files under `/tmp/suave`.

C++ (`suave_bt`, `suave_msgs`):
- `suave_bt` is C++17 with `-Wall -Wextra -Wpedantic` enabled. Headers are under `include/suave_bt`, implementation under `src/suave_bt`.
- Behavior tree node names are registered in `src/suave_bt.cpp` and XML trees live under `bts/`.
- `suave_msgs` uses standard ROSIDL service generation in CMake.
- Existing CMake skips some lint checks by setting `ament_cmake_copyright_FOUND` and `ament_cmake_cpplint_FOUND` in test blocks; preserve unless intentionally tightening lint policy.

Launch/config:
- Launch files are Python ROS launch descriptions and are installed by glob patterns in setup/CMake.
- The simulation launch uses MAVROS `node.launch` with local lightweight config/plugin list YAML files. Keep launch args overrideable for `fcu_url`, `gcs_url`, `mavros_config_yaml`, and `mavros_pluginlists_yaml`.
- When adding a new managing subsystem, include SUAVE's base launch with `task_bridge` disabled and wire it into `suave_missions/launch/mission.launch.py` through an `adaptation_manager` condition.
- Mission config changes may require rebuilding the workspace with `colcon build --symlink-install`.

Docker:
- Dockerfiles are intentionally lowercase (`docker/dockerfile-*`). The headless Dockerfile builds from the repository root and copies the local checkout after importing external deps from `suave.repos`.
- Keep `.dockerignore` aligned with repo-root Docker contexts so local build/install/log artifacts and `.serena` do not enter Docker build contexts.