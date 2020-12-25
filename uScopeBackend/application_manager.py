from flask import current_app, Blueprint, jsonify, request
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required
import json
import redis

############################################################
#                      IMPLEMENTATION                      #
############################################################

application_manager_bp = Blueprint('application_manager', __name__, url_prefix='/application')

api = Api(application_manager_bp)


class ApplicationSet(Resource):
    @jwt_required
    def get(self, application_name):
        current_app.plot_mgr.set_application(application_name)
        return jsonify(current_app.app_mgr.set_application(application_name))


class ApplicationParameters(Resource):
    @jwt_required
    def get(self):
        return jsonify(current_app.app_mgr.get_parameters())

    @jwt_required
    def post(self):
        parameters = request.get_json(force=True)
        current_app.app_mgr.set_parameters(parameters['payload'])
        return '200'


class ApplicationsDigest(Resource):
    @jwt_required
    def get(self):
        return current_app.app_mgr.get_applications_hash()


class ApplicationsSpecs(Resource):
    @jwt_required
    def get(self):
        return jsonify(current_app.app_mgr.get_all_applications())


class ApplicationAdd(Resource):
    @jwt_required
    def post(self):
        parameters = request.get_json(force=True)
        current_app.app_mgr.add_application(parameters)
        return '200'


class ApplicationEdit(Resource):
    @jwt_required
    def post(self):
        parameters = request.get_json(force=True)
        current_app.app_mgr.edit_application(parameters)
        return '200'


class ApplicationRemove(Resource):
    @jwt_required
    def get(self, application_name):
        current_app.app_mgr.remove_application(application_name)
        return '200'


