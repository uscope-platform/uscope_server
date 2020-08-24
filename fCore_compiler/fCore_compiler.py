import cppyy
from ctypes import c_uint32, c_int

if __name__ == "__main__":
    cppyy.add_include_path('/usr/include/antlr4-runtime')
    cppyy.add_include_path('/usr/local/include/fcore_has')
    cppyy.include('fcore_has.hpp')  # bring in C++ definitions

    cppyy.load_library('libantlr4-runtime.so')  # load linker symbol
    cppyy.add_library_path('/usr/local/lib/fcore_has')
    cppyy.load_library('fchas.so')  # load linker symbol
    program_raw = (c_uint32*4096)()
    test_raw = c_int(0)
    cppyy.gbl.fCore_has_embeddable('./test_add.s', program_raw, test_raw)

    program = program_raw[:]
    test = test_raw.value
    print(str(program[0:5]))
    print(str(test))
