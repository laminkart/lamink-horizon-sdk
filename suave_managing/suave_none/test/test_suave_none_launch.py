# Copyright 2026 KAS Lab
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for the no-manager launch description."""

import importlib.util
from pathlib import Path

from launch.actions import DeclareLaunchArgument


def _load_launch_description():
    launch_path = (
        Path(__file__).parents[1] / 'launch' / 'suave_none.launch.py')
    spec = importlib.util.spec_from_file_location(
        'suave_none_launch', launch_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.generate_launch_description()


def test_launch_arguments_are_declared_once():
    """Verify launch arguments are not duplicated."""
    launch_description = _load_launch_description()
    argument_names = [
        entity.name
        for entity in launch_description.entities
        if isinstance(entity, DeclareLaunchArgument)
    ]

    assert len(argument_names) == len(set(argument_names))
    assert argument_names.count('result_path') == 1
