import numpy as np
import redis

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

RESP_OK = '1'
RESP_ERR_BITSTREAM_NOT_FOUND = '2'


class uCube_interface:
    def __init__(self, redis_host):
        self.redis_if = redis.Redis(host=redis_host, port=6379, db=4)
        self.redis_response = redis.Redis(host=redis_host, port=6379, db=4).pubsub()
        self.redis_response.subscribe("response")
        self.buf = np.memmap('/dev/shm/uscope_mapped_mem', dtype='int32', mode='r', shape=(1024, 1))

    def read_data(self):
        self.redis_if.publish("command", f'{C_READ_DATA}')
        return self.buf

    def read_register(self, address):
        self.redis_if.publish("command", f'{C_SINGLE_REGISTER_READ} {address}')

    def write_register(self, address, value):
        self.redis_if.publish("command", f"{C_SINGLE_REGISTER_WRITE} {address} {value}")

    def write_proxied_register(self, proxy_address, address, value):
        self.redis_if.publish("command", f"{C_PROXIED_WRITE} {proxy_address},{address} {value}")

    def load_bitstream(self, bitstream):
        self.redis_if.publish("command", f'{C_LOAD_BITSTREAM} {bitstream}')

    def setup_capture_mode(self, n_buffers):
        self.redis_if.publish("command", f'{C_START_CAPTURE} {n_buffers}')

    def get_capture_data(self):
        pass