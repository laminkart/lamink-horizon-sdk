# Codebase Structure

Top-level folders/files:
- `README.md`, `docs/source/*.md`: main user/developer documentation for install, run, Docker, extending SUAVE, troubleshooting.
- `suave.repos`: VCS dependency file used by CI, workspace setup, and Docker image builds for external deps.
- `docker/`: Docker/Kasm image definitions and install scripts. Important files include `docker/dockerfile-kasm-core-jammy`, `docker/dockerfile-suave`, `docker/dockerfile-suave-headless`, and `docker/src/ubuntu/install/kasm_vnc/install_kasm_vnc.sh`.
- `runner/`: shell scripts for running the exemplar and experiments.
- `.github/workflows/`: CI; `main.yml` uses `ros-tooling/action-ros-ci` targeting ROS 2 Humble, and `container.yml` builds/pushes the browser and headless images.

ROS packages:
- `suave/` (`ament_python`): managed subsystem functionality, launch files, and simulation config. `suave/config/suave_mavros_apm_config.yaml` and `suave/config/suave_mavros_apm_pluginlists.yaml` tailor MAVROS for the lightweight simulation.
- `suave_monitor/` (`ament_python`): monitor nodes such as `thruster_monitor`, `battery_monitor`, `water_visibility_observer` that publish diagnostics/status.
- `suave_missions/` (`ament_python`): mission planners and launch files. Console scripts include `const_dist_mission` and `time_constrained_mission`.
- `suave_metrics/` (`ament_python`): metrics collection, console script `mission_metrics`.
- `suave_runner/` (`ament_python`): experiment runner and statistical analysis. Console scripts `suave_runner` and `statistical_analysis`; contains focused pytest tests. Its Dockerfile now lives at `docker/dockerfile-suave-headless` so it can copy the local checkout.
- `suave_tools/` (`ament_python`): auxiliary tools/config such as PlotJuggler config.
- `suave_msgs/` (`ament_cmake`): ROS service definitions `Task.srv` and `GetPath.srv` via `rosidl_generate_interfaces`.
- `suave_managing/suave_none/` (`ament_python`): no-manager variant launch package.
- `suave_managing/suave_random/` (`ament_python`): random managing subsystem, console script `task_bridge_random`.
- `suave_managing/suave_metacontrol/` (`ament_python`): MROS2/metacontrol managing subsystem, console script `task_bridge_metacontrol`.
- `suave_managing/suave_bt/` (`ament_cmake`): C++ BehaviorTree.CPP managing subsystem. Sources under `src/suave_bt`, headers under `include/suave_bt`, BT XML files under `bts/`, launch files under `launch/`.

Configuration:
- Mission configs live in `suave_missions/config/*.yaml`.
- Runner config lives in `suave_runner/config/runner_config.yml`.
- Package data is installed through each package's `setup.py` or `CMakeLists.txt`.