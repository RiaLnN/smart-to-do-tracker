from .. import db
from datetime import datetime

class Task(db.Model):
    __tablename__ = "task"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime)
    completed = db.Column(db.Boolean, default=False)
    priority = db.Column(db.String(10))  # e.g. High/Medium/Low
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
