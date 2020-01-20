from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Article(db.Model):
    __tablename__ = 'article'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(64), nullable=False)
    content = db.Column(db.Text, nullable=False)
    mark_code = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(8), nullable=False)
    # now()获取的是服务器第一次运行的时间
    # now就是每次创建一个模型的时候，都获取当前的时间
    create_time = db.Column(db.DateTime, default=datetime.now)
    views = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    comment = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)
    nickname = db.Column(db.String(16), nullable=False)
    mail = db.Column(db.String(32), nullable=False)
    url = db.Column(db.String(64))

    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))
    article = db.relationship('Article', backref=db.backref('comment'))


class Picture(db.Model):
    __tablename__ = 'picture'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    url = db.Column(db.String(64), nullable=False)
