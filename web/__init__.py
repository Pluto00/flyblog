from flask import Flask, render_template
from flask_session import Session
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from web import Environment
import redis
from web.config import Config
from datetime import timedelta
from IpManage import IpLimiter

app = Flask(__name__)
app.config.from_object(Config)

# BootStarp init
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
app.config['BOOTSTRAP_QUERYSTRING_REVVING'] = False
Bootstrap(app)

# Database init
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_NATIVE_UNICODE'] = True
db = SQLAlchemy()
db.init_app(app)
migrate = Migrate(app, db)

# redis init
r = redis.Redis(host=Environment.redis_host, port=Environment.redis_port, password=Environment.redis_pass)
r_web_html = "FlyBlogWebHtml"  # 网页html缓存key

# Session init
app.permanent_session_lifetime = timedelta(hours=1)
if Environment.redis_enable:
    app.config['SESSION_REFRESH_EACH_REQUEST'] = False
    app.config['SESSION_TYPE'] = 'redis'
    app.config['SESSION_REDIS'] = r
    Session(app)

# ip limit init
ip_limit = IpLimiter(r)


def decoded(string):
    return string.decode()


def redis_value(data):
    if isinstance(data, bytes):
        data = data.decode()
    value = r.get(data)
    if value:
        return value.decode()
    return "None"


def redis_ttl(data):
    if isinstance(data, bytes):
        data = data.decode()
    try:
        return str(timedelta(seconds=r.ttl(data)))
    except:
        return "None"


app.jinja_env.filters['decoded'] = decoded
app.jinja_env.filters['redis_value'] = redis_value
app.jinja_env.filters['redis_ttl'] = redis_ttl

import web.views  # 在这里import，防止循环依赖


@app.errorhandler(404)
def notfound(error=None):
    return render_template('errors/404.html'), 404
