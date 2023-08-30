# Copyright 2023 Filippo Savi
# Author: Filippo Savi <filssavi@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from flask import current_app, Blueprint, jsonify, request
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required

from . import role_required

############################################################
#                      BLUEPRINT                           #
############################################################


filters_manager_bp = Blueprint('filter_manager', __name__, url_prefix='/filters')


api = Api(filters_manager_bp)


class Filter(Resource):

    @jwt_required()
    @role_required("user")
    def get(self, filter_id):
        return jsonify(current_app.filter_mgr.get_filters())

    @jwt_required()
    @role_required("user")
    def post(self, filter_id):
        content = request.get_json()
        current_app.filter_mgr.add_filter(content)
        return '200'

    @jwt_required()
    @role_required("user")
    def patch(self, filter_id):
        edit = request.get_json()
        current_app.filter_mgr.edit_filter(edit)
        return '200'

    @jwt_required()
    @role_required("user")
    def delete(self, filter_id):
        current_app.filter_mgr.delete_filter(filter_id)
        return '200'


class FilterDigest(Resource):
    @jwt_required()
    @role_required("operator")
    def get(self):
        return current_app.filter_mgr.get_digest()


api.add_resource(FilterDigest, '/digest')
api.add_resource(Filter, '/<string:filter_id>')


############################################################
#                      IMPLEMENTATION                      #
############################################################


class FilterManager:

    def __init__(self, store):

        self.data_store = store.Elements

    def get_digest(self):
        return self.data_store.get_filters_hash()

    def get_filters(self):
        f = self.data_store.get_filters_dict()
        return f

    def add_filter(self, filter_obj: dict):
        self.data_store.add_filter(filter_obj)

    def edit_filter(self, edit_obj):
        filter_obj = self.data_store.get_filter(edit_obj['filter'])
        filter_obj[edit_obj['field']] = edit_obj['value']
        self.data_store.edit_filter(filter_obj)

    def delete_filter(self, filter_id):
        self.data_store.remove_filter(filter_id)
