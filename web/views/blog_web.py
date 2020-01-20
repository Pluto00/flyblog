from flask import request, redirect, url_for, render_template
from web import app, db
from web.models import Article, Comment, Picture
from sqlalchemy.sql.expression import func


@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Article.query.filter(Article.id > 10).order_by(-Article.id).paginate(page, per_page=10,
                                                                                      error_out=False)
    articles = pagination.items
    return render_template('index.html', ARTICLE=dict(zip(articles, random_article(len(articles)))),
                           page_cover=random_page(), pagination=pagination)


@app.route('/<path:key>/')
def article_sort(key):
    page = request.args.get('page', 1, type=int)
    pagination = Article.query.filter(Article.type == key).order_by(-Article.id).paginate(page, per_page=10,
                                                                                          error_out=False)
    articles = pagination.items
    return render_template('index.html', ARTICLE=dict(zip(articles, random_article(len(articles)))),
                           page_cover=random_page(), pagination=pagination)


@app.route('/detail/<int:article_id>/')
def detail(article_id):
    article_model = Article.query.filter(Article.id == article_id).first()
    article_model.views += 1
    db.session.commit()
    comments = Comment.query.filter(Comment.article == article_model).order_by(-Comment.id).all()
    return render_template('detail.html', page_cover=random_page(), article=article_model,
                           comments=comments)


@app.route('/comment/<int:article_id>/', methods=['POST'])
def add_comment(article_id):
    article = Article.query.filter(Article.id == article_id).first()
    article.comments += 1
    comment = Comment(comment=request.form.get('text'),
                      nickname=request.form.get('author'),
                      mail=request.form.get('mail'),
                      url=request.form.get('url'),
                      article_id=article_id,
                      article=article)
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('detail', article_id=article_id))


@app.route('/search/')
def search():
    keyword = request.args.get('s')
    page = request.args.get('page', 1, type=int)
    pagination = Article.query.filter(Article.title.contains(keyword)).order_by(-Article.id).paginate(page,
                                                                                                      per_page=10,
                                                                                                      error_out=False)
    articles = pagination.items
    return render_template('search.html', ARTICLE=dict(zip(articles, random_article(len(articles)))),
                           page_cover=random_page(), pagination=pagination)


def random_article(count):
    return Picture.query.order_by(func.rand()).limit(count).all()


def random_page():
    return Picture.query.order_by(func.rand()).first()
