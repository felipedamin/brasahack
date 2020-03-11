from flask_login import current_user
from flask import redirect, url_for
from functools import wraps


def role_required(roles):
    def decorator(f):
        @wraps(f)
        def funcao_decorada(*args, **kwargs):
            if not any([role in current_user.get_roles() for role in roles]):
                return redirect(url_for('denied'))
            return f(*args, **kwargs)
        return funcao_decorada
    return decorator