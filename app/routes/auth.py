import datetime as dt
from flask import request, jsonify

from app import db
from app.models import User, UserLoginHistory, UserProfile
from app.services.jwt_service import verify_google_jwt, generate_custom_token, verify_custom_token
from app.routes import auth_bp
from flask import current_app

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
            user = User(
                email=email,
                first_name=validated_data.get('given_name'),
                last_name=validated_data.get('family_name'),
                created_datetime=dt.datetime.utcnow(),
                created_by='google_oauth',
                user_type='holcim'
            )
            db.session.add(user)
            db.session.flush()
            user_profile = UserProfile(
                user_id=user.id,
                language=current_app.config['LANGUAGE'], 
                application_theme=current_app.config['APPLICATION_THEME'],
                is_speech=current_app.config['IS_SPEECH'],
                is_mic=current_app.config['IS_MIC'],
                is_holcim_data=current_app.config['IS_HOLCIM_DATA'],
                is_my_library=current_app.config['IS_MY_LIBRARY'],
                is_custom_copilot=current_app.config['IS_CUSTOM_COPILOT'],
                converse_style= current_app.config['CONVERSE_STYLE'],
                custom_instruction= current_app.config['CUSTOM_INSTRUCTION'],
                created_datetime=current_app.config['CREATED_DATETIME'],
                created_by=current_app.config['CREATED_BY']
            )
            db.session.add(user_profile)
        else:
            login_history = UserLoginHistory(
                user_id=user.id,
                login_datetime=dt.datetime.utcnow(),
                login_success=True,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent')
            )
            db.session.add(login_history)
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


