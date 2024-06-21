# Copyright 2021 University of Nottingham Ningbo China
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
import os

from flask import current_app, Blueprint, jsonify, request
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import role_required

############################################################
#                      IMPLEMENTATION                      #
############################################################


plot_manager_bp = Blueprint('plot_manager', __name__, url_prefix='/plot')

api = Api(plot_manager_bp)


class ChannelsData(Resource):
    @jwt_required()
    def get(self):
        user = get_jwt_identity()
        return jsonify(current_app.plot_mgr.get_data(user))


class ChannelStatus(Resource):
    @jwt_required()
    @role_required("operator")
    def post(self):
        statuses = request.get_json(force=True)
        user = get_jwt_identity()
        return current_app.plot_mgr.set_channel_status(statuses, user)


class ChannelScalingFactors(Resource):
    @jwt_required()
    @role_required("operator")
    def post(self):
        sfs = request.get_json(force=True)
        return current_app.plot_mgr.set_scaling_factors(sfs)


class ScopeAddress(Resource):
    @jwt_required()
    @role_required("operator")
    def post(self):
        args = request.get_json(force=True)
        return current_app.plot_mgr.set_scope_address(args)


class Acquisition(Resource):

    @jwt_required()
    @role_required("operator")
    def get(self):
        return current_app.plot_mgr.get_acquisition_status()

    @jwt_required()
    @role_required("operator")
    def post(self):
        args = request.get_json(force=True)
        return current_app.plot_mgr.set_acquisition(args)


api.add_resource(ChannelsData, '/channels/data')
api.add_resource(ChannelStatus, '/channels/status')
api.add_resource(ChannelScalingFactors, '/channels/scaling_factors')
api.add_resource(ScopeAddress, '/address')
api.add_resource(Acquisition, '/acquisition')


############################################################
#                      IMPLEMENTATION                      #
############################################################


class PlotManager:

    def __init__(self, low_level_interface, store):
        self.interface = low_level_interface
        self.data_store = store.Elements
        self.settings_store = store.Settings
        self.data_points_per_channel = 1024

        self.channel_data = None

    def set_application(self, name, username):
        """Set the current application

            Parameters:
                name: name of the application to set
                username: username of the requester
           """
        self.settings_store.clear_settings()

    def get_data(self, username):
        """Get the latest scope data
            Parameters:
                username: username of the requester
            Returns:
                List: Data
           """
        try:
            raw_data = self.interface.read_data()
        except RuntimeError:
            return self.channel_data

        self.channel_data = raw_data

        return raw_data

    def set_scaling_factors(self, sfs):
        self.interface.set_scaling_factors(sfs['scaling_factors'])



    def set_channel_status(self, status, username):
        self.interface.set_channel_status(status)
        return "200"

    def get_acquisition_status(self):
        return self.interface.get_acquisition_status()

    def set_acquisition(self, acquisition_obj):
        return self.interface.set_acquisition(acquisition_obj)

    def set_scope_address(self, scope_address):
        return self.interface.set_scope_address(scope_address)
