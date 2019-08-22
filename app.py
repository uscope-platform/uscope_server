import numpy as np
from flask import Flask, jsonify, request
import json, logging, os
from flask_restful import Resource, Api, reqparse
from flask_restful.utils import cors

from uCube_interface import uCube_interface

app = Flask(__name__)
app.config['SECRET_KEY'] = 'uScope-CORS-key'
app.config['CORS_HEADERS'] = 'Content-Type'


interface = uCube_interface.uCube_interface()
api = Api(app)

timescale = np.linspace(0, 1, 1024)
channel_0_data = np.zeros(1024)
enabled_channels = [False, False, False, False, False, False]
components_specs = {}
application_specs = {}
application_list = []

def load_peripherals():
    settings = [f for f in os.listdir('static') if os.path.isfile(os.path.join('static', f))]

    for fname in settings:
        if not fname.split('.')[1] =='json':
            continue
        else:
            name = fname.replace('.json', '')
        parsed = name.rsplit('_', 1)
        if parsed[1] =='descriptor':
            with open('static/'+fname,'r') as f:
                content = json.load(f)
                application_specs[content['name']] = content
        elif parsed[1] == 'registers':
            with open('static/'+fname,'r') as f:
                content = json.load(f)
                components_specs[content['peripheral_name']] = content

    for i in application_specs:
        application_list.append(i)

class Parameters(Resource):
    @cors.crossdomain(origin='*')
    def get(self):
        with open("static/parameters_setup.json", 'r') as f:
            parameters = json.load(f)
        return jsonify(parameters)

    @cors.crossdomain(origin='*')
    def post(self):
        parameters = request.get_json(force=True)
        for i in parameters:
            if i['param_name']=='uscope_timebase_change':
                interface.change_timebase(i['param_value'])
        return '200'


class ApplicationsList(Resource):
    @cors.crossdomain(origin='*')
    def get(self):
        return jsonify(application_list)


class Application(Resource):
    @cors.crossdomain(origin="*")
    def get(self, application_name):
        return jsonify(application_specs[application_name])


class RegistersDescription(Resource):
    @cors.crossdomain(origin='*')
    def get(self, data):

        if data in components_specs:
            parameters = components_specs[data]
        else:
            raise ValueError("The component register file was not found")

        base_address = int(application_specs['AdcTest']['peripherals'][data]['base_address'],0)
        for i in parameters['registers']:
            if 'R' in i['direction'] or 'r' in i['direction']:
                address = base_address + int(i['offset'], 0)
                i['value'] = interface.read_register(address)
            else:
                i['value'] = 0

        return jsonify(parameters)

    def post(self, data):
        registers_to_write = request.get_json(force=True)
        peripheral_registers = components_specs['SPI']['registers']

        for i in peripheral_registers:
            if i['name'] in registers_to_write:
                address = int(components_specs['SPI']['base_address'], 0)+int(i['offset'], 0)
                value = registers_to_write[i['name']]
                interface.write_register(address, value)
        return 200


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
    def get(self, channel_id):
        global channel_0_data
        interface.wait_for_data()
        dts = interface.read_data()
        channel_0_data = np.roll(channel_0_data, len(dts))
        channel_0_data[0:len(dts)] = dts
        data_to_send = jsonify(channel_0_data.tolist())
        return data_to_send


api.add_resource(Parameters, '/uscope/params')
api.add_resource(Channels, '/uscope/channels')
api.add_resource(ChannelsData, '/uscope/channels/data/<int:channel_id>')
api.add_resource(RegistersDescription, '/uscope/registers/<string:data>')
api.add_resource(ApplicationsList, '/uscope/applicationList')
api.add_resource(Application, '/uscope/application/<string:application_name>')

#log.setLevel(logging.ERROR)

if __name__ == '__main__':
    load_peripherals()
    app.run(host='0.0.0.0', threaded=True)
