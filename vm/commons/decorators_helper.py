from flask_jwt_extended.exceptions import NoAuthorizationError, WrongTokenError, RevokedTokenError
from jwt.exceptions import ExpiredSignatureError
from flask_jwt_extended import get_jwt_identity
from vm.models.user import User


def error_handler_jwt_extended(func):
    def inner_function(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (NoAuthorizationError, WrongTokenError, RevokedTokenError, ExpiredSignatureError) as e:
            return {"msg": str(e)}, 401

    return inner_function


def check_is_role(role_name):
    def check_is_role_decorator(func):
        def inner_function(*args, **kwargs):
            current_user = get_jwt_identity()
            user = User.query.get(current_user)
            if user.role.name != role_name:
                return {"msg": f"Error, your are not an {role_name}"}, 401
            return func(*args, **kwargs)
        return inner_function
    return check_is_role_decorator