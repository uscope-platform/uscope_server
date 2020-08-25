import cppyy
from ctypes import c_uint32, c_int


class CompilerBridge:

    def __init__(self):
        cppyy.add_include_path('/usr/include/antlr4-runtime')  ##
        cppyy.add_include_path('/usr/local/include/fcore_has')  ##
        cppyy.include('fcore_has.hpp')  ##

        cppyy.load_library('libantlr4-runtime.so')  ##
        cppyy.add_library_path('/usr/local/lib/fcore_has')
        cppyy.load_library('fchas.so')
        self.program_raw = (c_uint32*4096)()
        self.program_size_raw = c_int(0)

    def compile(self, file_content: str):
        try:
            cppyy.gbl.fCore_has_embeddable_s(file_content, self.program_raw, self.program_size_raw)
            return self.program_raw[:], self.program_size_raw.value
        except cppyy.gbl.std.runtime_error as error:
            raise ValueError(str(error).split('runtime_error: ')[1])