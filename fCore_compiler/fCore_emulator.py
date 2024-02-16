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
import os
import subprocess
from jinja2 import Template
import hashlib


def emulate(spec):

    with open("/tmp/emu_specs.json", 'w') as f:
        f.write(json.dumps(spec))
        f.close()

    result = subprocess.run(["fCore_emu", "/tmp/emu_specs.json", "--o", "/tmp/results.json", "--debug_autogen"],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd='/tmp')

    if not os.path.exists("/tmp/results.json"):
        if result.stdout:
            raise ValueError('INTERNAL ERROR:\n' + result.stdout.decode())
        else:
            raise ValueError('INTERNAL ERROR: Emulator output not found.')

    with open("/tmp/results.json") as json_file:
        out = json.load(json_file)

    os.remove("/tmp/emu_specs.json")
    os.remove("/tmp/results.json")

    return out

