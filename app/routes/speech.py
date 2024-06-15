from flask import request, jsonify
from app.routes import speech_bp
from app.services.google_cloud import transcribe_speech, synthesize_speech
from app.services.jwt_service import verify_custom_token

@speech_bp.route('/stt', methods=['POST'])
def speech_to_text():
    custom_token = request.headers.get('token')
    if not custom_token:
        return jsonify({'error': 'Missing custom token'}), 401

    tokenValidationResponse = verify_custom_token(custom_token)
    if 'error' in tokenValidationResponse:
        return jsonify(tokenValidationResponse), 401

    audio_file = request.files['file']
    text = transcribe_speech(audio_file.read())
    
    return jsonify({'text': text})

@speech_bp.route('/tts', methods=['POST'])
def text_to_speech():
    custom_token = request.headers.get('token')
    if not custom_token:
        return jsonify({'error': 'Missing custom token'}), 401

    tokenValidationResponse = verify_custom_token(custom_token)
    if 'error' in tokenValidationResponse:
        return jsonify(tokenValidationResponse), 401

    data = request.get_json()
    text = data.get('text')
    audio_content = synthesize_speech(text)
    
    return jsonify({'audio_content': audio_content})
