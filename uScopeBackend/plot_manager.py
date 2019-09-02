from flask import current_app, Blueprint, jsonify
from flask_restful import Api, Resource


############################################################
#                      IMPLEMENTATION                      #
############################################################


plot_manager_bp = Blueprint('plot_manager', __name__, url_prefix='/plot')


api = Api(plot_manager_bp)


class Channels(Resource):
    def get(self):
        pass
    def post(self):
        pass


class ChannelsData(Resource):
    def get(self,name):
        pass

class Timebase(Resource):
    def get(self):
        pass
    def post(self):
        pass


api.add_resource(Timebase, '/Timebase')
api.add_resource(Channels, '/channels')
api.add_resource(ChannelsData, '/channels/data/<int:channel_id>')

############################################################
#                      IMPLEMENTATION                      #
############################################################


class PlotManager:

    def __init__(self):
        pass
    

    def get_data(self, channel):
        pass