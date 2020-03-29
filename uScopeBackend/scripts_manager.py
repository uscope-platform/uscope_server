from flask import current_app, Blueprint, jsonify, request
from flask_restful import Api, Resource


############################################################
#                      BLUEPRINT                           #
############################################################


scripts__manager_bp = Blueprint('scripts__manager', __name__, url_prefix='/script')


api = Api(scripts__manager_bp)


class Script(Resource):
    def get(self, script_id):
        return jsonify(current_app.script_mgr.load_scripts())

    def post(self, script_id):
        content = request.get_json()
        current_app.script_mgr.upload_script(script_id, content)
        return '200'

    def patch(self, script_id):
        content = request.get_json()
        current_app.script_mgr.edit_script(script_id, content)
        return '200'

    def delete(self, script_id):
        current_app.script_mgr.delete_script(script_id)
        return '200'


class ScriptsHash(Resource):
    def get(self):
        return current_app.script_mgr.get_hash()


api.add_resource(ScriptsHash, '/hash')
api.add_resource(Script, '/<string:script_id>')

############################################################
#                      IMPLEMENTATION                      #
############################################################


class ScriptManager:

    def __init__(self, store):
        self.store = store

    def load_scripts(self):
        return self.store.load_scripts()

    def get_hash(self):
        return self.store.get_scripts_hash()

    def upload_script(self, script_id, content):
        self.store.add_scripts(script_id, content)

    def edit_script(self, script_id, content):
        self.store.add_scripts(script_id, content)

    def delete_script(self, script):
        self.store.remove_scripts(script)
