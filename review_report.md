# SUAVE Repository Review Report

**Date:** 2026-05-09
**Scope:** Simplicity, code reuse, functional bugs, experiment runner workflow, Dockerfiles, reproducibility.
**Method:** Full codebase read + codex peer-review validation.
**Policy:** Read-only. No code was modified.

---

## Table of Contents

1. [Functional Bugs](#1-functional-bugs)
2. [Code Quality and Reuse](#2-code-quality-and-reuse)
3. [Experiment Runner Workflow](#3-experiment-runner-workflow)
4. [Docker and Reproducibility](#4-docker-and-reproducibility)
5. [CI Pipeline](#5-ci-pipeline)
6. [Summary Table](#6-summary-table)

---

## 1. Functional Bugs

### 1.1 ✅ `MissionTimeConstrained.call_service()` is an exact duplicate of the parent

**File:** `suave_missions/suave_missions/time_constrained_mission.py`
**Severity:** Medium

`MissionTimeConstrained` overrides `call_service()` with a body that is character-for-character identical to `MissionPlanner.call_service()` (the parent class). The override provides no new behaviour and masks the inheritance. If the parent implementation is fixed or changed, this subclass will silently retain the old broken version.

**Fix:** Delete the method from `MissionTimeConstrained`; the parent implementation is already inherited.

**Status:** Completed. `MissionTimeConstrained` no longer overrides
`call_service()`, so service calls use `MissionPlanner.call_service()`.

---

### 1.2 ✅ `suave_none.launch.py` — `result_path_arg` added twice

**File:** `suave_managing/suave_none/launch/suave_none.launch.py`
**Severity:** Low (cosmetic/silent)

The `LaunchDescription([...])` list includes `result_path_arg` at two positions. ROS 2 launch silently accepts this without error, but it indicates a copy-paste error and obscures intent.

```
return LaunchDescription([
    result_path_arg,   # first occurrence
    result_path_arg,   # DUPLICATE — should be removed
    result_filename_arg,
    ...
])
```

**Status:** Completed. The duplicate `result_path_arg` entry was removed from
the `LaunchDescription`, and a launch-structure regression test now asserts
that launch arguments are declared once.

---

### 1.3 `/tmp/mission.done` IPC sentinel not cleared before each run

**Files:** `suave_metrics/suave_metrics/mission_metrics.py`, `suave_runner/suave_runner/suave_runner.py`
**Severity:** Medium

The experiment runner waits for `/tmp/mission.done` to appear, which the metrics node creates via a shell command after saving results. `remove_done_file()` is called at the *experiment* boundary (before the loop over runs), but not before each *individual run*. If the metrics node from one run writes the file just as the next run is starting, that run appears to complete instantly and its results are never actually saved.

Additional concerns:
- The path `/tmp/mission.done` is hardcoded in both writer and reader. If two SUAVE instances run on the same host (even sequentially without a clean `/tmp`), they interfere.
- If the metrics node crashes before saving, the sentinel is never written and the runner waits until `run_duration` timeout (up to 600 s) with no results recorded.
- The sentinel creation uses the deprecated `subprocess` wrapper rather than the `subprocess` module directly.

**Fix:** Call `remove_done_file()` at the start of every *run*, not just every experiment. Consider replacing the sentinel file with a ROS 2 action or a result topic so completion carries result status.

---

### 1.4 ✅  `recover_thrusters_lc.py::call_service()` leaks clients and never awaits results

**File:** `suave/suave/recover_thrusters_lc.py`
**Severity:** High

```python
def call_service(self, srv_type, srv_name, request):
    service = self.create_client(srv_type, srv_name)   # new client every call
    while not service.wait_for_service(timeout_sec=1.0):
        ...
    future = service.call_async(request)
    return future   # future is never awaited by caller
```

Two problems:
1. A new `rclpy` service client is created on every invocation and never destroyed — this is a memory and resource leak (ROS 2 middleware allocates DDS endpoints per client).
2. `call_async()` returns a `Future`; returning it without spinning until completion means the callers receive a pending future that is never resolved. The actual MAVROS parameter-set calls to recover thrusters may silently time out and be discarded.

The correct pattern (used in `MissionPlanner.call_service`) is to create the client once in `on_configure()`, store it, and call `executor.spin_until_future_complete(future)`.

---

### 1.5 ✅ `suave.repos` — mutable branch refs break reproducibility

**File:** `suave.repos`
**Severity:** High (for a benchmark)

Three of eight VCS dependencies use mutable branch names instead of commit SHAs:

| Dependency | `version` value | Risk |
|---|---|---|
| `mc_mdl_tomasys` | `ros2` | branch name — mutable |
| `mros_ontology` | `main` | branch name — mutable |
| `mc_mros_reasoner` | `master` | branch name — mutable |

A push to any of these upstream branches can silently change what is checked out, making results across different build dates incomparable. The other five dependencies correctly use commit hashes or release tags.

**Fix:** Pin all three to a specific commit SHA.

---

### 1.6 ✅ `TaskBridgeRandom` parameter name mismatch with config

**Files:** `suave_managing/suave_random/suave_random/task_bridge_random.py`, `suave_missions/config/mission_config.yaml`
**Severity:** Medium

In `task_bridge_random.py`:
```python
self.declare_parameter('adaptation_period', 15)
```

In `mission_config.yaml` under `/task_bridge/ros__parameters`:
```yaml
adapt_period: 30
```

The config key `adapt_period` does not match the declared parameter `adaptation_period`. ROS 2 will silently use the default value (15 s) and ignore the config file entry. The random adaptation fires every 15 s regardless of what the YAML says.

**Status:** Completed. `TaskBridgeRandom` now declares and reads `adapt_period`, matching the mission YAML files. The random launch node is also named `task_bridge`, so `/task_bridge` scoped YAML parameters apply to the node.

---

### 1.7 `water_visibiity_threshold` spelling error propagated

**Files:** `suave_missions/config/mission_config.yaml`, `suave_missions/config/runner_mission_config.yaml`, `suave_metrics/suave_metrics/mission_metrics.py`
**Severity:** Low

The parameter is declared and read with the same misspelling (`visibiity`, missing one `l`) consistently across YAML and Python, so it works — but it is confusing for users who try to set this parameter by spelling it correctly. ROS 2 would silently use the default value if a user provides the correctly-spelled version.

---

### 1.8 `bluerov_gazebo.py` — hardcoded depth constant

**File:** `suave/suave/bluerov_gazebo.py`
**Severity:** Low

```python
# TODO: make this a ros param
self.ground_depth_gz = -20
self.altitude = 1.25
```

Both `ground_depth_gz` and `altitude` are hardcoded. Experiments using a different world depth or desired altitude require code changes. The TODO acknowledges this but it has remained unfixed.

---

## 2. Code Quality and Reuse

### 2.1 ~80% boilerplate duplication across managing subsystem launch files

**Files:**
- `suave_managing/suave_none/launch/suave_none.launch.py`
- `suave_managing/suave_random/launch/suave_random.launch.py`
- `suave_managing/suave_bt/launch/suave_bt.launch.py`
- `suave_managing/suave_metacontrol/launch/suave_metacontrol.launch.py`

**Severity:** Medium

Each file independently declares and wires:
- `silent_arg` + `configure_logging` OpaqueFunction
- `result_path_arg`, `result_filename_arg`, `mission_config_arg`
- `mission_node` (identical `time_constrained_mission` node, same params)
- `mission_metrics_node` (identical node, only `adaptation_manager` string differs)
- `suave_launch` include (only `task_bridge: True/False` differs)

This means a change to any shared argument (e.g., adding a new mission config parameter) must be manually replicated in four files. A shared `suave_base.launch.py` that accepts `adaptation_manager` and `task_bridge` as arguments could eliminate this duplication.

---

### 2.2 `mission.launch.py` is a dispatch wrapper that does not compose well

**File:** `suave_missions/launch/mission.launch.py`
**Severity:** Medium

This file's only job is to conditionally include one of four managing subsystem launch files. However, those subsystem launch files already contain `mission_node` and `mission_metrics_node` duplicated inside them. The result is:
- The managing subsystem launches ARE standalone (can be called directly), which is good.
- But they carry mission infrastructure that conceptually belongs to `suave_missions`.
- Adding a fifth managing subsystem requires writing another ~80-line launch file replicating all boilerplate.

A cleaner design: the managing subsystem launches provide only the manager-specific nodes; `mission.launch.py` (or a shared base) provides mission/metrics nodes and includes the chosen manager launch.

---

### 2.3 `setup.py` metadata is incomplete across packages

**Severity:** Low

All `ament_python` packages have `description='TODO: Package description'` and `license='TODO: License declaration'`. Additionally, `suave_missions/setup.py` has a truncated maintainer email: `e.g.alberts@` (missing the domain). These fields appear in ROS package indexes and should be filled for a public exemplar.

---

### 2.4 `const_dist_mission` is deprecated but still fully wired

**File:** `suave_missions/launch/mission.launch.py`, `suave_missions/suave_missions/const_dist_mission.py`
**Severity:** Low

The launch file describes `mission_type` as `[time_constrained_mission or const_dist_mission (deprecated)]`. The deprecated option still has a console_script entry point and appears in `mission_type_arg`. It should either be removed or its deprecation should be documented with the recommended migration path.

---

### 2.5 `mission_config.yaml` and `runner_mission_config.yaml` are near-duplicates

**Files:** `suave_missions/config/mission_config.yaml`, `suave_missions/config/runner_mission_config.yaml`
**Severity:** Medium

The two configs are almost identical but differ in:

| Parameter | `mission_config.yaml` | `runner_mission_config.yaml` |
|---|---|---|
| `time_limit` | 300 s | 200 s |
| `water_visibility_period` | 80 s | 120 s |
| `result_path` | present | absent |

The `result_path` only in `mission_config.yaml` means interactive runs write to `~/suave/results` by default, but runner-managed runs get `result_path` injected programmatically. This is correct but not obvious. Any new parameter added to one file must be manually mirrored.

---

### 2.6 Three `planta_exp*_mission_config.yaml` files exist but are undocumented

**Files:** `suave_missions/config/planta_exp1_mission_config.yaml`, `planta_exp2_mission_config.yaml`, `planta_exp3_mission_config.yaml`
**Severity:** Low

These configs appear to be experiment-specific overrides (e.g., `exp1` sets `water_visibility_min/max` to 2.5 for constant visibility). They are installed via `data_files` glob but are not referenced in any launch file or documentation. Users cannot discover them or understand their intended use.

---

## 3. Experiment Runner Workflow

### 3.1 Startup delays rely on fixed `time.sleep(10)` with no readiness check

**File:** `suave_runner/suave_runner/suave_runner.py`
**Severity:** Medium

Three 10-second sleeps are hardcoded with no check that the process is actually ready:
- After launching ArduPilot
- After launching simulation
- Post-run cooldown

On slow machines, 10 s is insufficient; on fast machines it wastes 30 s per run. With 40 runs (4 managers × 10 runs), this adds up to 20 minutes of pure sleep per full campaign.

A readiness check (e.g., polling the ArduSub SITL UDP port, or waiting for MAVROS `/mavros/state` to become available) would be more robust and faster.

---

### 3.2 `run_duration` and mission `time_limit` are independent timeouts with undocumented interaction

**File:** `suave_runner/suave_runner/suave_runner.py`, `suave_missions/config/runner_mission_config.yaml`
**Severity:** Medium

- `run_duration` (default: 600 s) — runner-side timeout; kills all processes if `/tmp/mission.done` doesn't appear.
- `time_limit` (200 s in `runner_mission_config.yaml`) — mission-side timeout; tells `MissionTimeConstrained` to abort and call `mission_metrics/save`.

If `run_duration` fires before the metrics node has saved results (e.g., slow save), results are lost silently. There is no documentation of the intended relationship or recommended values. The runner logs a warning on timeout but does not record partial data.

---

### 3.3 Experiment configuration uses JSON-in-YAML

**File:** `suave_runner/config/runner_config.yml`
**Severity:** Low

JSON objects are embedded as YAML block scalars (`|`). This requires double parsing (YAML to string, then `json.loads`) and means the config cannot be validated by a YAML linter. Native YAML nesting would be simpler and require fewer moving parts.

Note: switching to native YAML nesting requires updating `ExperimentRunnerNode` (which calls `json.loads`) and the test fixtures in `test_suave_runner.py`.

---

### 3.4 `random.seed(100)` is hardcoded and undocumented

**File:** `suave_runner/suave_runner/suave_runner.py` line 43
**Severity:** Low

The fixed seed makes perturbation sequences reproducible across independent runs — desirable for a benchmark — but it is not documented anywhere as intentional and cannot be overridden via config without code changes.

**Recommendation:** Document the intent, expose it as a ROS parameter `random_seed` with default `100`.

---

### 3.5 No checkpoint/resume capability

**File:** `suave_runner/suave_runner/suave_runner.py`
**Severity:** Medium

`generate_mission_config_files()` creates all per-run configs upfront, but the runner has no way to resume from a partially-completed batch. If the runner crashes at run 7 of 40, the experimenter must manually skip completed runs by editing `runner_config.yml`. A simple state file (or checking for existing result CSVs) would make long campaigns more resilient.

---

### 3.6 ArduPilot stderr discarded when `experiment_logging: false`

**File:** `suave_runner/suave_runner/suave_runner.py`
**Severity:** Low

When `experiment_logging` is false, ArduPilot's stdout and stderr are redirected to `subprocess.DEVNULL`. Any ArduPilot crash or error that causes a run to hang is invisible. The runner will wait until `run_duration` timeout (up to 600 s) with no diagnostic output.

**Recommendation:** Always log ArduPilot output to a per-run log file in `result_path`, regardless of `experiment_logging`.

---

## 4. Docker and Reproducibility

### 4.1 ✅ `dockerfile-suave` uses `apt full-upgrade -y`

**File:** `docker/dockerfile-suave`
**Severity:** High (reproducibility)

The command `apt full-upgrade -y` upgrades ALL installed packages to whatever is current at build time. Two builds on different days will produce different images. For a benchmark where reproducibility is a primary goal, this should be replaced with a pinned set of package upgrades, or omitted entirely (accepting that the base image provides pinned versions).

---

### 4.2 ✅ Three `suave.repos` dependencies use mutable branch refs

*(See also §1.5)*
**File:** `suave.repos`
**Severity:** High

The `dockerfile-suave-headless` and `dockerfile-suave` both run `vcs import src < suave.repos`. If any of `mc_mdl_tomasys` (`ros2`), `mros_ontology` (`main`), or `mc_mros_reasoner` (`master`) receives a breaking commit upstream, both images fail to build or produce subtly different behaviour with no indication of what changed.

---

### 4.3 `kasm-jammy` base image used without digest pinning in CI

**File:** `.github/workflows/container.yml`
**Severity:** Medium

```yaml
- name: Build and push suave image
  with:
    build-args: BASE_IMAGE=${{ env.REGISTRY }}/kas-lab/kasm-jammy:latest
```

The `dockerfile-suave` build uses `kasm-jammy:latest` as its base. If the push of `kasm-jammy` fails or races, the `suave` image may use a stale base. Pinning to the image digest (`@sha256:...`) emitted by the build step would guarantee consistency.

---

### 4.4 ✅ `dockerfile-suave` does not pin Python scientific dependencies

**File:** `docker/dockerfile-suave`
**Severity:** Medium (reproducibility inconsistency)

`dockerfile-suave-headless` correctly pins `pandas==2.0.2 scipy==1.15.2 numpy==1.26.4`. `dockerfile-suave` installs these packages without version pins. The GUI image therefore gets whatever is current at build time, meaning statistical analysis results may differ between GUI and headless image runs.

---

### 4.5 ✅ `empy` installed via both `apt` and `pip` in `dockerfile-suave`

**File:** `docker/dockerfile-suave`
**Severity:** Low

The Debian package `python3-empy=3.3.4-2` is installed via `apt`, then uninstalled via `pip uninstall empy`, then reinstalled via `pip install empy==3.3.4`. This fragile dual-path installation exists because ROS 2 Humble has `empy` version conflicts with some packages. The approach works but is opaque. A comment explaining why this is needed would help maintainers.

---

### 4.6 ✅ `build_docker_images.sh` has no error checking

**File:** `build_docker_images.sh`
**Severity:** Medium

The script runs multiple `docker build` commands sequentially without `set -e` or explicit error checking between steps. A failed intermediate build (e.g., `kasm-jammy`) will not stop subsequent builds, which may then use a stale or non-existent base image.

**Fix:** Add `set -e` at the top of the script.

---

### 4.7 ✅ `suave_tools` is absent from headless image

**File:** `docker/dockerfile-suave-headless`
**Severity:** Low

The headless Dockerfile copies packages individually (`suave/`, `suave_managing/`, `suave_metrics/`, `suave_missions/`, `suave_monitor/`, `suave_msgs/`, `suave_runner/`) but omits `suave_tools/`. The GUI image installs `suave_tools/` via `install_suave.sh`. Depending on what `suave_tools` provides (PlotJuggler config, etc.), the headless image may behave differently from the GUI image.

---

## 5. CI Pipeline

### 5.1 Only the `suave` package is tested in CI

**File:** `.github/workflows/main.yml`
**Severity:** High

```yaml
package-name: suave
```

`suave_runner`, `suave_missions`, `suave_monitor`, `suave_metrics`, `suave_bt`, `suave_random`, `suave_metacontrol`, `suave_none`, and `suave_msgs` are never built or tested in CI. A regression in any of these packages would be invisible until someone runs locally.

**Fix:** Extend `package-name` to include all packages (space-separated list is supported by the action).

---

### 5.2 ✅ CI action versions are not pinned to SHA

**File:** `.github/workflows/main.yml`, `.github/workflows/container.yml`
**Severity:** Low

```yaml
uses: actions/checkout@v2
uses: ros-tooling/action-ros-ci@0.3.5
uses: docker/build-push-action@v4
```

These use mutable tags. GitHub recommends pinning to commit SHAs for security and reproducibility. This is particularly relevant for a benchmark repository where CI results should be stable across time.

---

### 5.3 ✅ `vcs-repo-file-url` in CI always points to `main` branch

**File:** `.github/workflows/main.yml`
**Severity:** Medium

```yaml
vcs-repo-file-url: https://raw.githubusercontent.com/kas-lab/suave/main/suave.repos
```

This always fetches the `.repos` file from the `main` branch HEAD, even when the CI is triggered by a PR. A PR that changes `suave.repos` will be tested against the *old* repos file until the PR is merged. The correct approach is to use the raw URL for the PR's own commit SHA, or reference the local checked-out file.

---

## 6. Summary Table

| # | Area | Issue | Severity |
|---|---|---|---|
| 1.1 ✅ | Code quality | `call_service()` duplicated in subclass without change | Medium |
| 1.2 ✅ | Bug | `result_path_arg` duplicated in `suave_none` launch list | Low |
| 1.3 | Bug | `/tmp/mission.done` sentinel not cleared before each run | Medium |
| 1.4 | Bug | `recover_thrusters_lc` leaks clients, callers never await results | **High** |
| 1.5 | Reproducibility | Mutable branch refs in `suave.repos` for 3 deps | **High** |
| 1.6 ✅ | Bug | `adapt_period` vs `adaptation_period` mismatch — config ignored | Medium |
| 1.7 | Quality | `water_visibiity_threshold` spelling error propagated | Low |
| 1.8 | Quality | Hardcoded depth constant with unresolved TODO | Low |
| 2.1 | Reuse | ~80% launch file boilerplate across 4 managing subsystems | Medium |
| 2.2 | Design | Managing subsystem launches own mission infrastructure | Medium |
| 2.3 | Quality | `setup.py` TODO placeholders and truncated email | Low |
| 2.4 | Quality | Deprecated `const_dist_mission` still active | Low |
| 2.5 | Reuse | Two near-duplicate mission config files | Medium |
| 2.6 | Quality | `planta_exp*` configs undocumented and unreferenced | Low |
| 3.1 | Runner | `time.sleep(10)` startup delays, no readiness check | Medium |
| 3.2 | Runner | `run_duration` vs `time_limit` interaction undocumented | Medium |
| 3.3 | Runner | JSON-in-YAML for experiment config | Low |
| 3.4 | Runner | Hardcoded undocumented `random.seed(100)` | Low |
| 3.5 | Runner | No checkpoint/resume for long experiment campaigns | Medium |
| 3.6 | Runner | ArduPilot stderr silently discarded on errors | Low |
| 4.1 | Docker | `apt full-upgrade` makes GUI image non-reproducible | **High** |
| 4.2 | Docker | Same mutable `.repos` branch refs used in Docker builds | **High** |
| 4.3 | Docker | `kasm-jammy` not digest-pinned in CI build chain | Medium |
| 4.4 | Docker | Python sci deps unpinned in GUI image, pinned in headless | Medium |
| 4.5 | Docker | `empy` dual apt/pip install is opaque, fragile | Low |
| 4.6 | Docker | `build_docker_images.sh` lacks `set -e` | Medium |
| 4.7 | Docker | `suave_tools` missing from headless image | Low |
| 5.1 | CI | Only `suave` package tested, 9+ packages untested | **High** |
| 5.2 | CI | Action versions not SHA-pinned | Low |
| 5.3 | CI | `.repos` fetched from `main` HEAD even in PR context | Medium |

---

### Priority Recommendations

**Immediate (reproducibility-critical for a benchmark):**
1. ~~Pin `mc_mdl_tomasys`, `mros_ontology`, `mc_mros_reasoner` to commit SHAs in `suave.repos` (affects both local builds and Docker images).~~
2. ~~Remove `apt full-upgrade -y` from `dockerfile-suave`; pin Python scientific deps to match headless image.~~
3. ~~Fix `recover_thrusters_lc.py::call_service()` — resource leak and missing await are silent correctness bugs.~~
4. ~~Fix the `adapt_period` / `adaptation_period` parameter name mismatch — the random manager silently ignores its config.~~
5. Extend CI to build and test all packages, not just `suave`.

**Short-term (workflow quality):**
6. Call `remove_done_file()` before each individual run, not just each experiment.
7. Replace JSON-in-YAML experiment config with native YAML nesting.
8. ~~Add `set -e` to `build_docker_images.sh`.~~
9. ~~Delete the duplicate `call_service()` from `MissionTimeConstrained`.~~
10. Expose `random_seed` as a configurable ROS parameter and document the reproducibility intent.

**Medium-term (maintainability):**
11. Create a shared base launch file to eliminate the ~80% duplication across managing subsystem launches.
12. Fill in `setup.py` metadata (`description`, `license`, `maintainer_email`).
13. Replace `time.sleep(10)` startup delays with readiness probes.
14. ~~Pin CI action versions to commit SHAs.~~
15. Document the `planta_exp*` configs or move them to a documented examples directory.
