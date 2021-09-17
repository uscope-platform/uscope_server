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

from flask import current_app, Blueprint, request
from flask_restful import Api, Resource
from passlib.context import CryptContext
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

import secrets
import hashlib
import time
import math
import hmac
from datetime import timedelta
from . import role_required

############################################################
#                      BLUEPRINT                           #
############################################################


auth_manager_bp = Blueprint('auth__manager', __name__, url_prefix='/auth')


api = Api(auth_manager_bp)


class Login(Resource):
    def post(self):
        content = request.get_json()
        token, response_code = current_app.auth_mgr.login(content)
        return token, response_code


class Logout(Resource):

    def get(self):
        return current_app.auth_mgr.logout()


class User(Resource):

    @jwt_required()
    @role_required("admin")
    def get(self):
        user = get_jwt_identity()
        return current_app.auth_mgr.get_users_list(user)

    @jwt_required()
    @role_required("admin")
    def post(self):
        content = request.get_json()
        current_app.auth_mgr.create_user(content)
        return '200'

    @jwt_required()
    @role_required("admin")
    def delete(self):
        content = request.get_json()
        return current_app.auth_mgr.remove_user(content)


class Onboarding(Resource):
    def get(self):
        return {'onboarding_needed': current_app.auth_mgr.get_onboarding_needed()}

    def post(self):
        content = request.get_json()
        if current_app.auth_mgr.get_onboarding_needed():
            current_app.auth_mgr.create_user(content)
            return '200'
        else:
            return '403'


api.add_resource(User, '/user')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(Onboarding, '/onboarding')

############################################################
#                      IMPLEMENTATION                      #
############################################################


class AuthManager:

    def __init__(self, store):
        self.auth_store = store.Auth
        self.crypto = CryptContext(schemes=["argon2"])
        self.token_duration = timedelta(hours=8)

    def get_onboarding_needed(self):
        users = self.auth_store.get_users_list()
        return len(users) == 0

    def get_users_list(self, username):
        users = self.auth_store.get_users_list()
        return users

    def create_user(self, content):
        user = {'username': content['user'], 'pw_hash': self.crypto.hash(content['password']), 'role': content['role']}
        self.auth_store.add_user(user)

    def remove_user(self, content):
        self.auth_store.remove_user(content['user'])
        return '200'

    def _automated_login(self, token):
        server_token = self.auth_store.get_token(token['selector'])
        if server_token:
            user = self.auth_store.get_user(server_token['username'])
            if not math.isclose(server_token['expiry'], token['expiry'], abs_tol=1e-6):
                print("ERROR")
                return '', 403
            if server_token['expiry'] < time.time():
                return '', 401
            validator_hash = hashlib.sha256(token['validator'].encode()).hexdigest()
            if hmac.compare_digest(validator_hash, server_token['validator']):
                access_token = create_access_token(expires_delta=self.token_duration, identity=server_token['username'])
                return {"access_token": access_token, "role": user['role']}, 200
            else:
                return '', 403

        else:
            return '', 401

    def _user_login(self, content):
        usr_token = None
        if content['remember_me']:
            selector = secrets.token_urlsafe(50)
            validator = secrets.token_urlsafe(50)
            usr_token = {'username': content['user'], 'expiry': time.time() + 86400 * 30,
                         'validator': hashlib.sha256(validator.encode()).hexdigest()}
            self.auth_store.add_token(selector, usr_token)
            del usr_token['username']

            usr_token['validator'] = validator
            usr_token['selector'] = selector

        user = self.auth_store.get_user(content['user'])

        if self.crypto.verify(content['password'], user['pw_hash']):
            access_token = create_access_token(expires_delta=self.token_duration, identity=content['user'])
            return {"access_token": access_token, "login_token": usr_token, "role": user['role']}, 200
        else:
            return '', 401

    def login(self, content):
        if content['login_type'] == 'automated':
            return self._automated_login(content)
        elif content['login_type'] == 'user':
            return self._user_login(content)
        else:
            return '', 403

    def logout(self):
        pass
