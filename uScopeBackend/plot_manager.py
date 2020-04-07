from flask import current_app, Blueprint, jsonify, request
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required

import json
import numpy as np
import redis
############################################################
#                      IMPLEMENTATION                      #
############################################################


plot_manager_bp = Blueprint('plot_manager', __name__, url_prefix='/plot')


api = Api(plot_manager_bp)


class ChannelsSpecs(Resource):
    @jwt_required
    def get(self):
        return jsonify(current_app.plot_mgr.get_channels_specs())


class ChannelParams(Resource):
    @jwt_required
    def post(self):
        message = request.get_json(force=True)
        current_app.plot_mgr.set_channel_params(message)
        return '200'


class ChannelsData(Resource):
    @jwt_required
    def get(self):
        channels = request.args.get('channels')
        return jsonify(current_app.plot_mgr.get_data(channels))


class SetupCapture(Resource):
    @jwt_required
    def get(self):
        data = jsonify(current_app.plot_mgr.get_capture_data())
        return data

    @jwt_required
    def post(self):
        parameters = request.get_json(force=True)
        current_app.plot_mgr.setup_capture(parameters)
        return '200'


api.add_resource(SetupCapture, '/capture')
api.add_resource(ChannelsSpecs, '/channels/specs')
api.add_resource(ChannelParams, '/channels/params')
api.add_resource(ChannelsData, '/channels/data')

############################################################
#                      IMPLEMENTATION                      #
############################################################


class PlotManager:

    def __init__(self, low_level_interface, store, redis_host):
        # TODO: enable dynamic number of channels based on the application channel specs
        self.channel_data = np.empty((6, 1024))
        self.store = store

        self.interface = low_level_interface
        self.redis_if = redis.Redis(host=redis_host, port=6379, db=0)

    def set_application(self, name):
        """Set the current application

            Parameters:
                name: name of the application to set
           """
        self.redis_if.set('channel_parameters', json.dumps(self.store.get_application(name)['parameters']))
        self.redis_if.set('channel_specs', json.dumps(self.store.get_application(name)['channels']))

    def get_data(self, channel):
        """Get the latest scope data

            Parameters:
                channel: Channels to get the data for
            Returns:
                List: Data
           """
        dts = self.interface.read_data()
        # TODO: implement channel selection mechanic
        self.channel_data[0] = np.roll(self.channel_data[0], len(dts))
        self.channel_data[0][0:len(dts)] = dts[:, 0]

        return {"channel": 0, "data": self.channel_data[0].tolist()}
        # return {"channel": 0, "data": np.random.rand(1024).tolist()}

    def get_channels_specs(self):
        """Returns the specifications for the scope channels of the current application

            Returns:
                Dict:specifications for the current channel
           """
        return json.loads(self.redis_if.get('channel_specs'))

    def get_channel_params(self, name):
        """Returns the specification for the registers of the specified peripheral

            Parameters:
                peripheral_name: name of the peripheral whose registers need to be returned
            Returns:
                List:list of registers in the peripheral
           """
        return json.loads(self.redis_if.get('channel_parameters'))[name]

    def set_channel_params(self, message):
        """Set the value for a channel parameter

            Parameters:
                message: dictionary with the values for the parameter to set
           """
        params = json.loads(self.redis_if.get('channel_parameters'))
        specs = json.loads(self.redis_if.get('channel_specs'))

        if type(message) is list:
            for s in message:
                specs['channels'][s['channel_id']][s['name']] = s['value']
        else:
            params[message['name']] = params[message['value']]

        self.redis_if.set('channel_parameters', json.dumps(params))
        self.redis_if.set('channel_specs', json.dumps(specs))

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
        returnval = {}
        returnval['elapsed'] = self.interface.get_capture_data()
        if returnval['elapsed'] == 0:
            with open('/dev/shm/uscope_capture_writeback', 'r') as f:
                returnval['data'] = f.read()
        return returnval



