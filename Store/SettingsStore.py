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

import redis
import json


class SettingsStore:
    def __init__(self, clear_settings=True, host='redis'):
        self.redis = redis.Redis(host=host, port=6379, db=0)
        if clear_settings:
            self.clear_settings()

    def get_per_user_value(self, name, username):
        return json.loads(self.redis.get(name+username))

    def set_per_user_value(self, name, value, username):
        self.redis.set(name+username, json.dumps(value))

    def get_per_server_value(self, name):
        return json.loads(self.redis.get(name))

    def set_per_server_value(self, name, value):
        self.redis.set(name, json.dumps(value))

    def delete_per_server_value(self, name):
        self.redis.dump(name)

    def clear_settings(self):
        print("CLEARED SETTINGS")
        self.redis.flushdb()

    def dump(self):
        pass

    def restore(self, data):
        pass