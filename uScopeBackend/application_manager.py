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
# limitations under the License

from flask import current_app, Blueprint, jsonify, request, abort, Response
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt_identity

from . import role_required

############################################################
#                      IMPLEMENTATION                      #
############################################################

application_manager_bp = Blueprint('application_manager', __name__, url_prefix='/application')

api = Api(application_manager_bp)


class ApplicationSet(Resource):
    @jwt_required()
    @role_required("operator")
    def get(self, application_id):
        try:
            return jsonify(current_app.app_mgr.set_application(application_id))
        except RuntimeError:
            abort(Response("Bitstream not found", 418))


class ApplicationGet(Resource):
    @jwt_required()
    @role_required("operator")
    def get(self, application_name):
        return jsonify(current_app.app_mgr.get_application(application_name))


class ApplicationsDigest(Resource):
    @jwt_required()
    @role_required("operator")
    def get(self):
        return current_app.app_mgr.get_applications_hash()


class ApplicationsSpecs(Resource):
    @jwt_required()
    @role_required("operator")
    def get(self):
        return jsonify(current_app.app_mgr.get_all_applications())


class ApplicationAdd(Resource):

    @jwt_required()
    @role_required("admin")
    def post(self):
        parameters = request.get_json(force=True)
        current_app.app_mgr.add_application(parameters)
        return '200'


class ApplicationEdit(Resource):
    @jwt_required()
    @role_required("user")
    def post(self):
        parameters = request.get_json(force=True)
        current_app.app_mgr.edit_application(parameters)
        return '200'


class ApplicationRemove(Resource):
    @jwt_required()
    @role_required("admin")
    def get(self, application_name):
        current_app.app_mgr.remove_application(application_name)
        return '200'


class ApplicationClock(Resource):
    @jwt_required()
    @role_required("operator")
    def get(self):
        return jsonify(current_app.app_mgr.get_clock())

    @jwt_required()
    @role_required("user")
    def post(self):
        parameters = request.get_json(force=True)
        current_app.app_mgr.set_clock(parameters)
        return '200'


api.add_resource(ApplicationClock, '/clock')
api.add_resource(ApplicationsSpecs, '/all/specs')
api.add_resource(ApplicationSet, '/set/<string:application_id>')
api.add_resource(ApplicationGet, '/get/<string:application_name>')
api.add_resource(ApplicationsDigest, '/digest')
api.add_resource(ApplicationAdd, '/add')
api.add_resource(ApplicationEdit, '/edit')
api.add_resource(ApplicationRemove, '/remove/<string:application_name>')

############################################################
#                      IMPLEMENTATION                      #
############################################################


