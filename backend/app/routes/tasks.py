from flask import Blueprint, request, render_template, url_for, redirect, jsonify
from flask_login import login_required, current_user
from ..models.task import Task
from .. import db
from datetime import datetime, timedelta

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("/")
@login_required
def index_task():
    filter_param = request.args.get('filter', 'all')

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    urgent_deadline = today_start + timedelta(days=1)

    query = Task.query.filter_by(user_id=current_user.id)
    if filter_param == 'active':
        query = query.filter_by(completed=False)
    elif filter_param == 'completed':
        query = query.filter_by(completed=True)

    tasks = query.all()

    total_tasks = Task.query.filter_by(user_id=current_user.id).count()
    active_tasks = Task.query.filter_by(user_id=current_user.id, completed=False).count()
    completed_tasks = Task.query.filter_by(user_id=current_user.id, completed=True).count()
    overdue_tasks = Task.query.filter(
        Task.user_id == current_user.id,
        Task.completed == False,
        Task.due_date != None,
        Task.due_date < datetime.utcnow()
    ).count()

    for t in tasks:
        t.is_urgent = (
                (t.priority == 'High') or
                (t.due_date and t.due_date <= urgent_deadline)
        )

    return render_template(
        'index.html',
        tasks=tasks,
        filter=filter_param,
        total_tasks=total_tasks,
        active_tasks=active_tasks,
        completed_tasks=completed_tasks,
        overdue_tasks=overdue_tasks
    )


# AJAX endpoint для получения задач
@tasks_bp.route("/api/tasks")
@login_required
def api_get_tasks():
    filter_param = request.args.get('filter', 'all')

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    urgent_deadline = today_start + timedelta(days=1)

    query = Task.query.filter_by(user_id=current_user.id)
    if filter_param == 'active':
        query = query.filter_by(completed=False)
    elif filter_param == 'completed':
        query = query.filter_by(completed=True)

    tasks = query.all()

    # Статистика
    total_tasks = Task.query.filter_by(user_id=current_user.id).count()
    active_tasks = Task.query.filter_by(user_id=current_user.id, completed=False).count()
    completed_tasks = Task.query.filter_by(user_id=current_user.id, completed=True).count()
    overdue_tasks = Task.query.filter(
        Task.user_id == current_user.id,
        Task.completed == False,
        Task.due_date != None,
        Task.due_date < datetime.utcnow()
    ).count()

    tasks_data = []
    for task in tasks:
        is_urgent = (
                (task.priority == 'High') or
                (task.due_date and task.due_date <= urgent_deadline)
        )

        tasks_data.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'completed': task.completed,
            'due_date': task.due_date.strftime('%d.%m.%Y') if task.due_date else None,
            'priority': task.priority,
            'is_urgent': is_urgent
        })

    return jsonify({
        'tasks': tasks_data,
        'stats': {
            'total_tasks': total_tasks,
            'active_tasks': active_tasks,
            'completed_tasks': completed_tasks,
            'overdue_tasks': overdue_tasks
        }
    })


@tasks_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        # Проверяем, это AJAX запрос или обычный
        if request.content_type == 'application/json':
            data = request.get_json()
            title = data.get("title", "New Task")
            description = data.get("description", "")
            due_date_str = data.get("due_date")
            priority = data.get("priority") or None
        else:
            title = request.form.get("title", "New Task")
            description = request.form.get("description", "")
            due_date_str = request.form.get("due_date")
            priority = request.form.get("priority") or None

        new_task = Task(title=title, description=description, user_id=current_user.id, priority=priority)

        if due_date_str:
            try:
                new_task.due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
            except ValueError:
                pass

        db.session.add(new_task)
        db.session.commit()

        # AJAX ответ
        if request.content_type == 'application/json':
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            urgent_deadline = today_start + timedelta(days=1)
            is_urgent = (
                    (new_task.priority == 'High') or
                    (new_task.due_date and new_task.due_date <= urgent_deadline)
            )

            return jsonify({
                'success': True,
                'task': {
                    'id': new_task.id,
                    'title': new_task.title,
                    'description': new_task.description,
                    'completed': new_task.completed,
                    'due_date': new_task.due_date.strftime('%d.%m.%Y') if new_task.due_date else None,
                    'priority': new_task.priority,
                    'is_urgent': is_urgent
                }
            })

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
        # Проверяем, это AJAX запрос или обычный
        if request.content_type == 'application/json':
            data = request.get_json()
            task.title = data.get('title', task.title)
            task.description = data.get('description', task.description)
            due_date_str = data.get("due_date")
            task.priority = data.get("priority") or None
        else:
            task.title = request.form['title']
            task.description = request.form['description']
            due_date_str = request.form.get("due_date")
            task.priority = request.form.get("priority") or None

        if due_date_str:
            try:
                task.due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
            except ValueError:
                task.due_date = None
        else:
            task.due_date = None

        db.session.commit()

        # AJAX ответ
        if request.content_type == 'application/json':
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            urgent_deadline = today_start + timedelta(days=1)
            is_urgent = (
                    (task.priority == 'High') or
                    (task.due_date and task.due_date <= urgent_deadline)
            )

            return jsonify({
                'success': True,
                'task': {
                    'id': task.id,
                    'title': task.title,
                    'description': task.description,
                    'completed': task.completed,
                    'due_date': task.due_date.strftime('%d.%m.%Y') if task.due_date else None,
                    'priority': task.priority,
                    'is_urgent': is_urgent
                }
            })

        return redirect(url_for('tasks.index_task'))

    return render_template('edit.html', task=task)


@tasks_bp.route('/<int:task_id>/description')
@login_required
def description(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        return "Forbidden", 403
    return render_template('description.html', task=task)


@tasks_bp.route("/complete", methods=["POST"])
@login_required
def complete():
    # Поддержка как JSON, так и form данных
    if request.content_type == 'application/json':
        task_id = request.get_json().get("task_id")
    else:
        task_id = request.form.get("task_id")

    if not task_id:
        if request.content_type == 'application/json':
            return jsonify({'success': False, 'error': 'Task ID is required'}), 400
        return "Task ID is required", 400

    task = Task.query.get(task_id)
    if not task or task.user_id != current_user.id:
        if request.content_type == 'application/json':
            return jsonify({'success': False, 'error': 'Task not found'}), 404
        return "Task not found", 404

    task.completed = True
    db.session.commit()

    if request.content_type == 'application/json':
        return jsonify({'success': True, 'task_id': task.id})

    return redirect(url_for('tasks.index_task'))


@tasks_bp.route("/delete", methods=["POST"])
@login_required
def delete():
    # Поддержка как JSON, так и form данных
    if request.content_type == 'application/json':
        task_id = request.get_json().get("task_id")
    else:
        task_id = request.form.get("task_id")

    if not task_id:
        if request.is_json:
            return jsonify({'success': False, 'error': 'Task ID is required'}), 400
        return "Task ID is required", 400

    task = Task.query.get(task_id)
    if not task or task.user_id != current_user.id:
        if request.content_type == 'application/json':
            return jsonify({'success': False, 'error': 'Task not found'}), 404
        return "Task not found", 404

    db.session.delete(task)
    db.session.commit()

    if request.content_type == 'application/json':
        return jsonify({'success': True, 'task_id': int(task_id)})

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