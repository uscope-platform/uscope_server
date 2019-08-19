import os
import ctypes
import numpy as np

channel_0_data = np.zeros(50000)
channel_data_raw = []


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

    def wait_for_data(self):
        return self.low_level_lib.wait_for_Interrupt()

    def read_data(self):
        rec_data = [0] * 1024
        arr = (ctypes.c_uint32 * len(rec_data))(*rec_data)
        self.low_level_lib.read_data(arr, 1024)
        rec_data = [arr[i] for i in range(1024)]
        return rec_data[::-1]


    def change_timebase(self, timebase):
        pass

if __name__ == '__main__':
    a = uCube_interface(dbg=True)
    while True:
        a.wait_for_data()
        data = a.read_data()
        channel_0_data = np.roll(channel_0_data, len(data))
        channel_0_data[0:len(data)] = data
        channel_data_raw.append(data)

