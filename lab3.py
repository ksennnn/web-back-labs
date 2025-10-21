from flask import Blueprint, render_template, request, make_response, redirect
lab3 = Blueprint('lab3', __name__)


@lab3.route('/lab3/')
def lab():
    name = request.cookies.get('name')
    name_color = request.cookies.get('name_color')
    age = request.cookies.get('age')
    return render_template('lab3/lab3.html', name=name, name_color=name_color, age=age)


@lab3.route('/lab3/cookie')
def cookie():
    resp = make_response(redirect('/lab3'))
    resp.set_cookie('name', 'Alex', max_age=5)
    resp.set_cookie('age', '20')
    resp.set_cookie('name_color', 'magenta')
    return resp


@lab3.route('/lab3/del_cookie')
def del_cookie():
    resp = make_response(redirect('/lab3/'))
    resp.delete_cookie('name')
    resp.delete_cookie('age')
    resp.delete_cookie('name_color')
    return resp


@lab3.route('/lab3/form1')
def form1():
    errors = {}
    user = request.args.get('user')
    if user == '':
        errors['user'] = 'Заполните поле!'
    
    age = request.args.get('age')
    if age == '':
        errors['age'] = 'Заполните поле!'

    sex = request.args.get('sex')
    return render_template('lab3/form1.html', user=user, age=age, sex=sex, errors=errors)


@lab3.route('/lab3/order')
def order():
    return render_template('lab3/order.html')


@lab3.route('/lab3/pay')
def pay():
    price = 0
    drink = request.args.get('drink')
    if drink == 'coffee':
        price = 120
    elif drink == 'black-tea' :
        price = 80
    else:
        price = 70
    
    if request.args.get('milk') == 'on':
        price += 30
    if request.args.get('sugar') == 'on':
        price += 10

    return render_template('lab3/pay.html', price=price)


@lab3.route('/lab3/success')
def success():
    price = request.args.get('price', 0)
    return render_template('lab3/success.html', price=price)


@lab3.route('/lab3/settings')
def settings():
    color = request.args.get('color')
    bg_color = request.args.get('bg_color')
    font_size = request.args.get('font_size')
    font_family = request.args.get('font_family')

    if any([color, bg_color, font_size, font_family]):
        resp = make_response(redirect('/lab3/settings'))
        if color:
            resp.set_cookie('color', color)
        if bg_color:
            resp.set_cookie('bg_color', bg_color)
        if font_size:
            resp.set_cookie('font_size', font_size)
        if font_family:
            resp.set_cookie('font_family', font_family)
        return resp

    color = request.cookies.get('color')
    bg_color = request.cookies.get('bg_color')
    font_size = request.cookies.get('font_size')
    font_family = request.cookies.get('font_family')

    return render_template('lab3/settings.html', color=color, bg_color=bg_color, font_size=font_size,
                           font_family=font_family)


@lab3.route('/lab3/ticket')
def ticket():
    fio = request.args.get('fio')
    polka = request.args.get('polka')
    belie = request.args.get('belie') == 'on'
    bagazh = request.args.get('bagazh') == 'on'
    age = request.args.get('age')
    viezd = request.args.get('viezd')
    naznachenie = request.args.get('naznachenie')
    data = request.args.get('data')
    strahovka = request.args.get('strahovka') == 'on'

    if not fio:
        return render_template('/lab3/train_form.html')
    if age:
        age_int = int(age)
    else:
        age_int = 0

    if age_int < 18:
        base_price = 700
    else:
        base_price = 1000
    
    if polka == 'bottom' or polka == 'bottom-bok':
        polka_price = 100
    else:
        polka_price = 0
    
    total_price = base_price + polka_price
    if belie:
        total_price += 75
    if bagazh:
        total_price += 250
    if strahovka:
        total_price += 150
    return render_template('/lab3/train_ticket.html', fio=fio, polka=polka, belie=belie, bagazh=bagazh, age=age_int, 
                        viezd=viezd, naznachenie=naznachenie, data=data, strahovka=strahovka, base_price=base_price,
                        polka_price=polka_price, total_price=total_price)