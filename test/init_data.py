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


test_app = [
    {
        'application_name': 'test_app',
        'bitstream': "test_bit.bin",
        'channels': [],
        'channel_groups': [],
        'initial_registers_values': [],
        'macro': [],
        'parameters': [],
        'peripherals': [],
        'test_misc_field': 'value'
    },
    {
        'application_name': 'test_app_2',
        'bitstream': "test_bit_2.bin",
        'channels': [],
        'channel_groups': [],
        'initial_registers_values': [],
        'macro': [],
        'parameters': [],
        'peripherals': [],
        'test_misc_field': 'value'
    }
]

test_users = [
    {'username': 'test_admin', 'pw_hash': 'hash', 'role': 'admin'},
    {'username': 'test_user', 'pw_hash': 'hash', 'role': 'user'},
    {'username': 'test_operator', 'pw_hash': 'hash', 'role': 'operator'}
]
