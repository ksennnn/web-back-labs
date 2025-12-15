from flask import Blueprint, render_template, redirect, request, session
from db import db
from db.models import users, articles
from flask_login import login_user, login_required, current_user, logout_user
from os import path
from werkzeug.security import check_password_hash, generate_password_hash


lab8 = Blueprint('lab8', __name__)


@lab8.route('/lab8/')
def lab():
    return render_template('lab8/lab8.html')


@lab8.route('/lab8/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('lab8/register.html')
    login_form = request.form.get('login')
    password_form = request.form.get('password')

    login_exists = users.query.filter_by(login = login_form).first()
    if login_exists:
        return render_template('lab8/register.html', error='Такой пользователь уже существует')
    
    if not login_form or not login_form.strip():
        return render_template('lab8/register.html', error='Введите логин')
    
    if not password_form or not password_form.strip():
        return render_template('lab8/register.html', error='Введите пароль')

    
    password_hash = generate_password_hash(password_form)
    new_user = users(login = login_form, password = password_hash)
    db.session.add(new_user)
    db.session.commit()

    login_user(new_user)
    return redirect('/lab8/')


@lab8.route('/lab8/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('lab8/login.html')
    
    login_form = request.form.get('login')
    password_form = request.form.get('password')
    remember = request.form.get('galka') == 'on'
    
    if not login_form or not login_form.strip():
        return render_template('lab8/login.html', error='Введите логин')
    
    if not password_form or not password_form.strip():
        return render_template('lab8/login.html', error='Введите пароль')
    
    user = users.query.filter_by(login = login_form).first()
    if user:
        if check_password_hash(user.password, password_form):
            login_user(user, remember=remember)
            return redirect('/lab8/')

    return render_template('lab8/login.html', error='Ошибка входа: логин и/или пароль неверны')


@lab8.route('/lab8/logout')
@login_required
def logout():
    logout_user()
    return redirect('/lab8/')


@lab8.route('/lab8/articles')
@login_required
def article_list():
    all_articles = articles.query.filter((articles.is_public == 1) | (articles.login_id == current_user.id)).all()
    return render_template('lab8/articles.html', articles=all_articles)


@lab8.route('/lab8/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'GET':
        return render_template('lab8/create.html')
    
    title_form = request.form.get('title', '').strip()
    article_text_form = request.form.get('article_text', '').strip()
    is_public = 1 if request.form.get('is_public') == 'on' else 0
    is_favorite = True if request.form.get('is_favorite') == 'on' else False

    if not title_form.strip() or not article_text_form.strip():
        return render_template('lab8/create.html', error="Заполните все поля")
    
    new_article = articles(
        login_id=current_user.id,
        title=title_form,
        article_text=article_text_form,
        is_favorite=is_favorite,
        is_public=int(is_public)
    )

    db.session.add(new_article)
    db.session.commit()
    return redirect('/lab8/articles')


@lab8.route('/lab8/edit/<int:article_id>', methods=['GET', 'POST'])
@login_required
def edit_article(article_id):
    article = articles.query.get(article_id)
    if not article:
        return "Статья не найдена", 404
    
    if request.method == 'GET':
        return render_template('lab8/edit.html', article=article)

    title_form = request.form.get('title', '').strip()
    article_text_form = request.form.get('article_text', '').strip()
    is_public = 1 if request.form.get('is_public') == 'on' else 0
    is_favorite = True if request.form.get('is_favorite') == 'on' else False

    if not title_form or not article_text_form:
        return render_template('lab8/edit.html', article=article, error="Заполните все поля")

    article.title = title_form
    article.article_text = article_text_form
    article.is_public = is_public
    article.is_favorite = is_favorite

    db.session.commit()
    return redirect('/lab8/articles')


@lab8.route('/lab8/delete/<int:article_id>', methods=['POST'])
@login_required
def delete(article_id):
    article = articles.query.get(article_id)
    if not article:
        return "Статья не найдена", 404
    db.session.delete(article)
    db.session.commit()
    return redirect('/lab8/articles')