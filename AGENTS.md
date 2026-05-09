# Repository Guidelines

## Project Structure & Module Organization

This repository is a ROS 2 Humble workspace for SUAVE, a self-adaptive underwater vehicle exemplar. Core managed-system Python nodes live in `suave/suave/`, with launch files in `suave/launch/`. Monitoring nodes are in `suave_monitor/`, missions and mission configs in `suave_missions/`, metrics in `suave_metrics/`, and experiment orchestration in `suave_runner/`. Managing subsystems are under `suave_managing/`, including `suave_random`, `suave_metacontrol`, `suave_none`, and the C++ BehaviorTree.CPP package `suave_bt`. Custom services are defined in `suave_msgs/srv/`. Tests are usually in each package's `test/` directory. Docker assets are in `docker/`, runner scripts in `runner/`, and documentation in `docs/source/`.

## Build, Test, and Development Commands

Run commands from the ROS workspace root unless noted.

```bash
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
colcon build --symlink-install --packages-select suave_runner
colcon test --packages-select suave_runner --event-handlers console_direct+
colcon test-result --verbose
```

Use `source install/setup.bash` after building. Run the exemplar with `ros2 launch suave_missions mission.launch.py adaptation_manager:=bt`, or use `cd runner && ./example_run.sh` for a full example.

## Coding Style & Naming Conventions

Python packages use `ament_python`, `rclpy`, four-space indentation, snake_case modules/functions/parameters, and PascalCase classes. Keep ROS node entry points as module-level `main()` functions and register console scripts in `setup.py`. C++ code in `suave_bt` targets C++17 and uses package headers under `include/suave_bt/`. Follow nearby launch, config, and package-data installation patterns.

## Testing Guidelines

Python tests use `pytest` plus ROS linters such as `ament_flake8`, `ament_pep257`, and `ament_copyright`. Name tests `test_*.py` and place them in the package `test/` directory. For CMake packages, use `colcon build` and `colcon test` on the affected package. Note any skipped tests when Gazebo, ArduSub, MAVROS, or Docker dependencies are unavailable.

## Commit & Pull Request Guidelines

Recent commits use short imperative subjects, for example `add statistical_analysis` or `pass mission_config to task_bridge_none`; an emoji prefix appears occasionally for fixes. Keep commits focused and mention the affected package when useful. Pull requests should describe behavior changes, list test commands and results, link related issues, and include screenshots or logs for simulator, UI, or mission-run changes.

## Agent-Specific Instructions

Before editing, check `git status --short` and preserve unrelated user changes. Prefer `rg` for searches and keep changes scoped to the relevant ROS package.
