# SUAVE Container Execution Rule

For this project, always run anything related to SUAVE execution inside the `suave_runner` Docker container. This includes tests, ROS launches, `colcon build`, `colcon test`, direct `pytest`, simulator/runtime checks, and commands that depend on ROS/SUAVE packages.

Do not assume the host machine has SUAVE or ROS dependencies installed. Do not run SUAVE tests or ROS commands on the host.

Use the container's default sourced workspace configuration and avoid overriding `PYTHONPATH`, `ROS_LOG_DIR`, or similar ROS/Python environment variables unless the user explicitly asks.

Default command pattern:

```bash
docker exec suave_runner bash -lc 'cd /home/ubuntu-user/suave_ws && source /opt/ros/humble/setup.bash && source install/setup.bash && <command>'
```

Example focused pytest:

```bash
docker exec suave_runner bash -lc 'cd /home/ubuntu-user/suave_ws && source /opt/ros/humble/setup.bash && source install/setup.bash && python3 -m pytest -q -rs src/suave/suave/test/test_recover_thrusters_lc.py'
```