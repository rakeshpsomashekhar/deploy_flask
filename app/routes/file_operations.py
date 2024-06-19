from flask import request, jsonify, current_app
from app.routes import file_ops_bp
from app.services.google_cloud import get_storage_client
from app.services.jwt_service import verify_custom_token


@file_ops_bp.route('/upload', methods=['POST'])
def upload_document():
    custom_token = request.headers.get('token')
   
    if not custom_token:
        return jsonify({'error': 'Missing custom token'}), 401
    tokenValidationResponse = verify_custom_token(custom_token)
    
    if 'error' in tokenValidationResponse:
        return jsonify(tokenValidationResponse), 401

    email = tokenValidationResponse['email']
    file = request.files['file']

    if not file:
        return jsonify({'error': 'File required'}), 422

    client = get_storage_client()
    bucket = client.bucket(current_app.config['BUCKET_NAME'])
    blob = bucket.blob(f'{email}/{file.filename}')
    blob.upload_from_file(file)
    
    return jsonify({'message': 'File uploaded successfully'})

@file_ops_bp.route('/list', methods=['GET'])
def list_documents():
    custom_token = request.headers.get('token')
    if not custom_token:
        return jsonify({'error': 'Missing custom token'}), 401

    tokenValidationResponse = verify_custom_token(custom_token)
    if 'error' in tokenValidationResponse:
        return jsonify(tokenValidationResponse), 401

    email = tokenValidationResponse['email']
    client = get_storage_client()
    bucket = client.bucket(current_app.config['BUCKET_NAME'])
    blobs = bucket.list_blobs(prefix=f'{email}/')
    documents = [blob.name.split('/')[-1] for blob in blobs]
    
    return jsonify({'documents': documents})

@file_ops_bp.route('/delete', methods=['DELETE'])
def delete_document():
    custom_token = request.headers.get('token')
    if not custom_token:
        return jsonify({'error': 'Missing custom token'}), 401

    tokenValidationResponse = verify_custom_token(custom_token)
    if 'error' in tokenValidationResponse:
        return jsonify(tokenValidationResponse), 401

    email = tokenValidationResponse['email']
    filename = request.args.get('filename')

    if not filename:
        return jsonify({'error': 'Filename required'}), 422

    client = get_storage_client()
    bucket = client.bucket(current_app.config['BUCKET_NAME'])
    blob = bucket.blob(f'{email}/{filename}')
    blob.delete()
    
    return jsonify({'message': 'File deleted successfully'})
