from flask import Blueprint, request, jsonify
from ..models.task import Task
from .. import db

tasks_bp = Blueprint("tasks", __name__)

@tasks_bp.route("/", methods=["GET"])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([{
        "id": t.id,
        "title": t.title,
        "completed": t.completed
    } for t in tasks])

@tasks_bp.route("/", methods=["POST"])
def create_task():
    data = request.json
    task = Task(title=data["title"], description=data.get("description"))
    db.session.add(task)
    db.session.commit()
    return jsonify({"message": "Task created"}), 201
