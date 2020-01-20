from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature
from web.Environment import secret_key


def generate_auth_token(expiration=3600):
    s = Serializer(secret_key, expires_in=expiration)
    return s.dumps({})


def verify_auth_token(token):
    s = Serializer(secret_key)
    try:
        data = s.loads(token)
    except SignatureExpired:
        return None  # valid token, but expired
    except BadSignature:
        return None  # invalid token
    return True
