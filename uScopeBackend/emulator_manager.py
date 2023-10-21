# Copyright 2023 Filippo Savi
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
import numpy as np
from flask import current_app, Blueprint, jsonify, request
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required
from filter_designer import FilterDesignEngine
from . import role_required

############################################################
#                      BLUEPRINT                           #
############################################################


emulator_manager_bp = Blueprint('emulator_manager', __name__, url_prefix='/emulators')


api = Api(emulator_manager_bp)


class Emulator(Resource):

    @jwt_required()
    @role_required("user")
    def get(self, emulator_id):
        if emulator_id == "none":
            return jsonify(current_app.emu_mgr.get_emulators())

    @jwt_required()
    @role_required("user")
    def post(self, emulator_id):
        content = request.get_json()
        current_app.emu_mgr.add_emulator(content)
        return '200'

    @jwt_required()
    @role_required("user")
    def patch(self, emulator_id):
        edit = request.get_json()
        current_app.emu_mgr.edit_emulator(edit)
        return '200'

    @jwt_required()
    @role_required("user")
    def delete(self, emulator_id):
        current_app.emu_mgr.delete_emulator(emulator_id)
        return '200'


class EmulatorDigest(Resource):
    @jwt_required()
    @role_required("user")
    def get(self):
        return jsonify(current_app.emu_mgr.get_digest())


api.add_resource(EmulatorDigest, '/digest')
api.add_resource(Emulator, '/<string:emulator_id>')

############################################################
#                      IMPLEMENTATION                      #
############################################################


class EmulatorManager:

    def __init__(self, store):

        self.data_store = store.Elements

    def get_digest(self):
        return self.data_store.get_emulators_hash()

    def get_emulators(self):
        return self.data_store.get_emulators_dict()

    def add_emulator(self, emulator_obj: dict):
        self.data_store.add_emulator(emulator_obj)

    def edit_emulator(self, edit_obj):
        emu_obj = self.data_store.get_emulator(edit_obj['emulator'])
        a = edit_obj['action']
        if a == 'add_core':
            emu_obj['cores'][edit_obj['core']['id']] = edit_obj['core']
        elif a == 'add_connection':
            emu_obj['connections'].append(edit_obj['connection'])
        self.data_store.edit_emulator(emu_obj)

    def delete_emulator(self, filter_id):
        self.data_store.remove_emulator(filter_id)