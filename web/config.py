import os
from web.Environment import mysql_host, mysql_name, mysql_pass, mysql_port, mysql_user, debug_model, secret_key, \
    mysql_charset


class Config(object):
    DEBUG = debug_model

    SECRET_KEY = secret_key

    BASEPATH = os.getcwd().replace('\\', r'\\')

    # 格式为mysql+pymysql://数据库用户名:密码@数据库地址:端口号/数据库的名字?数据库格式
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{mysql_user}:{mysql_pass}@{mysql_host}:{mysql_port}/{mysql_name}?{mysql_charset}'

    # 忽视警告
    SQLALCHEMY_TRACK_MODIFICATIONS = False
