from .. import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(20), nullable=False)
    avatar_url = db.Column(db.String(255), nullable=True)
    tasks = db.relationship("Task", backref="user", lazy=True)

    def __repr__(self):
        return f"<User {self.email}>"
