import os
import ctypes


class uCube_interface:
    def __init__(self, driver_file="/dev/uio0"):
        cwd = os.getcwd()
        # Compile low level functions
        os.system("rm low_level_functions.so")
        os.system("gcc -shared -fPIC -o low_level_functions.so low_level_functions.c > /dev/null")
        # Load FPGA with correct bitstream
        os.system("echo 0 > /sys/class/fpga_manager/fpga0/flags")
        os.system("echo AdcTest.bin > /sys/class/fpga_manager/fpga0/firmware")

        self.low_level_lib = ctypes.cdll.LoadLibrary(cwd+'/low_level_functions.so')

        self.buffer_size = 4096

        filename = ctypes.c_char_p(driver_file.encode("utf-8"))
        self.low_level_lib.low_level_init(filename, self.buffer_size, 0x7E200000, 0x43c00000)
        self.acknowledge_interrupt()

    def acknowledge_interrupt(self):
        return self.low_level_lib.acknowledge_interrupt()

    def wait_for_data(self):
        return self.low_level_lib.wait_for_Interrupt()

    def read_data(self):
        data = [0] * 20
        arr = (ctypes.c_int * len(data))(*data)
        self.low_level_lib.read_data(arr)
        data = [arr[i] for i in range(20)]
        return data


if __name__ == '__main__':
        a = uCube_interface()
        while True:
            a.wait_for_data()
            data = a.read_data()
            a.acknowledge_interrupt()