class ApplicationManager:
    def __init__(self, interface, store):
        self.parameters = {}
        self.data_store = store.Elements
        self.interface = interface
        self.item_types_map = {
            "channel": "channels",
            "irv": "initial_registers_values",
            "macro": "macro",
            "parameter": "parameters",
            "peripheral": "peripherals",
            "channel_group": "channel_groups",
            "soft_core": "soft_cores",
            "filter": "filters",
            "selected_script": "scripts",
            "selected_program": "programs"
        }
        self.item_id_map = {
            "channel": "name",
            "irv": "address",
            "macro": "name",
            "parameter": "parameter_id",
            "peripheral": "name",
            "channel_group": "group_name",
            "soft_core": "id",
            "filter": "id"
        }

    def add_application(self, application):
        """Adds the application from the parameters to the database

            Parameters:
                application: application to add
        """
        key, val = application.popitem()
        self.data_store.add_application(val)

    def edit_application(self, edit):
        if edit["action"] == "add":
            self.add_item(edit["object"], edit)
        if edit["action"] == "edit":
            self.edit_item(edit["object"], edit)
        if edit["action"] == "remove":
            self.delete_item(edit["object"], edit)

    def remove_application(self, application_name):
        """Remove application by name from the database

            Parameters:
                application_name: name of the application to remove
        """
        self.data_store.remove_application(application_name)

    def set_application(self, application_name):
        """Setup and start a capture

            Parameters:
                application_name: name of the application
        """

        chosen_app = self.data_store.get_application(application_name)

        if chosen_app['bitstream'] == "":
            return

        if self.load_bitstream(chosen_app['bitstream']) == 2:
            raise RuntimeError



    def get_all_applications(self):
        """ Get all the application specifications

            Returns:
                List: List of single application dictionaries
        """
        return self.data_store.get_applications_dict()

    def get_applications_hash(self):
        """Get the version hash for the current application database

            Returns:
                String: Hash
        """
        return self.data_store.get_applications_hash()

    def get_application(self, application_id):
        """Get the version hash for the current application database

            Returns:
                String: Hash
        """
        return self.data_store.get_application(application_id)

    def peripheral_is_proxied(self, application, peripheral, username):
        """Find out whether a peripheral is proxied or not

            Parameters:
                peripheral: peripheral id
                username: username of the requester
        """
        for tab in application['peripherals']:
            if tab['peripheral_id'] == peripheral:
                return tab['proxied']
            pass
        raise ValueError('could not find the periperal %s' % peripheral)

    def load_bitstream(self, name):
        """ Load the specified bitstream on the programmable logic

            Parameters:
                name: name of the bitstream to load
        """
        return self.interface.load_bitstream(name)

    def initialize_registers(self, registers):
        """ Initializes registers from arguments

            Parameters:
                registers: List of dictionaries containing the details of the registers to initialize
        """
        for reg in registers:
            addr = reg['address']
            value = reg['value']
            write_obj = {'type': 'direct', 'proxy_type': '', 'proxy_address': 0, 'address': addr, 'value': value}
            self.interface.write_register(write_obj)

    def set_clock(self, clock_obj):
        if clock_obj["type"] == "global":
            current_app.interface.set_pl_clock(clock_obj["clock_n"], clock_obj["frequency"])

    def get_clock(self):
        clocks = dict()
        for i in range(0,4):
            req = {"is_primary":True, "id":i}
            clocks[i] = current_app.interface.get_clock(req)
        return clocks

    def add_item(self, t, edit):
        current_app = self.data_store.get_application(edit["application"])

        if t == "misc":
            current_app['miscellaneous'][edit['item']['name']] = edit['item']['value']
        else:
            current_app[self.item_types_map[t]].append(edit["item"])

        self.data_store.edit_application(current_app)

    def edit_item(self, t, edit):
        current_app = self.data_store.get_application(edit["application"])
        if t == "misc":
            if not edit['item']['edit_name']:
                if edit["item"]['name'] == "application_name":
                    current_app['application_name'] = edit['item']['value']
                elif edit["item"]['name'] == "bitstream":
                    current_app['bitstream'] = edit['item']['value']
                else:
                    current_app['miscellaneous'][edit['item']['name']] = edit['item']['value']
            else:
                val = current_app['miscellaneous'][edit['item']['name']]
                del current_app['miscellaneous'][edit['item']['name']]
                current_app['miscellaneous'][edit['item']['value']] = val
        elif t == 'pl_clocks':
                current_app['pl_clocks'][edit['item']['item_id']] = edit['item']['value']
        else:
            present = False
            for idx, val in enumerate(current_app[self.item_types_map[t]]):
                if val[self.item_id_map[t]] == edit['item']['item_id']:
                    present = True
                    break
            if present:
                current_app[self.item_types_map[t]][idx][edit['item']['field']] = edit['item']['value']
        self.data_store.edit_application(current_app)

    def delete_item(self, t, edit):
        current_app = self.data_store.get_application(edit["application"])
        if t == "misc":
            del current_app['miscellaneous'][edit['item']]
        elif t in ["selected_script", "selected_program"]:
            if edit["item"] in current_app[self.item_types_map[t]]:
                current_app[self.item_types_map[t]].remove(edit["item"])
        else:
            present = False
            for idx, val in enumerate(current_app[self.item_types_map[t]]):
                if val[self.item_id_map[t]] == edit['item']:
                    present = True
                    break
            if present:
                del current_app[self.item_types_map[t]][idx]
        self.data_store.edit_application(current_app)
