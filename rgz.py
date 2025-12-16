from flask import Blueprint, render_template, request, session, redirect, current_app
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from os import path
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

def validate_login1(login1):
    if not login1 or len(login1) < 3 or len(login1) > 50:
        return False
    return bool(re.match(r'^[a-zA-Z0-9._-]+$', login1))

def validate_password(password):
    if not password or len(password) < 6:
        return False
    return bool(re.match(r'^[a-zA-Z0-9!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]+$', password))

def validate_recipe_data(title, ingredients, steps, photo_url):
    errors = []
    if not title or len(title) < 3 or len(title) > 100:
        errors.append("Название рецепта должно быть от 3 до 100 символов")
    if not ingredients or len(ingredients) < 10:
        errors.append("Укажите ингредиенты (минимум 10 символов)")
    if not steps or len(steps) < 20:
        errors.append("Опишите шаги приготовления (минимум 20 символов)")
    if photo_url and not photo_url.startswith(('http://', 'https://')):
        errors.append("Некорректный URL фотографии")
    return errors

@rgz.route('/rgz/')
def index():
    conn, cur = db_connect()
    
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT * FROM recipes LIMIT 21;")
    else:
        cur.execute("SELECT * FROM recipes LIMIT 21;")
    
    recipes = cur.fetchall()
    db_close(conn, cur)
    
    return render_template('rgz/index.html', 
                         recipes=recipes, 
                         login1=session.get('login1'))

@rgz.route('/rgz/recipes')
def all_recipes():
    conn, cur = db_connect()
    
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT * FROM recipes ORDER BY id DESC;")
    else:
        cur.execute("SELECT * FROM recipes ORDER BY id DESC;")
    
    recipes = cur.fetchall()
    db_close(conn, cur)
    
    return render_template('rgz/recipes.html', 
                         recipes=recipes, 
                         login1=session.get('login1'))

