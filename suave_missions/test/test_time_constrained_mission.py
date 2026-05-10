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

"""Tests for the time-constrained mission planner."""

from suave_missions.mission_planner import MissionPlanner
from suave_missions.time_constrained_mission import MissionTimeConstrained


def test_time_constrained_mission_inherits_call_service():
    """Verify the time-constrained mission uses the parent service helper."""
    assert 'call_service' not in MissionTimeConstrained.__dict__
    assert MissionTimeConstrained.call_service is MissionPlanner.call_service
