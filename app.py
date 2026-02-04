from flask import Flask, request, jsonify
from flask_login import LoginManager, login_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Usage
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/api/register", methods=["POST"])
def register():
    data = request.json

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "User exists"}), 400

    user = User(
        email=data["email"],
        password=generate_password_hash(data["password"])
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered"})

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(email=data["email"]).first()

    if not user or not check_password_hash(user.password, data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    login_user(user)
    return jsonify({"message": "Logged in"})


@app.route("/api/usage", methods=["POST"])
@login_required
def add_usage():
    data = request.json

    usage = Usage(
        remaining_data=data["remaining_data"],
        user_id=current_user.id
    )

    db.session.add(usage)
    db.session.commit()

    return jsonify({"message": "Usage saved"})


@app.route("/api/usage/latest", methods=["GET"])
@login_required
def latest_usage():
    usage = (
        Usage.query
        .filter_by(user_id=current_user.id)
        .order_by(Usage.updated_at.desc())
        .first()
    )

    if not usage:
        return jsonify({"message": "No data yet"})

    return jsonify({
        "remaining_data": usage.remaining_data,
        "updated_at": usage.updated_at.isoformat()
    })
