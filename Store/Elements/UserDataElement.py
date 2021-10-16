# Copyright 2021 University of Nottingham Ningbo China
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

import uuid


class UserDataElement:

    def __init__(self, session, settings_store):
        self.Session = session
        self.settings_store = settings_store

    def get_row(self, table, filter_name, filter_value):
        with self.Session() as session:
            return session.query(table).filter(getattr(table, filter_name) == filter_value).first()

    def get_element(self, table, filter_name, filter_value, creator_func):
        try:
            return creator_func(self.get_row(table, filter_name, filter_value))
        except AttributeError:
            raise KeyError('Element Not Found')

    def get_elements_dict(self, table, creator_func, key):
        with self.Session.begin() as session:
            result = session.query(table).all()
            scripts = {}
            for row in result:
                scripts[getattr(row, key)] = creator_func(row)
        return scripts

    def add_element(self, item, table):
        with self.Session.begin() as session:
            session.add(item)
            self.update_version(table)

    def remove_element(self, table, filter_name, filter_value):
        element = self.get_row(table, filter_name, filter_value)
        if element:
            self.update_version(table)
            with self.Session.begin() as session:
                session.delete(element)

    def add_version(self, table):
        self.settings_store.set_per_server_value(table.VersionTableName+'_version', str(uuid.uuid4()))

    def remove_version(self, table):
        return self.settings_store.delete_per_server_value(table.VersionTableName + '_version')

    def update_version(self, table):
        self.settings_store.set_per_server_value(table.VersionTableName + '_version', str(uuid.uuid4()))

    def get_version(self, table):
        return self.settings_store.get_per_server_value(table.VersionTableName+'_version')

    def dump(self, table, creator_func):
        with self.Session.begin() as session:
            result = session.query(table).all()
            dump = []
            for row in result:
                dump.append(creator_func(row))
        return dump
