from flask import current_app, Blueprint, Response, request
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required
import json

from . import role_required

############################################################
#                      BLUEPRINT                           #
############################################################


database_manager_bp = Blueprint('database__manager', __name__, url_prefix='/database')


api = Api(database_manager_bp)


class DatabaseExport(Resource):

    @jwt_required()
    @role_required("admin")
    def get(self):
        database = current_app.db_mgr.db_export()
        response = Response(json.dumps(database), mimetype='application/json',
                            headers={'Content-Disposition': 'attachment; filename=db_dump.json'})
        return response


class DatabaseImport(Resource):

    @jwt_required()
    @role_required("admin")
    def post(self):
        db_file = request.get_json()
        current_app.db_mgr.db_import(db_file)
        return '200'


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

    def db_import(self, database):
        self.store.restore(database)
