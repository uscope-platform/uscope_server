from flask import current_app, Blueprint, jsonify, request
from flask_restful import Api, Resource

import json
import numpy as np
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
        pass


api.add_resource(Timebase, '/timebase')
api.add_resource(ChannelsSpecs, '/channels/specs')
api.add_resource(ChannelParams, '/channels/params')
api.add_resource(ChannelsData, '/channels/data')

############################################################
#                      IMPLEMENTATION                      #
############################################################


class PlotManager:

    def __init__(self, low_level_interface, store):
        # TODO: enable dynamic number of channels based on the application channel specs
        self.channel_data = d = np.empty((6, 1024))
        self.store = store

        self.channel_parameters = {}
        self.interface = low_level_interface

    def set_application(self, name):
        self.channel_parameters = self.store.load_application(name)['parameters']
        self.channel_specs = self.store.load_application(name)['channels']

    def get_data(self, channel):
        #self.interface.wait_for_data()
        #dts = self.interface.read_data()
        # TODO: implement channel selection mechanic
        #self.channel_data[0] = np.roll(self.channel_data[0], len(dts))
        #self.channel_data[0][0:len(dts)] = dts

        #return self.channel_data[0].tolist()
        return {"channel":0, "data":np.random.rand(1024).tolist()}

    def get_channels_specs(self):
        return self.channel_specs

    def get_channel_params(self, name):
        return self.channel_parameters[name]

    def set_channel_params(self, message):
        if type(message) is list:
            for s in message:
                self.channel_specs['channels'][s['channel_id']][s['name']] = s['value']
        else:
            self.channel_parameters[name] = value