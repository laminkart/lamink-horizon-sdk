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

"""Tests for BlueROVGazebo parameters and setpoint helpers."""

import pytest
import rclpy
from geometry_msgs.msg import Point, Pose, PoseStamped
from rclpy.node import Node
from rclpy.parameter import Parameter

from suave.bluerov_gazebo import BlueROVGazebo


@pytest.fixture
def rclpy_context():
    """Create an isolated rclpy context."""
    context = rclpy.context.Context()
    rclpy.init(context=context)
    try:
        yield context
    finally:
        rclpy.shutdown(context=context)


class BlueROVGazeboTestDouble(BlueROVGazebo):
    """BlueROVGazebo test double that bypasses the MAVROS wrapper."""

    def __init__(self, node_name='test_bluerov_gz', **kwargs):
        """Create a lightweight BlueROVGazebo test double."""
        Node.__init__(self, node_name, **kwargs)
        self.local_pos_received = False

        self.declare_parameter('ground_depth_gz', -20.0)
        self.declare_parameter('altitude', 1.25)

        self.ground_depth_gz = self.get_parameter('ground_depth_gz').value
        self.altitude = self.get_parameter('altitude').value

        self.last_setpoint = None

    def setpoint_position_local(self,
                                x=.0,
                                y=.0,
                                z=.0,
                                rx=.0,
                                ry=.0,
                                rz=.0,
                                rw=1.0,
                                fixed_altitude=True):
        """Record the call and return a synthetic PoseStamped."""
        if fixed_altitude and not self.local_pos_received:
            return None
        if fixed_altitude:
            z = self.ground_depth_gz + self.altitude
        ps = PoseStamped()
        ps.pose.position.x = x
        ps.pose.position.y = y
        ps.pose.position.z = z
        self.last_setpoint = ps
        return ps


def test_bluerov_gazebo_uses_default_depth_and_altitude(rclpy_context):
    """Verify default Gazebo depth and fixed altitude values."""
    node = BlueROVGazeboTestDouble(context=rclpy_context)
    try:
        assert node.ground_depth_gz == -20.0
        assert node.altitude == 1.25
    finally:
        node.destroy_node()


def test_bluerov_gazebo_uses_parameter_overrides(rclpy_context):
    """Verify Gazebo depth and fixed altitude are configurable."""
    node = BlueROVGazeboTestDouble(
        context=rclpy_context,
        parameter_overrides=[
            Parameter('ground_depth_gz', value=-42.0),
            Parameter('altitude', value=3.5),
        ])
    try:
        assert node.ground_depth_gz == -42.0
        assert node.altitude == 3.5
    finally:
        node.destroy_node()


def test_setpoint_position_gz_returns_none_before_local_pos(rclpy_context):
    """setpoint_position_gz returns None when local_pos has not been received."""
    node = BlueROVGazeboTestDouble(context=rclpy_context)
    try:
        assert node.local_pos_received is False
        assert node.setpoint_position_gz(Pose()) is None
    finally:
        node.destroy_node()


def test_setpoint_position_gz_fixed_altitude_z(rclpy_context):
    """setpoint_position_gz uses ground_depth_gz + altitude for z."""
    node = BlueROVGazeboTestDouble(context=rclpy_context)
    node.local_pos_received = True
    try:
        gz_pose = Pose(position=Point(x=1.0, y=2.0, z=-5.0))
        setpoint = node.setpoint_position_gz(gz_pose, fixed_altitude=True)
        assert setpoint is not None
        assert setpoint.pose.position.x == pytest.approx(1.0)
        assert setpoint.pose.position.y == pytest.approx(2.0)
        assert setpoint.pose.position.z == pytest.approx(-20.0 + 1.25)
    finally:
        node.destroy_node()


def test_setpoint_position_gz_no_fixed_altitude_preserves_z(rclpy_context):
    """setpoint_position_gz uses the input z when fixed_altitude=False."""
    node = BlueROVGazeboTestDouble(context=rclpy_context)
    node.local_pos_received = True
    try:
        gz_pose = Pose(position=Point(x=3.0, y=4.0, z=-15.0))
        setpoint = node.setpoint_position_gz(gz_pose, fixed_altitude=False)
        assert setpoint is not None
        assert setpoint.pose.position.z == pytest.approx(-15.0)
    finally:
        node.destroy_node()


def test_setpoint_position_gz_does_not_mutate_input(rclpy_context):
    """setpoint_position_gz does not modify the caller's Pose object."""
    node = BlueROVGazeboTestDouble(context=rclpy_context)
    node.local_pos_received = True
    try:
        gz_pose = Pose(position=Point(x=1.0, y=2.0, z=-5.0))
        node.setpoint_position_gz(gz_pose, fixed_altitude=True)
        assert gz_pose.position.z == pytest.approx(-5.0)
    finally:
        node.destroy_node()


def test_setpoint_position_local_returns_none_before_local_pos(rclpy_context):
    """setpoint_position_local returns None when local_pos has not been received."""
    node = BlueROVGazeboTestDouble(context=rclpy_context)
    try:
        assert node.setpoint_position_local(fixed_altitude=True) is None
    finally:
        node.destroy_node()


def test_setpoint_position_local_fixed_altitude_z(rclpy_context):
    """setpoint_position_local uses ground_depth_gz + altitude for z."""
    node = BlueROVGazeboTestDouble(context=rclpy_context)
    node.local_pos_received = True
    try:
        setpoint = node.setpoint_position_local(
            x=5.0, y=6.0, z=-99.0, fixed_altitude=True)
        assert setpoint is not None
        assert setpoint.pose.position.x == pytest.approx(5.0)
        assert setpoint.pose.position.y == pytest.approx(6.0)
        assert setpoint.pose.position.z == pytest.approx(-20.0 + 1.25)
    finally:
        node.destroy_node()
