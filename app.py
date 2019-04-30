import numpy as np
from flask import Flask, jsonify
import json
from flask_restful import Resource, Api
from flask_restful.utils import cors

app = Flask(__name__)
app.config['SECRET_KEY'] = 'uScope-CORS-key'
app.config['CORS_HEADERS'] = 'Content-Type'


api = Api(app)

timescale = np.linspace(0,1,50000)

trace1 = 20*np.sin(2*np.pi*123*timescale+0)
trace2 = 20*np.sin(2*np.pi*123*timescale+2/3*np.pi)
trace3 = 20*np.sin(2*np.pi*123*timescale-2/3*np.pi)
traces = np.array([trace1, trace2, trace3])
trace_pointer = 0


class Parameters(Resource):
    @cors.crossdomain(origin='http://localhost')
    def get(self):
        with open("/home/fils/PycharmProjects/uScope_server/static/parameters_setup.json", 'r') as f:
            parameters = json.load(f)
        return jsonify(parameters)


class Channels(Resource):
    @cors.crossdomain(origin='http://localhost')
    def get(self):
        with open("/home/fils/PycharmProjects/uScope_server/static/channels_setup.json", 'r') as f:
            channels = json.load(f)
        return jsonify(channels)


class ChannelsData(Resource):
    @cors.crossdomain(origin='http://localhost')
    def get(self):
        global trace_pointer
        data_to_send = jsonify(traces[:, trace_pointer:trace_pointer+1000].tolist())
        trace_pointer = trace_pointer + 1000
        trace_pointer = trace_pointer % 50000
        return data_to_send


api.add_resource(Parameters, '/uscope/params')
api.add_resource(Channels, '/uscope/channels')
api.add_resource(ChannelsData, '/uscope/channels/data')

if __name__ == '__main__':
    app.run()
