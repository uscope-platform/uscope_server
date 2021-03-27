from .application_manager import application_manager_bp
from flask_jwt_extended import get_jwt_identity
from Store import Store
import hmac
from flask_restful import abort


def role_required(required_role):
    def decorator(func):
        def wrapper(*args, **kwargs):
            user = get_jwt_identity()
            store = Store()
            user = store.Auth.get_user(user)
            user_allowed = hmac.compare_digest(required_role, user['role'])

            if user_allowed:
                return func(*args, **kwargs)
            else:
                abort(403, error_message='The user does not have enough privileges')
        return wrapper
    return decorator
