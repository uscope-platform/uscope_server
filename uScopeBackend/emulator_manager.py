# Copyright 2023 Filippo Savi
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
from flask_jwt_extended import jwt_required
from . import role_required

############################################################
#                      BLUEPRINT                           #
############################################################


emulator_manager_bp = Blueprint('emulator_manager', __name__, url_prefix='/emulators')


api = Api(emulator_manager_bp)


class Emulator(Resource):

    @jwt_required()
    @role_required("user")
    def get(self, emulator_id):
        if emulator_id == "none":
            return jsonify(current_app.emu_mgr.get_emulators())

    @jwt_required()
    @role_required("user")
    def post(self, emulator_id):
        content = request.get_json()
        current_app.emu_mgr.add_emulator(content)
        return '200'

    @jwt_required()
    @role_required("user")
    def patch(self, emulator_id):
        edit = request.get_json()
        current_app.emu_mgr.edit_emulator(edit)
        return '200'

    @jwt_required()
    @role_required("user")
    def delete(self, emulator_id):
        current_app.emu_mgr.delete_emulator(emulator_id)
        return '200'


class EmulatorDigest(Resource):
    @jwt_required()
    @role_required("user")
    def get(self):
        return jsonify(current_app.emu_mgr.get_digest())


api.add_resource(EmulatorDigest, '/digest')
api.add_resource(Emulator, '/<string:emulator_id>')

############################################################
#                      IMPLEMENTATION                      #
############################################################


class EmulatorManager:

    def __init__(self, store):

        self.data_store = store.Elements

    def get_digest(self):
        return self.data_store.get_emulators_hash()

    def get_emulators(self):
        return self.data_store.get_emulators_dict()

    def add_emulator(self, emulator_obj: dict):
        emulators = self.data_store.get_emulators_dict();
        if emulator_obj['id'] in emulators:
            return "Duplicated emulator ID", '400'
        self.data_store.add_emulator(emulator_obj)

    def edit_emulator(self, edit_obj):
        emu_obj = self.data_store.get_emulator(edit_obj['emulator'])
        a = edit_obj['action']
        if a == 'add_core':
            emu_obj['cores'][edit_obj['core']['id']] = edit_obj['core']
        if a == 'edit_name':
            emu_obj['name'] = edit_obj['value']
        elif a == 'edit_core_props':
            emu_obj['cores'][edit_obj['core']][edit_obj['field_name']] = edit_obj['value']
        elif a == 'remove_core':
            del emu_obj['cores'][edit_obj['core']]
        elif a == 'add_connection':
            emu_obj['connections'].append(edit_obj['connection'])
        elif a == 'remove_connection':
            new_list = []
            for item in emu_obj['connections']:
                if item['source'] != edit_obj['source'] or item['target'] != edit_obj['target']:
                    new_list.append(item)
            emu_obj['connections'] = new_list
        elif a == 'remove_node_connections':
            new_list = []
            for item in emu_obj['connections']:
                if item['source'] != edit_obj['node'] and item['target'] != edit_obj['node']:
                    new_list.append(item)
            emu_obj['connections'] = new_list
            print(new_list)
        elif a == 'add_output':
            emu_obj['cores'][edit_obj['core']]['outputs'].append(edit_obj['output'])
        elif a == 'add_input':
            emu_obj['cores'][edit_obj['core']]['inputs'].append(edit_obj['input'])
        elif a == 'add_memory':
            emu_obj['cores'][edit_obj['core']]['memory_init'].append(edit_obj['memory'])
        elif a == 'edit_input':
            input_idx = -1
            for idx, item in enumerate(emu_obj['cores'][edit_obj['core']]['inputs']):
                if item['name'] == edit_obj['input']:
                    input_idx = idx
            if input_idx == -1:
                return
            emu_obj['cores'][edit_obj['core']]['inputs'][input_idx][edit_obj['field_name']] = edit_obj['value']
        elif a == 'edit_output':
            output_idx = -1
            for idx, item in enumerate(emu_obj['cores'][edit_obj['core']]['outputs']):
                if item['name'] == edit_obj['output']:
                    output_idx = idx
            if output_idx == -1:
                return
            emu_obj['cores'][edit_obj['core']]['outputs'][output_idx][edit_obj['field_name']] = edit_obj['value']
        elif a == 'edit_memory':
            memory_idx = -1
            for idx, item in enumerate(emu_obj['cores'][edit_obj['core']]['memory_init']):
                if item['name'] == edit_obj['memory']:
                    memory_idx = idx
            if memory_idx == -1:
                return
            emu_obj['cores'][edit_obj['core']]['memory_init'][memory_idx][edit_obj['field_name']] = edit_obj['value']
        elif a == 'remove_output':
            new_list = []
            for item in emu_obj['cores'][edit_obj['core']]['outputs']:
                if item['name'] != edit_obj["name"]:
                    new_list.append(item)
            emu_obj['cores'][edit_obj['core']]['outputs'] = new_list
        elif a == 'remove_input':
            new_list = []
            for item in emu_obj['cores'][edit_obj['core']]['inputs']:
                if item['name'] != edit_obj["name"]:
                    new_list.append(item)
            emu_obj['cores'][edit_obj['core']]['inputs'] = new_list
        elif a == 'remove_memory':
            new_list = []
            for item in emu_obj['cores'][edit_obj['core']]['memory_init']:
                if item['name'] != edit_obj["name"]:
                    new_list.append(item)
            emu_obj['cores'][edit_obj['core']]['memory_init'] = new_list
        elif a == 'add_dma_channel':
            connection_idx = -1
            for idx, item in enumerate(emu_obj['connections']):
                if item['source'] == edit_obj['source'] and item['target'] == edit_obj['target']:
                    connection_idx = idx
            if connection_idx == -1:
                return
            emu_obj['connections'][connection_idx]['channels'].append(edit_obj['channel'])
        elif a == 'edit_dma_channel':
            connection_idx = -1
            for idx, item in enumerate(emu_obj['connections']):
                if item['source'] == edit_obj['source'] and item['target'] == edit_obj['target']:
                    connection_idx = idx
            if connection_idx == -1:
                return
            channels_idx = -1
            for idx, item in enumerate(emu_obj['connections'][connection_idx]['channels']):
                if item['name'] == edit_obj['channel']:
                    channels_idx = idx
            if channels_idx == -1:
                return
            emu_obj['connections'][connection_idx]['channels'][channels_idx][edit_obj['field_name']] = edit_obj['value']
        elif a == 'remove_dma_channel':
            pass

        self.data_store.edit_emulator(emu_obj)

    def delete_emulator(self, filter_id):
        self.data_store.remove_emulator(filter_id)