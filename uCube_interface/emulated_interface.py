import subprocess
import random
import os

class EmulatedInterface:
    def __init__(self):
        wd = os.path.dirname(__file__)
        conf_path = os.path.join(wd, "redis.conf")
        self.redis_db = subprocess.Popen(["redis-server", conf_path, "dir", wd])

    def read_data(self):
        return [random.randrange(0, 100) for x in range(1, 1024)]

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
