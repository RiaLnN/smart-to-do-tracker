from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from ..models.user import User
from .. import db

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    hashed_pw = generate_password_hash(data["password"])
    user = User(email=data["email"], password=hashed_pw)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Registered successfully"})

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(email=data["email"]).first()
    if user and check_password_hash(user.password, data["password"]):
        session["user_id"] = user.id
        return jsonify({"message": "Login successful"})
    return jsonify({"message": "Invalid credentials"}), 401
