from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from web import Environment
import redis
from web.config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy()
db.init_app(app)
migrate = Migrate(app, db)
r = redis.Redis(host=Environment.redis_host, port=Environment.redis_port, password=Environment.redis_pass,
                decode_responses=True)

import web.views  # 在这里import，防止循环依赖
