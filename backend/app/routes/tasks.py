from flask import Blueprint, request, render_template, url_for, redirect
from flask_login import login_required, current_user
from ..models.task import Task
from .. import db
from datetime import datetime

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("/")
@login_required
def index_task():
    filter_param = request.args.get('filter', 'all')

    if filter_param == 'active':
        tasks = Task.query.filter_by(user_id=current_user.id, completed=False).all()
    elif filter_param == 'completed':
        tasks = Task.query.filter_by(user_id=current_user.id, completed=True).all()
    else:
        tasks = Task.query.filter_by(user_id=current_user.id).all()

    total_tasks = Task.query.filter_by(user_id=current_user.id).count()
    active_tasks = Task.query.filter_by(user_id=current_user.id, completed=False).count()
    completed_tasks = Task.query.filter_by(user_id=current_user.id, completed=True).count()
    overdue_tasks = Task.query.filter(Task.user_id == current_user.id, Task.due_date < datetime.utcnow(), Task.completed == False).count()

    return render_template(
        'index.html',
        tasks=tasks,
        filter=filter_param,
        total_tasks=total_tasks,
        active_tasks=active_tasks,
        completed_tasks=completed_tasks,
        overdue_tasks=overdue_tasks
    )



@tasks_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        title = request.form.get("title", "New task")
        description = request.form.get("description", "")
        due_date_str = request.form.get("due_date")

        new_task = Task(title=title, description=description, user_id=current_user.id)

        if due_date_str:
            try:
                new_task.due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
            except ValueError:
                pass

        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('tasks.edit', task_id=new_task.id))

    due_date_str = request.args.get("due_date", "")
    return render_template("edit.html", task=None, due_date=due_date_str)

@tasks_bp.route('/<int:task_id>/edit', methods=["GET", "POST"])
@login_required
def edit(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        return "Forbidden", 403

    if request.method == "POST":
        task.title = request.form['title']
        task.description = request.form['description']
        due_date_str = request.form.get("due_date")
        if due_date_str:
            try:
                task.due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
            except ValueError:
                task.due_date = None
        else:
            task.due_date = None
        db.session.commit()
        return redirect(url_for('tasks.index_task'))

    return render_template('edit.html', task=task)


@tasks_bp.route("/complete", methods=["POST"])
@login_required
def complete():
    task_id = request.form.get("task_id")
    if not task_id:
        return "Task ID is required", 400

    task = Task.query.get(task_id)
    if not task or task.user_id != current_user.id:
        return "Task not found", 404

    task.completed = True
    db.session.commit()

    return redirect(url_for('tasks.index_task'))


@tasks_bp.route("/delete", methods=["POST"])
@login_required
def delete():
    task_id = request.form.get("task_id")
    if not task_id:
        return "Task ID is required", 400

    task = Task.query.get(task_id)
    if not task or task.user_id != current_user.id:
        return "Task not found", 404

    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('tasks.index_task'))

@tasks_bp.route('/calendar')
@login_required
def calendar():
    tasks = Task.query.filter(Task.user_id == current_user.id, Task.due_date != None).all()

    events = [
        {
            "title": task.title,
            "due_date": task.due_date.strftime("%Y-%m-%d"),
            "priority": task.priority
        }
        for task in tasks
    ]

    return render_template('calendar.html', events=events)
