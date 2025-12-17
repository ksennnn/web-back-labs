from flask import Blueprint, render_template, session, jsonify, request
from flask_login import login_required, current_user
import json
import uuid

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
    # Для анонимных пользователей создаем уникальный идентификатор сессии
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())[:8]  # короткий уникальный ID
    
    user_key = f"boxes_{session['user_id']}"
    
    if user_key not in session:
        boxes = {}
        for i in range(1, BOX_COUNT + 1):
            boxes[str(i)] = {
                "opened": False,
                "text": f"Поздравление №{i}",
                "gift": f"lab9/gift{i}.jpg",
                "box": f"lab9/box{i}.png"
            }
        session[user_key] = json.dumps(boxes)
    
    return json.loads(session[user_key])

def save_user_boxes(boxes):
    user_key = f"boxes_{session['user_id']}"
    session[user_key] = json.dumps(boxes)

def get_user_opened_count():
    user_key = f"opened_count_{session['user_id']}"
    return session.get(user_key, 0)

def set_user_opened_count(count):
    user_key = f"opened_count_{session['user_id']}"
    session[user_key] = count

@lab9.route('/lab9')
def lab9_page():
    # Инициализируем user_id для анонимных пользователей
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())[:8]
    
    boxes = get_user_boxes()
    unopened_count = sum(not box['opened'] for box in boxes.values())
    opened_count = get_user_opened_count()
    
    return render_template(
        'lab9/index.html',
        boxes=boxes,
        positions=FIXED_POSITIONS,
        unopened_count=unopened_count,
        user_opened_count=opened_count
    )


@lab9.route('/lab9/open', methods=['POST'])
def open_box():
    try:
        data = request.get_json()
        if not data or 'box_id' not in data:
            return jsonify({"error": "Неверный запрос"}), 400
        
        box_id = str(data['box_id'])
        boxes = get_user_boxes()
        opened_count = get_user_opened_count()
        
        print(f"DEBUG: User {session['user_id']} trying to open box {box_id}, opened count: {opened_count}")
        
        # Проверка на VIP-коробку для неавторизованных пользователей
        if int(box_id) in VIP_BOXES and not current_user.is_authenticated:
            return jsonify({"error": "Этот подарок доступен только авторизованным пользователям"})
        
        # Проверка лимита открытий для текущего пользователя
        if opened_count >= 3:
            return jsonify({"error": "Вы уже открыли 3 подарка. Больше нельзя!"})
        
        # Проверка, не открыта ли уже эта коробка данным пользователем
        if boxes[box_id]['opened']:
            return jsonify({"error": "Вы уже открыли этот подарок"})
        
        # Открываем коробку
        boxes[box_id]['opened'] = True
        save_user_boxes(boxes)
        
        new_opened_count = opened_count + 1
        set_user_opened_count(new_opened_count)
        
        unopened_count = sum(not box['opened'] for box in boxes.values())
        
        print(f"DEBUG: Success! New opened count: {new_opened_count}")
        
        return jsonify({
            "text": boxes[box_id]['text'],
            "gift": boxes[box_id]['gift'],
            "opened_left": unopened_count,
            "user_opened_count": new_opened_count
        })
    
    except Exception as e:
        print(f"ERROR in open_box: {str(e)}")
        return jsonify({"error": f"Внутренняя ошибка сервера: {str(e)}"}), 500

@lab9.route('/lab9/reset', methods=['POST'])
@login_required
def reset():
    try:
        # Для авторизованных пользователей используем их ID
        user_id = str(current_user.id)
        user_key = f"boxes_{user_id}"
        opened_key = f"opened_count_{user_id}"
        
        boxes = {}
        for i in range(1, BOX_COUNT + 1):
            boxes[str(i)] = {
                "opened": False,
                "text": f"Поздравление №{i}",
                "gift": f"lab9/gift{i}.jpg",
                "box": f"lab9/box{i}.png"
            }
        
        session[user_key] = json.dumps(boxes)
        session[opened_key] = 0
        
        return jsonify({"ok": True})
    
    except Exception as e:
        print(f"ERROR in reset: {str(e)}")
        return jsonify({"error": f"Внутренняя ошибка сервера: {str(e)}"}), 500