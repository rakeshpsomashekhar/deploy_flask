from flask import request, jsonify
from app import db
from app.models import User
from app.services.jwt_service import verify_google_jwt, generate_custom_token, verify_custom_token
from app.routes import auth_bp

@auth_bp.route('/verify-oauth-token', methods=['POST'])
def verify_google_token():
    data = request.get_json()
    google_jwt = data.get('google_jwt')
    email = data.get('email')

    if not google_jwt or not email:
        return jsonify({'error': 'Missing parameters'}), 401

    validated_data = verify_google_jwt(google_jwt, email)
    if validated_data:
        token, expiration_time = generate_custom_token(email)
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(email=email, token=token, token_expiration=expiration_time)
            db.session.add(user)
        else:
            user.token = token
            user.token_expiration = expiration_time
        db.session.commit()

        return jsonify({'custom_token': token})
    else:
        return jsonify({'error': 'Invalid Google JWT token or email'}), 401

@auth_bp.route('/verify-token', methods=['POST'])
def verify_own_token():
    data = request.get_json()
    custom_token = data.get('custom_token')
    if not custom_token:
        return jsonify({'error': 'Missing custom token'}), 400

    result = verify_custom_token(custom_token)
    if 'error' in result:
        return jsonify(result), 401
    return jsonify({'email': result['email'], 'message': 'Token is valid'})
