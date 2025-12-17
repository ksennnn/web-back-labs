from flask import Blueprint, render_template, session, jsonify, request
from flask_login import login_required, current_user
import random

lab9 = Blueprint('lab9', __name__)


BOX_COUNT = 10
BOX_SIZE = 120  # размер коробки в px
VIP_BOXES = {1, 2, 3}  # VIP-подарки

# состояние коробок
boxes = {
    i: {
        "opened": False,
        "text": f"Поздравление №{i}",
        "gift": f"lab9/gift{i}.jpg",
        "box": f"lab9/box{i}.png"
    }
    for i in range(1, BOX_COUNT + 1)
}

# Фиксированные позиции для каждой коробки
FIXED_POSITIONS = {
    1: {"top": 0, "left": 70},
    2: {"top": 0, "left": 320},
    3: {"top": 0, "left": 570},
    4: {"top": 0, "left": 820},
    5: {"top": 0, "left": 1070},
    6: {"top": 250, "left": 100},
    7: {"top": 250, "left": 350},
    8: {"top": 250, "left": 600},
    9: {"top": 250, "left": 850},
    10: {"top": 250, "left": 1100}
}

@lab9.route('/lab9')
def lab9_page():
    session.setdefault('opened_count', 0)

    # Всегда используем фиксированные позиции
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