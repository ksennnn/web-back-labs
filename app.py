from flask import Flask, url_for, request, redirect, abort, render_template
import datetime
app = Flask(__name__)

log404 = []
@app.errorhandler(404)
def not_found(err):
    ip = request.remote_addr
    time = datetime.datetime.today()
    url = request.url

    log404.append(f"[<i>{time}</i>, пользователь <i>{ip}</i>] зашёл на адрес <i>{url}</i>")

    img_path = url_for("static", filename="404.jpg")

    # формируем HTML для журнала
    log_html = "<ul style='list-style:none; padding:0;'>"
    for entry in log404:
        log_html += f"<li style='margin:5px 0; padding:10px; background:#eee; border-radius:6px;'>{entry}</li>"
    log_html += "</ul>"

    return '''
<!doctype html>
<html>
    <head>
        <meta charset="utf-8">
        <title>404 — Страница не найдена</title>
        <style>
            body {
                background-color: #f2f2f2;
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 30px;
            }
            h1 {
                font-size: 48px;
                color: #4E5754;
            }
            p {
                font-size: 20px;
                color: #333;
            }
            img {
                max-width: 500px;
                margin-top: 20px;
            }
            a {
                display: inline-block;
                margin-top: 30px;
                padding: 10px 20px;
                background-color: #4E5754;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                transition: 0.3s;
            }
            a:hover {
                background-color: #480607;
            }
            .log {
                margin-top: 40px;
                text-align: left;
                background: #fff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            .log h2 {
                color: #4E5754;
                margin-bottom: 15px;
            }
        </style>
    </head>
    <body>
        <h1>Ой! Ошибка 404</h1>
        <p>О нет, ты потерялся</p>
        <p>Твой IP: ''' + ip + '''</p>
        <p>Дата и время: ''' + str(time) + '''</p>
        <p>Вы искали: ''' + url + '''</p>
        <img src="''' + img_path + '''">
        <br>
        <a href="/">Вернуться на главную</a>

        <div class="log">
            <h2>Журнал посещений 404:</h2>
            ''' + log_html + '''
        </div>
    </body>
</html>
''', 404

@app.route("/bad_request")
def bad_request():
    return '''
<!doctype html>
<html>
    <body>
        <h1>400 — Bad Request</h1>
        <p>Сервер не может обработать запрос из-за ошибки клиента.</p>
    </body>
</html>
''', 400


@app.route("/unauthorized")
def unauthorized():
    return '''
<!doctype html>
<html>
    <body>
        <h1>401 — Unauthorized</h1>
        <p>КТО ТЫ? Для доступа требуется авторизация.</p>
    </body>
</html>
''', 401


@app.route("/payment_required")
def payment_required():
    return '''
<!doctype html>
<html>
    <body>
        <h1>402 — Payment Required</h1>
        <p>Заплати, потом иди</p>
    </body>
</html>
''', 402


@app.route("/forbidden")
def forbidden():
    return '''
<!doctype html>
<html>
    <body>
        <h1>403 — Forbidden</h1>
        <p>Доступ запрещён.</p>
    </body>
</html>
''', 403


@app.route("/method_not_allowed")
def method_not_allowed():
    return '''
<!doctype html>
<html>
    <body>
        <h1>405 — Method Not Allowed</h1>
        <p>Метод запроса не разрешён для данного ресурса.</p>
    </body>
</html>
''', 405

@app.route("/teapot")
def teapot():
    return '''
<!doctype html>
<html>
    <body>
        <h1>418 — I'm a teapot</h1>
        <p>Я — чайник. Заваривать кофе я не умею.</p>
    </body>
</html>
''', 418

@app.route("/server-error")
def server_error():
    # специально вызовем ошибку делением на ноль
    return 1 / 0  


