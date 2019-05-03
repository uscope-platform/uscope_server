import os
import ctypes


class uCube_interface:
    def __init__(self, driver_file = "/dev/uio0"):
        cwd = os.getcwd()
        os.system("rm low_level_functions.so")
        os.system("gcc -shared -fPIC -o low_level_functions.so low_level_functions.c")
        self.low_level_lib = ctypes.cdll.LoadLibrary(cwd+'/low_level_functions.so')

        self.buffer_size = 4096

        filename = ctypes.c_char_p(driver_file.encode("utf-8"))
        self.low_level_lib.low_level_init(filename,self.buffer_size)
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

    def start_dma(self):
        os.system("devmem2 0x7E200018 w 0xC0000000>/dev/null")
        os.system("devmem2 0x7E200020 w 0x100000>/dev/null")
        os.system("devmem2 0x7E200028 w 0x1000>/dev/null")


if __name__ == '__main__':
        a = uCube_interface()
        while True:
            a.wait_for_data()
            a.start_dma()
            data = a.read_data()
            a.acknowledge_interrupt()
