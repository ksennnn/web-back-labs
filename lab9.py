from flask import Blueprint, render_template, session, jsonify, request
from flask_login import login_required, current_user
import json

lab9 = Blueprint('lab9', __name__)

BOX_COUNT = 10
BOX_SIZE = 120  # размер коробки в px
VIP_BOXES = {1, 2, 3}  # VIP-подарки

FIXED_POSITIONS = {
    '1': {"top": 0, "left": 100},
    '2': {"top": 0, "left": 350},
    '3': {"top": 0, "left": 600},
    '4': {"top": 0, "left": 850},
    '5': {"top": 0, "left": 1100},
    '6': {"top": 200, "left": 100},
    '7': {"top": 200, "left": 350},
    '8': {"top": 200, "left": 600},
    '9': {"top": 200, "left": 850},
    '10': {"top": 200, "left": 1100}
}

def get_user_boxes():
    if 'boxes' not in session:
        boxes = {}
        for i in range(1, BOX_COUNT + 1):
            boxes[str(i)] = {
                "opened": False,
                "text": f"Поздравление №{i}",
                "gift": f"lab9/gift{i}.jpg",
                "box": f"lab9/box{i}.png"
            }
        session['boxes'] = json.dumps(boxes)
    
    return json.loads(session['boxes'])

def save_user_boxes(boxes):
    session['boxes'] = json.dumps(boxes)

@lab9.route('/lab9')
def lab9_page():
    if 'opened_count' not in session:
        session['opened_count'] = 0
    
    boxes = get_user_boxes()
    unopened_count = sum(not box['opened'] for box in boxes.values())
    
    return render_template(
        'lab9/index.html',
        boxes=boxes,
        positions=FIXED_POSITIONS,
        unopened_count=unopened_count
    )


@lab9.route('/lab9/open', methods=['POST'])
def open_box():
    box_id = request.json['box_id']
    boxes = get_user_boxes()
    
    if int(box_id) in VIP_BOXES and not current_user.is_authenticated:
        return jsonify({"error": "Этот подарок доступен только авторизованным пользователям"})
    
    if session.get('opened_count', 0) >= 3:
        return jsonify({"error": "Вы уже открыли 3 подарка. Больше нельзя!"})
    
    if boxes[box_id]['opened']:
        return jsonify({"error": "Вы уже открыли этот подарок"})
    
    boxes[box_id]['opened'] = True
    save_user_boxes(boxes)
    session['opened_count'] = session.get('opened_count', 0) + 1
    
    unopened_count = sum(not box['opened'] for box in boxes.values())
    
    return jsonify({
        "text": boxes[box_id]['text'],
        "gift": boxes[box_id]['gift'],
        "opened_left": unopened_count,
        "user_opened_count": session['opened_count']
    })

@lab9.route('/lab9/reset', methods=['POST'])
@login_required
def reset():
    boxes = {}
    for i in range(1, BOX_COUNT + 1):
        boxes[str(i)] = {
            "opened": False,
            "text": f"Поздравление №{i}",
            "gift": f"lab9/gift{i}.jpg",
            "box": f"lab9/box{i}.png"
        }
    save_user_boxes(boxes)
    session['opened_count'] = 0
    return jsonify({"ok": True})