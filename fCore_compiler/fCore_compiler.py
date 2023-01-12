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

class CompilerBridge:

    def compile(self, file_content: str, file_type:str):
        tool = ''
        if file_type == 'asm':
            tool = 'fCore_has'
        elif file_type == 'C':
            tool = 'fCore_cc'

        fCore_has_input = '/tmp/fCore_toolchain_in.c'
        fCore_has_output = '/tmp/output.json'

        with open(fCore_has_input, 'w') as f:
            f.write(file_content)
            f.close()

        result = subprocess.run([tool, '--json', '--o', fCore_has_output, '--f', fCore_has_input],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        if not os.path.exists(fCore_has_output):
            if result.stdout:
                raise ValueError('INTERNAL ERROR:\n' + result.stdout.decode())
            else:
                raise ValueError('INTERNAL ERROR: Compiler output not found.')

        with open(fCore_has_output) as json_file:
            out = json.load(json_file)

        if 'error_code' not in out:
            raise ValueError('INTERNAL ERROR: The fCore_cc compiler returned a malformed message')

        if out['error_code'] != '':
            raise ValueError(out['error_code'])

        if 'program_size' in out:
            program_size = out['program_size']
        else:
            program_size = -1

        if os.environ.get("KEEP_FCORE_PRODUCTS") != "TRUE":
            os.remove(fCore_has_input)
            os.remove(fCore_has_output)

        return out['compiled_program'], program_size

if __name__ == '__main__':
    cb = CompilerBridge()
    print(cb.compile("add r1, r1, r1"))