from flask import current_app, Blueprint, jsonify, request
from flask_restful import Api, Resource


############################################################
#                      BLUEPRINT                           #
############################################################


scripts__manager_bp = Blueprint('scripts__manager', __name__, url_prefix='/script')


api = Api(scripts__manager_bp)


class Script(Resource):
    def get(self, name):
        return jsonify(current_app.script_mgr.load_scripts())

    def post(self, name):
        content = request.get_json()
        current_app.script_mgr.upload_script(name, content)
        return '200'

    def delete(self, name):
        current_app.script_mgr.delete_script(name)
        return '200'


class ScriptsHash(Resource):
    def get(self):
        return current_app.script_mgr.get_hash()


api.add_resource(ScriptsHash, '/hash')
api.add_resource(Script, '/<string:name>')

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

    def upload_script(self, name, content):
        self.store.add_scripts(name, content)

    def delete_script(self, script):
        self.store.remove_scripts(script)
