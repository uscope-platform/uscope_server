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

class CompilerBridge:

    def compile(self, file_content: str, file_type: str, dma_io=None):

        if file_type == 'asm':
            return self.compile_asm(file_content, file_type)
        elif file_type == 'C':
            return self.compile_c(file_content, file_type, dma_io=dma_io)


    def compile_c(self, file_content: str, file_type: str, dma_io=None):

        compilation_specs = {
                "input_file": '/tmp/fCore_toolchain_in.c',
                "output_format": "json",
                "output_file": "/tmp/output.json",
            }

        if dma_io:
            dma_specs = list()
            for item in dma_io:
                addr_list = item["address"].split(",")
                addr_list = list(map(int, addr_list))
                if len(addr_list) == 1:
                    addr_list = int(item["address"])
                dma_string = {"type": item["type"], "address": addr_list}
                dma_str = '"' + item["associated_io"] + '"' + " : " + json.dumps(dma_string)
                dma_specs.append(dma_str)
            compilation_specs["dma_io"] = dma_specs

        templates_dir = os.environ.get("TEMPLATES_DIR")

        with open(templates_dir + '/compiler_spec.jinja2') as f:
            tmpl = Template(f.read())
            spec = tmpl.render(compilation_specs)

        with open("/tmp/cc_specs.json", 'w') as f:
            f.write(spec)
            f.close()

        with open("/tmp/fCore_toolchain_in.c", 'w') as f:
            f.write(file_content)
            f.close()

        result = subprocess.run(["fCore_cc", "/tmp/cc_specs.json"],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        if not os.path.exists("/tmp/output.json"):
            if result.stdout:
                raise ValueError('INTERNAL ERROR:\n' + result.stdout.decode())
            else:
                raise ValueError('INTERNAL ERROR: Compiler output not found.')

        with open("/tmp/output.json") as json_file:
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
            os.remove("/tmp/fCore_toolchain_in.c")
            os.remove("/tmp/cc_specs.json")
            os.remove("/tmp/output.json")

        return out['compiled_program'], program_size

    def compile_asm(self, file_content: str, file_type: str):

        fCore_has_input = '/tmp/fCore_toolchain_in.c'
        fCore_has_output = '/tmp/output.json'

        with open(fCore_has_input, 'w') as f:
            f.write(file_content)
            f.close()

        result = subprocess.run(['fCore_has', '--json', '--o', fCore_has_output, '--f', fCore_has_input],
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