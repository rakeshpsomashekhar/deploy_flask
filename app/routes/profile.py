import datetime as dt
from flask import request, jsonify

from app import db
from app.models import User
from app.routes import profile_bp
from app.services.jwt_service import verify_custom_token

@profile_bp.route('/profile', method=['GET'])
def get_profile():
    custom_token = request.headers.get('token')
    if not custom_token:
        return jsonify({'error': 'Missing custom token'}), 401

    token_validation_response = verify_custom_token(custom_token)
    if 'error' in token_validation_response:
        return jsonify(token_validation_response), 401

    email = token_validation_response['email']
    user = User.query.filter_by(email=email).first()

    if not user or not user.user_profile:
        return jsonify({'error': 'Profile not found'}), 404

    profile = user.user_profile
    profile_data = {
        'language': profile.language,
        'application_theme': profile.application_theme,
        'is_speech': profile.is_speech,
        'is_mic': profile.is_mic,
        'is_holcim_data': profile.is_holcim_data,
        'is_my_library': profile.is_my_library,
        'is_custom_copilot': profile.is_custom_copilot,
        'converse_style': profile.converse_style,
        'custom_instruction': profile.custom_instruction,
    }

    return jsonify(profile_data)

@profile_bp.route('/profile', methods=['PUT'])
def update_profile():
    custom_token = request.headers.get('token')
    if not custom_token:
        return jsonify({'error': 'Missing custom token'}), 401

    token_validation_response = verify_custom_token(custom_token)
    if 'error' in token_validation_response:
        return jsonify(token_validation_response), 401

    email = token_validation_response['email']
    user = User.query.filter_by(email=email).first()

    if not user or not user.user_profile:
        return jsonify({'error': 'Profile not found'}), 404

    profile = user.user_profile
    data = request.json

    if 'language' in data:
        profile.language = data['language']
    
    if 'application_theme' in data:
        profile.application_theme = data['application_theme']

    if 'is_speech' in data:
        profile.is_speech = data['is_speech']

    if 'is_mic' in data:
        profile.is_mic = data['is_mic']

    if 'is_holcim_data' in data:
        profile.is_holcim_data = data['is_holcim_data']

    if 'is_my_library' in data:
        profile.is_my_library = data['is_my_library']

    if 'is_custom_copilot' in data:
        profile.is_custom_copilot = data['is_custom_copilot']

    if 'converse_style' in data:
        profile.converse_style = data['converse_style']

    if 'custom_instruction' in data:
        profile.custom_instruction = data['custom_instruction']

    profile.modified_datetime = dt.datetime.utcnow()
    profile.modified_by = 'user'

    db.session.commit()

    return jsonify({'message': 'Profile updated successfully'})