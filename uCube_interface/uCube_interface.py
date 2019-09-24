import os
import ctypes
from .low_level_emulator import emulator
import numpy as np
from threading import Lock

channel_0_data = np.zeros(50000)
channel_data_raw = []

class uCube_interface:
    def __init__(self, driver_file="/dev/uio0", dbg=False):
        self.dbg = dbg
        self.interface_lock = Lock()
        if not self.dbg:
            cwd = os.getcwd()
            lib = cwd + '/uCube_interface/low_level_functions.so'
            src = cwd + '/uCube_interface/low_level_functions.c'
            # Compile low level functions
            os.system('rm '+lib)
            os.system('gcc -shared -g -fPIC -o '+lib+' '+src+'&> /dev/null')
            # Load FPGA with correct bitstream
            os.system("echo 0 > /sys/class/fpga_manager/fpga0/flags")
            os.system("echo AdcTest.bin > /sys/class/fpga_manager/fpga0/firmware")

            self.low_level_lib = ctypes.cdll.LoadLibrary(lib)
        else:
            self.low_level_lib = emulator()
        filename = ctypes.c_char_p(driver_file.encode("utf-8"))

        self.buffer_size = 4 * 4096
        self.low_level_lib.low_level_init(filename, self.buffer_size, 0x7E200000, 0x43c00000)
        self.clock_frequency = 100e6
        return

    def wait_for_data(self):
        self.interface_lock.acquire()
        retval = self.low_level_lib.wait_for_Interrupt()
        self.interface_lock.release()
        return retval

    def read_data(self):
        rec_data = [0] * 1024
        arr = (ctypes.c_uint32 * len(rec_data))(*rec_data)

        self.interface_lock.acquire()
        self.low_level_lib.read_data(arr, 1024)
        self.interface_lock.release()

        rec_data = [arr[i] for i in range(1024)]
        return rec_data

    def change_timebase(self, timebase):

        counter_val = round(timebase/self.clock_frequency**-1)
        self.interface_lock.acquire()
        self.low_level_lib.write_register(0x43c00400, counter_val)
        self.interface_lock.release()

        return

    def read_register(self, address):
        self.interface_lock.acquire()
        val = self.low_level_lib.read_register(address)
        self.interface_lock.release()
        return val

    def write_register(self, address, value):
        self.interface_lock.acquire()
        self.low_level_lib.write_register(address, value)
        self.interface_lock.release()

if __name__ == '__main__':
    a = uCube_interface(dbg=True)
    while True:
        a.wait_for_data()
        data = a.read_data()
        channel_0_data = np.roll(channel_0_data, len(data))
        channel_0_data[0:len(data)] = data
        channel_data_raw.append(data)

