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
    from .models.task import Task  # Import Task model
    from .routes.tasks import tasks_bp
    from .auth.routes import auth_bp
    from .routes.main import main_bp

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(main_bp)
    app.register_blueprint(tasks_bp, url_prefix='/tasks')
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    # Create database tables
    with app.app_context():
        db.create_all()

    return app