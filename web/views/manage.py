from flask import request, redirect, url_for, render_template, session, flash, abort
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, validators

from web import app, db
from web.models import Article, Comment, Picture
from web.Environment import admin_name, admin_pwd
from functools import wraps


class ManagerLoginForm(FlaskForm):
    name = StringField('管理员账号', [validators.required()])
    pwd = PasswordField('管理员密码', [validators.required()])
    button = SubmitField('登录')


@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = ManagerLoginForm()
    if form.validate_on_submit():
        if form.name.data == admin_name and form.pwd.data == admin_pwd:
            session['ManagerLoginStatus'] = True
            return redirect(url_for('.admin', ))
        else:
            flash("请填写正确的账号和密码")
    return render_template('manage/login.html', form=form, title="管理员登录")


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("ManagerLoginStatus"):
            abort(404)
        return func(*args, **kwargs)
    return wrapper


@app.route('/admin/')
@login_required
def admin():
    if not session.get("ManagerLoginStatus"):
        return redirect(url_for('index'))
    else:
        page = request.args.get('page', 1, type=int)
        article_pagination = Article.query.order_by(-Article.id).paginate(page, per_page=100, error_out=False)
        comment_pagination = Comment.query.order_by(-Comment.id).paginate(page, per_page=100, error_out=False)
        picture_pagination = Picture.query.order_by(-Picture.id).paginate(page, per_page=100, error_out=False)
        return render_template('manage/admin.html',
                               articles=article_pagination.items, article_pagination=article_pagination,
                               pictures=picture_pagination.items, picture_pagination=picture_pagination,
                               comments=comment_pagination.items, comment_pagination=comment_pagination)


@app.route('/delete_article/')
@login_required
def delete_article():
    article_id = request.args.get('article_id')
    comments = Comment.query.filter(Comment.article_id == article_id).all()
    article = Article.query.filter(Article.id == article_id).first()
    if comments:
        db.session.delete(comments)
    if article:
        db.session.delete(article)
    db.session.commit()
    return redirect(url_for('admin'))


@app.route('/delete_comment/')
@login_required
def delete_comment():
    comment_id = request.args.get('comment_id')
    comment = Comment.query.filter(Comment.id == comment_id).first()
    if comment:
        db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('admin'))


@app.route('/delete_pic/')
@login_required
def delete_pic():
    picture_id = request.args.get('picture_id')
    picture = Picture.query.filter(Picture.id == picture_id).first()
    if picture:
        db.session.delete(picture)
    db.session.commit()
    return redirect(url_for('admin'))


@app.route('/edit_article/', methods=['GET', 'POST'])
@login_required
def edit_article():
    if request.method == 'GET':
        article_id = request.args.get('article_id')
        article = Article.query.filter(Article.id == article_id).first()
        return render_template('manage/edit_article.html', article=article)
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
@login_required
def add_article():
    if request.method == 'GET':
        return render_template('manage/add_article.html')
    elif request.method == 'POST':
        article = Article(content=request.form.get('fancy-editormd-html-code'),
                          mark_code=request.form.get('fancy-editormd-markdown-code'),
                          title=request.form.get('title'),
                          type=request.form.get('type'))
        db.session.add(article)
        db.session.commit()
        return redirect(url_for('index'))


@app.route('/upload_picture/', methods=['GET', 'POST'])
@login_required
def upload_picture():
    if request.method == 'GET':
        return render_template('manage/upload_picture.html')
    elif request.method == 'POST':
        urls = request.form.get('url').split()
        for url in urls:
            db.session.add(Picture(url=url))
        db.session.commit()
        return redirect(url_for('upload_picture'))
