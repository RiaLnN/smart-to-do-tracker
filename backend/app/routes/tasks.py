from flask import Blueprint, request, jsonify, render_template, url_for, redirect
from flask_login import login_required
from ..models.task import Task
from .. import db

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("/")
def index():
    tasks = Task.query.filter_by(completed=False).all()
    return render_template("index.html", tasks=tasks)


@tasks_bp.route("/tasks")
def index_task():
    return render_template("task.html")


@tasks_bp.route("/add", methods=["POST"])
def add():
    title = request.form['title']
    description = request.form['description']
    task = Task(title=title, description=description)
    db.session.add(task)
    db.session.commit()
    return redirect(url_for('tasks.index'))

@tasks_bp.route("/complete_task")
def complete_task():
    tasks = Task.query.all()
    return render_template("complete.html", tasks=tasks)

@tasks_bp.route("/description", methods=["GET"])
def description():
    task_id = request.args.get("task_id")
    if not task_id:
        return "Task ID is required", 400
    task = Task.query.get(task_id)
    if not task:
        return "Task not found", 404
    return render_template("description.html", task=task)

@tasks_bp.route("/complete", methods=["POST"])
def complete():
    task_id = request.form.get("task_id")  # get task id from form data
    if not task_id:
        return "Task ID is required", 400

    # Find the task by id
    task = Task.query.get(task_id)
    if not task:
        return "Task not found", 404

    # Mark it as completed
    task.completed = True

    # Save changes to the database
    db.session.commit()

    return redirect(url_for('tasks.index'))


@tasks_bp.route("/delete", methods=["POST"])
def delete():
    task_id = request.form.get("task_id")  # get task id from form data
    if not task_id:
        return "Task ID is required", 400

    # Find the task by id
    task = Task.query.get(task_id)
    if not task:
        return "Task not found", 404

    # Delete the task
    db.session.delete(task)
    db.session.commit()

    return redirect(url_for('tasks.index'))


# @tasks_bp.route("/tasks", methods=["GET"])
# def get_tasks():
#     """API endpoint to get all tasks as JSON"""
#     tasks = Task.query.all()
#     return jsonify([{
#         "id": t.id,
#         "title": t.title,
#         "completed": t.completed
#     } for t in tasks])
#
# @tasks_bp.route("/tasks", methods=["POST"])
# def create_task():
#     """API endpoint to create a new task"""
#     data = request.json
#     if not data or "title" not in data:
#         return jsonify({"error": "Title is required"}), 400
#
#     task = Task(title=data["title"], description=data.get("description"))
#     db.session.add(task)
#     db.session.commit()
#
#     return jsonify({
#         "message": "Task created",
#         "task": {
#             "id": task.id,
#             "title": task.title,
#             "completed": task.completed
#         }
#     }), 201