from flask import current_app, Blueprint, jsonify, request
from flask_restful import Api, Resource
import os, json
from sqlitedict import SqliteDict

############################################################
#                      IMPLEMENTATION                      #
############################################################

application_manager_bp = Blueprint('application_manager', __name__, url_prefix='/application')

api = Api(application_manager_bp)


class ApplicationList(Resource):
    def get(self):
        applist = list(current_app.app_mgr.get_all_applications().keys())
        return jsonify(applist)


class ApplicationSpecs(Resource):
    def get(self, application_name):
        current_app.plot_mgr.set_application(application_name)
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
    def __init__(self, interface, store):
        self.store = store
        self.parameters = {}
        self.interface = interface

    def get_application(self, application_name):
        with SqliteDict('.shared_storage.db') as storage:
            storage['chosen_application'] = self.store.get_applications()[application_name]
            storage['parameters'] = self.store.get_applications()[application_name]['parameters']
            storage.commit()

        self.load_bitstream(self.store.get_applications()[application_name]['bitstream'])
        if 'initial_registers_values' in self.store.get_applications()[application_name]:
            self.initialize_registers(self.store.get_applications()[application_name]['initial_registers_values'])

        return self.store.get_applications()[application_name]

    def get_all_applications(self):
        return self.store.get_applications()

    def get_peripheral_base_address(self, peripheral):
        with SqliteDict('.shared_storage.db') as storage:
            chosen_application = storage['chosen_application']
        for tab in chosen_application['tabs']:
            if tab['tab_id'] == peripheral:
                return tab['base_address']
            pass

        raise ValueError('could not find the periperal %s' % peripheral)


    def peripheral_is_proxied(self, peripheral):
        with SqliteDict('.shared_storage.db') as storage:
            chosen_application = storage['chosen_application']
        for tab in chosen_application['tabs']:
            if tab['tab_id'] == peripheral:
                return tab['proxied']
            pass

        raise ValueError('could not find the periperal %s' % peripheral)

    def get_peripheral_proxy_address(self, peripheral):
        with SqliteDict('.shared_storage.db') as storage:
            chosen_application = storage['chosen_application']
        for tab in chosen_application['tabs']:
            if tab['tab_id'] == peripheral:
                return tab['proxy_address']
            pass

    def get_parameters(self):
        with SqliteDict('.shared_storage.db') as storage:
            params = storage['parameters']

        return params

    def set_parameters(self, param):
        with SqliteDict('.shared_storage.db') as storage:
            params = storage['parameters']
            params[param['name']] = param['value']
            storage['parameters'] = param
            storage.commit()

    def load_bitstream(self, name):
        self.interface.load_bitstream(name)

    def initialize_registers(self, registers):
        for reg in registers:
            addr = int(reg['address'], 0)
            value = int(reg['value'], 0)
            self.interface.write_register(addr, value)