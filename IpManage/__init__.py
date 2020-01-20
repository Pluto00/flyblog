from flask import request, abort
from functools import wraps


class IpLimiter(object):
    def __init__(self, redis):
        self.r = redis

    def limiter(self, prefix='', per_day=10):
        def decorate(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                user_ip = prefix + request.remote_addr
                if self.r.exists(user_ip):
                    if self.r.incr(user_ip) > per_day:
                        abort(404)
                else:
                    self.r.set(user_ip, 0, ex=24 * 3600)
                return f(*args, **kwargs)

            return wrapper
        return decorate