@rgz.route('/rgz/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('rgz/register.html')
    
    login1 = request.form.get('login1', '').strip()
    password = request.form.get('password', '').strip()
    full_name = request.form.get('full_name', '').strip()
    
    # Валидация
    if not validate_login1(login1):
        return render_template('rgz/register.html', 
                             error='Логин должен содержать только латинские буквы, цифры и знаки ._- (от 3 до 50 символов)')
    
    if not validate_password(password):
        return render_template('rgz/register.html', 
                             error='Пароль должен содержать только латинские буквы, цифры и спецсимволы (минимум 6 символов)')
    
    conn, cur = db_connect()
    
    # Проверка существования пользователя
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT id FROM polzovat WHERE login1 = %s;", (login1,))
    else:
        cur.execute("SELECT id FROM polzovat WHERE login1 = ?;", (login1,))
    
    if cur.fetchone():
        db_close(conn, cur)
        return render_template('rgz/register.html', 
                             error='Пользователь с таким логином уже существует')
    
    # Хеширование пароля
    password_hash = generate_password_hash(password)
    
    # Создание пользователя
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("INSERT INTO polzovat (login1, password, full_name) VALUES (%s, %s, %s);", 
                   (login1, password_hash, full_name))
    else:
        cur.execute("INSERT INTO polzovat (login1, password, full_name) VALUES (?, ?, ?);", 
                   (login1, password_hash, full_name))
    
    db_close(conn, cur)
    return redirect('/rgz/login')

@rgz.route('/rgz/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('rgz/login.html')
    
    login1 = request.form.get('login1', '').strip()
    password = request.form.get('password', '').strip()
    
    if not validate_login1(login1):
        return render_template('rgz/register.html', 
                             error='Логин должен содержать только латинские буквы, цифры и знаки ._- (от 3 до 50 символов)')
    
    if not validate_password(password):
        return render_template('rgz/register.html', 
                             error='Пароль должен содержать только латинские буквы, цифры и спецсимволы (минимум 6 символов)')

    if not login1 or not password:
        return render_template('rgz/login.html', 
                             error='Заполните все поля')
    
    conn, cur = db_connect()
    
    # Поиск пользователя
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT * FROM polzovat WHERE login1 = %s;", (login1,))
    else:
        cur.execute("SELECT * FROM polzovat WHERE login1 = ?;", (login1,))
    
    user = cur.fetchone()
    
    if not user:
        db_close(conn, cur)
        return render_template('rgz/login.html', 
                             error='Неверный логин или пароль')
    
    # Проверка пароля
    if not check_password_hash(user['password'], password):
        db_close(conn, cur)
        return render_template('rgz/login.html', 
                             error='Неверный логин или пароль')
    
    # Сохраняем в сессии
    session['login1'] = login1
    
    db_close(conn, cur)
    return redirect('/rgz/')

@rgz.route('/rgz/logout')
def logout():
    session.pop('login1', None)
    return redirect('/rgz/')

@rgz.route('/rgz/delete_account', methods=['POST'])
def delete_account():
    login1 = session.get('login1')
    if not login1:
        return redirect('/rgz/login')
    
    conn, cur = db_connect()
    
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("DELETE FROM polzovat WHERE login1 = %s;", (login1,))
    else:
        cur.execute("DELETE FROM polzovat WHERE login1 = ?;", (login1,))
    
    db_close(conn, cur)
    
    # Очищаем сессию
    session.pop('login1', None)
    
    return redirect('/rgz/')

@rgz.route('/rgz/recipe/<int:recipe_id>')
def view_recipe(recipe_id):
    conn, cur = db_connect()
    
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT * FROM recipes WHERE id = %s;", (recipe_id,))
    else:
        cur.execute("SELECT * FROM recipes WHERE id = ?;", (recipe_id,))
    
    recipe = cur.fetchone()
    db_close(conn, cur)
    
    if not recipe:
        return "Рецепт не найден", 404
    
    return render_template('rgz/recipe.html', 
                         recipe=recipe,
                         login1=session.get('login1'))

@rgz.route('/rgz/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        return render_template('rgz/search.html',
                             login1=session.get('login1'))
    
    search_query = request.form.get('query', '').strip()
    ingredients = request.form.get('ingredients', '').strip()
    search_mode = request.form.get('mode', 'any')
    
    conn, cur = db_connect()
    
    #Загружаем все рецепты для фильтрации на стороне Python
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT * FROM recipes ORDER BY id DESC;")
    else:
        cur.execute("SELECT * FROM recipes ORDER BY id DESC;")
    
    all_recipes = cur.fetchall()
    db_close(conn, cur)
    
    #Фильтрация на стороне Python
    filtered_recipes = []
    
    for recipe in all_recipes:
        matches = True
        
        #Поиск по названию
        if search_query:
            recipe_title = recipe['title'].lower() if isinstance(recipe['title'], str) else ''
            search_lower = search_query.lower()
            if search_lower not in recipe_title:
                matches = False
        
        # Поиск по ингредиентам
        if ingredients and matches:
            ingredient_list = [ing.strip().lower() for ing in ingredients.split(',') if ing.strip()]
            recipe_ingredients = recipe['ingredients'].lower() if isinstance(recipe['ingredients'], str) else ''
            
            if search_mode == 'all':
                #Все ингредиенты должны быть в рецепте
                for ingredient in ingredient_list:
                    if ingredient not in recipe_ingredients:
                        matches = False
                        break
            else:  #хотя бы один ингредиент
                any_found = False
                for ingredient in ingredient_list:
                    if ingredient in recipe_ingredients:
                        any_found = True
                        break
                if not any_found:
                    matches = False
        
        if matches:
            filtered_recipes.append(recipe)
    
    return render_template('rgz/search_results.html',
                         recipes=filtered_recipes,
                         search_query=search_query,
                         ingredients=ingredients,
                         search_mode=search_mode,
                         login1=session.get('login1'))

@rgz.route('/rgz/add_recipe', methods=['GET', 'POST'])
def add_recipe():
    if not session.get('login1'):
        return redirect('/rgz/login')
    
    if request.method == 'GET':
        return render_template('rgz/add_recipe.html',
                             login1=session.get('login1'))
    
    #Получение данных из формы
    title = request.form.get('title', '').strip()
    ingredients = request.form.get('ingredients', '').strip()
    steps = request.form.get('steps', '').strip()
    photo_url = request.form.get('photo_url', '').strip()
    
    #Валидация
    errors = validate_recipe_data(title, ingredients, steps, photo_url)
    if errors:
        return render_template('rgz/add_recipe.html',
                             errors=errors,
                             title=title,
                             ingredients=ingredients,
                             steps=steps,
                             photo_url=photo_url,
                             login1=session.get('login1'))
    
    conn, cur = db_connect()
    
    #Добавление рецепта
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("""
            INSERT INTO recipes (title, ingredients, steps, photo_url) 
            VALUES (%s, %s, %s, %s);
        """, (title, ingredients, steps, photo_url or None))
    else:
        cur.execute("""
            INSERT INTO recipes (title, ingredients, steps, photo_url) 
            VALUES (?, ?, ?, ?);
        """, (title, ingredients, steps, photo_url or None))
    
    db_close(conn, cur)
    
    return redirect('/rgz/recipes')

@rgz.route('/rgz/edit_recipe/<int:recipe_id>', methods=['GET', 'POST'])
def edit_recipe(recipe_id):
    if not session.get('login1'):
        return redirect('/rgz/login')
    
    conn, cur = db_connect()
    
    if request.method == 'GET':
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT * FROM recipes WHERE id = %s;", (recipe_id,))
        else:
            cur.execute("SELECT * FROM recipes WHERE id = ?;", (recipe_id,))
        
        recipe = cur.fetchone()
        db_close(conn, cur)
        
        if not recipe:
            return "Рецепт не найден", 404
        
        return render_template('rgz/edit_recipe.html',
                             recipe=recipe,
                             login1=session.get('login1'))
    
    title = request.form.get('title', '').strip()
    ingredients = request.form.get('ingredients', '').strip()
    steps = request.form.get('steps', '').strip()
    photo_url = request.form.get('photo_url', '').strip()
    
    #Валидация
    errors = validate_recipe_data(title, ingredients, steps, photo_url)
    if errors:
        return render_template('rgz/edit_recipe.html',
                             errors=errors,
                             recipe={'id': recipe_id, 'title': title, 'ingredients': ingredients, 
                                    'steps': steps, 'photo_url': photo_url},
                             login1=session.get('login1'))
    
    #Обновление рецепта
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("""
            UPDATE recipes 
            SET title = %s, ingredients = %s, steps = %s, photo_url = %s 
            WHERE id = %s;
        """, (title, ingredients, steps, photo_url or None, recipe_id))
    else:
        cur.execute("""
            UPDATE recipes 
            SET title = ?, ingredients = ?, steps = ?, photo_url = ? 
            WHERE id = ?;
        """, (title, ingredients, steps, photo_url or None, recipe_id))
    
    db_close(conn, cur)
    
    return redirect(f'/rgz/recipe/{recipe_id}')

@rgz.route('/rgz/delete_recipe/<int:recipe_id>', methods=['POST'])
def delete_recipe(recipe_id):
    if not session.get('login1'):
        return redirect('/rgz/login')
    
    
    conn, cur = db_connect()
    
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("DELETE FROM recipes WHERE id = %s;", (recipe_id,))
    else:
        cur.execute("DELETE FROM recipes WHERE id = ?;", (recipe_id,))
    
    db_close(conn, cur)
    
    return redirect('/rgz/recipes')