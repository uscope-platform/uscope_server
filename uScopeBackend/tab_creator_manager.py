from flask import current_app, Blueprint, jsonify, request
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required

from sqlitedict import SqliteDict
import os


############################################################
#                      BLUEPRINT                           #
############################################################


tab_creator_manager_bp = Blueprint('tab_creator_manager', __name__, url_prefix='/tab_creator')


api = Api(tab_creator_manager_bp)


class EditPeripheral(Resource):
    @jwt_required()
    def post(self):
        edit = request.get_json()
        current_app.tab_creator_mgr.edit_peripheral(edit)
        return '200'


class CreatePeripheral(Resource):
    @jwt_required()
    def get(self, peripheral):
        pass

    @jwt_required()
    def post(self):
        peripheral = request.get_json()
        current_app.tab_creator_mgr.create_peripheral(peripheral)
        return '200'


class PeripheralTabImage(Resource):
    @jwt_required()
    def get(self, peripheral):
        pass

    @jwt_required()
    def post(self):
        content = request.files['file'].read()
        current_app.tab_creator_mgr.set_image_file(content, request.files['file'].filename)
        return '200'


class RemovePeripheral(Resource):
    @jwt_required()
    def get(self, peripheral):
        current_app.tab_creator_mgr.remove_peripheral(peripheral)

    @jwt_required()
    def post(self):
        pass


api.add_resource(PeripheralTabImage, '/diagram')
api.add_resource(CreatePeripheral, '/create_peripheral')
api.add_resource(EditPeripheral, '/edit_peripheral')
api.add_resource(RemovePeripheral, '/remove_peripheral/<string:peripheral>')

############################################################
#                      IMPLEMENTATION                      #
############################################################


class TabCreatorManager:

    def __init__(self, store):
        self.data_store = store.Elements
        self.image_filename = ''
        self.image_content = None

    def set_image_file(self, image_content, name):
        """Stores the the image file for a peripheral tab

            Parameters:
                image_content: Content of the image file to store
                name: Name of the image file to store
           """
        with SqliteDict('.shared_storage.db') as storage:
            storage['image_content'] = image_content
            storage['image_filename'] = name
            storage.commit()

    def create_peripheral(self, periph):
        """Adds a peripheral to the database

            Parameters:
                periph: peripheral to store into the database
           """
        image_path = ""
        if periph['image']:
            with SqliteDict('.shared_storage.db') as storage:
                image_path = 'static/Images/' + storage['image_filename']
                if os.path.exists(image_path):
                    os.remove(image_path)
                with open(image_path, 'wb') as f:
                    f.write(storage['image_content'])
        periph['payload'][list(periph['payload'])[0]]['image'] = image_path

        label, periph =periph['payload'].popitem()
        self.data_store.add_peripheral(label, periph)

    def edit_peripheral(self, edit):
        current_periph = self.data_store.get_peripheral(edit["peripheral"])
        if edit["action"] == "change_image":
            with SqliteDict('.shared_storage.db') as storage:
                image_path = 'static/Images/' + storage['image_filename']
                if os.path.exists(image_path):
                    os.remove(image_path)
                with open(image_path, 'wb') as f:
                    f.write(storage['image_content'])
        elif edit["action"] == "edit_version":
            current_periph['version'] = edit['version']
        elif edit["action"] == "add_register":
            current_periph['registers'].append(edit['register'])
        elif edit["action"] == "edit_register":
            present = False
            for idx, val in enumerate(current_periph['registers']):
                if val['register_name'] == edit['register']:
                    present = True
                    break
            if present:
                current_periph['registers'][idx][edit['field']] = edit['value']
        elif edit["action"] == "remove_register":
            present = False
            for idx, val in enumerate(current_periph['registers']):
                if val['register_name'] == edit['register']:
                    present = True
                    break
            if present:
                del current_periph['registers'][idx]
        self.data_store.add_peripheral(edit["peripheral"], current_periph)


    def remove_peripheral(self, peripheral):
        """Removes a peripheral from the database

            Parameters:
                peripheral: name of the peripheral to remove
           """
        self.data_store.remove_peripheral(peripheral)