@app.errorhandler(500)
def internal_error(err):
    return '''
<!doctype html>
<html>
    <head>
        <meta charset="utf-8">
        <title>Ошибка сервера</title>
        <style>
            body {
                background-color: #fff3f3;
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 50px;
            }
            h1 {
                font-size: 48px;
                color: #B00000;
            }
            p {
                font-size: 20px;
                color: #333;
            }
            img {
                max-width: 300px;
                margin-top: 20px;
            }
            a {
                display: inline-block;
                margin-top: 30px;
                padding: 10px 20px;
                background-color: #B00000;
                color: white;
                text-decoration: none;
                border-radius: 8px;
                transition: 0.3s;
            }
            a:hover {
                background-color: #293133;
            }
        </style>
    </head>
    <body>
        <h1>500 — Внутренняя ошибка сервера</h1>
        <p>Упс! На сервере что-то пошло не так</p>
        <p>Уже бежим исправлять.</p>
        <br>
        <a href="/">Вернуться на главную</a>
    </body>
</html>
''', 500

@app.route('/')
@app.route('/index')
def index():
    return '''
<!doctype html>
<html>
    <body>
        <header>
            НГТУ, ФБ, WEB-программирование, часть 2. Список лабораторных
        </header>
        <main>
        <ol>
            <li>
            <a href='/lab1'>Первая лабораторная</a>
            </li>
        </ol>
        </main>
        <footer>
            Ковалёва Ксения Николаевна, ФБИ-32, 3 курс, 2025
        </footer>
    </body>
</html>
'''

@app.route("/lab1/web")
def web():
    return """<!doctype html>
        <html>
           <body>
               <h1>web-сервер на flask </h1>
               <a href="/lab1/author">author</a>
           </body>
        </html>""", 200, {
            'X-Server': 'sample',
            'Content-Type': 'text/plain; charset=utf-8'
        }

@app.route("/lab1/author")
def author():
    name = "Ковалёва Ксения Николаевна"
    group = "ФБИ-32"
    faculty = "ФБ"

    return """<!doctype html>
        <html>
           <body>
               <p>Студент: """ + name + """ </p>
               <p>Группа: """ + group + """ </p>
               <p>Факультет: """ + faculty + """ </p>
               <a href="/lab1/web">web</a>
           </body>
        </html>"""

@app.route("/lab1/image")
def image():
    path = url_for("static", filename="oak.jpg")
    style_path = url_for("static", filename="lab1.css")
    return '''
<!doctype html>
<html>
    <head>
        <link rel="stylesheet" href="''' + style_path + '''">
    </head>
    <body>
        <h1>Дуб</h1>
        <img src="''' + path + '''">
    </body>
</html>
''', 200, {
    'Content-Language': 'ru',
    'Student-Name': 'Kovalyova Ksenia',
    'Lab-Number': 'Lab1'
}

count = 0

@app.route("/lab1/counter")
def counter():
    global count
    count += 1
    time = datetime.datetime.today()
    url = request.url
    client_ip = request.remote_addr

    return '''
<!doctype html>
<html>
    <body>
        Сколько раз вы сюда заходили: ''' + str(count) + '''
        <hr>
        Дата и время: ''' + str(time) + '''<br>
        Запрошенный адрес: ''' + url + '''<br>
        Ваш IP-адрес: ''' + client_ip + '''<br>
        <hr>
        <a href="/counter/reset">Сбросить счётчик</a>
    </body>
</html>
'''

@app.route("/counter/reset")
def reset_counter():
    global count
    count = 0
    return redirect("/lab1/counter")

@app.route("/lab1/info")
def info():
    return redirect("/lab1/author")

@app.route("/lab1/created")
def created():
    return '''
<!doctype html>
<html>
    <body>
        <h1>Создано успешно</h1>
        <div><i>что-то создано...</i></div>
    </body>
</html>
''', 201

