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


hil_manager_bp = Blueprint('hil_manager', __name__, url_prefix='/hil')


api = Api(hil_manager_bp)


class HIL_deploy(Resource):

    @jwt_required()
    @role_required("user")
    def post(self):
        spec = request.get_json()
        return jsonify(current_app.hil_mgr.deploy(spec))


api.add_resource(HIL_deploy, '/deploy')

############################################################
#                      IMPLEMENTATION                      #
############################################################


class HilManager:

    def __init__(self, low_level_interface):
        self.interface = low_level_interface

    def deploy(self, specs):
        return self.interface.deploy_hil(specs)
