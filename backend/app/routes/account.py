from flask import Blueprint, render_template, redirect, url_for, request, current_app, jsonify
from flask_login import current_user, login_required
from ..models.task import Task
from werkzeug.utils import secure_filename
from PIL import Image, ImageOps, ImageDraw
from .. import db
import os

acc_bp = Blueprint("account", __name__, template_folder="templates")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@acc_bp.route('/upload-avatar', methods=['POST'])
@login_required
def upload_avatar():
    if 'avatar' not in request.files:
        return redirect(url_for('account.profile'))

    file = request.files['avatar']
    if file.filename == '':
        return redirect(url_for('account.profile'))

    if file and allowed_file(file.filename):
        filename = secure_filename(f"{current_user.id}_avatar.png")
        upload_path = os.path.join(current_app.static_folder, 'avatars')
        os.makedirs(upload_path, exist_ok=True)
        filepath = os.path.join(upload_path, filename)


        img = Image.open(file).convert("RGBA")


        size = (256, 256)
        img = ImageOps.fit(img, size, Image.LANCZOS)


        mask = Image.new("L", size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0) + size, fill=255)


        img.putalpha(mask)


        img.save(filepath, format="PNG")


        current_user.avatar_url = url_for('static', filename=f'avatars/{filename}', _external=False)
        db.session.commit()

    return redirect(url_for('account.profile'))

@acc_bp.route('/profile')
@login_required
def profile():

    tasks = (
        Task.query
        .filter_by(user_id=current_user.id)
        .order_by(Task.created_at.desc())
        .limit(20)
        .all()
    )

    recent_activity = []

    for task in tasks:

        recent_activity.append({
            "icon": "🆕",
            "text": f"Create new task «{task.title}»",
            "date": task.created_at
        })


        if task.completed:
            recent_activity.append({
                "icon": "✅",
                "text": f"Complete task «{task.title}»",
                "date": task.due_date if task.due_date else task.created_at
            })


    recent_activity.sort(key=lambda x: x["date"], reverse=True)

    return render_template(
        'profile.html',
        user=current_user,
        recent_activity=recent_activity[:5]
    )


@acc_bp.route('/update_appearance', methods=['POST'])
@login_required
def update_appearance():
    theme = request.json.get('theme')
    font_size = request.json.get('font_size')
    density = request.json.get('density')

    # Сохраняем в модель пользователя
    current_user.theme = theme
    current_user.font_size = font_size
    current_user.density = density
    db.session.commit()

    return jsonify({"status": "ok"})