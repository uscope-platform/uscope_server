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


