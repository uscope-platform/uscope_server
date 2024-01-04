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
from flask_jwt_extended import jwt_required, get_jwt_identity

import base64
import os
import subprocess

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
        self.arch = "zynq"
        if "ARCH" in os.environ:
            self.arch = os.environ.get("ARCH")
        self.target_arch = os.environ.get("DEBUG")
        self.debug = debug_config == "TRUE"

        if self.debug:
            self.bitstream_storage_path = "/tmp/firmware"
        else:
            self.bitstream_storage_path = "/lib/firmware"

        if not os.path.exists(self.bitstream_storage_path):
            os.makedirs(self.bitstream_storage_path)

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

    def name_to_path(self, name: str):
        return  self.bitstream_storage_path + f'/{name}.bin'

    def path_to_name(self, path: str):
        name = path.replace('.bin', '')
        name = name.replace(self.bitstream_storage_path+'/', '')
        return name

    def add_bitstream(self, raw_bitstream_obj: dict):
        print(f"ADD BITSTREAM {raw_bitstream_obj['name']}")
        bitstream_path = self.name_to_path(raw_bitstream_obj["name"])

        if not self.debug:
            if self.arch == "zynq":
                self.write_zynq_bitstream(raw_bitstream_obj, bitstream_path)
            elif self.arch == "zynqmp":
                self.write_zynqmp_bitstream(raw_bitstream_obj, bitstream_path)
            else:
                return

        bitstream_obj = {'id': raw_bitstream_obj['id'], 'path': bitstream_path}
        self.data_store.add_bitstream(bitstream_obj)

    def edit_bitstream(self, edit_obj):
        field = edit_obj['field']
        bitstream = self.data_store.get_bitstream(edit_obj['id'])

        if field['name'] == 'name':
            new_path = self.name_to_path(field['value'])
            if not self.debug:
                os.replace(bitstream['path'], new_path)

            bitstream['path'] = new_path
            self.data_store.edit_bitstream(bitstream)

        elif field['name'] == 'file_content':
            content = base64.b64decode(field['value'])
            if not self.debug:
                with open(bitstream['path'], "wb+") as f:
                    f.write(content)

    def delete_bitstream(self, bitstream_id):
        bitstream = self.data_store.get_bitstream(bitstream_id)
        if not self.debug:
            os.remove(bitstream['path'])
        self.data_store.remove_bitstream(bitstream_id)


    def write_zynqmp_bitstream(self, bit_file, bitstream_path):
        content = base64.b64decode(bit_file['content'])
        bif_content = '''
            //arch = zynqmp; split = false; format = BIN
            all:
            {
                 [destination_device = pl] {{input_dir}}/input.bit
            }
            '''

        bif_content = bif_content.replace("{{input_dir}}", self.bitstream_storage_path)

        input_file_path = f'{self.bitstream_storage_path}/input.bit'
        input_bif_path = f'{self.bitstream_storage_path}/input.bif'
        with open(input_file_path, "wb+") as f:
            f.write(content)
        with open(input_bif_path, "w") as f:
            f.write(bif_content)
        processed_file = f'{input_file_path}.bin'
        subprocess.run(["bootgen", "-image", input_bif_path, "-arch", "zynqmp", "-o", "./"+processed_file, '-w'])
        os.rename(processed_file, bitstream_path)
        os.remove(input_file_path)
        os.remove(input_bif_path)

    def write_zynq_bitstream(self, bit_file, bitstream_path):
        content = base64.b64decode(bit_file['content'])
        bif_content = '''
        //arch = zynq; split = false; format = BIN
        all:
        {
            {{input_dir}}/input.bit
        }
        '''

        bif_content = bif_content.replace("{{input_dir}}", self.bitstream_storage_path)

        input_file_path = f'{self.bitstream_storage_path}/input.bit'
        input_bif_path = f'{self.bitstream_storage_path}/input.bif'
        with open(input_file_path, "wb+") as f:
            f.write(content)
        with open(input_bif_path, "w") as f:
            f.write(bif_content)
        subprocess.run(["bootgen", "-process_bitstream", "bin", "-arch", "zynq", "-image", input_bif_path])
        processed_file = f'{input_file_path}.bin'
        os.rename(processed_file, bitstream_path)
        os.remove(input_file_path)
        os.remove(input_bif_path)
