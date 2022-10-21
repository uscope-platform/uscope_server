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
import json

from flask import current_app, Blueprint, jsonify, request
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import role_required

############################################################
#                      IMPLEMENTATION                      #
############################################################


registers_manager_bp = Blueprint('regusters_manager', __name__, url_prefix='/registers')


api = Api(registers_manager_bp)


class RegisterDescriptions(Resource):
    @jwt_required()
    @role_required("operator")
    def get(self, peripheral):
        user = get_jwt_identity()
        return jsonify(current_app.register_mgr.get_registers_descriptions(peripheral,user))

    @jwt_required()
    @role_required("operator")
    def post(self):
        pass


class PeripheralsSpecs(Resource):
    @jwt_required()
    @role_required("operator")
    def get(self):
        return jsonify(current_app.register_mgr.get_all_peripherals())


class PeripheralsDigest(Resource):
    @jwt_required()
    @role_required("operator")
    def get(self):
        return current_app.register_mgr.get_peripherals_digest()


class RegistersBulkWrite(Resource):

    @jwt_required()
    @role_required("operator")
    def get(self, address):
        return current_app.register_mgr.get_register_value(address)

    @jwt_required()
    @role_required("operator")
    def post(self):
        registers_to_write = request.get_json(force=True)
        current_app.register_mgr.bulk_write(registers_to_write['payload'])
        return '200'


class RegistersRead(Resource):

    @jwt_required()
    @role_required("operator")
    def get(self, address):
        return current_app.register_mgr.get_register_value(address)


api.add_resource(RegisterDescriptions, '/<string:peripheral>/descriptions')
api.add_resource(PeripheralsSpecs, '/all_peripheral/descriptions')
api.add_resource(RegistersBulkWrite, '/bulk_write')
api.add_resource(RegistersRead, '/direct_read/<string:address>')
api.add_resource(PeripheralsDigest, '/digest')

############################################################
#                      IMPLEMENTATION                      #
############################################################


class RegistersManager:

    def __init__(self, interface, store):
        self.interface = interface
        self.data_store = store.Elements
        self.settings_store = store.Settings

    def get_all_peripherals(self):
        """Returns all the peripherals present in the database

            Returns:
                List:list of peripherals in the database
           """
        return self.data_store.get_peripherals_dict()

    def get_peripherals_digest(self):
        """Returns an hash of the jsonified peripherals list

            Returns:
                str:Digest of the peripherals present in the database
           """
        return self.data_store.get_peripherals_hash()

    def get_registers_descriptions(self, peripheral_name, username):
        """Returns the specification for the registers of the specified peripheral

            Parameters:
                peripheral_name: name of the peripheral whose registers need to be returned
                username: username of the request issuer
            Returns:
                List:list of registers in the peripheral

           """

        app = self.settings_store.get_per_user_value('chosen_application', username)
        found = False
        for peripheral in app['peripherals']:
            if peripheral_name in peripheral['peripheral_id']:
                found = True
                parameters = self.data_store.get_peripheral(peripheral['spec_id'])
                base_address = int(peripheral['base_address'], 0)

        if not found:
            raise ValueError("The component register file was not found")

        registers_values = {}
        for i in parameters['registers']:
            if ('R' in i['direction'] or 'r' in i['direction']) and not current_app.app_mgr.peripheral_is_proxied(
                    peripheral_name, username):
                address = base_address + int(i['offset'], 0)
                if i['register_format'] == 'words':
                    registers_values[i['register_name']] = self.interface.read_register(address)
                else:
                    registers_values[i['register_name']] = self.interface.read_register(address)

            else:
                registers_values[i['register_name']] = 0

        return {'peripheral_name': parameters['peripheral_name'], 'registers': registers_values}

    def get_register_value(self, address):
        if isinstance(address, str):
            addr = int(address, 0)
        else:
            addr = address
        return {"response": self.interface.read_register(addr)}

    def bulk_write(self, registers):
        """ Perform a bulk register write operations

            Parameters:
                registers: List of dictionaries containing the details for a single register write
           """
        for i in registers:
            self.interface.write_register(i)