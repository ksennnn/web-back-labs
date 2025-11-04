from flask import Blueprint, render_template, request, redirect, session
lab4 = Blueprint('lab4', __name__)


@lab4.route('/lab4/')
def lab():
    return render_template('lab4/lab4.html')


@lab4.route('/lab4/div-form')
def div_form():
    return render_template('lab4/div-form.html')


@lab4.route('/lab4/div', methods=['POST'])
def div():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    if x1 == '' or x2 == '':
        return render_template('lab4/div.html', error='Оба поля должны быть заполнены!')
    x1 = int(x1)
    x2 = int(x2)
    if x2 == 0:
        return render_template('lab4/div.html', error='На ноль делить нельзя!')
    result = x1 / x2
    return render_template('lab4/div.html', x1=x1, x2=x2, result=result)


@lab4.route('/lab4/sum-form')
def sum_form():
    return render_template('lab4/sumform.html')


@lab4.route('/lab4/sum', methods = ['POST'])
def sum():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    if x1 == '':
        x1 = 0
    else:
        x1 = int(x1) 
    if x2 == '':
        x2 = 0
    else:
        x2 = int(x2)
    result = x1 + x2
    return render_template('lab4/sum.html', x1=x1, x2=x2, result=result)


@lab4.route('/lab4/mul-form')
def mul_form():
    return render_template('lab4/mulform.html')


@lab4.route('/lab4/mul', methods = ['POST'])
def mul():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    if x1 == '':
        x1 = 1
    else:
        x1 = int(x1) 
    if x2 == '':
        x2 = 1
    else:
        x2 = int(x2)
    result = x1 * x2
    return render_template('lab4/mul.html', x1=x1, x2=x2, result=result)


@lab4.route('/lab4/sub-form')
def sub_form():
    return render_template('lab4/subform.html')


@lab4.route('/lab4/sub', methods = ['POST'])
def sub():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    if x1 == '' or x2 == '':
        return render_template('lab4/sub.html', error='Оба поля должны быть заполнены!')
    x1 = int(x1)
    x2 = int(x2)
    result = x1 - x2
    return render_template('lab4/sub.html', x1=x1, x2=x2, result=result)


@lab4.route('/lab4/exp-form')
def exp_form():
    return render_template('lab4/expform.html')


@lab4.route('/lab4/exp', methods = ['POST'])
def exp():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    if x1 == '' or x2 == '':
        return render_template('lab4/exp.html', error='Оба поля должны быть заполнены!')
    x1 = int(x1)
    x2 = int(x2)
    if x1 == 0 and x2 == 0 :
        return render_template('lab4/exp.html', error='Оба поля не могут быть равны 0!')
    result = x1 ** x2
    return render_template('lab4/exp.html', x1=x1, x2=x2, result=result)


tree_count = 0

@lab4.route('/lab4/tree', methods = ['GET','POST'])
def tree():
    global tree_count
    if request.method == 'GET':
        return render_template('lab4/tree.html', tree_count=tree_count)
    
    operation = request.form.get('operation')

    if operation == 'cut':
        if tree_count > 0:
            tree_count -= 1
    elif operation == 'plant':
        if tree_count < 8:
            tree_count += 1
        
    return redirect('/lab4/tree')


users = [
    {'login': 'alex', 'password': '123', 'name': 'Алекс', 'gender': 'м'},
    {'login': 'bob', 'password': '555', 'name': 'Боб', 'gender': 'м'},
    {'login': 'ksenia', 'password': '456', 'name': 'Ксения', 'gender': 'ж'},
    {'login': 'sofi', 'password': '789', 'name': 'София', 'gender': 'ж'},
    {'login': 'mira', 'password': '000', 'name': 'Мира', 'gender': 'ж'},
]

@lab4.route('/lab4/login', methods = ['GET','POST'])
def login():
    if request.method == 'GET':
        if 'login' in session:
            authorized=True
            name = ''
            gender = ''
            for user in users:
                if user['login'] == session['login']:
                    name = user['name']
                    gender = user['gender']
                    break
        else:
            authorized=False
            name = ''
            gender = ''
        return render_template("lab4/login.html", authorized=authorized, name=name, gender=gender)
    
    login = request.form.get('login')
    password = request.form.get('password')

    if not login and not password:
        error = 'Не введён логин и пароль!'
        return render_template('lab4/login.html', error=error, authorized=False, login=login)
    if not login:
        error = 'Не введён логин!'
        return render_template('/lab4/login.html', error=error, authorized=False, login=login)
    
    if not password:
        error = 'Не введён пароль!'
        return render_template('/lab4/login.html', error=error, authorized=False, login=login)

    authorized = False
    for user in users:
        if login == user['login'] and password == user['password']:
            session['login'] = login
            session['name'] = user['name']
            authorized = True
            break

    if authorized:
        return redirect('/lab4/users')
    else:
        error = 'Неверные логин и/или пароль!'
        return render_template('lab4/login.html', error=error, authorized=False, login=login)

@lab4.route('/lab4/logout', methods = ['POST'])
def logout():
    session.pop('login', None)
    session.pop('name', None)
    return redirect('/lab4/login')

