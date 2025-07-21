from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from .models.user import User  
    from .routes.tasks import tasks_bp, page
    from .auth.routes import auth_bp

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(page)
    app.register_blueprint(tasks_bp, url_prefix="/api/tasks")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    return app
