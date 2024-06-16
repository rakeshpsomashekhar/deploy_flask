from sqlalchemy import Enum
from datetime import datetime

from app import db

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    last_login_datetime = db.Column(db.DateTime)
    created_datetime = db.Column(db.DateTime, default=datetime.utcnow)
    modified_datetime = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(255))
    modified_by = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    deactivated_at = db.Column(db.DateTime)
    deactivated_by = db.Column(db.String(255))
    user_type = db.Column(db.String(255))

    login_history = db.relationship('UserLoginHistory', backref='user', lazy=True)
    user_profile = db.relationship('UserProfile', backref='user', lazy=True, uselist=False)

class UserLoginHistory(db.Model):
    __tablename__ = 'user_login_history'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    login_datetime = db.Column(db.DateTime, default=datetime.utcnow)
    login_success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.String(255))
    ip_address = db.Column(db.String(45))  # IPv6 length
    user_agent = db.Column(db.String(255))

class UserProfile(db.Model):
    __tablename__ = 'user_profile'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    language = db.Column(db.String(255))
    application_theme = db.Column(db.String(255))
    is_speech = db.Column(db.Boolean, default=False)
    is_mic = db.Column(db.Boolean, default=False)
    is_holcim_data = db.Column(db.Boolean, default=False)
    is_my_library = db.Column(db.Boolean, default=False)
    is_custom_copilot = db.Column(db.Boolean, default=False)
    converse_style = db.Column(db.String(255))
    custom_instruction = db.Column(db.String(255))
    created_datetime = db.Column(db.DateTime, default=datetime.utcnow)
    modified_datetime = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(255))
    modified_by = db.Column(db.String(255))

    my_library = db.relationship('MyLibrary', backref='user_profile', lazy=True)

class MyLibrary(db.Model):
    __tablename__ = 'my_library'
    
    id = db.Column(db.Integer, primary_key=True)
    user_profile_id = db.Column(db.Integer, db.ForeignKey('user_profile.id'), nullable=False)
    document_name = db.Column(db.String(255))
    document_description = db.Column(db.String(255))
    is_selected = db.Column(db.Boolean, default=False)
    is_processed = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)
    created_datetime = db.Column(db.DateTime, default=datetime.utcnow)
    modified_datetime = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.String(255))
    modified_by = db.Column(db.String(255))
    deleted_by = db.Column(db.String(255))
    processed_datetime = db.Column(db.DateTime)
    deleted_datetime = db.Column(db.DateTime)
