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
import hashlib


class CacheHitException(Exception):
    pass


class CompilerBridge:

    def compile(self, file_content: str, file_type: str, dma_io=None, cached_hash="", headers=None):

        if file_type == 'asm':
            return self.process_asm(file_content)
        elif file_type == 'C':
            return self.process_c(file_content, dma_io=dma_io, cached_hash=cached_hash, headers=headers)

    def process_c(self, file_content: str, dma_io=None, cached_hash="", headers=None):

        dma_specs = dict()
        if dma_io:
            for item in dma_io:
                addr_list = item["address"].split(",")
                addr_list = list(map(int, addr_list))
                if len(addr_list) == 1:
                    addr_list = int(item["address"])
                dma_string = {"type": item["type"], "address": addr_list}
                dma_specs[item["associated_io"]] = dma_string

        spec = self.produce_compiler_specs(dma_specs)
        spec['headers'] = list()
        headers_cat = ""
        if headers:
            for h in headers:
                headers_cat += h['content']
                spec['headers'].append('/tmp/' + h['name'] + '.h')

        spec = json.dumps(spec, indent=4)

        design_id = spec + file_content + headers_cat
        sha = hashlib.sha256()
        sha.update(design_id.encode())
        design_hash = sha.hexdigest()

        if design_hash == cached_hash and dma_io is not None:
            raise CacheHitException("cached")
        else:
            return self.compile_c(spec, file_content, headers, design_hash)

    def compile_c(self, compilation_spec, program_content, headers, design_hash):

        with open("/tmp/cc_specs.json", 'w') as f:
            f.write(compilation_spec)
            f.close()

        with open("/tmp/fCore_toolchain_in.c", 'w') as f:
            f.write(program_content)
            f.close()

        if headers:
            for h in headers:
                with open('/tmp/' + h['name'] + '.h', 'w') as f:
                    f.write(h['content'])
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

        return out['compiled_program'], program_size, design_hash

    def process_asm(self, file_content: str):

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

        return out['compiled_program'], program_size, ""

    def get_cached_binary(self, file_content: str, build_settings: str):
        hashes = hash(file_content + build_settings)


    def produce_compiler_specs(self, dma_specs):
        res = dict()
        res['input_file'] = '/tmp/fCore_toolchain_in.c'
        res['output'] = {
            'format': 'json',
            'file': '/tmp/output.json'
        }
        res['force'] = True
        res['dma_io'] = dma_specs
        return res


if __name__ == '__main__':
    cb = CompilerBridge()
    print(cb.compile("add r1, r1, r1"))
