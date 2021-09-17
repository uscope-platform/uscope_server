# Copyright 2021 University of Nottingham Ningbo China
# Author: Filippo Savi <filssavi@gmail.com>
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

import json

import pytest

import app_factory


@pytest.fixture
def client():
        app = app_factory.create_app(debug=True)
        with app.test_client() as client:
            yield client

def test_plotChannels(client):
    # pre-test setup, select application
    response = client.get('/application/specs/AdcTest')
    # test proper
    known_good_response = b'[{"enabled":false,"id":1,"max_value":180,"min_value":0,"name":"Current A"},{"enabled":false,"id":2,"max_value":180,"min_value":0,"name":"Current B"},{"enabled":false,"id":3,"max_value":180,"min_value":0,"name":"Current C"},{"enabled":false,"id":4,"max_value":600,"min_value":0,"name":"Voltage A"},{"enabled":false,"id":5,"max_value":600,"min_value":0,"name":"Voltage B"},{"enabled":false,"id":6,"max_value":600,"min_value":0,"name":"Voltage C"}]\n'
    response = client.get('/plot/channels/specs')
    assert known_good_response in response.data

def test_data(client):
    # pre-test setup, select application
    response = client.get('/application/specs/AdcTest')
    # test proper
    response = client.get('/plot/channels/data')
    data = json.loads(response.data)['data']
    assert len(data) == 1024


