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

        text_file = open(fCore_has_input, 'w')
        n = text_file.write(file_content)
        text_file.close()

        subprocess.run([tool, '--json', '--o', fCore_has_output, '--f', fCore_has_input])

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

        os.remove(fCore_has_input)
        os.remove(fCore_has_output)
        return out['compiled_program'], program_size

if __name__ == '__main__':
    cb = CompilerBridge()
    print(cb.compile("add r1, r1, r1"))