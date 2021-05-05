from flask import current_app, Blueprint, jsonify, request
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

from . import role_required

############################################################
#                      IMPLEMENTATION                      #
############################################################


plot_manager_bp = Blueprint('plot_manager', __name__, url_prefix='/plot')

api = Api(plot_manager_bp)


class ChannelsSpecs(Resource):
    @jwt_required()
    @role_required("operator")
    def get(self):
        user = get_jwt_identity()
        return jsonify(current_app.plot_mgr.get_channels_specs(user))


class ChannelParams(Resource):
    @jwt_required()
    @role_required("operator")
    def post(self):
        message = request.get_json(force=True)
        user = get_jwt_identity()
        current_app.plot_mgr.set_channel_params(message, user)
        return '200'


class ChannelsData(Resource):
    @jwt_required()
    def get(self):
        user = get_jwt_identity()
        return jsonify(current_app.plot_mgr.get_data(user))


class SetupCapture(Resource):
    @jwt_required()
    @role_required("operator")
    def get(self):
        data = jsonify(current_app.plot_mgr.get_capture_data())
        return data

    @jwt_required()
    @role_required("operator")
    def post(self):
        parameters = request.get_json(force=True)
        current_app.plot_mgr.setup_capture(parameters)
        return '200'


class ChannelStatus(Resource):
    @jwt_required()
    @role_required("operator")
    def post(self):
        statuses = request.get_json(force=True)
        user = get_jwt_identity()
        return current_app.plot_mgr.set_channel_status(statuses, user)


class ChannelWidths(Resource):
    @jwt_required()
    @role_required("operator")
    def post(self):
        widths = request.get_json(force=True)
        return current_app.plot_mgr.set_channel_widths(widths)


api.add_resource(SetupCapture, '/capture')
api.add_resource(ChannelsSpecs, '/channels/specs')
api.add_resource(ChannelParams, '/channels/params')
api.add_resource(ChannelsData, '/channels/data')
api.add_resource(ChannelStatus, '/channels/status')
api.add_resource(ChannelWidths, '/channels/widths')

############################################################
#                      IMPLEMENTATION                      #
############################################################


class PlotManager:

    def __init__(self, low_level_interface, store, debug):
        self.interface = low_level_interface
        self.debug = debug
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
        parameters = self.data_store.get_application(name)['parameters']
        channels = self.data_store.get_application(name)['channels']
        self.settings_store.set_value('channel_parameters', parameters, username)
        self.settings_store.set_value('channel_specs', channels, username)

    def get_data(self, username):
        """Get the latest scope data
            Parameters:
                username: username of the requester
            Returns:
                List: Data
           """
        status = self.settings_store.get_value('channel_status', username)
        ret_val = list()
        try:
            raw_data = self.interface.read_data()
        except RuntimeError:
            return self.channel_data

        split_data = [raw_data[x:x + self.data_points_per_channel] for x in range(0, len(raw_data), self.data_points_per_channel)]
        for i in status:
            if status[i]:
                ret_val.append({"channel": int(i), "data": split_data[int(i)]})

        self.channel_data = ret_val

        return ret_val

    def set_channel_widths(self, widths):
        self.interface.set_channel_widths(widths['widths'])

    def get_channels_specs(self, username):
        """Returns the specifications for the scope channels of the current application
            Parameter:
                username: username of the requester
            Returns:
                Dict:specifications for the current channel
           """
        specs = self.settings_store.get_value('channel_specs', username)
        return specs

    def set_channel_params(self, message, username):
        """Set the value for a channel parameter

            Parameters:
                message: dictionary with the values for the parameter to set
                username: username of the requester
           """
        params = self.settings_store.get_value('channel_parameters', username)
        specs = self.settings_store.get_value('channel_specs', username)

        if type(message) is list:
            for s in message:
                specs['channels'][s['channel_id']][s['name']] = s['value']
        else:
            params[message['name']] = params[message['value']]

        self.settings_store.set_value('channel_parameters', params, username)
        self.settings_store.set_value('channel_specs', specs, username)

    def setup_capture(self, param):
        """Setup and start a capture

            Parameters:
                param: parameters of the capture
           """
        n_buffers = param['length']
        self.interface.setup_capture_mode(n_buffers)

    def get_capture_data(self):
        """Get the captured data

            Returns:
                String:Content of the file to upload to the client with the capture data
           """
        returnval = {'elapsed': self.interface.get_capture_data()}
        if returnval['elapsed'] == 0:
            with open('/dev/shm/uscope_capture_writeback', 'r') as f:
                returnval['data'] = f.read()
        return returnval

    def set_channel_status(self, status, username):
        self.settings_store.set_value('channel_status', status, username)
        return "200"

