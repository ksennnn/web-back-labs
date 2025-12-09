from flask import Blueprint, render_template, request, abort, current_app
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3
from os import path
from datetime import datetime


lab7 = Blueprint('lab7', __name__)


def db_connect():
    if current_app.config['DB_TYPE'] == 'postgres':
        conn = psycopg2.connect(
                host = '127.0.0.1',
                database = 'ksenia_kovalyova_knowledge_base',
                user = 'ksenia_kovalyova_knowledge_base',
                password = '140981'
            )
        cur = conn.cursor(cursor_factory= RealDictCursor)
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


@lab7.route('/lab7/')
def main():
    return render_template('lab7/index.html')


def validate_film_data(film):
    errors = {}
    
    title_ru = film.get('title_ru', '').strip()
    if not title_ru:
        errors['title_ru'] = 'Русское название обязательно для заполнения'
    
    title = film.get('title', '').strip()
    if not title and not title_ru:
        errors['title'] = 'Хотя бы одно название должно быть заполнено'
    
    year_str = film.get('year', '')
    current_year = datetime.now().year
    
    if not year_str:
        errors['year'] = 'Год обязателен для заполнения'
    else:
        try:
            year = int(year_str)
            if year < 1895:
                errors['year'] = f'Год должен быть не раньше 1895'
            elif year > current_year:
                errors['year'] = f'Год не может быть больше текущего ({current_year})'
        except (ValueError, TypeError):
            errors['year'] = 'Год должен быть числом'
    
    description = film.get('description', '').strip()
    if not description:
        errors['description'] = 'Описание обязательно для заполнения'
    elif len(description) > 2000:
        errors['description'] = f'Описание не должно превышать 2000 символов (сейчас {len(description)})'
    
    return errors


@lab7.route('/lab7/rest-api/films/', methods=['GET'])
def get_films():
    conn, cur = db_connect()
    
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT id, title, title_ru, year, description FROM films ORDER BY id")
    else:
        cur.execute("SELECT id, title, title_ru, year, description FROM films ORDER BY id")
    
    rows = cur.fetchall()
    db_close(conn, cur)
    
    films = []
    for row in rows:
        films.append({
            "id": row["id"],
            "title": row["title"],
            "title_ru": row["title_ru"],
            "year": row["year"],
            "description": row["description"]
        })
    
    return films

@lab7.route('/lab7/rest-api/films/<int:id>', methods=['GET'])
def get_film(id):
    conn, cur = db_connect()
    
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT id, title, title_ru, year, description FROM films WHERE id = %s", (id,))
    else:
        cur.execute("SELECT id, title, title_ru, year, description FROM films WHERE id = ?", (id,))
    
    row = cur.fetchone()
    db_close(conn, cur)

    if row is None:
        abort(404)

    film = {
        "id": row["id"],
        "title": row["title"],
        "title_ru": row["title_ru"],
        "year": row["year"],
        "description": row["description"]
    }

    return film  


@lab7.route('/lab7/rest-api/films/<int:id>', methods=['DELETE'])
def del_film(id):
    conn, cur = db_connect()
    
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT id FROM films WHERE id = %s", (id,))
    else:
        cur.execute("SELECT id FROM films WHERE id = ?", (id,))
    
    exists = cur.fetchone()
    
    if not exists:
        db_close(conn, cur)
        abort(404, description=f"Фильм с ID {id} не найден")
    
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("DELETE FROM films WHERE id = %s", (id,))
    else:
        cur.execute("DELETE FROM films WHERE id = ?", (id,))
    
    db_close(conn, cur)

    return '', 204


@lab7.route('/lab7/rest-api/films/<int:id>', methods=['PUT'])
def put_film(id):
    film = request.get_json()
    errors = validate_film_data(film)
    if errors:
        return errors, 400  
    
    if film.get('title', '').strip() == '' and film.get('title_ru', '').strip() != '':
        film['title'] = film['title_ru']
    
    conn, cur = db_connect()
    
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT id FROM films WHERE id = %s", (id,))
    else:
        cur.execute("SELECT id FROM films WHERE id = ?", (id,))
    
    exists = cur.fetchone()
    
    if not exists:
        db_close(conn, cur)
        abort(404, description=f"Фильм с ID {id} не найден")
    
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("""
            UPDATE films 
            SET title = %s, title_ru = %s, year = %s, description = %s 
            WHERE id = %s 
            RETURNING id, title, title_ru, year, description
        """, (film['title'], film['title_ru'], film['year'], film['description'], id))
        updated = cur.fetchone()
    else:
        cur.execute("""
            UPDATE films 
            SET title = ?, title_ru = ?, year = ?, description = ? 
            WHERE id = ?
        """, (film['title'], film['title_ru'], film['year'], film['description'], id))
        
        cur.execute("SELECT id, title, title_ru, year, description FROM films WHERE id = ?", (id,))
        updated = cur.fetchone()
    
    db_close(conn, cur)
    
    return {
        "id": updated["id"],
        "title": updated["title"],
        "title_ru": updated["title_ru"],
        "year": updated["year"],
        "description": updated["description"]
    }


@lab7.route('/lab7/rest-api/films/', methods=['POST'])
def add_film():
    film = request.get_json()
    errors = validate_film_data(film)
    if errors:
        return errors, 400 
    
    if film.get('title', '').strip() == '' and film.get('title_ru', '').strip() != '':
        film['title'] = film['title_ru']
    
    conn, cur = db_connect()

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("""
            INSERT INTO films (title, title_ru, year, description) 
            VALUES (%s, %s, %s, %s) 
            RETURNING id
        """, (film['title'], film['title_ru'], film['year'], film['description']))
        new_id = cur.fetchone()['id']
    else:
        cur.execute("""
            INSERT INTO films (title, title_ru, year, description) 
            VALUES (?, ?, ?, ?)
        """, (film['title'], film['title_ru'], film['year'], film['description']))
        new_id = cur.lastrowid
    
    db_close(conn, cur)
    
    return {'id': new_id}, 201  