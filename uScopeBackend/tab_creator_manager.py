from flask import current_app, Blueprint, jsonify, request
from flask_restful import Api, Resource

from sqlitedict import SqliteDict
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


class RemovePeripheral(Resource):
    def get(self, peripheral):
        current_app.tab_creator_mgr.remove_peripheral(peripheral)

    def post(self):
        pass


api.add_resource(PeripheralTabImage, '/diagram')
api.add_resource(CreatePeripheral, '/create_peripheral')
api.add_resource(RemovePeripheral, '/remove_peripheral/<string:peripheral>')

############################################################
#                      IMPLEMENTATION                      #
############################################################


class TabCreatorManager:

    def __init__(self, store):
        self.store = store
        self.image_filename = ''
        self.image_content = None

    def set_image_file(self, image_content, name):
        with SqliteDict('.shared_storage.db') as storage:
            storage['image_content'] = image_content
            storage['image_filename'] = name
            storage.commit()

    def create_peripheral(self, periph):
        with SqliteDict('.shared_storage.db') as storage:
            self.store.add_peripheral(periph)
            image_path = 'static/Images/' + storage['image_filename']
            if os.path.exists(image_path):
                os.remove(image_path)
            with open(image_path, 'wb') as f:
                f.write(storage['image_content'])

    def remove_peripheral(self,peripheral):
        self.store.remove_peripheral(peripheral)