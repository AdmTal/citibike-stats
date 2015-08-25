from functools import wraps
from flask import request, abort


def ssl_required(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        if not request.is_secure:
            abort(403, "Must use HTTPS for this endpoint")

        return fn(*args, **kwargs)

    return decorated_view