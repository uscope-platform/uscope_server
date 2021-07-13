import json
import os
import subprocess

class CompilerBridge:

    def compile(self, file_content: str):

        fCore_has_input = '/tmp/fCore_has_in.s'
        fCore_has_output = '/tmp/output.json'

        text_file = open(fCore_has_input, 'w')
        n = text_file.write(file_content)
        text_file.close()


        subprocess.run(['fCore_has', '--json', '--o', fCore_has_output, fCore_has_input])

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