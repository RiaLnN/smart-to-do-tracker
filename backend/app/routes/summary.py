from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user, login_required
from ..services.insights import generate_summary
from ..models.task import Task

summary_bp = Blueprint("summary", __name__)

@summary_bp.route('/')
@login_required
def summary():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    summary = generate_summary(tasks)

    return render_template(
        'summary.html',
        tasks=tasks,
        summary=summary
    )