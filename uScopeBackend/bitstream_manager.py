from flask import current_app, Blueprint, jsonify, request
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

import base64
import os

from . import role_required

############################################################
#                      IMPLEMENTATION                      #
############################################################


bitstream_manager_bp = Blueprint('bitstream_manager', __name__, url_prefix='/bitstream')

api = Api(bitstream_manager_bp)


class Bitstream(Resource):

    @jwt_required()
    @role_required("operator")
    def get(self, bitstream_id):
        return jsonify(current_app.bitstream_mgr.load_bitstreams())

    @jwt_required()
    @role_required("admin")
    def post(self, bitstream_id):
        content = request.get_json()
        current_app.bitstream_mgr.add_bitstream(content)
        return '200'

    @jwt_required()
    @role_required("admin")
    def patch(self, bitstream_id):
        edit = request.get_json()
        current_app.bitstream_mgr.edit_bitstream(edit)
        return '200'

    @jwt_required()
    @role_required("admin")
    def delete(self, bitstream_id):
        current_app.bitstream_mgr.delete_bitstream(bitstream_id)
        return '200'


class BitstreamsDigest(Resource):
    @jwt_required()
    @role_required("operator")
    def get(self):
        return current_app.bitstream_mgr.get_digest()


api.add_resource(BitstreamsDigest, '/digest')
api.add_resource(Bitstream, '/<string:bitstream_id>')


############################################################
#                      IMPLEMENTATION                      #
############################################################


class BitstreamManager:

    def __init__(self, store):
        debug_config = os.environ.get("DEBUG")
        self.debug = debug_config == "TRUE"

        self.data_store = store.Elements
        self.settings_store = store.Settings

    def get_digest(self):
        return self.data_store.get_bitstreams_hash()

    def load_bitstreams(self):
        bitstreams_dict = self.data_store.get_bitstreams_dict()
        for i in bitstreams_dict:
            bitstreams_dict[i]['name'] = self.path_to_name(bitstreams_dict[i]['path'])
            del bitstreams_dict[i]['path']
        return bitstreams_dict

    def name_to_path(self, name:str):
        return  f'/lib/firmware/{name}.bin'

    def path_to_name(self, path:str):
        name = path.replace('.bin', '')
        name = name.replace('/lib/firmware/', '')
        return name

    def add_bitstream(self, raw_bitstream_obj:dict):
        content = base64.b64decode(raw_bitstream_obj['content'])
        bitstream_path = self.name_to_path(raw_bitstream_obj["name"])

        if not self.debug:
            with open(bitstream_path, "wb+") as f:
                f.write(content)

        bitstream_obj = {'id':raw_bitstream_obj['id'], 'path':bitstream_path}
        self.data_store.add_bitstream(bitstream_obj)

    def edit_bitstream(self, edit_obj):
        field = edit_obj['field']
        bitstream = self.data_store.get_bitstream(edit_obj['id'])
        if field['name'] == 'name':
            new_path = self.name_to_path(field['value'])
            if not self.debug:
                os.replace(bitstream['path'], new_path)

            bitstream['path'] = new_path

        elif field['name'] == 'file_content':
            content = base64.b64decode(field['value'])
            if not self.debug:
                with open(bitstream['path'], "wb+") as f:
                    f.write(content)
            return

        self.data_store.edit_bitstream(bitstream)

    def delete_bitstream(self, bitstream_id):
        bitstream = self.data_store.get_bitstream(bitstream_id)
        os.remove(bitstream['path'])
        self.data_store.remove_bitstream(bitstream_id)
