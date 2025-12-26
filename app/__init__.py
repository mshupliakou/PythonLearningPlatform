import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from flask_login import LoginManager

load_dotenv()

login_manager = LoginManager()

db = SQLAlchemy()

# app/__init__.py

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'super-secret-key'

    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    db.init_app(app)

    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    from .routes import main
    app.register_blueprint(main)

    with app.app_context():
        from . import models
        db.create_all()

    return app