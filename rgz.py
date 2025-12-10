from flask import Blueprint, render_template, request, redirect, session, current_app, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3
from os import path
from functools import wraps
import re

rgz = Blueprint('rgz', __name__)

def db_connect():
    if current_app.config['DB_TYPE'] == 'postgres':
        conn = psycopg2.connect(
            host='127.0.0.1',
            database='ksenia_kovalyova_knowledge_base',
            user='ksenia_kovalyova_knowledge_base',
            password='140981'
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
    else:
        dir_path = path.dirname(path.realpath(__file__))
        db_path = path.join(dir_path, "database.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
    return conn, cur

def db_close(conn, cur):
    conn.commit()
    cur.close()
    conn.close()

# === Валидация простая ===
def valid_login(login):
    if not login:
        return False
    # латиница, цифры и знаки пунктуации ASCII
    return re.match(r'^[A-Za-z0-9!@#\$%\^&\*\(\)_\-\+=\[\]\{\};:\'",\.<>\/\?\\\|`~]+$', login) is not None

def valid_password(pw):
    if not pw:
        return False
    # печатаемые ASCII символы
    return re.match(r'^[\x21-\x7E]+$', pw) is not None

def valid_title(title):
    return bool(title) and len(title) <= 200

# === Утилиты ===
def get_user_by_login(cur, login):
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT * FROM userss WHERE login=%s;", (login,))
        return cur.fetchone()
    else:
        cur.execute("SELECT * FROM userss WHERE login=?;", (login,))
        r = cur.fetchone()
        return dict(r) if r else None

def is_admin_user(login):
    if not login:
        return False
    conn, cur = db_connect()
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT is_admin FROM userss WHERE login=%s;", (login,))
        r = cur.fetchone()
    else:
        cur.execute("SELECT is_admin FROM userss WHERE login=?;", (login,))
        r = cur.fetchone()
        r = dict(r) if r else None
    db_close(conn, cur)
    if not r:
        return False
    return bool(r['is_admin'])

def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        login = session.get('login')
        if not login or not is_admin_user(login):
            return redirect(url_for('rgz.login'))
        return f(*args, **kwargs)
    return wrapper

# === Маршруты ===

@rgz.route('/rgz/')
def index():
    conn, cur = db_connect()
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT id, title, description, photo_url FROM recipes ORDER BY id;")
        recipes = cur.fetchall()
    else:
        cur.execute("SELECT id, title, description, photo_url FROM recipes ORDER BY id;")
        rows = cur.fetchall()
        recipes = [dict(r) for r in rows]
    db_close(conn, cur)
    return render_template('/rgz/index.html', recipes=recipes, login=session.get('login'))

@rgz.route('/rgz/recipe/<int:recipe_id>')
def recipe_view(recipe_id):
    conn, cur = db_connect()
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT * FROM recipes WHERE id=%s;", (recipe_id,))
        recipe = cur.fetchone()
        cur.execute("""
            SELECT i.name, ri.amount FROM recipe_ingredients ri
            JOIN ingredients i ON ri.ingredient_id=i.id
            WHERE ri.recipe_id=%s ORDER BY i.name;
        """, (recipe_id,))
        ingredients = cur.fetchall()
    else:
        cur.execute("SELECT * FROM recipes WHERE id=?;", (recipe_id,))
        r = cur.fetchone()
        recipe = dict(r) if r else None
        cur.execute("""
            SELECT i.name, ri.amount FROM recipe_ingredients ri
            JOIN ingredients i ON ri.ingredient_id=i.id
            WHERE ri.recipe_id=? ORDER BY i.name;
        """, (recipe_id,))
        rows = cur.fetchall()
        ingredients = [dict(x) for x in rows]
    db_close(conn, cur)
    return render_template('/rgz/recipe.html', recipe=recipe, ingredients=ingredients, login=session.get('login'), is_admin=is_admin_user(session.get('login')))

@rgz.route('/rgz/search', methods=['GET','POST'])
def search():
    if request.method == 'GET':
        return render_template('/rgz/search.html', login=session.get('login'))
    q_title = request.form.get('title','').strip()
    ing_text = request.form.get('ingredients','').strip()
    mode = request.form.get('mode','any')
    ingredients = [i.strip().lower() for i in ing_text.split(',') if i.strip()]

    conn, cur = db_connect()
    recipes = []

    # Если заданы ингредиенты
    if ingredients:
        # найти ids ингредиентов
        if current_app.config['DB_TYPE'] == 'postgres':
            placeholders = ','.join(['%s']*len(ingredients))
            cur.execute(f"SELECT id, lower(name) as name FROM ingredients WHERE lower(name) IN ({placeholders});", tuple(ingredients))
            found = cur.fetchall()
        else:
            placeholders = ','.join(['?']*len(ingredients))
            cur.execute(f"SELECT id, lower(name) as name FROM ingredients WHERE lower(name) IN ({placeholders});", tuple(ingredients))
            rows = cur.fetchall()
            found = [dict(r) for r in rows]
        found_ids = [r['id'] for r in found]
        if not found_ids:
            db_close(conn, cur)
            return render_template('search_results.html', recipes=[], login=session.get('login'), q_title=q_title, ingredients=ingredients)

        if mode == 'any':
            if current_app.config['DB_TYPE'] == 'postgres':
                cur.execute("SELECT DISTINCT r.* FROM recipes r JOIN recipe_ingredients ri ON r.id=ri.recipe_id WHERE ri.ingredient_id = ANY(%s);", (found_ids,))
                recipes = cur.fetchall()
            else:
                ph = ','.join(['?']*len(found_ids))
                cur.execute(f"SELECT DISTINCT r.* FROM recipes r JOIN recipe_ingredients ri ON r.id=ri.recipe_id WHERE ri.ingredient_id IN ({ph});", tuple(found_ids))
                recipes = [dict(r) for r in cur.fetchall()]
        else:  # all
            if current_app.config['DB_TYPE'] == 'postgres':
                cur.execute(f"""
                    SELECT r.* FROM recipes r
                    JOIN recipe_ingredients ri ON r.id=ri.recipe_id
                    WHERE ri.ingredient_id = ANY(%s)
                    GROUP BY r.id
                    HAVING COUNT(DISTINCT ri.ingredient_id) >= %s;
                """, (found_ids, len(found_ids)))
                recipes = cur.fetchall()
            else:
                ph = ','.join(['?']*len(found_ids))
                cur.execute(f"""
                    SELECT r.*, COUNT(DISTINCT ri.ingredient_id) as cnt FROM recipes r
                    JOIN recipe_ingredients ri ON r.id=ri.recipe_id
                    WHERE ri.ingredient_id IN ({ph})
                    GROUP BY r.id
                    HAVING COUNT(DISTINCT ri.ingredient_id) >= ?
                """, tuple(found_ids) + (len(found_ids),))
                recipes = [dict(r) for r in cur.fetchall()]

        # если есть фильтр по названию, применим
        if q_title:
            recipes = [r for r in recipes if q_title.lower() in r['title'].lower()]
    else:
        # только поиск по названию или пустой — вернуть все совпадения
        if current_app.config['DB_TYPE'] == 'postgres':
            if q_title:
                cur.execute("SELECT * FROM recipes WHERE lower(title) LIKE %s ORDER BY id;", (f"%{q_title.lower()}%",))
            else:
                cur.execute("SELECT * FROM recipes ORDER BY id;")
            recipes = cur.fetchall()
        else:
            if q_title:
                cur.execute("SELECT * FROM recipes WHERE lower(title) LIKE ? ORDER BY id;", (f"%{q_title.lower()}%",))
            else:
                cur.execute("SELECT * FROM recipes ORDER BY id;")
            recipes = [dict(r) for r in cur.fetchall()]

    db_close(conn, cur)
    return render_template('search_results.html', recipes=recipes, login=session.get('login'), q_title=q_title, ingredients=ingredients)

# === Регистрация / Вход / Выход / Удаление аккаунта ===
@rgz.route('/rgz/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('/rgz/register.html', login=session.get('login'))
    login_in = request.form.get('login','').strip()
    password = request.form.get('password','')
    full_name = request.form.get('full_name','').strip()
    if not login_in or not password or not full_name:
        return render_template('/rgz/register.html', error='Заполните все поля', login=session.get('login'))
    if not valid_login(login_in):
        return render_template('/rgz/register.html', error='Логин может содержать только латинские буквы, цифры и знаки пунктуации', login=session.get('login'))
    if not valid_password(password):
        return render_template('/rgz/register.html', error='Пароль содержит недопустимые символы', login=session.get('login'))

    conn, cur = db_connect()
    # проверка на существование
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT login FROM userss WHERE login=%s;", (login_in,))
        exists = cur.fetchone()
    else:
        cur.execute("SELECT login FROM userss WHERE login=?;", (login_in,))
        exists = cur.fetchone()
    if exists:
        db_close(conn, cur)
        return render_template('/rgz/register.html', error='Пользователь уже существует', login=session.get('login'))
    password_hash = generate_password_hash(password)
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("INSERT INTO userss (login, password, full_name, is_admin) VALUES (%s, %s, %s, FALSE);", (login_in, password_hash, full_name))
    else:
        cur.execute("INSERT INTO userss (login, password, full_name, is_admin) VALUES (?, ?, ?, 0);", (login_in, password_hash, full_name))
    db_close(conn, cur)
    flash('Регистрация пройдена. Войдите в систему.')
    return redirect(url_for('rgz.login'))

@rgz.route('/rgz/login', methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('/rgz/login.html', login=session.get('login'))
    login_in = request.form.get('login','').strip()
    password = request.form.get('password','')
    if not login_in or not password:
        return render_template('/rgz/login.html', error='Заполните поля', login=session.get('login'))
    conn, cur = db_connect()
    user = get_user_by_login(cur, login_in)
    if not user:
        db_close(conn, cur)
        return render_template('/rgz/login.html', error='Логин и/или пароль неверны', login=session.get('login'))
    user_password = user['password'] if isinstance(user, dict) else user['password']
    if not check_password_hash(user_password, password):
        db_close(conn, cur)
        return render_template('/rgz/login.html', error='Логин и/или пароль неверны', login=session.get('login'))
    # ставим в сессию логин
    session['login'] = login_in
    db_close(conn, cur)
    return redirect(url_for('rgz.index'))

@rgz.route('/rgz/logout')
def logout():
    session.pop('login', None)
    return redirect(url_for('rgz.index'))

@rgz.route('/rgz/delete_account', methods=['POST'])
def delete_account():
    login_in = session.get('login')
    if not login_in:
        return redirect(url_for('rgz.login'))
    conn, cur = db_connect()
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("DELETE FROM userss WHERE login=%s;", (login_in,))
    else:
        cur.execute("DELETE FROM userss WHERE login=?;", (login_in,))
    db_close(conn, cur)
    session.pop('login', None)
    flash('Аккаунт удалён.')
    return redirect(url_for('rgz.index'))

# === Админ: CRUD для рецептов ===
@rgz.route('/rgz/admin/recipes')
@admin_required
def admin_recipes():
    conn, cur = db_connect()
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT r.*, u.login as author FROM recipes r LEFT JOIN userss u ON r.created_by=u.id ORDER BY r.id;")
        recipes = cur.fetchall()
    else:
        cur.execute("SELECT r.*, u.login as author FROM recipes r LEFT JOIN userss u ON r.created_by=u.id ORDER BY r.id;")
        rows = cur.fetchall()
        recipes = [dict(r) for r in rows]
    db_close(conn, cur)
    return render_template('/rgz/recipes.html', recipes=recipes, login=session.get('login'))

@rgz.route('/rgz/admin/add', methods=['GET','POST'])
@admin_required
def admin_add():
    if request.method == 'GET':
        return render_template('/rgz/add.html', login=session.get('login'))
    title = request.form.get('title','').strip()
    steps = request.form.get('steps','').strip()
    photo_url = request.form.get('photo','').strip()
    ing_text = request.form.get('ingredients','').strip()
    if not valid_title(title) or not steps:
        return render_template('/rgz/add.html', error='Заполните название и шаги', login=session.get('login'))
    ingredients = [s.strip() for s in ing_text.split(',') if s.strip()]
    conn, cur = db_connect()
    # created_by
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT id FROM userss WHERE login=%s;", (session.get('login'),))
        row = cur.fetchone()
        created_by = row['id'] if row else None
        cur.execute("INSERT INTO recipes (title, steps, photo_url, created_by) VALUES (%s,%s,%s,%s) RETURNING id;", (title, steps, photo_url, created_by))
        recipe_id = cur.fetchone()['id']
    else:
        cur.execute("SELECT id FROM userss WHERE login=?;", (session.get('login'),))
        row = cur.fetchone()
        created_by = row['id'] if row else None
        cur.execute("INSERT INTO recipes (title, steps, photo_url, created_by) VALUES (?,?,?,?);", (title, steps, photo_url, created_by))
        recipe_id = cur.lastrowid
    # ингредиенты: find or insert, then link
    for ing in ingredients:
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT id FROM ingredients WHERE lower(name)=lower(%s);", (ing,))
            f = cur.fetchone()
            if f:
                iid = f['id']
            else:
                cur.execute("INSERT INTO ingredients (name) VALUES (%s) RETURNING id;", (ing,))
                iid = cur.fetchone()['id']
            cur.execute("INSERT INTO recipe_ingredients (recipe_id, ingredient_id, amount) VALUES (%s,%s,%s);", (recipe_id, iid, ''))
        else:
            cur.execute("SELECT id FROM ingredients WHERE lower(name)=lower(?);", (ing,))
            r = cur.fetchone()
            if r:
                iid = r['id']
            else:
                cur.execute("INSERT INTO ingredients (name) VALUES (?);", (ing,))
                iid = cur.lastrowid
            cur.execute("INSERT OR IGNORE INTO recipe_ingredients (recipe_id, ingredient_id) VALUES (?,?);", (recipe_id, iid))
    db_close(conn, cur)
    return redirect(url_for('rgz.admin_recipes'))

@rgz.route('/rgz/admin/edit/<int:recipe_id>', methods=['GET','POST'])
@admin_required
def admin_edit(recipe_id):
    conn, cur = db_connect()
    if request.method == 'GET':
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT * FROM recipes WHERE id=%s;", (recipe_id,))
            recipe = cur.fetchone()
            cur.execute("SELECT i.name FROM recipe_ingredients ri JOIN ingredients i ON ri.ingredient_id=i.id WHERE ri.recipe_id=%s ORDER BY i.name;", (recipe_id,))
            ing_rows = cur.fetchall()
        else:
            cur.execute("SELECT * FROM recipes WHERE id=?;", (recipe_id,))
            r = cur.fetchone()
            recipe = dict(r) if r else None
            cur.execute("SELECT i.name FROM recipe_ingredients ri JOIN ingredients i ON ri.ingredient_id=i.id WHERE ri.recipe_id=? ORDER BY i.name;", (recipe_id,))
            rows = cur.fetchall()
            ing_rows = [dict(x) for x in rows]
        db_close(conn, cur)
        ing_str = ', '.join([i['name'] for i in ing_rows]) if ing_rows else ''
        return render_template('/rgz/edit.html', recipe=recipe, ingredients_str=ing_str, login=session.get('login'))
    # POST -> update
    title = request.form.get('title','').strip()
    steps = request.form.get('steps','').strip()
    photo_url = request.form.get('photo','').strip()
    ing_text = request.form.get('ingredients','').strip()
    if not valid_title(title) or not steps:
        db_close(conn, cur)
        return render_template('/rgz/edit.html', error='Заполните обязательные поля', login=session.get('login'))
    ingredients = [s.strip() for s in ing_text.split(',') if s.strip()]
    conn, cur = db_connect()
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("UPDATE recipes SET title=%s, steps=%s, photo_url=%s WHERE id=%s;", (title, steps, photo_url, recipe_id))
        cur.execute("DELETE FROM recipe_ingredients WHERE recipe_id=%s;", (recipe_id,))
    else:
        cur.execute("UPDATE recipes SET title=?, steps=?, photo_url=? WHERE id=?;", (title, steps, photo_url, recipe_id))
        cur.execute("DELETE FROM recipe_ingredients WHERE recipe_id=?;", (recipe_id,))
    for ing in ingredients:
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT id FROM ingredients WHERE lower(name)=lower(%s);", (ing,))
            f = cur.fetchone()
            if f:
                iid = f['id']
            else:
                cur.execute("INSERT INTO ingredients (name) VALUES (%s) RETURNING id;", (ing,))
                iid = cur.fetchone()['id']
            cur.execute("INSERT INTO recipe_ingredients (recipe_id, ingredient_id) VALUES (%s,%s);", (recipe_id, iid))
        else:
            cur.execute("SELECT id FROM ingredients WHERE lower(name)=lower(?);", (ing,))
            r = cur.fetchone()
            if r:
                iid = r['id']
            else:
                cur.execute("INSERT INTO ingredients (name) VALUES (?);", (ing,))
                iid = cur.lastrowid
            cur.execute("INSERT OR IGNORE INTO recipe_ingredients (recipe_id, ingredient_id) VALUES (?,?);", (recipe_id, iid))
    db_close(conn, cur)
    return redirect(url_for('rgz.admin_recipes'))

@rgz.route('/rgz/admin/delete/<int:recipe_id>', methods=['POST'])
@admin_required
def admin_delete(recipe_id):
    conn, cur = db_connect()
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("DELETE FROM recipes WHERE id=%s;", (recipe_id,))
    else:
        cur.execute("DELETE FROM recipes WHERE id=?;", (recipe_id,))
    db_close(conn, cur)
    return redirect(url_for('rgz.admin_recipes'))
