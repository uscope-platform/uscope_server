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
import numpy as np
from flask import current_app, Blueprint, jsonify, request
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required
from filter_designer import FilterDesignEngine
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
        if filter_id == "none":
            return jsonify(current_app.filter_mgr.get_filters())
        else:
            return current_app.filter_mgr.get_plots(filter_id)

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


class FilterDesigner(Resource):
    @jwt_required()
    @role_required("user")
    def get(self, filter_id):
        return jsonify(current_app.filter_mgr.design_filter(filter_id))


class FilterImplementer(Resource):
    @jwt_required()
    @role_required("user")
    def get(self, filter_id):
        return jsonify(current_app.filter_mgr.implement_filter(filter_id))


class FilterDigest(Resource):
    @jwt_required()
    @role_required("operator")
    def get(self):
        return current_app.filter_mgr.get_digest()


api.add_resource(FilterDigest, '/digest')
api.add_resource(Filter, '/<string:filter_id>')
api.add_resource(FilterDesigner, '/design/<string:filter_id>')
api.add_resource(FilterImplementer, '/implement/<string:filter_id>')


############################################################
#                      IMPLEMENTATION                      #
############################################################


class FilterManager:

    def __init__(self, store):

        self.data_store = store.Elements

    def get_digest(self):
        return self.data_store.get_filters_hash()

    def get_filters(self):
        return self.data_store.get_filters_dict()

    def get_plots(self, filter_id):
        ret = {
            "ideal": {"frequency": [], "response": []},
            "quantized": {"frequency": [], "response": []},
        }
        if int(filter_id) == 0:
            return ret
        flt_object = self.data_store.get_filters_dict()[int(filter_id)]
        fs = flt_object["parameters"]["sampling_frequency"]
        id_data = FilterDesignEngine.get_plot_data(np.array(flt_object["ideal_taps"]), fs)
        ret["ideal"] = {"frequency": id_data[0], "response": id_data[1]}
        q_data = np.array(flt_object["quantized_taps"]) / (2 ** flt_object["parameters"]["taps_width"])
        q_data = FilterDesignEngine.get_plot_data(q_data, fs)
        ret["quantized"] = {"frequency": q_data[0], "response": q_data[1]}
        return ret



    def add_filter(self, filter_obj: dict):
        self.data_store.add_filter(filter_obj)

    def edit_filter(self, edit_obj):
        filter_obj = self.data_store.get_filter(edit_obj['filter'])
        filter_obj[edit_obj['field']] = edit_obj['value']
        self.data_store.edit_filter(filter_obj)

    def delete_filter(self, filter_id):
        self.data_store.remove_filter(filter_id)

    def design_filter(self, filter_id):
        flt_object = self.data_store.get_filters_dict()[int(filter_id)]

        try:
            taps, plot = FilterDesignEngine.design_filter(flt_object["parameters"])
            flt_object["ideal_taps"] = taps
            self.data_store.edit_filter(flt_object)
            return plot
        except ValueError:
            return 500

    def implement_filter(self, filter_id):
        flt_object = self.data_store.get_filters_dict()[int(filter_id)]

        if not flt_object['ideal_taps']:
            return 500

        try:
            taps, plot = FilterDesignEngine.implement_filter(flt_object['ideal_taps'], flt_object["parameters"]["taps_width"], flt_object["parameters"]["sampling_frequency"])
            flt_object["quantized_taps"] = taps
            self.data_store.edit_filter(flt_object)
            return plot
        except ValueError:
            return 500

    def apply_filter(self, filter_id):
        pass