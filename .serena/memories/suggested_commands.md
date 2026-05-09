# Suggested Commands

Workspace setup/build:
- From the ROS workspace root, e.g. `/home/gus/ros_workspaces/suave_rebetmc_ws`: `source /opt/ros/humble/setup.bash`.
- Install dependencies from the workspace root: `rosdep install --from-paths src --ignore-src -r -y`.
- Build all packages: `colcon build --symlink-install`.
- Low-memory build: `colcon build --symlink-install --executor sequential --parallel-workers 1`.
- Build selected package: `colcon build --symlink-install --packages-select <package_name>`.
- After build: `source install/setup.bash`.

Testing/linting:
- Test selected package from workspace root: `colcon test --packages-select <package_name> --event-handlers console_direct+`.
- Show test results: `colcon test-result --verbose`.
- Run Python tests directly when dependencies are sourced/available: `python3 -m pytest -q <package>/test`.
- Common package lint tests are pytest tests wrapping `ament_flake8`, `ament_pep257`, and `ament_copyright`.
- CI builds package `suave` through `ros-tooling/action-ros-ci` against ROS 2 Humble and `suave.repos`.

Running SUAVE:
- Try example: `cd runner && ./example_run.sh`.
- Start ArduSub SITL: `sim_vehicle.py -L RATBeach -v ArduSub --model=JSON --console`.
- Start simulation: `ros2 launch suave simulation.launch.py x:=-17.0 y:=2.0`.
- MAVROS launch args include `fcu_url`, `gcs_url`, `mavros_config_yaml`, and `mavros_pluginlists_yaml`; defaults use the local lightweight ArduPilot config in `suave/config/`.
- Start default mission: `ros2 launch suave_missions mission.launch.py`.
- Start mission with manager: `ros2 launch suave_missions mission.launch.py adaptation_manager:=bt result_filename:=measurement_1`.
- Runner launch: `ros2 launch suave_runner suave_runner.launch.py`.
- Runner CLI examples are in `docs/source/run.md` and `suave_runner/README.md`.

Docker:
- Pull/run main GUI image: `docker run -it --shm-size=512m -p 6901:6901 -e VNC_PW=password --security-opt seccomp=unconfined ghcr.io/kas-lab/suave:main`.
- Build local images: `./build_docker_images.sh`.
- Build just the headless image from the repo root: `docker build -t suave-headless:dev -f docker/dockerfile-suave-headless .`.
- Build-check headless Dockerfile: `docker build --check -f docker/dockerfile-suave-headless .`.
- Build-check browser Dockerfile with local base: `docker build --check --build-arg BASE_IMAGE=kasm-jammy:dev -f docker/dockerfile-suave .`.
- If checking `docker/dockerfile-suave` without `BASE_IMAGE`, GHCR access to `ghcr.io/kas-lab/kasm-jammy:latest` may fail with `denied`; use the local `kasm-jammy:dev` base after building it.

Useful Linux/repo commands:
- Fast file search: `rg --files`.
- Fast text search: `rg '<pattern>'`.
- Git status: `git status --short`.
- Inspect package metadata: `find . -maxdepth 3 -name package.xml -print`.