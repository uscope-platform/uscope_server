from flask import current_app, Blueprint, jsonify, request
from flask_restful import Api, Resource
from passlib.context import CryptContext
from flask_jwt_extended import create_access_token, jwt_required
import secrets
import hashlib
import time
import hmac

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

    def post(self):
        content = request.get_json()
        current_app.auth_mgr.create_user(content)
        return '200'

    @jwt_required
    def delete(self):
        content = request.get_json()
        return current_app.auth_mgr.remove_user(content)


api.add_resource(User, '/user')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')

############################################################
#                      IMPLEMENTATION                      #
############################################################


class AuthManager:

    def __init__(self, store):
        self.store = store
        self.crypto = CryptContext(schemes=["argon2"])

    def create_user(self, content):
        user = {}
        user['username'] = content['user']
        user['pw_hash'] = self.crypto.hash(content['password'])
        self.store.add_user(content['user'], user)

    def remove_user(self, content):
        pw_hash = self.store.get_password_hash(content['user'])
        if self.crypto.verify(content['password'], pw_hash):
            self.store.remove_user(content['user'])
            return '200'
        else:
            return '401'

    def _automated_login(self, token):
        server_token = self.store.get_token(token['selector'])
        if server_token:
            if server_token['expiry'] != token['expiry']:
                return '', 403
            if server_token['expiry'] < time.time():
                return '', 401
            validator_hash = hashlib.sha256(token['validator'].encode()).hexdigest()
            if hmac.compare_digest(validator_hash, server_token['validator']):
                access_token = create_access_token(identity=server_token['username'])
                return {"access_token": access_token}, 200
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
            self.store.add_token(selector, usr_token)
            del usr_token['username']

            usr_token['validator'] = validator
            usr_token['selector'] = selector
        pw_hash = self.store.get_password_hash(content['user'])
        if self.crypto.verify(content['password'], pw_hash):
            access_token = create_access_token(identity=content['user'])
            return {"access_token": access_token, "login_token": usr_token}, 200
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