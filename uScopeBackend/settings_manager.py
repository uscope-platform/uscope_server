# Copyright 2024 Filippo Savi
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
from . import role_required

############################################################
#                      BLUEPRINT                           #
############################################################


settings_bp = Blueprint('settings', __name__, url_prefix='/settings')


api = Api(settings_bp)


class DebugLevel(Resource):

    @jwt_required()
    @role_required("user")
    def get(self):
        return current_app.settings_mgr.get_debug_level()

    @jwt_required()
    @role_required("user")
    def post(self):
        spec = request.get_json()
        return jsonify(current_app.settings_mgr.set_debug_level(spec['level']))


class HilAddressMap(Resource):

    @jwt_required()
    @role_required("user")
    def get(self):
        return current_app.settings_mgr.get_hil_address_map()

    @jwt_required()
    @role_required("user")
    def post(self):
        spec = request.get_json()
        return jsonify(current_app.settings_mgr.set_hil_address_map(spec))


api.add_resource(DebugLevel, '/debug_level')
api.add_resource(HilAddressMap, '/hil_address_map')

############################################################
#                      IMPLEMENTATION                      #
############################################################


class SettingsManager:

    def __init__(self, low_level_interface):
        self.interface = low_level_interface

    def set_debug_level(self, level):
        self.interface.set_debug_level(level)

    def get_debug_level(self):
        return self.interface.get_debug_level()

    def get_hil_address_map(self):
        return self.interface.get_hil_address_map()

    def set_hil_address_map(self, level):
        self.interface.set_hil_address_map(level)
