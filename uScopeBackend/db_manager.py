from flask import current_app, Blueprint, Response, request
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required
import json
import os

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
        dump['bitstream_contents'] = self.export_bitstreams()
        return dump

    def db_import(self, database):
        self.restore_bitstreams(database['bitstream_contents'])
        self.store.restore(database)

    def export_bitstreams(self):
        bitstreams_dict = {}
        debug_config = os.environ.get("DEBUG")
        if debug_config == "TRUE":
            bitstreams_dict = self.store.Elements.get_bitstreams_dict()
            bitstreams_dump = {}
            for i in bitstreams_dict:
                path = bitstreams_dict[i]['path']
                with open(path, mode='rb') as file:
                    bitstreams_dump[path] = file.read()

        return bitstreams_dict

    def restore_bitstreams(self, dump):
        for i in dump:
            with open(i, mode='wb') as file:
                file.write(dump[i])