@app.route('/lab1')
def lab1():
    return '''
<!doctype html>
<html>
    <head>
        <title>Лабораторная 1</title>
    </head>
    <body>
        <p>
            Flask — фреймворк для создания веб-приложений на языке программирования Python,
            использующий набор инструментов Werkzeug, а также шаблонизатор Jinja2.
            Относится к категории так называемых микрофреймворков — минималистичных каркасов
            веб-приложений, сознательно предоставляющих лишь самые базовые возможности.
        </p>
        <a href='/'>Вернуться на главную страницу</a>
        <h2>Список роутов</h2>
        <ul>
            <li>
                <a href='/lab1/web'>Web-serber на Flask</a>
            </li>
            <li>
                <a href='/lab1/image'>Картинка</a>
            </li>
            <li>
                <a href='/lab1/author'>Автор</a>
            </li>
            <li>
                <a href='/lab1/counter'>Счетчик</a>
            </li>
            <li>
                <a href='/lab1/info'>Перенаправление</a>
            </li>
            <li>
                <a href='/lab1/created'>Код ответа 201</a>
            </li>
            <li>
                <a href='/bad_request'>Ошибка 400</a>
            </li>
            <li>
                <a href='/unauthorized'>Ошибка 401</a>
            </li>
            <li>
                <a href='/payment_required'>Ошибка 402</a>
            </li>
            <li>
                <a href='/forbidden'>Ошибка 403</a>
            </li>
            <li>
                <a href='/lab1/oops'>Ошибка 404</a>
            </li>
            <li>
                <a href='/method_not_allowed'>Ошибка 405</a>
            </li>
            <li>
                <a href='/teapot'>Ошибка 418</a>
            </li>
            <li>
                <a href='/server-error'>Ошибка 500</a>
            </li>
    </body>
</html>
'''
@app.route('/lab2/a')
def a1():
    return 'без слэша'

@app.route('/lab2/a/')
def a2():
    return 'со слэшем'

flower_list = ['роза', 'тюльпан', 'незабудка', 'ромашка']
@app.route('/lab2/flowers/<int:flower_id>')
def flowers(flower_id):
    if flower_id >= len(flower_list):
        abort(404)
    else:
        flower = flower_list[flower_id] 
        all_flowers_url = url_for('all_flowers')
        return render_template('flowers.html', flower_id=flower_id, flower=flower,
        all_flowers_url=all_flowers_url)

@app.route('/lab2/add_flower/<name>')
def add_flower(name):
    flower_list.append(name)
    return f'''
<!doctype html>
<html>
    <body>
        <h1>Добавлен новый цветок</h1>
        <p>Название нового цветка: {name}</p>
        <p>Всего цветов: {len(flower_list)}</p>
        <a href="/lab2/flowers/all">Полный список</a>
    </body>
</html>
'''

@app.route('/lab2/add_flower/')
def add_flower_error():
    return '''
<!doctype html>
<html>
    <body>
        <h1>Вы не задали имя цветка<h1>
    </body>
</html>
''', 400

@app.route('/lab2/flowers/all')
def all_flowers():
    return f'''
<!doctype html>
<html>
    <body>
        <p>Количество цветов: {len(flower_list)}</p>
        <p>Список цветов:</p>
        <ul>
            {''.join(f'<li>{flower}</li>' for flower in flower_list)}
        </ul>
        <a href="/lab2/clean_flower">Очистить список цветов</a>
    </body>
</html>
'''

@app.route('/lab2/clean_flower')
def f_cleaner():
        global flower_list
        flower_list = []
        return '''
<!doctype html>
<html>
    <body>
        <p>Список цветов очищен</p>
        <a href="/lab2/flowers/all">К списку цветов</a>
    </body>
</html>
'''

@app.route('/lab2/example')
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

@app.route('/lab2/')
def lab2():
    return render_template('lab2.html')

@app.route('/lab2/filters')
def filters():
    phrase = 'О <b>сколько</b> <u>нам</u> <i>открытий</i> чудных...'
    return render_template('filter.html', phrase=phrase)

@app.route('/lab2/calc/<int:a>/<int:b>')
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

@app.route('/lab2/calc/')
def calc_1_1():
    return redirect('/lab2/calc/1/1')

@app.route('/lab2/calc/<int:a>')
def calc_a_1(a):
    return redirect(url_for('calc', a=a, b=1))