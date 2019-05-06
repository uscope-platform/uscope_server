import os
import ctypes


class uCube_interface:
    def __init__(self, driver_file="/dev/uio0",dbg=False):
        cwd = os.getcwd()
        if dbg:
            lib = cwd + '/low_level_functions.so'
            src = cwd + '/low_level_functions.c'
        else:
            lib = cwd + '/uCube_interface/low_level_functions.so'
            src = cwd + '/uCube_interface/low_level_functions.c'
        # Compile low level functions
        os.system('rm '+lib)
        os.system('gcc -shared -g -fPIC -o '+lib+' '+src+'&> /dev/null')
        # Load FPGA with correct bitstream
        os.system("echo 0 > /sys/class/fpga_manager/fpga0/flags")
        os.system("echo AdcTest.bin > /sys/class/fpga_manager/fpga0/firmware")

        self.low_level_lib = ctypes.cdll.LoadLibrary(lib)

        self.buffer_size = 4*4096

        filename = ctypes.c_char_p(driver_file.encode("utf-8"))
        self.low_level_lib.low_level_init(filename, self.buffer_size, 0x7E200000, 0x43c00000)
        self.acknowledge_interrupt()

    def acknowledge_interrupt(self):
        return self.low_level_lib.acknowledge_interrupt()

    def wait_for_data(self):
        return self.low_level_lib.wait_for_Interrupt()

    def read_data(self):
        data = [0] * 1024
        arr = (ctypes.c_int * len(data))(*data)
        self.low_level_lib.read_data(arr, 1024)
        data = [arr[i] for i in range(1024)]
        return data

if __name__ == '__main__':
    a = uCube_interface(dbg=True)
    while True:
        a.wait_for_data()
        data = a.read_data()
        a.acknowledge_interrupt()
