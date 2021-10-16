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

import datetime as dt

from sqlalchemy.orm import declarative_base, sessionmaker

from sqlalchemy import create_engine
from .Elements import Users


class AuthStore:
    def __init__(self, host):
        self.engine = create_engine(host)

        Base = declarative_base()
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

        self.auth_db = Users.AuthenticationDatabase(self.Session)

    # PERIPHERALS

    def get_users_list(self):
        return self.auth_db.get_users_list()

    def add_user(self, content):
        self.auth_db.add_user(content['username'], content['pw_hash'], content['role'])

    def user_exists(self, username):
        self.auth_db.user_exists(username)

    def get_password_hash(self, username):
        return self.auth_db.get_password_hash(username)

    def get_user(self, username):
        return self.auth_db.get_user(username)

    def remove_user(self, username):
        self.auth_db.remove_user(username)

    def get_token(self, selector):
        token = self.auth_db.get_token(selector)
        return {'username': token.username, 'expiry': token.expiry.timestamp(), 'validator': token.validator}

    def add_token(self, selector, token_obj):
        timestamp = dt.datetime.fromtimestamp(token_obj['expiry'])
        self.auth_db.add_token(token_obj['username'], timestamp, token_obj['validator'], selector)

    def dump(self):
        return self.auth_db.dump()

    def restore(self, data):
        self.auth_db.restore(data)

    def remove_token(self, username):
        pass
