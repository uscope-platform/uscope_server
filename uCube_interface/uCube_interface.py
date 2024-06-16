# Copyright 2021 University of Nottingham Ningbo China
# Author: Filippo Savi <filssavi@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import socket
import msgpack
import json

channel_data_raw = []

C_NULL_COMMAND = 'null'
C_LOAD_BITSTREAM = 'load_bitstream'
C_SINGLE_REGISTER_WRITE = 'register_write'
C_SINGLE_REGISTER_READ = 'register_read'
C_START_CAPTURE = 'start_capture'
C_READ_DATA = 'read_data'
C_CHECK_CAPTURE_PROGRESS = 'check_capture'
C_SET_CHANNEL_WIDTHS = 'set_channel_widths'
C_COMPILE_PROGRAM = 'compile_program'
C_APPLY_PROGRAM = 'apply_program'
C_SET_SCALING_FACTORS = 'set_scaling_factors'
C_SET_CHANNEL_STATUS = 'set_channel_status'
C_APPLY_FILTER = 'apply_filter'
C_SET_CHANNEL_SIGNS = 'set_channel_signs'
C_GET_VERSION = 'get_version'
C_SET_SCOPE_DATA = 'set_scope_data'
C_ENABLE_MANUAL_METADATA = 'enable_manual_metadata'
C_DEPLOY_HIL = 'deploy_hil'
C_EMULATE_HIL = 'emulate_hil'
C_HIL_SELECT_OUT = 'hil_select_out'
C_HIL_SET_IN = 'hil_set_in'
C_HIL_START = 'hil_start'
C_HIL_STOP = 'hil_stop'
C_GET_ACQUISITION_STATUS = 'get_acquisition_status'
C_SET_ACQUISITION = 'set_acquisition'
C_SET_SCOPE_ADDRESS = 'set_scope_address'
C_SET_PL_CLOCK = 'set_pl_clock'
C_GET_CLOCK =  'get_clock'

RESP_OK = '1'
RESP_ERR_BITSTREAM_NOT_FOUND = '2'
RESP_DATA_NOT_READY = '3'
RESP_BITSTREAM_LOAD_FAILED = '5'


class DriverError(Exception):
    def __init__(self, message, code, data):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)

        # Now for your custom code...
        self.code = code
        self.data = data
        self.message =  message


class uCube_interface:
    def __init__(self, hw_host, hw_port):
        self.hw_host = hw_host
        self.hw_port = hw_port

    def socket_recv(self, socket, n_bytes):
        raw_data = b''
        while len(raw_data) != n_bytes:
            raw_data += socket.recv(n_bytes - len(raw_data))
        return raw_data

    def send_command(self, command_idx: str, arguments):
        command_obj = {"cmd": command_idx, "args": arguments}
        command = json.dumps(command_obj)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            data = 0
            s.connect((self.hw_host, self.hw_port))

            raw_command = command.encode()

            command_length = str(len(raw_command)).zfill(10)

            s.send(command_length.encode())
            self.socket_recv(s, 2)
            s.send(raw_command)

            raw_status_resp = self.socket_recv(s, 4)
            response_length = int.from_bytes(raw_status_resp, "big")
            raw_response = self.socket_recv(s, response_length)

            resp_obj = msgpack.unpackb(raw_response)
            response = resp_obj["body"]
            response_code = response["response_code"]

            if response_code != 1:
                if 'duplicates' in response:
                    raise DriverError(response["data"], response_code, response['duplicates'])
                elif response_code == 6:
                    raise DriverError("Generic acquisition error", response_code, [])
                else:
                    raise DriverError(response["data"], response_code, [])

            if "data" in response:
                return response["data"]
            return response_code

    def read_data(self):
        return self.send_command(C_READ_DATA, [])

    def read_register(self, address):
        data = self.send_command(C_SINGLE_REGISTER_READ, address)
        return data

    def write_register(self, write_obj):
        response = self.send_command(C_SINGLE_REGISTER_WRITE, write_obj)

    def load_bitstream(self, bitstream):
        response = self.send_command(C_LOAD_BITSTREAM, bitstream)
        return response

    # DEPRECATED
    def setup_capture_mode(self, n_buffers):
        response = self.send_command(C_START_CAPTURE, n_buffers)

    # DEPRECATED
    def get_capture_data(self):
        return self.send_command(C_CHECK_CAPTURE_PROGRESS, []).split(b' ')

    def set_channel_widths(self, widths):
        return self.send_command(C_SET_CHANNEL_WIDTHS, widths)

    def set_channel_signs(self, signs):
        self.send_command(C_SET_CHANNEL_SIGNS, signs)

    def set_scaling_factors(self, factors):
        return self.send_command(C_SET_SCALING_FACTORS, factors)

    def set_channel_status(self, status):
        return self.send_command(C_SET_CHANNEL_STATUS, status)

    def apply_program(self, program, core_address):

        if isinstance(core_address, str):
            addr = int(core_address, 0)
        else:
            addr = core_address

        response = self.send_command(C_APPLY_PROGRAM, {"address": addr, "program": program})

    def compile_program(self, program):
        response = self.send_command(C_COMPILE_PROGRAM, program)
        return response

    def apply_filter(self, filter_address, taps):

        if isinstance(filter_address, str):
            addr = int(filter_address, 0)
        else:
            addr = filter_address
        return self.send_command(C_APPLY_FILTER, {"address": addr, "taps": taps})

    def get_version(self, component):
        return self.send_command(C_GET_VERSION, component)

    def set_scope_data(self, scope_data):
        return self.send_command(C_SET_SCOPE_DATA, scope_data)

    def enable_manual_metadata(self):
        return self.send_command(C_ENABLE_MANUAL_METADATA, {})

    def deploy_hil(self, spec):
        res = "Generic Deployment error"
        try:
            res = self.send_command(C_DEPLOY_HIL, spec)
        except DriverError as ex:
            res = {'code': ex.code, 'error': ex.message, 'duplicates': ex.data}
        return res

    def select_out(self, spec):
        return self.send_command(C_HIL_SELECT_OUT, spec)

    def set_in(self, spec):
        return self.send_command(C_HIL_SET_IN, spec)

    def start_hil(self):
        return self.send_command(C_HIL_START, {})

    def stop_hil(self):
        return self.send_command(C_HIL_STOP, {})

    def get_acquisition_status(self):
        return self.send_command(C_GET_ACQUISITION_STATUS, {})

    def set_acquisition(self, arg):
        return self.send_command(C_SET_ACQUISITION, arg)

    def set_scope_address(self, address):
        return self.send_command(C_SET_SCOPE_ADDRESS, address)

    def set_pl_clock(self, clock_n, frequency):
        return self.send_command(C_SET_PL_CLOCK, {"id":clock_n, "value":frequency, "is_primary":True})

    def get_clock(self, clock_n):
        return self.send_command(C_GET_CLOCK, clock_n)


    def emulate_hil(self, spec):
        res = "Generic Emulation error"
        try:
            res = json.loads(self.send_command(C_EMULATE_HIL, spec))
        except DriverError as ex:
            res = {'code': ex.code, 'error': ex.message,  'duplicates': ex.data}
        return res
