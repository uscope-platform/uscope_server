from flask import current_app, Blueprint, jsonify, request
from flask_restful import Api, Resource
import os, json

############################################################
#                      IMPLEMENTATION                      #
############################################################

application_manager_bp = Blueprint('application_manager', __name__, url_prefix='/application')

api = Api(application_manager_bp)


class ApplicationList(Resource):
    def get(self):
        return jsonify(current_app.app_mgr.applications_list)


class ApplicationSpecs(Resource):
    def get(self, application_name):
        return jsonify(current_app.app_mgr.get_application(application_name))


class ApplicationParameters(Resource):
    def get(self):
        return jsonify(current_app.app_mgr.get_parameters())

    def post(self):
        parameters = request.get_json(force=True)
        current_app.app_mgr.set_parameters(parameters['payload'])
        return '200'


api.add_resource(ApplicationList, '/list')
api.add_resource(ApplicationSpecs, '/specs/<string:application_name>')
api.add_resource(ApplicationParameters, '/parameters')
############################################################
#                      IMPLEMENTATION                      #
############################################################


class ApplicationManager:
    def __init__(self, interface):
        self.applications, self.applications_list = self.load_applications()
        with open("static/parameters_setup.json", 'r') as f:
            # TODO: add support for per application parameters
            self.parameters_specs = json.load(f)
        self.parameters = {}
        self.chosen_application = {}
        self.interface = interface

    @staticmethod
    def load_applications():
        settings = [f for f in os.listdir('static') if os.path.isfile(os.path.join('static', f))]
        application_specs = {}
        application_list = []
        for fname in settings:
            if not fname.split('.')[1] == 'json':
                continue
            else:
                name = fname.replace('.json', '')

            parsed = name.rsplit('_', 1)

            if parsed[1] == 'descriptor':
                with open('static/'+fname,'r') as f:
                    content = json.load(f)
                    application_specs[parsed[0]] = content

        for i in application_specs:
            application_list.append(i)

        return application_specs, application_list

    def get_parameters(self):
        return self.parameters_specs['parameters']

    def get_application(self, application_name):
        self.chosen_application = self.applications[application_name]
        self.load_bitstream(application_name)
        return self.chosen_application

    def get_peripheral_base_address(self, peripheral):
        for tab in self.chosen_application['tabs']:
            if tab['tab_id'] == peripheral:
                return tab['base_address']
            pass

        raise ValueError('could not find the periperal %s' % peripheral)

    def set_parameters(self, param):
        self.parameters[param['name']] = param['value']
        if param['name'] == 'uscope_timebase_change':
            self.interface.change_timebase(param['value'])

    def load_bitstream(self, name):
        pass