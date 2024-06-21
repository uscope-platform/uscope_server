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
