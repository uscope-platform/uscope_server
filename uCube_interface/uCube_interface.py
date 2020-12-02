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
C_SET_CHANNEL_STATUS = '10'
C_APPLY_PROGRAM = '11'

RESP_OK = '1'
RESP_ERR_BITSTREAM_NOT_FOUND = '2'
RESP_DATA_NOT_READY = '3'


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
            
            raw_command = command.encode()

            command_length = str(len(raw_command)).zfill(10)
            
            s.send(command_length.encode())
            self.socket_recv(s, 2)
            s.send(raw_command)

            raw_status_resp = self.socket_recv(s, 6)
            status_response = struct.unpack("<3h", raw_status_resp)
            if status_response[1] != 1:
                if status_response[0] == 8:
                    raise RuntimeError
            if status_response[2] == 1:
                raw_resp_length = self.socket_recv(s, 8)
                response_length = struct.unpack("<Q", raw_resp_length)[0]

                raw_data = self.socket_recv(s, response_length)
                data = struct.unpack(f"<{response_length // 4}i", raw_data)
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
        return self.send_command(command).split(b' ')  

    def set_channel_status(self, status):
        status_string = ""
        for i in status:
            if status[i]:
                status_string += "1,"
            else:
                status_string += "0,"
        status_string = status_string.rstrip(',')
        command = f'{C_SET_CHANNEL_STATUS} {status_string}'
        response = self.send_command(command)

    def apply_program(self, program, core_address):
        program_string = ""
        for i in program['hex']:
            program_string += str(i) + ','

        command = f'{C_APPLY_PROGRAM} {core_address} {program_string}'
        response = self.send_command(command)
