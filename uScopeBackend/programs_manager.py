from flask import current_app, Blueprint, jsonify, request
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required

############################################################
#                      BLUEPRINT                           #
############################################################


programs_manager_bp = Blueprint('programs_manager', __name__, url_prefix='/program')


api = Api(programs_manager_bp)


class Program(Resource):
    @jwt_required
    def get(self, program_id):
        return jsonify(current_app.programs_mgr.load_programs())

    @jwt_required
    def post(self, program_id):
        content = request.get_json()
        current_app.programs_mgr.upload_program(program_id, content)
        return '200'

    @jwt_required
    def patch(self, program_id):
        edit = request.get_json()
        current_app.programs_mgr.edit_program(edit)
        return '200'

    @jwt_required
    def delete(self, program_id):
        current_app.programs_mgr.remove_program(program_id)
        return '200'


class ProgramHash(Resource):
    @jwt_required
    def get(self):
        return current_app.programs_mgr.get_hash()


api.add_resource(ProgramHash, '/hash')
api.add_resource(Program, '/<string:program_id>')

############################################################
#                      IMPLEMENTATION                      #
############################################################


class ProgramsManager:

    def __init__(self, store):
        self.store = store

    def load_programs(self):
        return self.store.get_programs()

    def get_hash(self):
        return self.store.get_program_hash()

    def upload_program(self, program_id, content):
        self.store.add_program(program_id, content)

    def edit_program(self, edit):
        program = self.store.get_programs()[str(edit['program'])]
        program[edit['field']] = edit['value']
        self.store.add_program(str(edit['program']), program)

    def remove_program(self, program):
        self.store.remove_program(program)
