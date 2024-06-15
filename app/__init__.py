from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
migrate = Migrate()

from app.config import Config
from app.routes import auth_bp, file_ops_bp, genai_bp, speech_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(file_ops_bp, url_prefix='/file')
    app.register_blueprint(genai_bp, url_prefix='/genai')
    app.register_blueprint(speech_bp, url_prefix='/speech')

    return app
