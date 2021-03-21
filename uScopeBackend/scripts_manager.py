from flask import current_app, Blueprint, jsonify, request
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required

import json
############################################################
#                      BLUEPRINT                           #
############################################################


scripts_manager_bp = Blueprint('scripts__manager', __name__, url_prefix='/script')


api = Api(scripts_manager_bp)


class Script(Resource):
    @jwt_required()
    def get(self, script_id):
        return jsonify(current_app.script_mgr.load_scripts())

    @jwt_required()
    def post(self, script_id):
        content = request.get_json()
        current_app.script_mgr.upload_script(content)
        return '200'

    @jwt_required()
    def patch(self, script_id):
        edit = request.get_json()
        current_app.script_mgr.edit_script(edit)
        return '200'

    @jwt_required()
    def delete(self, script_id):
        current_app.script_mgr.delete_script(script_id)
        return '200'


class ScriptsHash(Resource):
    @jwt_required()
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
        self.data_store.add_scripts(content)

    def edit_script(self, edit):
        script = self.data_store.get_script(edit['script'])
        script[edit['field']] = edit['value']
        self.data_store.edit_script(script)

    def delete_script(self, script):
        self.data_store.remove_scripts(script)
