# Copyright 2021 Filippo Savi
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

import datetime as dt
import copy

class MockSettingsStore:
    def __init__(self):
        self._store = {}

    def get_per_user_value(self, name, username):
        return self._store[name + '__' + username]

    def set_per_user_value(self, name, value, username):
        self._store[name + '__' + username] = value

    def get_per_server_value(self, name):
        return self._store[name]

    def set_per_server_value(self, name, value):
        self._store[name] = value

    def delete_per_server_value(self, name):
        del self._store[name]

    def clear_settings(self):
        self._store = {}

    def dump(self):
        pass

    def restore(self, data):
        pass

class MockAuthStore:
    def __init__(self):
        self._users_table = {}
        self._tokens_table = {}

    def add_user(self, content):
        self._users_table[content['username']] = {'pw_hash': content, 'role': content['role']}

    def get_password_hash(self, username):
        return self._users_table[username]['pw_hash']

    def get_user(self, username):
        return self._users_table[username]

    def remove_user(self, username):
        del self._users_table[username]

    def get_token(self, selector):
        tok = self._tokens_table[selector]
        return {'username': tok.username, 'expiry': tok.expiry.timestamp(), 'validator': tok.validator}

    def add_token(self, selector, token_obj):
        timestamp = dt.datetime.fromtimestamp(token_obj['expiry'])
        record = {'username': token_obj['username'], 'timestamp': timestamp, 'validator': token_obj['validator']}
        self._tokens_table[selector] = record

    def dump(self):
        pass

    def restore(self, data):
        pass

    def remove_token(self, username):
        pass


class MockElementsAuthStore:

    def __init__(self):
        self._applications_table = {}
        self._bitstreams_table = {}
        self._peripherals_table = {}
        self._programs_table = {}
        self._scripts_table = {}

    def add_application(self, app):
        misc_app = copy.copy(app)

        entries_to_remove = ('application_name', 'bitstream', 'clock_frequency', 'channels', 'channel_groups',
                             'initial_registers_values', 'macro', 'parameters', 'peripherals')
        for k in entries_to_remove:
            misc_app.pop(k, None)

        item = {'application_name': app["application_name"], 'bitstream': app['bitstream'],
                'clock_frequency': app['clock_frequency'], 'channels': app['channels'],
                'channel_groups': app['channel_groups'], 'miscellaneous': misc_app,
                'initial_registers_values': app['initial_registers_values'], 'macro': app['macro'],
                'parameters': app['parameters'], 'peripherals': app['peripherals']}

        self._applications_table[app["application_name"]] = item

    def _construct_app(self, item):
        result = {'application_name': item["application_name"], 'bitstream': item['bitstream'],
                  'clock_frequency': item['clock_frequency'], 'channels': item['channels'],
                  'channel_groups': item['channel_groups'],
                  'initial_registers_values': item['initial_registers_values'], 'macro': item['macro'],
                  'parameters': item['parameters'], 'peripherals': item['peripherals']}
        for i in item['miscellaneous']:
            result[i] = item['miscellaneous'][i]
        return result

    def get_applications_dict(self):
        result = {}
        for key in self._applications_table:
            result[key] = self._construct_app(self._applications_table[key])
        return result

    def get_application(self, name):
        return self._construct_app(self._applications_table[name])

    def edit_application(self, app):
        self.remove_application(app["application_name"])
        self.add_application(app)

    def remove_application(self, name):
        del self._applications_table[name]

    # SCRIPTS

    def _construct_script(self, id, item):
        result = {'id': id, 'name': item['name'], 'content': item['script_content'], 'triggers': item['triggers']}
        return result

    def get_scripts_dict(self):
        result = {}
        for key in self._scripts_table:
            result[key] = self._construct_script(key, self._scripts_table[key])
        return result

    def get_script(self, script_id):
        return self._construct_script(script_id, self._scripts_table[script_id])

    def add_script(self, script):
        item = {'name': script['name'], 'content': script['script_content'], 'triggers': script['triggers']}
        self._scripts_table[script["id"]] = item

    def edit_script(self, script):
        self.remove_script(script['id'])
        self.add_script(script)

    def remove_script(self, script):
        del self._scripts_table[script['id']]

    # PROGRAMS

    def _construct_program(self, id, item):
        if 'hex' in item:
            hex_field = item['hex']
        else:
            hex_field = []

        result = {'id': id, 'name': item['name'],
                  'content': item['program_content'], 'type': item['program_type'], 'hex': hex_field}
        return result

    def get_program(self, id):
        return self._construct_program(id, self._programs_table[id])

    def get_programs_dict(self):
        result = {}
        for key in self._programs_table:
            result[key] = self._construct_program(key, self._programs_table[key])
        return result

    def add_program(self, program):
        if 'hex' in program:
            hex_field = program['hex']
        else:
            hex_field = []

        item = {'name': program['name'],
                'content': program['program_content'], 'type': program['program_type'], 'hex': hex_field}
        self._programs_table[program["id"]] = item

    def edit_program(self, program):
        self.remove_program(program["id"])
        self.add_program(program)

    def remove_program(self, program):
        del self._programs_table[program["id"]]

    # PERIPHERALS

    def get_peripherals_dict(self):
        result = {}
        for key in self._peripherals_table:
            result[key] = self._peripherals_table[key]
        return result

    def get_peripheral(self, name):
        return self._peripherals_table[name]

    def add_peripheral(self, periph: dict):
        item = {'name': periph["peripheral_name"], 'version': periph['version'], 'registers': periph['registers']}
        self._peripherals_table['name'] = item

    def edit_peripheral(self, periph):
        self.remove_peripheral(periph["peripheral_name"])
        self.add_peripheral(periph)

    def remove_peripheral(self, peripheral):
        del self._peripherals_table[peripheral]

    # VERSIONS

    def get_peripherals_hash(self):
        pass

    def get_applications_hash(self):
        pass

    def get_scripts_hash(self):
        pass

    def get_program_hash(self):
        pass

    def get_bitstreams_hash(self):
        pass

    # BITSTREAMS

    def get_bitstreams_dict(self):
        result = {}
        for key in self._bitstreams_table:
            result[key] = self._bitstreams_table[key]
        return result

    def get_bitstream(self, id):
        return self._bitstreams_table[id]

    def add_bitstream(self, bitstream: dict):
        item = {'id':bitstream['id'], 'path': bitstream['path']}
        self._bitstreams_table[bitstream['id']] = item

    def edit_bitstream(self, bitstream):
        self.remove_bitstream(bitstream["id"])
        self.add_bitstream(bitstream)

    def remove_bitstream(self, bitstream_id):
        del self._bitstreams_table[bitstream_id]

    def dump(self):
        pass

    def restore(self, data):
        pass
