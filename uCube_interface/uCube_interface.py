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
C_ENABLE_CHANNEL = '10'
C_DISABLE_CHANNEL = '11'

RESP_OK = '1'
RESP_ERR_BITSTREAM_NOT_FOUND = '2'


class uCube_interface:
    def __init__(self, hw_host, hw_port):
        self.hw_host = hw_host
        self.hw_port = hw_port

    def socket_recv(self,socket, n_bytes):
        raw_data = b''
        while len(raw_data) != n_bytes:
            raw_data += socket.recv(n_bytes - len(raw_data))
        return raw_data

    def send_command(self, command: str):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            data = 0
            s.connect((self.hw_host, self.hw_port))
            s.send(len(command).to_bytes(8, byteorder='little'))

            s.send(command.encode())

            raw_status_resp = self.socket_recv(s, 6)
            status_response = struct.unpack("<3h", raw_status_resp)

            if status_response[2] == 1:
                raw_resp_length = self.socket_recv(s, 8)
                response_length = struct.unpack("<Q", raw_resp_length)[0]

                raw_data = self.socket_recv(s, response_length)
                data = struct.unpack(f"<{response_length // 4}I", raw_data)

        return data

    def read_data(self):
        command = f'{C_READ_DATA}'
        return self.send_command(command)

    def read_register(self, address):
        command = f'{C_SINGLE_REGISTER_READ} {address}'
        data = self.send_command(command)
        return data

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

    def get_capture_data(self):
        command = f'{C_CHECK_CAPTURE_PROGRESS}'
        while True:
            response = self.send_command(command).split(b' ')
            if response[0] == command:
                return response
            else:
                time.sleep(1e-3)

    def enable_channel(self, channel):
        command = f'{C_ENABLE_CHANNEL} {channel}'
        response = self.send_command(command)

    def disable_channel(self, channel):
        command = f'{C_DISABLE_CHANNEL} {channel}'
        response = self.send_command(command)
