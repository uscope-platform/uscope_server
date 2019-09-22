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
        content = request.files['file'].read()
        current_app.tab_creator_mgr.set_image_file(content, request.files['file'].filename)
        return '200'


api.add_resource(PeripheralTabImage, '/diagram')
api.add_resource(CreatePeripheral, '/create_peripheral')

############################################################
#                      IMPLEMENTATION                      #
############################################################


class TabCreatorManager:

    def __init__(self, store):
        self.store = store
        self.image_filename = ''
        self.image_content = None

    def set_image_file(self, image_content, name):
        self.image_content = image_content
        self.image_filename = name

    def create_peripheral(self, periph):
        self.store.add_peripheral(periph)
        image_path = 'static/Images/' + self.image_filename
        if os.path.exists(image_path):
            os.remove(image_path)
        with open(image_path, 'wb') as f:
            f.write(self.image_content)
