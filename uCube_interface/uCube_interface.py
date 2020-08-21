import numpy as np
import socket
import struct
import time

channel_0_data = np.zeros(50000)
channel_data_raw = []

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


class uCube_interface:
    def __init__(self, hw_host, hw_port):
        self.hw_host = hw_host
        self.hw_port = hw_port

    def send_command(self, command: str):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.hw_host, self.hw_port))
            s.send(len(command).to_bytes(8, byteorder='little'))

            s.send(command.encode())

            raw_resp_length = s.recv(8)
            response_length = struct.unpack("<Q", raw_resp_length)[0]

            data = s.recv(response_length).rstrip(b'\x00').decode()

        return data

    def read_data(self):
        command = f'{C_READ_DATA}'
        response = self.send_command(command)
        data_str = response.split(' ', 2)[2]
        data = data_str.split(', ', )
        return list(map(int, data))

    def read_register(self, address):
        command = f'{C_SINGLE_REGISTER_READ} {address}'
        response = self.send_command(command)
        #return random.randrange(0, 100)

    def write_register(self, address, value):
        command = f'{C_SINGLE_REGISTER_WRITE} {address} {value}'
        response = self.send_command(command)

    def write_proxied_register(self, proxy_address, address, value):
        command = f'{C_PROXIED_WRITE} {proxy_address},{address} {value}'
        response = self.send_command(command)

    def load_bitstream(self, bitstream):
        command = f'{C_LOAD_BITSTREAM} {bitstream}'
        response = self.send_command(command)
        return

    def setup_capture_mode(self, n_buffers):
        command = f'{C_START_CAPTURE} {n_buffers}'
        response = self.send_command(command)
        return

    def get_capture_data(self):
        command = f'{C_CHECK_CAPTURE_PROGRESS}'
        while True:
            response = self.send_command(command).split(b' ')
            if response[0] == command:
                return response
            else:
                time.sleep(1e-3)
