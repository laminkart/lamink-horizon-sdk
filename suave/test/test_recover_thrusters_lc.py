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

"""Tests for the recover thrusters lifecycle node."""

import threading

import pytest
import rclpy

from rcl_interfaces.msg import Parameter
from rcl_interfaces.msg import ParameterType
from rcl_interfaces.msg import ParameterValue
from rcl_interfaces.msg import SetParametersResult
from rcl_interfaces.srv import SetParameters
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node

from suave.recover_thrusters_lc import RecoverThrustersLC


@pytest.fixture(scope='session', autouse=True)
def rclpy_runtime():
    """Initialize rclpy for the test module."""
    if not rclpy.ok():
        rclpy.init()
    try:
        yield
    finally:
        if rclpy.ok():
            rclpy.shutdown()


@pytest.fixture
def test_node():
    """Create a helper ROS node."""
    node = Node('test_recover_thrusters_helper')
    try:
        yield node
    finally:
        node.destroy_node()


@pytest.fixture
def recover_node():
    """Create the recover thrusters lifecycle node under test."""
    node = RecoverThrustersLC('test_recover_thrusters_lc')
    try:
        yield node
    finally:
        node.destroy_node()


@pytest.fixture
def executor(test_node, recover_node):
    """Spin the helper and recover nodes in a background executor."""
    ex = MultiThreadedExecutor()
    ex.add_node(test_node)
    ex.add_node(recover_node)
    thread = threading.Thread(target=ex.spin, daemon=True)
    thread.start()
    try:
        yield ex
    finally:
        ex.shutdown()
        thread.join(timeout=2.0)


def test_recover_thrusters_uses_configured_client_and_waits_for_response(
        executor, test_node, recover_node):
    """Verify the stored client completes a real ROS service call."""
    requests = []

    def _set_parameters_cb(request, response):
        requests.append(request)
        response.results.append(SetParametersResult(successful=True))
        return response

    service = test_node.create_service(
        SetParameters,
        '/mavros/param/set_parameters',
        _set_parameters_cb
    )

    parameter = Parameter()
    parameter.name = 'SERVO1_FUNCTION'
    parameter.value = ParameterValue(
        type=ParameterType.PARAMETER_INTEGER,
        integer_value=33
    )
    request = SetParameters.Request(parameters=[parameter])

    response = recover_node.call_service(
        recover_node.set_parameters_service, request)

    assert response is not None
    assert len(response.results) == 1
    assert response.results[0].successful is True
    assert len(requests) == 1
    assert requests[0].parameters[0].name == 'SERVO1_FUNCTION'
    assert requests[0].parameters[0].value.integer_value == 33
    assert recover_node.set_parameters_service is not None

    test_node.destroy_service(service)


def test_destroy_set_parameters_service_releases_configured_client(
        recover_node):
    """Verify cleanup destroys the configured parameter client."""
    client = recover_node.set_parameters_service

    recover_node.destroy_set_parameters_service()

    assert client is not None
    assert recover_node.set_parameters_service is None
