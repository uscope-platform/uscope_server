from flask import current_app, Blueprint, jsonify, request
from flask_restful import Api, Resource

import os, json


############################################################
#                      BLUEPRINT                           #
############################################################


tab_creator_manager_bp = Blueprint('tab_creator_manager', __name__, url_prefix='/tab_creator')


api = Api(tab_creator_manager_bp)


class CreatePeripheral(Resource):
    def get(self, peripheral):
        pass

    def post(self):
        peripheral = request.get_json()
        current_app.tab_creator_mgr.create_peripheral(peripheral['payload'])
        return '200'


class PeripheralTabImage(Resource):
    def get(self, peripheral):
        pass

    def post(self):
        uploaded_file = request.files['file']
        current_app.tab_creator_mgr.set_file(uploaded_file)
        return '200'


api.add_resource(PeripheralTabImage, '/diagram')
api.add_resource(CreatePeripheral, '/create_peripheral')

############################################################
#                      IMPLEMENTATION                      #
############################################################


class TabCreatorManager:

    def __init__(self, store):
        self.store = store
        self.new_tab = {}
        self.file = None

    def set_image(self, image):
        pass

    def set_file(self, file):
        self.file = file
        self.new_tab['filename'] = file.filename

    def create_peripheral(self, periph):
        self.store.add_peripheral(periph)