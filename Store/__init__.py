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

from .ElementDataStore import ElementsDataStore
from .AuthStore import AuthStore
from .MockStore import MockAuthStore, MockElementsAuthStore

from sqlalchemy.exc import OperationalError
import os
import time


class Store:
    def __init__(self, clear_settings=True):

        pg_host = os.environ.get("DB_HOST")
        redis_host = os.environ.get("REDIS_HOST")

        pg_available = False
        pg_start_tries_left = 300
        while not pg_available:
            try:
                self.Auth = AuthStore(pg_host)
                self.Elements = ElementsDataStore(host=pg_host)
            except OperationalError:
                if pg_start_tries_left == 0:
                    raise RuntimeError("ERROR: Could not connect to the postgres database")
                pg_start_tries_left -= 1
                time.sleep(0.8)
            else:
                pg_available = True

    def dump(self):
        dump = {'auth': self.Auth.dump(), 'elements': self.Elements.dump()}
        return dump

    def restore(self, data):
        print("restoring Users")
        self.Auth.restore(data['auth'])
        print("restoring Elements")
        self.Elements.restore(data['elements'])


class MockStore:
    def __init__(self):
        self.Auth = MockAuthStore()
        self.Elements = MockElementsAuthStore()

    def dump(self):
        dump = {'auth': self.Auth.dump(), 'elements': self.Elements.dump()}
        return dump

    def restore(self, data):
        print("restoring Users")
        self.Auth.restore(data['auth'])
        print("restoring Elements")
        self.Elements.restore(data['elements'])