@lab4.route('/lab4/register', methods=['GET','POST'])
def register():
    error = ''
    if request.method == 'POST':
        login_form = request.form.get('login')
        name = request.form.get('name')
        gender = request.form.get('gender')
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        if not login_form or not name or not password or not confirm or not gender:
            error = 'Все поля обязательны'
        elif password != confirm:
            error = 'Пароли не совпадают'
        else:
            login_exists = False
            for u in users:
                if u['login'] == login_form:
                    login_exists = True
                    break
            if login_exists:
                error = 'Такой логин уже существует'
            else:
                users.append({
                    'login': login_form,
                    'password': password,
                    'name': name,
                    'gender': gender
                })
                session['login'] = login_form
                session['name'] = name
                return redirect('/lab4/users')

    return render_template('lab4/register.html', error=error)


@lab4.route('/lab4/users', methods=['GET'])
def user_list():
    if 'login' not in session:
        return redirect('/lab4/login')
    return render_template('lab4/users.html', users=users, current_login=session['login'])


@lab4.route('/lab4/users/edit', methods=['GET','POST'])
def edit_user():
    if 'login' not in session:
        return redirect('/lab4/login')

    current_user = None
    for u in users:
        if u['login'] == session['login']:
            current_user = u
            break
    if not current_user:
        return redirect('/lab4/login')

    error = ''
    if request.method == 'POST':
        login_form = request.form.get('login')
        name = request.form.get('name')
        gender = request.form.get('gender')
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        if not login_form or not name or not gender:
            error = 'Логин, имя и пол не могут быть пустыми'
        elif password != confirm:
            error = 'Пароли не совпадают'
        else:
            login_exists = False
            for u in users:
                if u['login'] == login_form and u != current_user:
                    login_exists = True
                    break
            if login_exists:
                error = 'Такой логин уже существует'
            else:
                current_user['login'] = login_form
                current_user['name'] = name
                current_user['gender'] = gender
                if password:
                    current_user['password'] = password
                session['login'] = login_form
                session['name'] = name
                return redirect('/lab4/users')

    return render_template('lab4/edit_user.html', user=current_user, error=error)


@lab4.route('/lab4/users/delete', methods=['POST'])
def delete_user():
    if 'login' not in session:
        return redirect('/lab4/login')

    for i, u in enumerate(users):
        if u['login'] == session['login']:
            users.pop(i)
            break

    session.pop('login', None)
    session.pop('name', None)
    return redirect('/lab4/login')

@lab4.route('/lab4/fridge', methods=['GET', 'POST'])
def fridge():
    if request.method == 'GET':
        return render_template('lab4/fridge.html')
    
    temp = request.form.get('temperature')
    mess = ''
    snowflakes = 0
    temperature = ''

    if temp == '':
        mess = 'Ошибка: не задана температура'
    else:
        temperature = int(temp)

        if temperature < -12:
            mess = 'Не удалось установить температуру — слишком низкое значение'
        elif temperature > -1:
            mess = 'Не удалось установить температуру — слишком высокое значение'
        elif -12 <= temperature <= -9:
            mess = f'Установлена температура: {temperature}°C'
            snowflakes = 3
        elif -8 <= temperature <= -5:
            mess = f'Установлена температура: {temperature}°C'
            snowflakes = 2
        elif -4 <= temperature <= -1:
            mess = f'Установлена температура: {temperature}°C'
            snowflakes = 1

    return render_template('lab4/fridge.html', mess=mess, snowflakes=snowflakes, temperature=temperature)


@lab4.route('/lab4/grain', methods=['GET', 'POST'])
def grain():
    message = ''
    zerno = ''
    weight = ''
    total_price = 0
    discount = 0
    prices = {
        'ячмень': 12000,
        'овёс': 8500,
        'пшеница': 9000,
        'рожь': 15000
    }

    if request.method == 'GET':
        return render_template('lab4/zerno.html')

    zerno = request.form.get('zerno')
    weight_str = request.form.get('weight')

    if not weight_str:
        message = 'Ошибка: не указан вес'
        return render_template('lab4/zerno.html', message=message)

    weight = float(weight_str)

    if weight <= 0:
        message = 'Ошибка: вес должен быть больше 0'
    elif weight > 100:
        message = 'Ошибка: такого объёма сейчас нет в наличии'
    else:
        if zerno not in prices:
            message = 'Ошибка: выберите тип зерна'
        else:
            price_per_ton = prices[zerno]
            total_price = price_per_ton * weight

            if weight > 10:
                discount = total_price * 0.1
                total_price -= discount
                message = (f'Заказ успешно сформирован.Вы заказали {zerno}. Вес: {weight} т. '
                           f'Сумма к оплате: {total_price:.2f} руб. '
                           f'<br>Применена скидка 10% за большой объём (скидка: {discount:.2f} руб).')
            else:
                message = (f'Заказ успешно сформирован. Вы заказали {zerno}. Вес: {weight} т. '
                           f'Сумма к оплате: {total_price:.2f} руб.')

    return render_template('lab4/zerno.html', message=message, zerno=zerno, weight=weight)
