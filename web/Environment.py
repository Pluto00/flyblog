import os

# redis
redis_enable = True
redis_host = 'localhost'
redis_port = 6379
redis_pass = ''

# mysql
mysql_host = 'localhost'
mysql_port = 3306
mysql_user = 'root'
mysql_pass = ''
mysql_name = 'flyblog'
mysql_charset = 'utf8mb4'

# app运行
app_host = '127.0.0.1'
app_port = 5000
debug_model = True
secret_key = os.urandom(24)

# 管理账号密码
admin_name = "admin"
admin_pwd = "admin"
