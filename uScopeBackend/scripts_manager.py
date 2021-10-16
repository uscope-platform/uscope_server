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


scripts_manager_bp = Blueprint('scripts__manager', __name__, url_prefix='/script')


api = Api(scripts_manager_bp)


class Script(Resource):

    @jwt_required()
    @role_required("operator")
    def get(self, script_id):
        return jsonify(current_app.script_mgr.load_scripts())

    @jwt_required()
    @role_required("user")
    def post(self, script_id):
        content = request.get_json()
        current_app.script_mgr.upload_script(content)
        return '200'

    @jwt_required()
    @role_required("user")
    def patch(self, script_id):
        edit = request.get_json()
        current_app.script_mgr.edit_script(edit)
        return '200'

    @jwt_required()
    @role_required("user")
    def delete(self, script_id):
        current_app.script_mgr.delete_script(script_id)
        return '200'


class ScriptsHash(Resource):
    @jwt_required()
    @role_required("operator")
    def get(self):
        return current_app.script_mgr.get_hash()


api.add_resource(ScriptsHash, '/hash')
api.add_resource(Script, '/<string:script_id>')

############################################################
#                      IMPLEMENTATION                      #
############################################################


class ScriptManager:

    def __init__(self, store):
        self.data_store = store.Elements

    def load_scripts(self):
        return self.data_store.get_scripts_dict()

    def get_hash(self):
        return self.data_store.get_scripts_hash()

    def upload_script(self, content):
        self.data_store.add_script(content)

    def edit_script(self, edit):
        script = self.data_store.get_script(edit['script'])
        script[edit['field']] = edit['value']
        self.data_store.edit_script(script)

    def delete_script(self, script):
        self.data_store.remove_script(script)
