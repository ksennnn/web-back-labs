from flask import Flask, url_for, request, redirect, abort, render_template
from lab1 import lab1
from lab2 import lab2
from lab3 import lab3
import datetime

app = Flask(__name__)
app.register_blueprint(lab1)
app.register_blueprint(lab2)
app.register_blueprint(lab3)

log404 = []
@app.errorhandler(404)
def not_found(err):
    ip = request.remote_addr
    time = datetime.datetime.today()
    url = request.url

    log404.append(f"[<i>{time}</i>, пользователь <i>{ip}</i>] зашёл на адрес <i>{url}</i>")

    img_path = url_for("static", filename="/lab1/404.jpg")

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
            <li>
            <a href='/lab2'>Вторая лабораторная работа</a>
            </li>
            <li>
            <a href='/lab3'>Третья лабораторная работа</a>
            </li>
        </ol>
        </main>
        <footer>
            Ковалёва Ксения Николаевна, ФБИ-32, 3 курс, 2025
        </footer>
    </body>
</html>
'''
