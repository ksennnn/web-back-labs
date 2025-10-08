from flask import Blueprint, url_for, request, redirect, abort, render_template
lab2 = Blueprint('lab2', __name__)


@lab2.route('/lab2/a')
def a1():
    return 'без слэша'


@lab2.route('/lab2/a/')
def a2():
    return 'со слэшем'


flower_list = [
    {'name': 'роза', 'price': 300},
    {'name': 'тюльпан', 'price': 310},
    {'name': 'незабудка', 'price': 320},
    {'name': 'ромашка', 'price': 330},
    {'name': 'георгин', 'price': 300},
    {'name': 'пион', 'price': 310}
]


@lab2.route('/lab2/flowers/<int:flower_id>')
def flowers(flower_id):
    if flower_id < 0 or flower_id >= len(flower_list):
        abort(404)
    else:
        flower = flower_list[flower_id] 
        all_flowers_url = url_for('lab2.all_flowers')
        return render_template('flowers.html', flower_id=flower_id, flower=flower,
        all_flowers_url=all_flowers_url)


@lab2.route('/lab2/add_flower/<name>/<int:price>')
def add_flower(name, price):
    flower_list.append({'name': name, 'price': price})
    return render_template('add_flower.html', name=name, price=price)


@lab2.route('/lab2/add_flower')
def add_flower_in():
    name = request.args.get('name')
    price = request.args.get('price', type=int)
    if not name or price is None:
        return render_template('error.html'), 404
    flower_list.append({'name': name, 'price': price})
    return redirect(url_for('lab2.all_flowers'))


@lab2.route('/lab2/flowers/all')
def all_flowers():
    return render_template('flowers_all.html', flower_list=flower_list)


@lab2.route('/lab2/clean_flower')
def clean_flower():
        flower_list.clear()
        return render_template('cleaner_flowers.html')


@lab2.route('/lab2/delete_flower/<int:flower_id>')
def delete_flower(flower_id):
    if flower_id < 0 or flower_id >= len(flower_list):
        abort(404)
    flower_list.pop(flower_id) 
    return redirect(url_for('lab2.all_flowers'))


@lab2.route('/lab2/example')
def example():
    name, number, group, kurs  = 'Ковалёва Ксения', 2, 'ФБИ-32', 3
    fruits = [
        {'name': 'яблоки', 'price': 100},
        {'name': 'груши', 'price': 120},
        {'name': 'апельсины', 'price': 80},
        {'name': 'мандарины', 'price': 95},
        {'name': 'манго', 'price': 321}
    ]
    return render_template('example.html',
                           name=name, number=number, group=group,
                           kurs=kurs, fruits=fruits)


@lab2.route('/lab2/')
def lab():
    return render_template('lab2.html')


@lab2.route('/lab2/filters')
def filters():
    phrase = 'О <b>сколько</b> <u>нам</u> <i>открытий</i> чудных...'
    return render_template('filter.html', phrase=phrase)


@lab2.route('/lab2/calc/<int:a>/<int:b>')
def calc(a, b):
    css = url_for('static', filename='main.css')
    return f'''
<!doctype html>
<html>
    <head>
        <title>Выражения</title>
    </head>
    <body>
        <h1>Расчёт с параметрами:</h1>
        <p>{a} + {b} = {a + b}</p>
        <p>{a} - {b} = {a - b}</p>
        <p>{a} × {b} = {a * b}</p>
        <p>{a} : {b} = {a / b if b != 0 else '&infin;'}</p>
        <p>{a}<sup>{b}</sup> = {a ** b}</p>
    </body>
</html>
'''


@lab2.route('/lab2/calc/')
def calc_1_1():
    return redirect('/lab2/calc/1/1')


@lab2.route('/lab2/calc/<int:a>')
def calc_a_1(a):
    return redirect(url_for('calc', a=a, b=1))


