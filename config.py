import os
from random import choice, sample
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired, BadSignature
import requests


class ConFig():
    DEBUG = True

    SECRET_KEY = os.urandom(24)

    BASEPATH = os.getcwd().replace('\\', r'\\')

    # 格式为mysql+pymysql://数据库用户名:密码@数据库地址:端口号/数据库的名字?数据库格式
    SQLALCHEMY_DATABASE_URI = r'mysql+pymysql://root:@localhost:3306/flyblog?charset=utf8mb4'

    # 忽视警告
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 后台密码
    ADMIN_PWD = "xxxxxxx"

    @staticmethod
    def generate_auth_token(expiration=3600):
        s = Serializer(ConFig.SECRET_KEY, expires_in=expiration)
        return s.dumps({})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(ConFig.SECRET_KEY)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        return True
