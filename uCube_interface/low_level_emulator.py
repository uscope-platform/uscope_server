class emulator:
    def __init__(self):
        pass

    def low_level_init(self, filename, buffer_size, addr1, addr2):
        return 0

    def write_register(self, addr, val):
        return 0

    def read_register(self, addr):
        return  0

    def wait_for_Interrupt(self):
        return

    def read_data(self, data, size):
        return

    def init_adcTest_registers(self):
        return

    def write_proxied_register(self, proxy_address, address, value):
        return
