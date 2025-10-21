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
    resp.set_cookie('age', '20', max_age=5)
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


@lab3.route("/lab3/settings/reset")
def reset_settings():
    resp = make_response(redirect('/lab3/settings'))
    resp.delete_cookie('color')
    resp.delete_cookie('bg_color')
    resp.delete_cookie('font_size')
    resp.delete_cookie('font_family')
    return resp


@lab3.route('/lab3/products')
def products():
    items = [
        {"name": "iPhone 15", "brand": "Apple", "price": 120000, "color": "чёрный"},
        {"name": "Samsung Galaxy S23", "brand": "Samsung", "price": 95000, "color": "серебристый"},
        {"name": "Xiaomi 14", "brand": "Xiaomi", "price": 78000, "color": "синий"},
        {"name": "Google Pixel 8", "brand": "Google", "price": 88000, "color": "зелёный"},
        {"name": "OnePlus 12", "brand": "OnePlus", "price": 89000, "color": "чёрный"},
        {"name": "Nothing Phone 2", "brand": "Nothing", "price": 65000, "color": "белый"},
        {"name": "Honor Magic 6", "brand": "Honor", "price": 72000, "color": "серый"},
        {"name": "Realme GT 6", "brand": "Realme", "price": 55000, "color": "синий"},
        {"name": "Sony Xperia 1 V", "brand": "Sony", "price": 110000, "color": "фиолетовый"},
        {"name": "Asus Zenfone 10", "brand": "Asus", "price": 93000, "color": "зелёный"},
        {"name": "Huawei P60", "brand": "Huawei", "price": 81000, "color": "чёрный"},
        {"name": "Poco F6 Pro", "brand": "Poco", "price": 48000, "color": "белый"},
        {"name": "Infinix GT 20", "brand": "Infinix", "price": 41000, "color": "красный"},
        {"name": "Motorola Edge 40", "brand": "Motorola", "price": 59000, "color": "серебристый"},
        {"name": "Nokia XR21", "brand": "Nokia", "price": 52000, "color": "чёрный"},
        {"name": "Tecno Phantom X2", "brand": "Tecno", "price": 47000, "color": "оранжевый"},
        {"name": "ZTE Nubia Z60", "brand": "ZTE", "price": 76000, "color": "серый"},
        {"name": "Vivo X100", "brand": "Vivo", "price": 85000, "color": "белый"},
        {"name": "Meizu 21", "brand": "Meizu", "price": 68000, "color": "синий"},
        {"name": "Oppo Find X6", "brand": "Oppo", "price": 94000, "color": "золотой"},
    ]

    min_price_total = min(i["price"] for i in items)
    max_price_total = max(i["price"] for i in items)

    if request.args.get('reset'):
        resp = make_response(redirect('/lab3/products'))
        resp.delete_cookie('min_price')
        resp.delete_cookie('max_price')
        return resp

    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')

    if not min_price:
        min_price = request.cookies.get('min_price')
    if not max_price:
        max_price = request.cookies.get('max_price')

    try:
        min_price = int(min_price) if min_price else None
        max_price = int(max_price) if max_price else None
    except ValueError:
        min_price, max_price = None, None

    if min_price and max_price and min_price > max_price:
        min_price, max_price = max_price, min_price

    filtered = []
    for item in items:
        price = item["price"]
        if (min_price is None or price >= min_price) and (max_price is None or price <= max_price):
            filtered.append(item)

    resp = make_response(render_template(
        'lab3/products.html',
        items=filtered,
        total=len(filtered),
        min_price=min_price,
        max_price=max_price,
        min_price_total=min_price_total,
        max_price_total=max_price_total
    ))
    if min_price is not None:
        resp.set_cookie('min_price', str(min_price))
    if max_price is not None:
        resp.set_cookie('max_price', str(max_price))
    return resp
