import subprocess
import random
import os
import socket
import struct

C_NULL_COMMAND = '0'
C_LOAD_BITSTREAM = '1'
C_SINGLE_REGISTER_WRITE = '2'
C_BULK_REGISTER_WRITE = '3'
C_SINGLE_REGISTER_READ = '4'
C_BULK_REGISTER_READ = '5'
C_START_CAPTURE = '6'
C_PROXIED_WRITE = '7'
C_READ_DATA = '8'
C_CHECK_CAPTURE_PROGRESS = '9'

RESP_OK = '1'
RESP_ERR_BITSTREAM_NOT_FOUND = '2'

class EmulatedInterface:
    def __init__(self):
        self.data_host = "localhost"
        self.data_port = 6666

        wd = os.path.dirname(__file__)
        conf_path = os.path.join(wd, "redis.conf")
        self.redis_db = subprocess.Popen(["redis-server", conf_path, "dir", wd])

    def read_data(self):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.data_host, self.data_port))
            command = f'{C_READ_DATA}'
            s.send(len(command).to_bytes(8, byteorder='little'))

            s.send(command.encode())

            data = s.recv(4096)
            data = struct.unpack("<1024I", data)
            data = [x for x in data]
        return data

    def read_register(self, address):
        return random.randrange(0, 100)

    def write_register(self, address, value):
        return

    def write_proxied_register(self, proxy_address, address, value):
        return

    def load_bitstream(self, bitstream):
        return

    def setup_capture_mode(self, n_buffers):
        return

    def get_capture_data(self):
        return [random.randrange(0, 100) for x in range(1, 1024)]

    def __del__(self):
        self.redis_db.kill()
