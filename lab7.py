from flask import Blueprint, render_template, request, abort, redirect, session, current_app
import sqlite3
from os import path

lab7 = Blueprint('lab7', __name__)

@lab7.route('/lab7/')
def main():
    return render_template('lab7/index.html')


films = [
    {
        "title": "The Matrix",
        "title_ru": "Матрица",
        "year": 1999,
        "description": "Нео узнаёт, что мир, в котором живёт человечество, — всего лишь симуляция, \
        созданная машинами. Он вступает в сопротивление, чтобы освободить людей от цифрового рабства."
    },
    {
        "title": "Gladiator",
        "title_ru": "Гладиатор",
        "year": 2000,
        "description": "Римский генерал Максимус становится жертвой предательства и попадает в рабство. \
        Судьба делает его гладиатором, который должен бороться не только за жизнь, но и за справедливость."
    },
    {
        "title": "The Lord of the Rings: The Fellowship of the Ring",
        "title_ru": "Властелин колец: Братство кольца",
        "year": 2001,
        "description": "Фродо отправляется в опасное путешествие, чтобы уничтожить Кольцо Всевластия, \
        способное поработить весь мир Средиземья."
    },
    {
        "title": "Avatar",
        "title_ru": "Аватар",
        "year": 2009,
        "description": "Бывший морской пехотинец Джейк Салли оказывается на Пандоре, где должен выбрать \
        сторону: служить корпорации или защитить народ На'ви и их уникальный мир."
    },
    {
        "title": "The Dark Knight",
        "title_ru": "Тёмный рыцарь",
        "year": 2008,
        "description": "Бэтмен сталкивается с Джокером — преступным гением, бросающим вызов всем законам. \
        Ставки высоки: судьба Готэма и моральные границы самого героя."
    }
]


@lab7.route('/lab7/rest-api/films/<int:id>', methods=['GET'])
def get_films(id):
    if id < 0 or id >= len(films):
        abort(404) 
    return films[id]


@lab7.route('/lab7/rest-api/films/<int:id>', methods=['DELETE'])
def del_film(id):
    if id < 0 or id >= len(films):
        abort(404)
    del films[id]
    return '', 204


@lab7.route('/lab7/rest-api/films/<int:id>', methods=['PUT'])
def put_film(id):
    film = request.get_json()
    films[id] = film
    if id < 0 or id >= len(films):
        abort(404)
    return films[id]


@lab7.route('/lab7/rest-api/films/', methods=['POST'])
def add_film():
    film = request.get_json()
    films[id] = film
    return {'id': len(films) - 1}, 201