books = [
        {'author': 'Фёдор Достоевский', 'title': 'Преступление и наказание', 'genre': 'Роман', 'pages': 672},
        {'author': 'Лев Толстой', 'title': 'Война и мир', 'genre': 'Роман-эпопея', 'pages': 1225},
        {'author': 'Александр Пушкин', 'title': 'Евгений Онегин', 'genre': 'Роман в стихах', 'pages': 384},
        {'author': 'Николай Гоголь', 'title': 'Мёртвые души', 'genre': 'Роман', 'pages': 512},
        {'author': 'Иван Тургенев', 'title': 'Отцы и дети', 'genre': 'Роман', 'pages': 368},
        {'author': 'Антон Чехов', 'title': 'Вишнёвый сад', 'genre': 'Пьеса', 'pages': 96},
        {'author': 'Михаил Булгаков', 'title': 'Мастер и Маргарита', 'genre': 'Мистика', 'pages': 480},
        {'author': 'Даниил Гранин', 'title': 'Иду на грозу', 'genre': 'Роман', 'pages': 544},
        {'author': 'Александр Дюма', 'title': 'Три мушкетёра', 'genre': 'Приключения', 'pages': 640},
        {'author': 'Жюль Верн', 'title': 'Двадцать тысяч лье под водой', 'genre': 'Приключения', 'pages': 464}
]


@lab2.route('/lab2/books')
def show_books():
    return render_template('books.html', books=books)


cats = [
        {'name': 'Барсик', 'desc': 'Любит спать на подоконнике и наблюдать за птицами.', 'image': 'cat1.jpg'},
        {'name': 'Мурка', 'desc': 'Очень ласковая и мурлыкает, когда её гладят.', 'image': 'cat2.jpg'},
        {'name': 'Снежок', 'desc': 'Белоснежный кот, который обожает играть со снежинками.', 'image': 'cat3.jpg'},
        {'name': 'Черныш', 'desc': 'Чёрный как ночь, но с добрым сердцем.', 'image': 'cat4.jpg'},
        {'name': 'Рыжик', 'desc': 'Настоящий охотник за мышами.', 'image': 'cat5.jpg'},
        {'name': 'Пушок', 'desc': 'Очень пушистый и обожает сидеть на руках.', 'image': 'cat6.jpg'},
        {'name': 'Симба', 'desc': 'Главный кот в доме, любит быть в центре внимания.', 'image': 'cat7.jpg'},
        {'name': 'Милка', 'desc': 'Кошка с самыми красивыми голубыми глазами.', 'image': 'cat8.jpg'},
        {'name': 'Луна', 'desc': 'Ночная охотница и любительница уюта.', 'image': 'cat9.jpg'},
        {'name': 'Том', 'desc': 'Любит молоко и мультфильмы.', 'image': 'cat10.jpg'},
        {'name': 'Багира', 'desc': 'Грациозная, умная и немного надменная.', 'image': 'cat11.jpg'},
        {'name': 'Миша', 'desc': 'Очень активный котёнок, всегда в движении.', 'image': 'cat12.jpg'},
        {'name': 'Карамелька', 'desc': 'Милый котёнок цвета карамели.', 'image': 'cat13.jpg'},
        {'name': 'Шарик', 'desc': 'Несмотря на имя, кот, не собака.', 'image': 'cat14.jpg'},
        {'name': 'Тиша', 'desc': 'Тихий и спокойный, любит одиночество.', 'image': 'cat15.jpg'},
        {'name': 'Феликс', 'desc': 'Почти как кот из рекламы корма.', 'image': 'cat16.jpg'},
        {'name': 'Зефир', 'desc': 'Нежный и пушистый, как облачко.', 'image': 'cat17.jpg'},
        {'name': 'Соня', 'desc': 'Любит спать днём и бодрствовать ночью.', 'image': 'cat18.jpg'},
        {'name': 'Лео', 'desc': 'Маленький, но смелый как лев.', 'image': 'cat19.jpg'},
        {'name': 'Печенька', 'desc': 'Обожает лакомства и внимание.', 'image': 'cat20.jpg'},
]


@lab2.route('/lab2/cats')
def show_cats():
    return render_template('cats.html', cats=cats)