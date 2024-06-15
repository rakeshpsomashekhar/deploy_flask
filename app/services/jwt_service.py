import jwt
import datetime
from google.oauth2 import id_token
from google.auth.transport import requests
from flask import current_app

def verify_google_jwt(google_jwt, email):
    try:
        idinfo = id_token.verify_oauth2_token(google_jwt, requests.Request())
        if idinfo['email'] == email:
            return idinfo
    except Exception as e:
        return None

def generate_custom_token(email):
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=current_app.config['TOKEN_EXPIRATION_MINUTES'])
    token = jwt.encode({'email': email, 'exp': expiration_time}, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token, expiration_time

def verify_custom_token(token):
    try:
        data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return {'email': data['email']}
    except jwt.ExpiredSignatureError:
        return {'error': 'Token expired'}
    except jwt.InvalidTokenError:
        return {'error': 'Invalid token'}
