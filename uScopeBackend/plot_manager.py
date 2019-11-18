from flask import current_app, Blueprint, jsonify, request
from flask_restful import Api, Resource

import json
import numpy as np
from sqlitedict import SqliteDict
############################################################
#                      IMPLEMENTATION                      #
############################################################


plot_manager_bp = Blueprint('plot_manager', __name__, url_prefix='/plot')


api = Api(plot_manager_bp)


class ChannelsSpecs(Resource):
    def get(self):
        return jsonify(current_app.plot_mgr.get_channels_specs())


class ChannelParams(Resource):
    def post(self):
        message = request.get_json(force=True)
        current_app.plot_mgr.set_channel_params(message)
        return '200'


class ChannelsData(Resource):
    def get(self):
        channels = request.args.get('channels')
        return jsonify(current_app.plot_mgr.get_data(channels))


class Timebase(Resource):
    def get(self):
        pass

    def post(self):
        parameters = request.get_json(force=True)
        current_app.plot_mgr.set_timebase(parameters)
        return '200'


class SetupCapture(Resource):
    def get(self):
        data = jsonify(current_app.plot_mgr.get_capture_data())
        print(data)
        return data


    def post(self):
        parameters = request.get_json(force=True)
        current_app.plot_mgr.setup_capture(parameters)
        return '200'


api.add_resource(Timebase, '/timebase')
api.add_resource(SetupCapture, '/capture')
api.add_resource(ChannelsSpecs, '/channels/specs')
api.add_resource(ChannelParams, '/channels/params')
api.add_resource(ChannelsData, '/channels/data')

############################################################
#                      IMPLEMENTATION                      #
############################################################


class PlotManager:

    def __init__(self, low_level_interface, store):
        # TODO: enable dynamic number of channels based on the application channel specs
        self.channel_data = np.empty((6, 1024))
        self.store = store

        self.interface = low_level_interface

    def set_application(self, name):
        with SqliteDict('.shared_storage.db') as storage:
            storage['channel_parameters'] = self.store.get_application(name)['parameters']
            storage['channel_specs'] = self.store.get_application(name)['channels']
            storage.commit()

    def get_data(self, channel):
        dts = self.interface.read_data()
        # TODO: implement channel selection mechanic
        self.channel_data[0] = np.roll(self.channel_data[0], len(dts))
        self.channel_data[0][0:len(dts)] = dts[:, 0]

        return {"channel": 0, "data": self.channel_data[0].tolist()}
        # return {"channel": 0, "data": np.random.rand(1024).tolist()}

    def get_channels_specs(self):
        with SqliteDict('.shared_storage.db') as storage:
            specs = storage['channel_specs']
        return specs

    def get_channel_params(self, name):
        with SqliteDict('.shared_storage.db') as storage:
            params = storage['channel_parameters']
        return params[name]

    def set_channel_params(self, message):

        with SqliteDict('.shared_storage.db') as storage:
            params = storage['channel_parameters']
            specs = storage['channel_specs']

            if type(message) is list:
                for s in message:
                    specs['channels'][s['channel_id']][s['name']] = s['value']
            else:
                params[name] = value
            storage['channel_parameters'] = params
            storage['channel_specs'] = specs
            storage.commit()

    def set_timebase(self, param):
        self.interface.change_timebase(param['value'])

    def setup_capture(self, param):
        n_buffers = param['length']

        self.interface.setup_capture_mode(n_buffers)

    def get_capture_data(self):
        return self.interface.get_capture_data()