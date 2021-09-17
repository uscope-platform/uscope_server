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

from sqlalchemy import Column, String
from .OrmBase import Base
from sqlalchemy.dialects import postgresql

import uuid
import datetime
from multiprocessing import Lock

version_update_lock = Lock()

class Versions(Base):

    __tablename__ = 'data_versions'

    table = Column(String, primary_key=True)
    version = Column(postgresql.UUID(as_uuid=True))
    last_modified = Column(postgresql.TIMESTAMP)

    def __repr__(self):
        return "<Version(table='%s', version='%s', last_modified='%s')>" % (
                             self.table, self.version, self.last_modified)


class UserDataElement:

    def __init__(self, session):
        self.Session = session

    def get_row(self, table, filter_name, filter_value):
        with self.Session() as session:
            return session.query(table).filter(getattr(table, filter_name) == filter_value).first()

    def get_element(self, table, filter_name, filter_value, creator_func):
        try:
            return creator_func(self.get_row(table,filter_name,filter_value))
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
        with self.Session.begin() as session:
            item = Versions(table=table.VersionTableName, version=uuid.uuid4(), last_modified=datetime.datetime.now())
            session.add(item)

    def remove_version(self, table):
        ver = self.__get_version(table)
        if ver:
            with self.Session.begin() as session:
                session.delete(ver)

    def update_version(self, table):
        version_update_lock.acquire()
        try:
            self.remove_version(table)
            self.add_version(table)
        finally:
            version_update_lock.release()

    def __get_version(self, table):
        with self.Session.begin() as session:
            version = session.query(Versions).filter_by(table=table.VersionTableName).first()
            return version

    def get_version(self, table):
        with self.Session.begin() as session:
            version = session.query(Versions).filter_by(table=table.VersionTableName).first()
            return version.version

    def dump(self, table, creator_func):
        with self.Session.begin() as session:
            result = session.query(table).all()
            dump = []
            for row in result:
                dump.append(creator_func(row))
        return dump
