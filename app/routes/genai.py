from flask import request, jsonify
from app.routes import genai_bp
from app.services.genai_service import genaiChatVertexCall, get_web_search
from app.services.jwt_service import verify_custom_token

@genai_bp.route('/chat', methods=['POST'])
def genai_chat():
    custom_token = request.headers.get('token')
    if not custom_token:
        return jsonify({'error': 'Missing custom token'}), 401

    tokenValidationResponse = verify_custom_token(custom_token)
    if 'error' in tokenValidationResponse:
        return jsonify(tokenValidationResponse), 401

    data = request.get_json()
    message = data.get('message')
    temperature = data.get('temperature')

    if not message or not message.strip() or not temperature:
        return jsonify({'error': 'Invalid input'}), 422

    email = tokenValidationResponse['email']
    response = genaiChatVertexCall(message, temperature)

    return jsonify({'response': response})
