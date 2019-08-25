from flask import Flask, render_template, request, redirect, url_for
from config import ConFig
from models import db, Comment, Article, Picture
from sqlalchemy.sql.expression import func

app = Flask(__name__)
app.config.from_object(ConFig)
db.init_app(app)


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


@app.route('/login/')
def login():
    pwd = request.args.get('pwd')
    if pwd != ConFig.ADMIN_PWD:
        return redirect(url_for('index'))
    token = ConFig.generate_auth_token()
    return redirect(url_for('admin', token=token))


@app.route('/admin/')
def admin():
    token = request.args.get('token')
    if not ConFig.verify_auth_token(token):
        return redirect(url_for('index'))
    else:
        page = request.args.get('page', 1, type=int)
        pagination = Article.query.order_by(-Article.id).paginate(page, per_page=100, error_out=False)
        articles = pagination.items
        comments = Comment.query.order_by(-Comment.id).paginate(page, per_page=100, error_out=False).items
        pictures = Picture.query.order_by(-Picture.id).paginate(page, per_page=100, error_out=False).items
        return render_template('admin.html', articles=articles, pagination=pagination, pictures=pictures,
                               comments=comments, token=token)


@app.route('/delete_article/')
def delete_article():
    token = request.args.get('token')
    article_id = request.args.get('article_id')
    if not ConFig.verify_auth_token(token):
        return redirect(url_for('index'))
    else:
        comments = Comment.query.filter(Comment.article_id == article_id).all()
        article = Article.query.filter(Article.id == article_id).first()
        if comments:
            db.session.delete(comments)
        if article:
            db.session.delete(article)
        db.session.commit()
        return redirect(url_for('admin', token=token))


@app.route('/delete_comment/')
def delete_comment():
    token = request.args.get('token')
    comment_id = request.args.get('comment_id')
    if not ConFig.verify_auth_token(token):
        return redirect(url_for('index'))
    else:
        comment = Comment.query.filter(Comment.id == comment_id).first()
        if comment:
            db.session.delete(comment)
        db.session.commit()
        return redirect(url_for('admin', token=token))


@app.route('/delete_pic/')
def delete_pic():
    token = request.args.get('token')
    picture_id = request.args.get('picture_id')
    if not ConFig.verify_auth_token(token):
        return redirect(url_for('index'))
    else:
        picture = Picture.query.filter(Picture.id == picture_id).first()
        if picture:
            db.session.delete(picture)
        db.session.commit()
        return redirect(url_for('admin', token=token))


@app.route('/edit_article/', methods=['GET', 'POST'])
def edit_article():
    if request.method == 'GET':
        token = request.args.get('token')
        if not ConFig.verify_auth_token(token):
            return redirect(url_for('index'))
        article_id = request.args.get('article_id')
        article = Article.query.filter(Article.id == article_id).first()
        return render_template('edit_article.html', article=article)
    elif request.method == 'POST':
        article_id = request.args.get('article_id')
        article = Article.query.filter(Article.id == article_id).first()
        article.title = request.form.get('title')
        article.type = request.form.get('type')
        article.content = request.form.get('fancy-editormd-html-code')
        article.mark_code = request.form.get('fancy-editormd-markdown-code')  # markdown源码
        db.session.commit()
        return redirect(url_for('index'))


@app.route('/add_article/', methods=['GET', 'POST'])
def add_article():
    if request.method == 'GET':
        token = request.args.get('token')
        if not ConFig.verify_auth_token(token):
            return redirect(url_for('index'))
        return render_template('add_article.html')
    elif request.method == 'POST':
        article = Article(content=request.form.get('fancy-editormd-html-code'),
                          mark_code=request.form.get('fancy-editormd-markdown-code'),
                          title=request.form.get('title'),
                          type=request.form.get('type'))
        db.session.add(article)
        db.session.commit()
        return redirect(url_for('index'))


@app.route('/upload_picture/', methods=['GET', 'POST'])
def upload_picture():
    token = request.args.get('token')
    if request.method == 'GET':
        if not ConFig.verify_auth_token(token):
            return redirect(url_for('index'))
        return render_template('upload_picture.html', token=token)
    elif request.method == 'POST':
        urls = request.form.get('url').split()
        for url in urls:
            db.session.add(Picture(url=url))
        db.session.commit()
        return redirect(url_for('upload_picture', token=token))


def random_article(count):
    return Picture.query.order_by(func.rand()).limit(count).all()


def random_page():
    return Picture.query.order_by(func.rand()).first()


if __name__ == '__main__':
    app.run()


