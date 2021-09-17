# Copyright 2021 University of Nottingham Ningbo China
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

from sqlalchemy import Column, String, ForeignKey
from .OrmBase import Base
from sqlalchemy.dialects import postgresql


class Settings(Base):
    __tablename__ = 'app_settings'

    name = Column(String, primary_key=True)
    user = Column(String, ForeignKey('users.username'))
    value = Column(postgresql.JSONB)

    def __repr__(self):
        return "<Setting(name='%s', value='%s, instance='%s')>" % (self.name, self.value, self.instance_id)


class SettingsDatabase:

    def __init__(self, session):
        self.Session = session

    def get_value(self, name, user):
        with self.Session.begin() as session:
            res = session.query(Settings).filter_by(name=name, user=user).first()
            return res.value

    def set_value(self, name, value, user):

        item = Settings(name=name, value=value, user=user)
        with self.Session.begin() as session:
            setting = session.query(Settings).filter_by(name=name, user=user).first()
            if setting:
                setting.value = value
            else:
                session.add(item)

    def clear_settings(self):
        with self.Session.begin() as session:
            session.query(Settings).delete()

    def dump(self):
        return []

    def restore(self, data):
        pass
