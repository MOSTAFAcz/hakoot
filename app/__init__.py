from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_login import LoginManager

from config import Config

db = SQLAlchemy()
socketio = SocketIO()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    socketio.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "login"

    from app import models
    from app.routes import register_routes
    from app.socket_events import register_socket_events

    register_routes(app)
    register_socket_events(socketio)

    with app.app_context():
        db.create_all()

    return app


@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return db.session.get(User, int(user_id))