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
from flask_jwt_extended import jwt_required
import fCore_compiler

from . import role_required

############################################################
#                      BLUEPRINT                           #
############################################################


programs_manager_bp = Blueprint('programs_manager', __name__, url_prefix='/program')


api = Api(programs_manager_bp)


class Program(Resource):
    @jwt_required()
    @role_required("operator")
    def get(self, program_id):
        return jsonify(current_app.programs_mgr.load_programs())

    @jwt_required()
    @role_required("user")
    def post(self, program_id):
        content = request.get_json()
        current_app.programs_mgr.upload_program(content)
        return '200'

    @jwt_required()
    @role_required("user")
    def patch(self, program_id):
        edit = request.get_json()
        current_app.programs_mgr.edit_program(edit)
        return '200'

    @jwt_required()
    @role_required("user")
    def delete(self, program_id):
        current_app.programs_mgr.remove_program(program_id)
        return '200'


class ProgramApply(Resource):
    @jwt_required()
    @role_required("operator")
    def post(self, program_id):
        content = request.get_json()
        return current_app.programs_mgr.apply_program(program_id, content['core_id'], content["application"])


class ProgramHash(Resource):
    @jwt_required()
    @role_required("operator")
    def get(self):
        return current_app.programs_mgr.get_hash()


class ProgramCompile(Resource):
    @jwt_required()
    @role_required("user")
    def get(self, program_id):
        return jsonify(current_app.programs_mgr.compile_program(program_id))


api.add_resource(ProgramHash, '/hash')
api.add_resource(Program, '/<string:program_id>')
api.add_resource(ProgramCompile, '/compile/<string:program_id>')
api.add_resource(ProgramApply, '/Apply/<string:program_id>')

############################################################
#                      IMPLEMENTATION                      #
############################################################


class ProgramsManager:

    def __init__(self, interface, store):
        self.interface = interface
        self.data_store = store.Elements
        self.bridge = fCore_compiler.CompilerBridge()

    def load_programs(self):
        return self.data_store.get_programs_dict()

    def get_hash(self):
        return str(self.data_store.get_program_hash())

    def upload_program(self, content):
        self.data_store.add_program(content)

    def edit_program(self, edit):
        program = self.data_store.get_program(edit['program'])
        program[edit['field']] = edit['value']
        self.data_store.edit_program(program)

    def remove_program(self, program):
        self.data_store.remove_program(program)

    def compile_program(self, program_id):
        program = self.data_store.get_program(program_id)
        try:
            compiled_res, program_size, new_hash = self.bridge.compile(program['program_content'], program['program_type'])
        except ValueError as err:
            error_codes = [{"status": "failed", "file": program['name'], "error": str(err)}]
            return error_codes
        program['hex'] = compiled_res
        self.data_store.edit_program(program)
        error_codes = [{"status": "passed", "file": program['name'], "error": None}]
        return error_codes


    def apply_program(self, program_id, core_id, application_name):
        print(f'APPLY PROGRAM ID: {program_id} TO CORE: {core_id}')
        app = self.data_store.get_application(application_name)
        programs = self.data_store.get_programs_dict()
        key = None
        for key in programs:
            if program_id == programs[key]['name']:
                break
        if not key:
            raise RuntimeError(f"ERROR: program named {program_id} not found")
        program = self.data_store.get_program(key)
        core = list(filter(lambda x: x["id"] == core_id, app["soft_cores"]))[0]
        program_hex = program["hex"]
        if "io" in core:
            if core["io"]:
                try:
                    program_hex, program_size, new_hash = self.bridge.compile(
                        program['program_content'],
                        program['program_type'],
                        dma_io=core["io"],
                        cached_hash=program['cached_bin_version']
                    )
                    if new_hash != program['cached_bin_version']:
                        program["hex"] = program_hex
                        program['cached_bin_version'] = new_hash
                        self.data_store.edit_program(program)
                except ValueError as err:
                    return "501"
                except fCore_compiler.CacheHitException as err:
                    pass

        self.interface.apply_program(program_hex, core["address"])
        return '200'

