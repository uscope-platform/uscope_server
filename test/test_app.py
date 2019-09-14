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
    known_good_response = b'{"channels":[{"enabled":false,"id":1,"max_value":180,"min_value":0,"name":"Current A"},{"enabled":false,"id":2,"max_value":180,"min_value":0,"name":"Current B"},{"enabled":false,"id":3,"max_value":180,"min_value":0,"name":"Current C"},{"enabled":false,"id":4,"max_value":600,"min_value":0,"name":"Voltage A"},{"enabled":false,"id":5,"max_value":600,"min_value":0,"name":"Voltage B"},{"enabled":false,"id":6,"max_value":600,"min_value":0,"name":"Voltage C"}],"parameters":[{"default-unit":"kS/s","description":"","max-limit":400,"min-limit":0.1,"parameter_name":"ADC Samping Speed","value":10},{"default-unit":"kHz","description":"","max-limit":150,"min-limit":1,"parameter_name":"Switching Frequency","value":120},{"default-unit":"","description":"","max-limit":100,"min-limit":0,"parameter_name":"Torque Kp","value":1}],"tabs":[{"name":"Plot","tab_id":"Plot","type":"Scope","user_accessible":true},{"base_address":"0x43c00000","image_src":"assets/Images/ADC_processing.png","name":"ADC processing","tab_id":"ADC_processing","type":"Registers","user_accessible":true},{"base_address":"0x43c00100","image_src":"assets/Images/SPI.png","name":"SPI","tab_id":"SPI","type":"Registers","user_accessible":true},{"base_address":"0x43c00300","name":"GPIO","tab_id":"GPIO","type":"Registers","user_accessible":false},{"base_address":"0x43c00400","name":"enable generator","tab_id":"enable_generator","type":"Registers","user_accessible":false}]}\n'
    response = client.get('/application/specs/AdcTest')
    assert known_good_response in response.data

def test_appParameters(client):
    # pre-test setup, select application
    response = client.get('/application/specs/AdcTest')
    # test proper
    known_good_response = b'[{"default-unit":"kS/s","description":"","max-limit":400,"min-limit":0.1,"parameter_name":"ADC Samping Speed","value":10},{"default-unit":"kHz","description":"","max-limit":150,"min-limit":1,"parameter_name":"Switching Frequency","value":120},{"default-unit":"","description":"","max-limit":100,"min-limit":0,"parameter_name":"Torque Kp","value":1}]\n'
    response = client.get('/application/parameters')
    assert known_good_response in response.data