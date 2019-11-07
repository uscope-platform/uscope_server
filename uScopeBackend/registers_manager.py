from flask import current_app, Blueprint, jsonify, request
from flask_restful import Api, Resource

import time

############################################################
#                      IMPLEMENTATION                      #
############################################################


registers_manager_bp = Blueprint('regusters_manager', __name__, url_prefix='/registers')


api = Api(registers_manager_bp)


class RegisterValue(Resource):
    def get(self):
        pass

    def post(self, peripheral):
        registers_to_write = request.get_json(force=True)
        current_app.register_mgr.set_register_value(peripheral, registers_to_write['payload'])
        return '200'


class RegisterDescriptions(Resource):
    def get(self, peripheral):
        return jsonify(current_app.register_mgr.get_registers_descriptions(peripheral))

    def post(self):
        pass


class PeripheralsSpecs(Resource):
    def get(self):
        return jsonify(current_app.register_mgr.get_all_peripherals())


class PeripheralsDigest(Resource):
    def get(self):
        return current_app.register_mgr.get_peripherals_digest()


class RegistersBulkWrite(Resource):

    def post(self):
        registers_to_write = request.get_json(force=True)
        current_app.register_mgr.bulk_write(registers_to_write['payload'])
        return '200'


api.add_resource(RegisterValue, '/<string:peripheral>/value')
api.add_resource(RegisterDescriptions, '/<string:peripheral>/descriptions')
api.add_resource(PeripheralsSpecs, '/all_peripheral/descriptions')
api.add_resource(RegistersBulkWrite, '/bulk_write')
api.add_resource(PeripheralsDigest, '/digest')

############################################################
#                      IMPLEMENTATION                      #
############################################################


class RegistersManager:

    def __init__(self, interface, store):
        self.interface = interface
        self.store = store

    def get_all_peripherals(self):
        return self.store.get_peripherals()

    def get_peripherals_digest(self):
        return self.store.get_peripherals_hash()

    def get_registers_descriptions(self, peripheral_name):
        if peripheral_name in self.store.get_peripherals():
            parameters = self.store.get_peripherals()[peripheral_name]
        else:
            raise ValueError("The component register file was not found")
        base_address = int(current_app.app_mgr.get_peripheral_base_address(peripheral_name), 0)
        registers_values = {}
        for i in parameters['registers']:
            if ('R' in i['direction'] or 'r' in i['direction']) and not current_app.app_mgr.peripheral_is_proxied(peripheral_name):
                address = base_address + int(i['offset'], 0)
                if i['register_format'] == 'words':
                    registers_values[i['register_name']] = self.interface.read_register(address)
                else:
                    registers_values[i['register_name']] = self.interface.read_register(address)

            else:
                registers_values[i['register_name']] = 0

        return {'peripheral_name': parameters['peripheral_name'], 'registers': registers_values}

    def get_register_value(self, peripheral_name, register_name):
        pass

    def set_register_value(self, peripheral, register):
        base_address = int(current_app.app_mgr.get_peripheral_base_address(peripheral), 0)
        if current_app.app_mgr.peripheral_is_proxied(peripheral):
            proxy_addr = int(current_app.app_mgr.get_peripheral_proxy_address(peripheral), 0)
            self.__set_proxied_register_value(register, base_address, proxy_addr)
        else:
            self.__set_direct_register_value(register, base_address)

    def bulk_write(self, registers):
        for i in registers:
            self.set_register_value(i['peripheral'], i)

    def __set_direct_register_value(self, register, base_address):
        periph = register['peripheral']
        peripheral_registers = self.store.get_peripherals()[periph]['registers']
        for i in peripheral_registers:
            if i['ID'] == register['name'] or i['register_name'] == register['name']:
                address = base_address + int(i['offset'], 0)
                value = register['value']
                print(f'DIRECT WRITE: writen: {value} to register at address: {hex(address)}')
                self.interface.write_register(address, value)

    def __set_proxied_register_value(self, register, base_address, proxy_addr):
        periph = register['peripheral']

        peripheral_registers = self.store.get_peripherals()[periph]['registers']
        for i in peripheral_registers:
            if i['ID'] == register['name'] or i['register_name'] == register['name']:
                address = base_address + int(i['offset'], 0)
                value = register['value']
                print(f'PROXY WRITE: writen: {value} to register at address: {hex(address)} through proxy at address: {hex(proxy_addr)}')
                self.interface.write_proxied_register(proxy_addr, address, value)

    def __split_dword(self, val):
        w1 = int(val & 0xffff)
        w2 = int((val >> 16) & 0xffff)
        return w1, w2
