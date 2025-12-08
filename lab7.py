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
    if film['description'] == '':
        return {'description': 'Заполните описание'}, 400
    if len(film['description']) > 2000:
        return {'description': 'Описание не должно превышать 2000 символов'}, 400
    
    if film['title'] == '':
        film['title'] = film['title_ru']
    
    if film['title'] == '' and film['title_ru'] == '':
        return {'title': 'Заполните название'}, 400

    if film['title_ru'] == '':
        return {'title_ru': 'Заполните название'}, 400

    current_year = datetime.now().year

    if 'year' not in film or film['year'].strip() == '' or not film['year'].isdigit():
        return {'year': 'Год должен быть числом'}, 400

    year = int(film['year'])
    if year < 1895 or year > current_year:
        return {'year': f'Введите год от 1895 до {current_year}'}, 400
    
    conn, cur = db_connect()
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("UPDATE films SET title=%s, title_ru=%s, year=%s, description=%s WHERE id=%s RETURNING *;", 
                    (film['title'], film['title_ru'], film['year'], film['description'], id))
        updated = cur.fetchone()
        conn.commit()
    else:
        cur.execute("UPDATE films SET title=?, title_ru=?, year=?, description=? WHERE id=?;", 
                    (film['title'], film['title_ru'], film['year'], film['description'], id))
        conn.commit()

        cur.execute("SELECT * FROM films WHERE id=?;", (id,))
        updated = cur.fetchone()

    if updated is None:
        abort(404)
    
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
    if film['description'] == '':
        return {'description': 'Заполните описание'}, 400
    if len(film['description']) > 2000:
        return {'description': 'Описание не должно превышать 2000 символов'}, 400
    
    if film['title'] == '':
        film['title'] = film['title_ru']

    if film['title'] == '' and film['title_ru'] == '':
        return {'title': 'Заполните название'}, 400

    if film['title_ru'] == '':
        return {'title_ru': 'Заполните название'}, 400
    
    current_year = datetime.now().year

    if 'year' not in film or film['year'].strip() == '' or not film['year'].isdigit():
        return {'year': 'Год должен быть числом'}, 400

    year = int(film['year'])
    if year < 1895 or year > current_year:
        return {'year': f'Введите год от 1895 до {current_year}'}, 400
        

    conn, cur = db_connect()

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("INSERT INTO films (title, title_ru, year, description) VALUES (%s, %s, %s, %s) RETURNING id;", 
                    (film['title'], film['title_ru'], film['year'], film['description']))
        new_id = cur.fetchone()['id']
        conn.commit()
    else:
        cur.execute("INSERT INTO films (title, title_ru, year, description) VALUES (?, ?, ?, ?);", 
                    (film['title'], film['title_ru'], film['year'], film['description']))

        conn.commit()
        new_id = cur.lastrowid

    db_close(conn, cur)

    return {'id': new_id}, 201