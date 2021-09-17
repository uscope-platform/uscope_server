# Copyright 2021 University of Nottingham Ningbo China
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

import pytest

import app_factory


@pytest.fixture
def client():
        app = app_factory.create_app(debug=True)
        with app.test_client() as client:
            yield client


def test_applist(client):
    known_good_response = b'["AdcTest"]\n'
    response = client.get('/application/list')
    assert known_good_response in response.data

def test_appSpecs(client):
    known_good_response = b'{"channels":[{"enabled":false,"id":1,"max_value":180,"min_value":0,"name":"Current A"},{"enabled":false,"id":2,"max_value":180,"min_value":0,"name":"Current B"},{"enabled":false,"id":3,"max_value":180,"min_value":0,"name":"Current C"},{"enabled":false,"id":4,"max_value":600,"min_value":0,"name":"Voltage A"},{"enabled":false,"id":5,"max_value":600,"min_value":0,"name":"Voltage B"},{"enabled":false,"id":6,"max_value":600,"min_value":0,"name":"Voltage C"}],"parameters":[{"default-unit":"kS/s","description":"","max-limit":400,"min-limit":0.1,"parameter_name":"ADC Samping Speed","value":10},{"default-unit":"kHz","description":"","max-limit":150,"min-limit":1,"parameter_name":"Switching Frequency","value":120},{"default-unit":"","description":"","max-limit":100,"min-limit":0,"parameter_name":"Torque Kp","value":1}],"peripherals":[{"name":"Plot","peripheral_id":"Plot","type":"Scope","user_accessible":true},{"base_address":"0x43c00000","image_src":"assets/Images/ADC_processing.png","name":"ADC processing","peripheral_id":"ADC_processing","type":"Registers","user_accessible":true},{"base_address":"0x43c00100","image_src":"assets/Images/SPI.png","name":"SPI","peripheral_id":"SPI","type":"Registers","user_accessible":true},{"base_address":"0x43c00300","name":"GPIO","peripheral_id":"GPIO","type":"Registers","user_accessible":false},{"base_address":"0x43c00400","name":"enable generator","peripheral_id":"enable_generator","type":"Registers","user_accessible":false},{"name":"Tab creator","peripheral_id":"tab_creator","type":"utility","user_accessible":true}]}\n'
    response = client.get('/application/specs/AdcTest')
    assert known_good_response in response.data

def test_appParameters(client):
    # pre-test setup, select application
    response = client.get('/application/specs/AdcTest')
    # test proper
    known_good_response = b'[{"default-unit":"kS/s","description":"","max-limit":400,"min-limit":0.1,"parameter_name":"ADC Samping Speed","value":10},{"default-unit":"kHz","description":"","max-limit":150,"min-limit":1,"parameter_name":"Switching Frequency","value":120},{"default-unit":"","description":"","max-limit":100,"min-limit":0,"parameter_name":"Torque Kp","value":1}]\n'
    response = client.get('/application/parameters')
    assert known_good_response in response.data