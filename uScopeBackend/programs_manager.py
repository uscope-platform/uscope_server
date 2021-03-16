from flask import current_app, Blueprint, jsonify, request
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required
import fCore_compiler
############################################################
#                      BLUEPRINT                           #
############################################################


programs_manager_bp = Blueprint('programs_manager', __name__, url_prefix='/program')


api = Api(programs_manager_bp)


class Program(Resource):
    @jwt_required()
    def get(self, program_id):
        return jsonify(current_app.programs_mgr.load_programs())

    @jwt_required()
    def post(self, program_id):
        content = request.get_json()
        current_app.programs_mgr.upload_program(program_id, content)
        return '200'

    @jwt_required()
    def patch(self, program_id):
        edit = request.get_json()
        current_app.programs_mgr.edit_program(edit)
        return '200'

    @jwt_required()
    def delete(self, program_id):
        current_app.programs_mgr.remove_program(program_id)
        return '200'


class ProgramApply(Resource):
    @jwt_required()
    def post(self, program_id):
        content = request.get_json()
        return current_app.programs_mgr.apply_program(program_id, content['core_address'])


class ProgramHash(Resource):
    @jwt_required()
    def get(self):
        return current_app.programs_mgr.get_hash()


class ProgramCompile(Resource):
    @jwt_required()
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

    def __init__(self, interface, data_store):
        self.interface = interface
        self.data_store = data_store
        self.bridge = fCore_compiler.CompilerBridge()

    def load_programs(self):
        return self.data_store.get_programs_dict()

    def get_hash(self):
        return str(self.data_store.get_program_hash())

    def upload_program(self, program_id, content):
        self.data_store.add_program(program_id, content)

    def edit_program(self, edit):
        program = self.data_store.get_program(edit['program'])
        program[edit['field']] = edit['value']
        self.data_store.add_program(str(edit['program']), program)

    def remove_program(self, program):
        self.data_store.remove_program(program)

    def compile_program(self, program_id):
        program = self.data_store.get_program(program_id)
        try:
            result = self.bridge.compile(program['program_content'])
        except ValueError as err:
            error_codes = [{"status": "failed", "file": program['path'], "error": str(err)}]
            return error_codes
        program['hex'] = result[0][0:result[1]]
        self.data_store.add_program(program_id, program)
        error_codes = [{"status": "passed", "file": program['path'], "error": None}]
        return error_codes

    def apply_program(self, program_id, core_address):
        print(f'APPLY PROGRAM ID: {program_id} TO CORE AT ADDRESS: {core_address}')
        program = self.data_store.get_program(program_id)
        self.interface.apply_program(program, core_address)
        return '200'

