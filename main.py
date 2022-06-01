from copy import copy, deepcopy
from flask import Flask, jsonify, request
import sqlalchemy
import db_session
from models import User
import uuid
import json


app = Flask(__name__)
db_session.global_init("data.db")
session = db_session.create_session()

def hash_passw(passw):
    new_passw = ""
    for char in passw:
        value = ord(char)
        if value % 2 == 0:
            new_char = value % 10 * 24 + value // 10
        else:
            new_char = value % 10 * 24 + value // 10
        new_passw += chr(new_char)
    return new_passw


def get_achievements():
    import json
    json_data = open("achievements.json", "r").read().replace("\n", "")
    return json_data


g_achievements = get_achievements()


def update_achievements():
    global g_achievements
    g_achievements = get_achievements()
    for userinfo in session.query(User).all():
        cur_achievements = json.loads(userinfo.achievements)
        new_achievements = deepcopy(g_achievements)
        new_achievements = {key: (key in cur_achievements and cur_achievements[key])
                           for key in json.loads(new_achievements).keys()}
        userinfo.achievements = json.dumps(new_achievements)
    session.commit()


@app.route("/login", methods=["POST"])
def login():
    json_data = request.json
    if "passw" not in json_data or "email" not in json_data:
        return jsonify({
            "status": 0,
            "msg": "Missed out 'passw' and 'email'"
        })
    email = json_data['email']
    passw = json_data['passw']
    userinfo = session.query(User).filter(((User.email == email) and
                                           (User.hashed_password == passw))).first()
    if userinfo is None:
        return jsonify({
            "status": 0,
            "msg": "Wrong passw and email"
        })
    sid = str(uuid.uuid4())
    userinfo.sid = sid
    session.commit()
    
    return jsonify({
        "status": 1,
        "msg": sid
    })


@app.route("/signup", methods=["POST"])
def signup():
    json_data = request.json
    if not all(key in json_data 
               for key in ["name", "email", "passw"]):
        return jsonify({
            "status": 0,
            "msg": "Missed out 'name', 'email' or 'passw'"
        })
    name = json_data['name']
    email = json_data['email']
    passw = json_data['passw']
    
    userinfo = User()
    try:
        userinfo.email = email
        if session.query(User).filter(User.email == email).first(): raise Exception
        userinfo.hashed_password = hash_passw(passw)
        userinfo.name = name
        userinfo.achievements = deepcopy(g_achievements)
        session.add(userinfo)
        session.commit()
    except Exception:
        return jsonify({
            "status": 0,
            "msg": "This email already exists"
        })
    return jsonify({
        "status": 1,
        "msg": "You successfuly signed up"
    })


@app.route("/update", methods=["POST"])
def update():
    update_achievements()
    return jsonify({"status": 1, "msg": "Successfuly updated!"})


@app.route("/achievements", methods=["GET"])
def achievements_():
    usersinfo = session.query(User).all()
    return jsonify({
        "status": 1,
        "data": [{"name": user.name, "achievements": json.loads(user.achievements)}
                 for user in usersinfo]
    })


@app.route("/achievement", methods=["GET", "PUT"])
def achievements():
    if request.method == "GET":
        json_data = request.json
        if "sid" not in json_data:
            return jsonify({
                "status": 0,
                "msg": "Missed out key 'sid'"
            })
        user = session.query(User).filter(User.sid == json_data['sid']).first()
        if not user:
            return jsonify({
                "status": 0,
                "msg": "Wrong 'sid' value, doesn't exist"
            })
        return jsonify({
            "status": 1,
            "data": json.loads(user.achievements)
        })
    elif request.method == "PUT":
        json_data = request.json
        if "sid" not in json_data or "achieve" not in json_data:
            return jsonify({
                "status": 0,
                "msg": "Missed out key 'sid' or 'achieve'"
            })
        achieve = json_data['achieve']
        if achieve not in g_achievements:
            return jsonify({
                "status": 0,
                "msg": "Wrong achieve name"
            })
        user = session.query(User).filter(User.sid == json_data['sid']).first()
        if not user:
            return jsonify({
                "status": 0,
                "msg": "Wrong 'sid' value, doesn't exist"
            })
        achievs = json.loads(user.achievements)
        achievs[achieve] = True
        user.achievements = json.dumps(achievs)
        session.commit()
        return jsonify({
            "status": 1,
            "msg": "Successfuly changed"
        })


app.run(host="127.0.0.1", port=8000)
