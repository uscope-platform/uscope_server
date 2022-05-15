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

from flask_jwt_extended import get_jwt_identity
from flask_restful import abort
from flask import current_app


def role_required(required_role):
    def decorator(func):
        def wrapper(*args, **kwargs):
            roles_equivalence = {"admin": 1, "user": 2, "operator": 3}
            user = get_jwt_identity()
            store = current_app.store
            user = store.Auth.get_user(user)
            user_role = roles_equivalence[user['role']]
            max_role = roles_equivalence[required_role]

            if user_role <= max_role:
                return func(*args, **kwargs)
            else:
                abort(403, error_message='The user does not have enough privileges')

        return wrapper
    return decorator
