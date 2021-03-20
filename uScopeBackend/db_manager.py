from flask import current_app, Blueprint, Response
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required
import json
############################################################
#                      BLUEPRINT                           #
############################################################


database_manager_bp = Blueprint('database__manager', __name__, url_prefix='/database')


api = Api(database_manager_bp)


class DatabaseExport(Resource):
    @jwt_required()
    def get(self):
        database = current_app.db_mgr.db_export()
        response = Response(json.dumps(database), mimetype='application/json',
                            headers={'Content-Disposition': 'attachment; filename=db_dump.json'})
        return response


class DatabaseImport(Resource):
    @jwt_required()
    def post(self):
        return current_app.script_mgr.get_hash()


api.add_resource(DatabaseImport, '/import')
api.add_resource(DatabaseExport, '/export')

############################################################
#                      IMPLEMENTATION                      #
############################################################


class DatabaseManager:

    def __init__(self, store):
        self.store = store

    def db_export(self):
        dump = self.store.dump()
        return dump

    def db_import(self):
        pass


