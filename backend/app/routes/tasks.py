from flask import Blueprint, request, jsonify, render_template
from ..models.task import Task
from .. import db

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route('/')
def home():
    """Home page that displays all tasks"""
    tasks = Task.query.all()
    return render_template("base.html", tasks=tasks)


@tasks_bp.route("/tasks", methods=["GET"])
def get_tasks():
    """API endpoint to get all tasks as JSON"""
    tasks = Task.query.all()
    return jsonify([{
        "id": t.id,
        "title": t.title,
        "completed": t.completed
    } for t in tasks])


@tasks_bp.route("/tasks", methods=["POST"])
def create_task():
    """API endpoint to create a new task"""
    data = request.json
    if not data or "title" not in data:
        return jsonify({"error": "Title is required"}), 400

    task = Task(title=data["title"], description=data.get("description"))
    db.session.add(task)
    db.session.commit()

    return jsonify({
        "message": "Task created",
        "task": {
            "id": task.id,
            "title": task.title,
            "completed": task.completed
        }
    }), 201