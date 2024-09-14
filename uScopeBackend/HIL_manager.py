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

import json
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


class Hil_select_output(Resource):
    @jwt_required()
    @role_required("user")
    def post(self):
        spec = request.get_json()
        return jsonify(current_app.hil_mgr.select_out(spec))


class Hil_set_input(Resource):
    @jwt_required()
    @role_required("user")
    def post(self):
        spec = request.get_json()
        return jsonify(current_app.hil_mgr.set_input(spec))


class Hil_start(Resource):
    @jwt_required()
    @role_required("user")
    def get(self):
        return jsonify(current_app.hil_mgr.start_hil())


class Hil_stop(Resource):
    @jwt_required()
    @role_required("user")
    def get(self):
        return jsonify(current_app.hil_mgr.stop_hil())


api.add_resource(HIL_deploy, '/deploy')
api.add_resource(Hil_select_output, '/select_out')
api.add_resource(Hil_set_input, '/set_input')
api.add_resource(Hil_start, '/start')
api.add_resource(Hil_stop, '/stop')

############################################################
#                      IMPLEMENTATION                      #
############################################################


class HilManager:

    def __init__(self, low_level_interface):
        self.interface = low_level_interface


    def deploy(self, specs):
        res = self.interface.deploy_hil(specs)
        if res == 1:
            return json.loads(res["results"])
        else:
            return {"code": res["error_code"], "error": res["error"], "duplicates": res["duplicates"]}


    def select_out(self, specs):
        return self.interface.select_out(specs)

    def set_input(self, specs):
        return self.interface.set_in(specs)

    def start_hil(self):
        return self.interface.start_hil()

    def stop_hil(self):
        return self.interface.stop_hil()
