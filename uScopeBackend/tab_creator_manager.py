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

from flask import current_app, Blueprint, jsonify, request
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required

from . import role_required

############################################################
#                      BLUEPRINT                           #
############################################################


peripheral_manager_bp = Blueprint('tab_creator_manager', __name__, url_prefix='/tab_creator')


api = Api(peripheral_manager_bp)


class EditPeripheral(Resource):
    @jwt_required()
    @role_required("admin")
    def post(self):
        edit = request.get_json()
        current_app.peripheral_mgr.edit_peripheral(edit)
        return '200'


class CreatePeripheral(Resource):
    @jwt_required()
    @role_required("admin")
    def get(self, peripheral):
        pass

    @jwt_required()
    @role_required("admin")
    def post(self):
        peripheral = request.get_json()
        current_app.peripheral_mgr.create_peripheral(peripheral)
        return '200'


class RemovePeripheral(Resource):
    @jwt_required()
    @role_required("admin")
    def get(self, peripheral):
        current_app.peripheral_mgr.remove_peripheral(peripheral)

    @jwt_required()
    @role_required("admin")
    def post(self):
        pass


api.add_resource(CreatePeripheral, '/create_peripheral')
api.add_resource(EditPeripheral, '/edit_peripheral')
api.add_resource(RemovePeripheral, '/remove_peripheral/<string:peripheral>')

############################################################
#                      IMPLEMENTATION                      #
############################################################


class PeripheralManager:

    def __init__(self, store):
        self.data_store = store.Elements
        self.image_filename = ''
        self.image_content = None

    def create_peripheral(self, periph):
        """Adds a peripheral to the database

            Parameters:
                periph: peripheral to store into the database
           """

        label, periph =periph['payload'].popitem()
        periph['image'] = ""
        self.data_store.add_peripheral(periph)

    def edit_peripheral(self, edit):
        current_periph = self.data_store.get_peripheral(edit["peripheral"])
        if edit["action"] == "edit_version":
            current_periph['version'] = edit['version']
        elif edit["action"] == "add_register":
            current_periph['registers'].append(edit['register'])
        elif edit["action"] == "edit_register":
            present = False
            for idx, val in enumerate(current_periph['registers']):
                if val['register_name'] == edit['register']:
                    present = True
                    break
            if present:
                current_periph['registers'][idx][edit['field']] = edit['value']
        elif edit["action"] == "remove_register":
            present = False
            for idx, val in enumerate(current_periph['registers']):
                if val['register_name'] == edit['register']:
                    present = True
                    break
            if present:
                del current_periph['registers'][idx]
        self.data_store.edit_peripheral(current_periph)

    def remove_peripheral(self, peripheral):
        """Removes a peripheral from the database

            Parameters:
                peripheral: name of the peripheral to remove
           """
        self.data_store.remove_peripheral(peripheral)
