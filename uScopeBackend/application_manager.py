from flask import current_app, Blueprint, jsonify, request
from flask_restful import Api, Resource
import json
import redis

############################################################
#                      IMPLEMENTATION                      #
############################################################

application_manager_bp = Blueprint('application_manager', __name__, url_prefix='/application')

api = Api(application_manager_bp)


class ApplicationSet(Resource):
    def get(self, application_name):
        current_app.plot_mgr.set_application(application_name)
        return jsonify(current_app.app_mgr.set_application(application_name))

class ApplicationParameters(Resource):
    def get(self):
        return jsonify(current_app.app_mgr.get_parameters())

    def post(self):
        parameters = request.get_json(force=True)
        current_app.app_mgr.set_parameters(parameters['payload'])
        return '200'


class ApplicationsDigest(Resource):
    def get(self):
        return current_app.app_mgr.get_applications_hash()


class ApplicationsSpecs(Resource):
    def get(self):
        return jsonify(current_app.app_mgr.get_all_applications())


class ApplicationRemove(Resource):
    def get(self, application_name):
        current_app.app_mgr.remove_application(application_name)
        return '200'


class ApplicationAdd(Resource):

    def post(self):
        parameters = request.get_json(force=True)
        current_app.app_mgr.add_application(parameters)
        return '200'


api.add_resource(ApplicationRemove, '/remove/<string:application_name>')
api.add_resource(ApplicationsSpecs, '/all/specs')
api.add_resource(ApplicationSet, '/set/<string:application_name>')
api.add_resource(ApplicationParameters, '/parameters')
api.add_resource(ApplicationsDigest, '/digest')
api.add_resource(ApplicationAdd, '/add')

############################################################
#                      IMPLEMENTATION                      #
############################################################


class ApplicationManager:
    def __init__(self, interface, store, redis_host):
        self.store = store
        self.parameters = {}
        self.interface = interface
        self.redis_if = redis.Redis(host=redis_host, port=6379, db=0)

    def add_application(self, application):
        self.store.add_application(application)

    def remove_application(self, application_name):
        self.store.remove_application(application_name)

    def set_application(self, application_name):
        self.redis_if.set('chosen_application', json.dumps(self.store.get_applications()[application_name]))
        self.redis_if.set('parameters', json.dumps(self.store.get_applications()[application_name]['parameters']))

        self.load_bitstream(self.store.get_applications()[application_name]['bitstream'])
        if 'initial_registers_values' in self.store.get_applications()[application_name]:
            self.initialize_registers(self.store.get_applications()[application_name]['initial_registers_values'])

    def get_all_applications(self):
        return self.store.get_applications()

    def get_applications_hash(self):
        return self.store.get_applications_hash()

    def get_peripheral_base_address(self, peripheral):
        chosen_application = json.loads(self.redis_if.get('chosen_application'))
        for tab in chosen_application['tabs']:
            if tab['tab_id'] == peripheral:
                return tab['base_address']
            pass

        raise ValueError('could not find the periperal %s' % peripheral)

    def peripheral_is_proxied(self, peripheral):
        chosen_application = json.loads(self.redis_if.get('chosen_application'))
        for tab in chosen_application['tabs']:
            if tab['tab_id'] == peripheral:
                return tab['proxied']
            pass
        raise ValueError('could not find the periperal %s' % peripheral)

    def get_peripheral_proxy_address(self, peripheral):
        chosen_application = json.loads(self.redis_if.get('chosen_application'))
        for tab in chosen_application['tabs']:
            if tab['tab_id'] == peripheral:
                return tab['proxy_address']
            pass

    def get_parameters(self):
        params = json.loads(self.redis_if.get('parameters'))
        return params

    def set_parameters(self, param):
        params = json.loads(self.redis_if.get('parameters'))
        params[param['name']] = param['value']
        self.redis_if.set('parameters', json.dumps(params))

    def load_bitstream(self, name):
        self.interface.load_bitstream(name)

    def initialize_registers(self, registers):
        for reg in registers:
            addr = int(reg['address'], 0)
            value = int(reg['value'], 0)
            self.interface.write_register(addr, value)