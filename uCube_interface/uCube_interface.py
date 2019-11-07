import os
import ctypes
from .low_level_emulator import emulator
import numpy as np
from threading import Lock
import redis

channel_0_data = np.zeros(50000)
channel_data_raw = []


class uCube_interface:
    def __init__(self, driver_file="/dev/uio0", dbg=False, redis_host='localhost'):
        self.dbg = dbg
        self.interface_lock = Lock()
        self.redis_if = redis.Redis(host=redis_host, port=6379, db=1)

        self.redis_if.set('bitstream_loaded', 'false')

        if not self.dbg:
            cwd = os.getcwd()
            lib = cwd + '/uCube_interface/low_level_functions.so'
            src = cwd + '/uCube_interface/low_level_functions.c'
            # Compile low level functions
            os.system('rm '+lib)
            os.system('gcc -shared -g -fPIC -o '+lib+' '+src+'&> /dev/null')

            self.low_level_lib = ctypes.cdll.LoadLibrary(lib)
        else:
            self.low_level_lib = emulator()
        filename = ctypes.c_char_p(driver_file.encode("utf-8"))

        #TODO: clean up this dirty hack
        self.timebase_addr = 0x43c00400


        self.buffer_size = 4 * 4096
        self.low_level_lib.low_level_init(filename, self.buffer_size, 0x7E200000, 0x43c00000)
        self.clock_frequency = 100e6
        return

    def wait_for_data(self):
        bitstream_loaded = self.redis_if.get('bitstream_loaded')

        if bitstream_loaded == b'true' or self.dbg:
            self.interface_lock.acquire()
            retval = self.low_level_lib.wait_for_Interrupt()
            self.interface_lock.release()
            return retval
        else:
            raise RuntimeError("FPGA access before bitstream loading is done")

    def read_data(self):
        bitstream_loaded = self.redis_if.get('bitstream_loaded')

        if bitstream_loaded == b'true' or self.dbg:
            rec_data = [0] * 1024
            arr = (ctypes.c_int32 * len(rec_data))(*rec_data)

            self.interface_lock.acquire()
            self.low_level_lib.read_data(arr, 1024)
            self.interface_lock.release()

            rec_data = [arr[i] for i in range(1024)]
            return rec_data
        else:
            raise RuntimeError("FPGA access before bitstream loading is done")

    def change_timebase(self, timebase):
        bitstream_loaded = self.redis_if.get('bitstream_loaded')

        if bitstream_loaded == b'true' or self.dbg:
            counter_val = round(timebase / self.clock_frequency ** -1)
            self.interface_lock.acquire()
            self.low_level_lib.write_register(self.timebase_addr, counter_val)
            self.interface_lock.release()
            return
        else:
            raise RuntimeError("FPGA access before bitstream loading is done")

    def read_register(self, address):
        bitstream_loaded = self.redis_if.get('bitstream_loaded')

        if bitstream_loaded == b'true' or self.dbg:
            self.interface_lock.acquire()
            val = self.low_level_lib.read_register(address)
            self.interface_lock.release()
            return val
        else:
            raise RuntimeError("FPGA access before bitstream loading is done")

    def write_register(self, address, value):
        bitstream_loaded = self.redis_if.get('bitstream_loaded')
        if bitstream_loaded == b'true' or self.dbg:
            self.interface_lock.acquire()
            self.low_level_lib.write_register(address, value)
            self.interface_lock.release()
        else:
            raise RuntimeError("FPGA access before bitstream loading is done")

    def write_proxied_register(self, proxy_address, address, value):
        bitstream_loaded = self.redis_if.get('bitstream_loaded')

        if bitstream_loaded == b'true' or self.dbg:
            self.interface_lock.acquire()
            self.low_level_lib.write_proxied_register(proxy_address, address, value)
            self.interface_lock.release()
        else:
            raise RuntimeError("FPGA access before bitstream loading is done")

    def load_bitstream(self, bitstream):
        if self.dbg:
            self.redis_if.set('bitstream_loaded', 'true')
            return
        # The low level interface is not used here, however the lock is acquired
        # to prevent other threads hitting the bus before the configuration is done
        self.redis_if.set('bitstream_loaded', 'false')

        # TODO: clean up this dirty hack
        if bitstream == 'cl_master.bin':
            self.timebase_addr = 0x43c00300

        self.interface_lock.acquire()

        os.system("echo 0 > /sys/class/fpga_manager/fpga0/flags")
        os.system(f'echo {bitstream} > /sys/class/fpga_manager/fpga0/firmware')
        self.redis_if.set('bitstream_loaded', 'true')

        self.interface_lock.release()


if __name__ == '__main__':
    a = uCube_interface(dbg=True)
    while True:
        a.wait_for_data()
        data = a.read_data()
        channel_0_data = np.roll(channel_0_data, len(data))
        channel_0_data[0:len(data)] = data
        channel_data_raw.append(data)

