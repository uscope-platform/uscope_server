from flask import current_app, Blueprint, jsonify, request, Response
from flask_restful import Api, Resource


############################################################
#                      BLUEPRINT                           #
############################################################


database__manager_bp = Blueprint('database__manager', __name__, url_prefix='/database')


api = Api(database__manager_bp)


class DatabaseExport(Resource):

    def get(self):
        database = current_app.db_mgr.db_export()
        response = Response(database, mimetype='application/octet-stream', headers={'Content-Disposition': 'attachment; filename=db_dump.rdb'})
        return response


class DatabaseImport(Resource):

    def post(self):
        return current_app.script_mgr.get_hash()


api.add_resource(DatabaseImport, '/import')
api.add_resource(DatabaseExport, '/export')

############################################################
#                      IMPLEMENTATION                      #
############################################################


class DatabaseManager:

    def __init__(self, db_path):
        self.db_path = db_path

    def db_export(self):
        with open(self.db_path, 'rb') as f:
            file_content = f.read()

        return file_content

    def db_import(self):
        return self.store.get_scripts_hash()


