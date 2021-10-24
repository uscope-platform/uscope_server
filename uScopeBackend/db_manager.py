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

from flask import current_app, Blueprint, Response, request
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required
import json
import os
import base64

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
        dump['elements']['bitstream_contents'] = self.export_bitstreams()
        return dump

    def db_import(self, database):
        self.restore_bitstreams(database['elements']['bitstream_contents'])
        self.store.restore(database)

    def export_bitstreams(self):
        bitstreams_dict = {}
        bitstreams_dump = {}
        debug_config = os.environ.get("DEBUG")
        if debug_config != "TRUE":
            bitstreams_dict = self.store.Elements.get_bitstreams_dict()
            for i in bitstreams_dict:
                path = bitstreams_dict[i]['path']
                with open(path, mode='rb') as file:
                    b64_bytes = base64.b64encode(file.read())
                    bitstreams_dump[path] = b64_bytes.decode('utf-8')

        return bitstreams_dump

    def restore_bitstreams(self, dump):
            for i in dump:
                with open(i, mode='wb') as file:
                    encoded_bytes = dump[i].encode('utf-8')
                    file.write(base64.b64decode(encoded_bytes))
