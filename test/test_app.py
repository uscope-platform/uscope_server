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

import pytest
from flask_jwt_extended import create_access_token
import app_factory
from .init_data import test_app,test_users

headers = None
@pytest.fixture
def client():
        app = app_factory.create_app()

        app.store.Elements.add_application(test_app[0])
        app.store.Elements.add_application(test_app[1])

        app.store.Auth.add_user(test_users[0])
        app.store.Auth.add_user(test_users[1])
        app.store.Auth.add_user(test_users[2])

        with app.app_context():
            access_token = create_access_token('test_admin')
            global headers
            headers = {
                'Authorization': 'Bearer {}'.format(access_token)
            }
        with app.test_client() as client:
            yield client


def test_getApp(client):


    global headers
    response = client.get('/uscope/application/get/test_app', headers=headers)
    assert test_app[0] == response.json


def test_getAppsDict(client):

    global headers
    response = client.get('/uscope/application/all/specs', headers=headers)
    assert {test_app[0]['application_name']:test_app[0], test_app[1]['application_name']:test_app[1]} == response.json

