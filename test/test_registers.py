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
        app = app_factory.create_app()
        with app.test_client() as client:
            yield client

def test_register_descriptions(client):
    # pre-test setup, select application
    response = client.get('/application/specs/AdcTest')
    # test proper
    known_good_response = b'{"peripheral_name":"ADC_processing","registers":[{"description":"This register controls the thresholds for the low (latching mode) and low-falling (normal mode) thresholds, for the filtered (lower word) and fast acting (higher word) comparators","direction":"R/W","field_descriptions":["Threshold for the filtered comparator","Threshold for the fast acting comparator"],"field_names":["Filtered threshold","Fast threshold"],"offset":"0x0","register_format":"words","register_name":"Comparators threshold 1","value":0},{"description":"This register controls the thresholds for the low-raising (normal mode) thresholds, for the filtered (lower word) and fast acting (higher word) comparators","direction":"R/W","field_descriptions":["Threshold for the filtered comparator","Threshold for the fast acting comparator"],"field_names":["Filtered threshold","Fast threshold"],"offset":"0x4","register_format":"words","register_name":"Comparators threshold 2","value":0},{"description":"This register controls the thresholds for the high-falling (normal mode) thresholds, for the filtered (lower word) and fast acting (higher word) comparators","direction":"R/W","field_descriptions":["Threshold for the filtered comparator","Threshold for the fast acting comparator"],"field_names":["Filtered threshold","Fast threshold"],"offset":"0x8","register_format":"words","register_name":"Comparators threshold 3","value":0},{"description":"This register controls the thresholds for the high (latching mode) and high-raising (normal mode) thresholds, for the filtered (lower word) and fast acting (higher word) comparators","direction":"R/W","field_descriptions":["Threshold for the filtered comparator","Threshold for the fast acting comparator"],"field_names":["Filtered threshold","Fast threshold"],"offset":"0xC","register_format":"words","register_name":"Comparators threshold 4","value":0},{"description":"This register controls the value of the tap coefficients #1(low word) and #2(high word)","direction":"R/W","field_descriptions":["1st tap for the FIR filter","2nd tap for the FIR filter"],"field_names":["Tap #1","Tap #2"],"offset":"0x10","register_format":"words","register_name":"filter tap 1","value":0},{"description":"This register controls the value of the tap coefficients #2(low word) and #3(high word)","direction":"R/W","field_descriptions":["3rd tap for the FIR filter","4th tap for the FIR filter"],"field_names":["Tap #3","Tap #4"],"offset":"0x14","register_format":"words","register_name":"filter tap 2","value":0},{"description":"This register controls the value of the tap coefficients #4(low word) and #5(high word)","direction":"R/W","field_descriptions":["5th tap for the FIR filter","6th tap for the FIR filter"],"field_names":["Tap #5","Tap #6"],"offset":"0x18","register_format":"words","register_name":"filter tap 3","value":0},{"description":"This register controls the value of the tap coefficients #6(low word) and #7(high word)","direction":"R/W","field_descriptions":["7th tap for the FIR filter","8th tap for the FIR filter"],"field_names":["Tap #7","Tap #8"],"offset":"0x1C","register_format":"words","register_name":"filter tap 4","value":0},{"description":"This register controls the value of the tap coefficient #9(low word)","direction":"R/W","offset":"0x20","register_format":"single","register_name":"filter tap 5","value":0},{"description":"This register stores the additive(high word) and multiplicative(low word) coefficients for a first order calibration","direction":"R/W","field_descriptions":["additive offset correction coefficient","multiplicative gain correction coefficient"],"field_names":["Offset coefficient1","gain correction"],"offset":"0x24","register_format":"words","register_name":"calibration","value":0},{"description":"Main control register for the ADC post processing module","direction":"R/W","offset":"0x28","register_format":"complex","register_name":"Control register","value":0}],"version":0.1}\n'
    response = client.get('/registers/ADC_processing/descriptions')
    assert known_good_response in response.data