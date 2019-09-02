from flask import current_app, Blueprint, jsonify
from flask_restful import Api, Resource


############################################################
#                      IMPLEMENTATION                      #
############################################################


registers_manager_bp = Blueprint('plot_manager', __name__, url_prefix='/registers')


api = Api(registers_manager_bp)


class RegisterValue(Resource):
    def get(self):
        pass
    def post(self):
        pass




api.add_resource(RegisterValue, '/value/<string:data>')


############################################################
#                      IMPLEMENTATION                      #
############################################################


class RegistersManager:

    def __init__(self):
        pass