api.add_resource(ApplicationsSpecs, '/all/specs')
api.add_resource(ApplicationSet, '/set/<string:application_name>')
api.add_resource(ApplicationParameters, '/parameters')
api.add_resource(ApplicationsDigest, '/digest')
api.add_resource(ApplicationAdd, '/add')
api.add_resource(ApplicationEdit, '/edit')
api.add_resource(ApplicationRemove, '/remove/<string:application_name>')

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
        """Adds the application from the parameters to the database

            Parameters:
                application: application to add
        """
        key, val = application.popitem()
        self.store.add_application(key, val)

    def edit_application(self, edit):
        current_app = self.store.get_applications()[edit["application"]]
        if edit["action"] == "add_channel":
            current_app['channels'].append(edit['channel'])
        elif edit["action"] == "edit_channel":
            present = False
            for idx, val in enumerate(current_app['channels']):
                if val['name'] == edit['channel']:
                    present = True
                    break
            if present:
                current_app['channels'][idx][edit['field']] = edit['value']
        elif edit["action"] == "remove_channel":
            present = False
            for idx, val in enumerate(current_app['channels']):
                if val['name'] == edit['channel']:
                    present = True
                    break
            if present:
                del current_app['channels'][idx]
        elif edit["action"] == "add_irv":
            current_app['initial_registers_values'].append(edit['irv'])
        elif edit["action"] == "edit_irv":
            present = False
            for idx, val in enumerate(current_app['initial_registers_values']):
                if val['address'] == edit['address']:
                    present = True
                    break
            if present:
                current_app['initial_registers_values'][idx][edit['field']] = edit['value']
        elif edit["action"] == "remove_irv":
            present = False
            for idx, val in enumerate(current_app['initial_registers_values']):
                if val['address'] == edit['address']:
                    present = True
                    break
            if present:
                del current_app['initial_registers_values'][idx]
        elif edit["action"] == "add_macro":
            current_app['macro'].append(edit['macro'])
        elif edit["action"] == "edit_macro":
            present = False
            for idx, val in enumerate(current_app['macro']):
                if val['name'] == edit['name']:
                    present = True
                    break
            if present:
                current_app['macro'][idx][edit['field']] = edit['value']
        elif edit["action"] == "remove_macro":
            present = False
            for idx, val in enumerate(current_app['macro']):
                if val['name'] == edit['name']:
                    present = True
                    break
            if present:
                del current_app['macro'][idx]
        elif edit["action"] == "add_parameter":
            current_app['parameters'].append(edit['parameter'])
        elif edit["action"] == "edit_parameter":
            present = False
            for idx, val in enumerate(current_app['parameters']):
                if val['parameter_id'] == edit['parameter']:
                    present = True
                    break
            if present:
                current_app['parameters'][idx][edit['field']] = edit['value']
        elif edit["action"] == "remove_parameter":
            present = False
            for idx, val in enumerate(current_app['parameters']):
                if val['parameter_id'] == edit['parameter']:
                    present = True
                    break
            if present:
                del current_app['parameters'][idx]
        elif edit["action"] == "add_peripheral":
            current_app['peripherals'].append(edit['peripheral'])
        elif edit["action"] == "edit_peripheral":
            present = False
            for idx, val in enumerate(current_app['peripherals']):
                if val['name'] == edit['peripheral']:
                    present = True
                    break
            if present:
                current_app['peripherals'][idx][edit['field']] = edit['value']
        elif edit["action"] == "remove_peripheral":
            present = False
            for idx, val in enumerate(current_app['peripherals']):
                if val['name'] == edit['peripheral']:
                    present = True
                    break
            if present:
                del current_app['peripherals'][idx]
        elif edit["action"] == "add_misc":
            current_app[edit['field']['name']] = edit['field']['value']
        elif edit["action"] == "edit_misc":
            if edit['field']['old_name'] is None:
                current_app[edit['field']['name']] = edit['field']['value']
            else:
                val = current_app[edit['field']['old_name']]
                del current_app[edit['field']['old_name']]
                current_app[edit['field']['name']] = val
        elif edit["action"] == "remove_misc":
            del current_app[edit['field']['name']]
        elif edit["action"] == "add_channel_group":
            current_app['channel_groups'].append(edit['group'])
        elif edit["action"] == "edit_channel_group":
            present = False
            for idx, val in enumerate(current_app['channel_groups']):
                if val['group_name'] == edit['group']:
                    present = True
                    break
            if present:
                current_app['channel_groups'][idx][edit['field']] = edit['value']
        elif edit["action"] == "remove_channel_group":
            present = False
            for idx, val in enumerate(current_app['channel_groups']):
                if val['group_name'] == edit['group']:
                    present = True
                    break
            if present:
                del current_app['channel_groups'][idx]

        self.store.add_application(edit["application"], current_app)

    def remove_application(self, application_name):
        """Remove application by name from the database

            Parameters:
                application_name: name of the application to remove
        """
        self.store.remove_application(application_name)

    def set_application(self, application_name):
        """Setup and start a capture

            Parameters:
                param: parameters of the capture 
        """
        chosen_app = self.store.get_applications()[application_name]
        self.redis_if.set('chosen_application', json.dumps(chosen_app))
        self.redis_if.set('parameters', json.dumps(chosen_app['parameters']))

        self.load_bitstream(chosen_app['bitstream'])
        if 'initial_registers_values' in chosen_app:
            self.initialize_registers(chosen_app['initial_registers_values'])
        if 'default_program' in chosen_app:
            print(chosen_app['default_program'])
            print(chosen_app['default_core_address'])
            current_app.programs_mgr.apply_program(chosen_app['default_program'], chosen_app['default_core_address'])


    def get_all_applications(self):
        """ Get all the application specifications

            Returns:
                List: List of single application dictionaries
        """
        return self.store.get_applications()

    def get_applications_hash(self):
        """Get the version hash for the current application database

            Returns:
                String: Hash
        """
        return self.store.get_applications_hash()

    def get_peripheral_base_address(self, peripheral):
        """ Get base address for the specified peripheral

            Parameters:
                peripheral: peripheral id
        """
        chosen_application = json.loads(self.redis_if.get('chosen_application'))
        for tab in chosen_application['peripherals']:
            if tab['peripheral_id'] == peripheral:
                return tab['base_address']
            pass

        raise ValueError('could not find the periperal %s' % peripheral)

    def peripheral_is_proxied(self, peripheral):
        """Find out whether a peripheral is proxied or not

            Parameters:
                peripheral: peripheral id
        """
        chosen_application = json.loads(self.redis_if.get('chosen_application'))
        for tab in chosen_application['peripherals']:
            if tab['peripheral_id'] == peripheral:
                return tab['proxied']
            pass
        raise ValueError('could not find the periperal %s' % peripheral)

    def get_peripheral_proxy_address(self, peripheral):
        """ Get proxy address for the specified peripheral

            Parameters:
                peripheral: peripheral id
        """
        chosen_application = json.loads(self.redis_if.get('chosen_application'))
        for tab in chosen_application['peripherals']:
            if tab['peripheral_id'] == peripheral:
                return tab['proxy_address']
            pass

    def get_parameters(self):
        """ Get parameters for the current peripheral


        """
        params = json.loads(self.redis_if.get('parameters'))
        return params

    def set_parameters(self, param):
        """ set parameter of the current peripheral

            Parameters:
                param: dictionary containing name and value of the parameter to set
        """
        params = json.loads(self.redis_if.get('parameters'))
        params[param['name']] = param['value']
        self.redis_if.set('parameters', json.dumps(params))

    def load_bitstream(self, name):
        """ Load the specified bitstream on the programmable logic

            Parameters:
                name: name of the bitstream to load
        """
        self.interface.load_bitstream(name)

    def get_timebase_addr(self):
        """ Get address of the timebase IP in the current application

            Parameters:
                peripheral: peripheral id
        """
        chosen_application = json.loads(self.redis_if.get('chosen_application'))
        return int(chosen_application['timebase_address'], 16)

    def initialize_registers(self, registers):
        """ Initializes registers from arguments

            Parameters:
                registers: List of dictionaries containing the details of the registers to initialize
        """
        for reg in registers:
            addr = int(reg['address'], 0)
            value = int(reg['value'], 0)
            self.interface.write_register(addr, value)