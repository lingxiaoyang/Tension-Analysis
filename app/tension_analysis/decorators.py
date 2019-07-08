from functools import wraps
import re
import uuid

from flask import g, make_response, request

import global_config

RE_UUID_HEX = re.compile('^[0-9a-f]{32}$')


def ensure_user_cookie(f):
    @wraps(f)
    def decorated_function(*a, **k):
        cookie_name = global_config.USER_IDENTIFICATION_COOKIE_NAME
        g.user_id = request.cookies.get(cookie_name)
        if not RE_UUID_HEX.match(str(g.user_id)):
            g.user_id = uuid.uuid4().hex
        response = make_response(f(*a, **k))
        response.set_cookie(cookie_name, g.user_id)
        return response
    return decorated_function
