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

"""BlueROV Gazebo pose conversion helpers."""

import copy

from mavros_wrapper.ardusub_wrapper import BlueROVArduSubWrapper


class BlueROVGazebo(BlueROVArduSubWrapper):
    """BlueROV helper that sends Gazebo/map-frame position setpoints."""

    def __init__(self, node_name='bluerov_gz'):
        """Create a BlueROV Gazebo helper node."""
        super().__init__(node_name)

        self.declare_parameter('ground_depth_gz', -20.0)
        self.declare_parameter('altitude', 1.25)

        self.ground_depth_gz = self.get_parameter('ground_depth_gz').value
        self.altitude = self.get_parameter('altitude').value

    def setpoint_position_gz(self, gz_pose, fixed_altitude=True):
        """Send a Gazebo/map-frame position setpoint."""
        if not self.local_pos_received:
            return None

        pose = copy.deepcopy(gz_pose)
        if fixed_altitude:
            pose.position.z = self.ground_depth_gz + self.altitude

        return self.setpoint_position_local(
            pose.position.x, pose.position.y, pose.position.z,
            fixed_altitude=False)

    def setpoint_position_local(self,
                                x=.0,
                                y=.0,
                                z=.0,
                                rx=.0,
                                ry=.0,
                                rz=.0,
                                rw=1.0,
                                fixed_altitude=True):
        """Send a local/map-frame position setpoint."""
        if fixed_altitude and not self.local_pos_received:
            return None

        if fixed_altitude:
            z = self.ground_depth_gz + self.altitude
        return super().setpoint_position_local(x, y, z)
