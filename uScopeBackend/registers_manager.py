from flask import current_app, Blueprint, jsonify, request
from flask_restful import Api, Resource

import os, json


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


api.add_resource(RegisterValue, '/<string:peripheral>/value')
api.add_resource(RegisterDescriptions, '/<string:peripheral>/descriptions')

############################################################
#                      IMPLEMENTATION                      #
############################################################


class RegistersManager:

    def __init__(self, interface):
        self.interface = interface
        self.components_specs = {}

        settings = [f for f in os.listdir('static') if os.path.isfile(os.path.join('static', f))]

        for fname in settings:
            if not fname.split('.')[1] == 'json':
                continue
            else:
                name = fname.replace('.json', '')
            parsed = name.rsplit('_', 1)
            if parsed[1] == 'registers':
                with open('static/' + fname, 'r') as f:
                    content = json.load(f)
                    self.components_specs[content['peripheral_name']] = content

    def get_registers_descriptions(self, peripheral_name):
        if peripheral_name in self.components_specs:
            parameters = self.components_specs[peripheral_name]
        else:
            raise ValueError("The component register file was not found")

        base_address = int(current_app.app_mgr.get_peripheral_base_address(peripheral_name),0)

        for i in parameters['registers']:
            if 'R' in i['direction'] or 'r' in i['direction']:
                address = base_address + int(i['offset'], 0)
                if i['register_format'] == 'words':
                    i['value'] = self.__split_dword(self.interface.read_register(address))
                else:
                    i['value'] = self.interface.read_register(address)

            else:
                i['value'] = 0

        return parameters

    def get_register_value(self, peripheral_name, register_name):
        pass

    def set_register_value(self, peripheral, register):
        periph = register['peripheral']
        peripheral_registers = self.components_specs[periph]['registers']

        base_address = int(current_app.app_mgr.get_peripheral_base_address(peripheral), 0)

        for i in peripheral_registers:
            if i['register_name'] == register['name']:
                address = base_address + int(i['offset'], 0)
                value = register['value']
                self.interface.write_register(address, value)

    def __split_dword(self, val):
        w1 = int(val & 0xffff)
        w2 = int((val >> 16) & 0xffff)
        return w1, w2
