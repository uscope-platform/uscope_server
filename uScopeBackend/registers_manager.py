from flask import current_app, Blueprint, jsonify, request
from flask_restful import Api, Resource

import os, json


############################################################
#                      IMPLEMENTATION                      #
############################################################


registers_manager_bp = Blueprint('regusters_manager', __name__, url_prefix='/registers')


api = Api(registers_manager_bp)


class ProxiedRegisterValue(Resource):
    def get(self):
        pass

    def post(self, peripheral):
        registers_to_write = request.get_json(force=True)
        current_app.register_mgr.set_proxied_register_value(peripheral, registers_to_write['payload'])
        return '200'


class DirectRegisterValue(Resource):
    def get(self):
        pass

    def post(self, peripheral):
        registers_to_write = request.get_json(force=True)
        current_app.register_mgr.set_direct_register_value(peripheral, registers_to_write['payload'])
        return '200'


class RegisterDescriptions(Resource):
    def get(self, peripheral):
        return jsonify(current_app.register_mgr.get_registers_descriptions(peripheral))

    def post(self):
        pass


api.add_resource(ProxiedRegisterValue, '/<string:peripheral>/proxied-value')
api.add_resource(DirectRegisterValue, '/<string:peripheral>/value')
api.add_resource(RegisterDescriptions, '/<string:peripheral>/descriptions')

############################################################
#                      IMPLEMENTATION                      #
############################################################


class RegistersManager:

    def __init__(self, interface, store):
        self.interface = interface
        self.components_specs = {}

        self.components_specs = store.load_peripherals()

    def get_registers_descriptions(self, peripheral_name):
        if peripheral_name in self.components_specs:
            parameters = self.components_specs[peripheral_name]
        else:
            raise ValueError("The component register file was not found")

        base_address = int(current_app.app_mgr.get_peripheral_base_address(peripheral_name), 0)

        for i in parameters['registers']:
            if 'R' in i['direction'] or 'r' in i['direction']:
                address = base_address + int(i['offset'], 0)
                if i['register_format'] == 'words':
                    i['value'] = self.interface.read_register(address)
                else:
                    i['value'] = self.interface.read_register(address)

            else:
                i['value'] = 0

        return parameters

    def get_register_value(self, peripheral_name, register_name):
        pass

    def set_direct_register_value(self, peripheral, register):
        periph = register['peripheral']
        peripheral_registers = self.components_specs[periph]['registers']

        base_address = int(current_app.app_mgr.get_peripheral_base_address(peripheral), 0)

        for i in peripheral_registers:
            if i['register_name'] == register['name']:
                address = base_address + int(i['offset'], 0)
                value = register['value']
                self.interface.write_register(address, value)

    def set_proxied_register_value(self, peripheral, register):
        periph = register['peripheral']
        peripheral_registers = self.components_specs[periph]['registers']

        base_address = int(current_app.app_mgr.get_peripheral_base_address(peripheral), 0)
        proxy_addr = int(current_app.app_mgr.get_peripheral_proxy_address(peripheral), 0)
        for i in peripheral_registers:
            if i['register_name'] == register['name']:
                address = base_address + int(i['offset'], 0)
                value = register['value']
                self.interface.write_proxied_registers(proxy_addr, address, value)

    def __split_dword(self, val):
        w1 = int(val & 0xffff)
        w2 = int((val >> 16) & 0xffff)
        return w1, w2
