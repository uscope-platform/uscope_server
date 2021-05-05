from flask_jwt_extended import get_jwt_identity
from Store import Store
from flask_restful import abort



def role_required(required_role):
    def decorator(func):
        def wrapper(*args, **kwargs):
            roles_equivalence = {"admin": 1, "user": 2, "operator": 3}
            user = get_jwt_identity()
            store = Store(clear_settings=False, update_ude_versions_on_init=False)
            user = store.Auth.get_user(user)
            user_role = roles_equivalence[user['role']]
            max_role = roles_equivalence[required_role]

            if user_role <= max_role:
                return func(*args, **kwargs)
            else:
                abort(403, error_message='The user does not have enough privileges')

        return wrapper
    return decorator
