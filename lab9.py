from flask import Blueprint, render_template, session, jsonify, request
from flask_login import login_required, current_user
import random

lab9 = Blueprint('lab9', __name__)


BOX_COUNT = 10
BOX_SIZE = 120  # размер коробки в px
VIP_BOXES = {1, 2, 3}  # VIP-подарки

congratulate = {
    1: "Пусть под ёлкой в Новый год, Вас удача поджидает! И весь год, как на блюдечке, Всё желаемое достает!",
    2: "Желаю, чтобы в новом году каждый день был наполнен волшебством и чудесами, а снежинки приносили только радость!",
    3: "Пусть Дед Мороз положит под ёлку не только подарки, но и море счастья, здоровья и любви!",
    4: "Пусть свечи на праздничном столе освещают путь к удаче, а бой курантов принесёт исполнение самых заветных желаний!",
    5: "Пусть звезда, что загорится на верхушке ёлки, осветит весь следующий год только яркими и счастливыми событиями!",
    6: "Желаю, чтобы шампанское в новогоднюю ночь было игривым, как настроение, и бодрым, как первый день года!",
    7: "Пусть олени Санты принесут вам не только подарки, но и море позитива на весь предстоящий год!",
    8: "Желаю, чтобы борода Деда Мороза всегда была пушистой, а мешок с подарками — бесконечно глубоким именно для вас!",
    9: "Пусть бенгальские огни зажгут в душе искорки счастья, которые будут греть вас весь следующий год!",
    10: "Поднимаю бокал за то, чтобы снег за окном был только для красоты, а дороги — всегда чистыми и ведущими к успеху!"
}

# состояние коробок
boxes = {
    i: {
        "opened": False,
        "text": congratulate[i],
        "gift": f"lab9/gift{i}.jpg",
        "box": f"lab9/box{i}.png"
    }
    for i in range(1, BOX_COUNT + 1)
}

# Фиксированные позиции для каждой коробки
FIXED_POSITIONS = {
    1: {"top": 0, "left": 150},
    2: {"top": 0, "left": 330},
    3: {"top": 0, "left": 610},
    4: {"top": 0, "left": 950},
    5: {"top": 0, "left": 1200},
    6: {"top": 250, "left": 200},
    7: {"top": 250, "left": 480},
    8: {"top": 250, "left": 740},
    9: {"top": 250, "left": 920},
    10: {"top": 250, "left": 1200}
}

@lab9.route('/lab9')
def lab9_page():
    session.setdefault('opened_count', 0)

    positions = FIXED_POSITIONS.copy()

    unopened_count = sum(not b['opened'] for b in boxes.values())
    return render_template(
        'lab9/index.html',
        boxes=boxes,
        positions=positions,
        unopened_count=unopened_count
    )


@lab9.route('/lab9/open', methods=['POST'])
def open():
    box_id = int(request.json['box_id'])

    if box_id in VIP_BOXES and not current_user.is_authenticated:
        return jsonify({"error": "Этот подарок доступен только авторизованным пользователям"})

    if session.get('opened_count', 0) >= 3:
        return jsonify({"error": "Можно открыть не более 3 подарков"})

    if boxes[box_id]['opened']:
        return jsonify({"error": "Этот подарок уже забрали"})

    boxes[box_id]['opened'] = True
    session['opened_count'] += 1

    return jsonify({
        "text": boxes[box_id]['text'],
        "gift": boxes[box_id]['gift'],
        "opened_left": sum(not b['opened'] for b in boxes.values())
    })

@lab9.route('/lab9/reset', methods=['POST'])
@login_required
def reset():
    for box in boxes.values():
        box['opened'] = False
    session['opened_count'] = 0
    return jsonify({"ok": True})