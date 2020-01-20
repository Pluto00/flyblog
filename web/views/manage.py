from flask import request, redirect, url_for, render_template
from web import app, db
from web.models import Article, Comment, Picture
from web.Environment import admin_pass
from web.utils.token import generate_auth_token, verify_auth_token


@app.route('/login/')
def login():
    pwd = request.args.get('pwd')
    if pwd != admin_pass:
        return redirect(url_for('index'))
    token = generate_auth_token()
    return redirect(url_for('admin', token=token))


@app.route('/admin/')
def admin():
    token = request.args.get('token')
    if not verify_auth_token(token):
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
    if not verify_auth_token(token):
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
    if not verify_auth_token(token):
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
    if not verify_auth_token(token):
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
        if not verify_auth_token(token):
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
        if not verify_auth_token(token):
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
        if not verify_auth_token(token):
            return redirect(url_for('index'))
        return render_template('upload_picture.html', token=token)
    elif request.method == 'POST':
        urls = request.form.get('url').split()
        for url in urls:
            db.session.add(Picture(url=url))
        db.session.commit()
        return redirect(url_for('upload_picture', token=token))
