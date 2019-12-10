import numpy as np
import redis
import time
from subprocess import Popen
import signal

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
    def __init__(self, redis_host):
        self.redis_if = redis.Redis(host=redis_host, port=6379, db=4)
        self.redis_response = redis.Redis(host=redis_host, port=6379, db=4).pubsub()

        self.driver = Popen(["/home/root/uScope/driver/build/uscope_driver", ""])

        self.redis_response.subscribe("response")
        message = self.redis_response.get_message()
        self.buf = np.memmap('/dev/shm/uscope_mapped_mem', dtype='int32', mode='r', shape=(1024, 1))

    def read_data(self):
        self.redis_if.publish("command", f'{C_READ_DATA}')
        return self.buf

    def read_register(self, address):
        self.redis_if.publish("command", f'{C_SINGLE_REGISTER_READ} {address}')
        message = self.redis_response.get_message()

    def write_register(self, address, value):
        self.redis_if.publish("command", f"{C_SINGLE_REGISTER_WRITE} {address} {value}")

    def write_proxied_register(self, proxy_address, address, value):
        self.redis_if.publish("command", f"{C_PROXIED_WRITE} {proxy_address},{address} {value}")

    def load_bitstream(self, bitstream):
        self.redis_if.publish("command", f'{C_LOAD_BITSTREAM} {bitstream}')

    def setup_capture_mode(self, n_buffers):
        self.redis_if.publish("command", f'{C_START_CAPTURE} {n_buffers}')

    def get_capture_data(self):
        self.redis_if.publish("command", f'{C_CHECK_CAPTURE_PROGRESS}')
        response = self.wait_for_response(C_CHECK_CAPTURE_PROGRESS.encode())
        return int(response[2].decode())

    def wait_for_response(self, command):
        response = None
        while True:
            message = self.redis_response.get_message()
            if message is None:
                continue
            response = message['data'].split(b' ')
            if response[0] == command:
                return response
            else:
                time.sleep(1e-3)
        return response
