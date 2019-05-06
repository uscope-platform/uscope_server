import numpy as np
from flask import Flask, jsonify, request
import json
from flask_restful import Resource, Api, reqparse
from flask_restful.utils import cors
import logging

from uCube_interface import uCube_interface
app = Flask(__name__)
app.config['SECRET_KEY'] = 'uScope-CORS-key'
app.config['CORS_HEADERS'] = 'Content-Type'


interface = uCube_interface.uCube_interface()

api = Api(app)

timescale = np.linspace(0,1,50000)

trace1 = 20*np.sin(2*np.pi*123*timescale+0)
trace2 = 20*np.sin(2*np.pi*123*timescale+2/3*np.pi)
trace3 = 20*np.sin(2*np.pi*123*timescale-2/3*np.pi)
traces = np.array([trace1, trace2, trace3])
trace_pointer = 0

enabled_channels = [False, False, False, False, False, False]


class Parameters(Resource):
    @cors.crossdomain(origin='*')
    def get(self):
        with open("static/parameters_setup.json", 'r') as f:
            parameters = json.load(f)
        return jsonify(parameters)

    @cors.crossdomain(origin='*')
    def post(self):
        parameters = request.get_json(force=True)
        return '200'

class Channels(Resource):

    @cors.crossdomain(origin='*')
    def get(self):
        with open("static/channels_setup.json", 'r') as f:
            channels = json.load(f)
        return jsonify(channels)

    @cors.crossdomain(origin='*')
    def post(self):
        global enabled_channels
        enabled_channels = request.get_json(force=True)
        return '200'


class ChannelsData(Resource):
    @cors.crossdomain(origin='*')
    def get(self,channel_id):

        interface.wait_for_data()
        dts = interface.read_data()
        interface.acknowledge_interrupt()
        data_to_send = jsonify(dts)
        return data_to_send


api.add_resource(Parameters, '/uscope/params')
api.add_resource(Channels, '/uscope/channels')
api.add_resource(ChannelsData, '/uscope/channels/data/<int:channel_id>')

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

if __name__ == '__main__':
    app.run(host='0.0.0.0', threaded=True)
