from datetime import datetime, timedelta
from flask import Flask, request, jsonify, make_response
import requests, os, tempfile, mimetypes, jwt, json, vertexai, time
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import texttospeech
from vertexai.language_models._language_models import ChatModel, TextGenerationModel
from google.oauth2 import service_account
from flask_cors import CORS
import google.oauth2.id_token
import concurrent.futures
from genai import get_ctx, get_genai_params
from google.cloud import storage


history_users={}

app = Flask(__name__)
CORS(app)
#DANTE TEST
cors = CORS(app, resources={r"/*": {"origins": "*"}})

TOKEN_EXPIRATION_MINUTES = 1400
HISTORY_TOKEN_EXPIRATION_MINUTES = 120
SECRET_KEY = '@ndsdwesdsd'
PROJECT_ID = 'e3fsf34fdf'
BUCKET_NAME = 'dvfeeec'



def get_storage_client():
    return storage.Client(project=PROJECT_ID)

@app.route('/upload', methods=['POST'])
def upload_document():
    
    custom_token = request.headers.get('token')
    print("token : ",custom_token)
    if not (custom_token and (custom_token in history_users)):
        print("token has expired so you will be logged out: ",history_users)
        return jsonify({'error': 'Missing custom token'}), 401

    tokenValidationResponse = verify_custom_token(custom_token)
    print("tokenValidationResponse", tokenValidationResponse)
    if 'error' in tokenValidationResponse:
        return jsonify(tokenValidationResponse), 401

    # DO NOT LISTEN EMAIL FROM REQUEST. INSTEAD USE IT FROM APP CUSTOM TOKEN
    email = request.form.get('email')
    file = request.files['file']

    _, path = tempfile.mkstemp()
    with open(path, 'wb') as f:
        f.write(file.read())
    filetype = mimetypes.guess_type(path)
    print("filetype === ", filetype)

    if email and file:
        client = get_storage_client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(f'{email}/{file.filename}')
        file.seek(0)
        blob.upload_from_file(file)
        return jsonify({'message': 'File uploaded successfully','filetype': filetype})
    
    return jsonify({'error': 'Email and file required'}), 422

@app.route('/list', methods=['GET'])
def list_documents():
     # DO NOT LISTEN EMAIL FROM REQUEST. INSTEAD USE IT FROM APP CUSTOM TOKEN
    custom_token = request.headers.get('token')
    print("token : ",custom_token)
    if not (custom_token and (custom_token in history_users)):
        print("token has expired so you will be logged out: ",history_users)
        return jsonify({'error': 'Missing custom token'}), 401

    tokenValidationResponse = verify_custom_token(custom_token)
    print("tokenValidationResponse", tokenValidationResponse)
    if 'error' in tokenValidationResponse:
        return jsonify(tokenValidationResponse), 401

    email = request.args.get('email')

    if email:
        client = get_storage_client()
        bucket = client.bucket(BUCKET_NAME)
        blobs = bucket.list_blobs(prefix=email + '/')
        documents = [blob.name.split('/')[-1] for blob in blobs]
        return jsonify({'documents': documents})

    return jsonify({'error': 'Email required'}), 422

@app.route('/delete', methods=['DELETE'])
def delete_document():
     # DO NOT LISTEN EMAIL FROM REQUEST. INSTEAD USE IT FROM APP CUSTOM TOKEN
    
    custom_token = request.headers.get('token')
    print("token : ",custom_token)
    if not (custom_token and (custom_token in history_users)):
        print("token has expired so you will be logged out: ",history_users)
        return jsonify({'error': 'Missing custom token'}), 401
    
    tokenValidationResponse = verify_custom_token(custom_token)
    print("tokenValidationResponse", tokenValidationResponse)
    if 'error' in tokenValidationResponse:
        return jsonify(tokenValidationResponse), 401

    email = request.args.get('email')
    filename = request.args.get('filename')
    print("file to be deleted is ===== ", filename)

    if email and filename:
        client = get_storage_client()
        bucket = client.bucket(BUCKET_NAME)
        delfile = str(f'{email}/{filename}')  # filename = str(f'{email}/{file}')
        print("file to be delfile is ===== ", delfile)
        blob = bucket.blob(delfile)
        #blob = bucket.blob(f'{email}/{filename}')
        blob.delete()
        return jsonify({'message': 'File deleted successfully'})
    
    return jsonify({'error': 'Email and filename required'}), 422

# @app.route('/chat-stt', methods=['POST'])
# def speech_to_text():
#     print("We are in stt function====")
#     audio_file = request.files['file']

#     client = speech.SpeechClient()
#     audio = speech.RecognitionAudio(content=audio_file.read())

#     config = speech.RecognitionConfig(
#         encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
#         language_code='en-US'
#     )

#     response = client.recognize(config=config, audio=audio)

#     text = ""
#     for result in response.results:
#         text += result.alternatives[0].transcript
#     print("Text tanscript ======", text)
#     return jsonify({'text': text})


@app.route('/chat-stt', methods=['POST'])
def speech_to_text():
    print("We are in stt function====")
    start = time.time()

    custom_token = request.headers.get('token')
    
    if not (custom_token and (custom_token in history_users)):
        print("token has expired so you will be logged out: ",history_users)
        return jsonify({'error': 'Missing custom token'}), 401
    
   
    tokenValidationResponse = verify_custom_token(custom_token)
    print("tokenValidationResponse", tokenValidationResponse)
    if 'error' in tokenValidationResponse:
        return jsonify(tokenValidationResponse), 401

    audio_file = request.files['file'].read()

    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(content=audio_file)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code="en-US",
        audio_channel_count=2,
        enable_separate_recognition_per_channel=False,
    )

    response = client.recognize(config=config, audio=audio)
    print("Response from Google STT : ", response.results)
    
    text = ""
    for result in response.results:
        text = result.alternatives[0].transcript
    end = time.time()

    return jsonify({'text': text})

@app.route('/chat-tts', methods=['POST'])
def text_to_speech():
    print("We are in chat-tts function====")
    custom_token = request.headers.get('token')
    
    if not (custom_token and (custom_token in history_users)):
        print("token has expired so you will be logged out: ",history_users)
        return jsonify({'error': 'Missing custom token'}), 401
    
   
    tokenValidationResponse = verify_custom_token(custom_token)
    print("tokenValidationResponse", tokenValidationResponse)
    if 'error' in tokenValidationResponse:
        return jsonify(tokenValidationResponse), 401
        
    text = request.json.get('text', '')

    tts_client = texttospeech.TextToSpeechClient()
    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code='en-US',
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    tts_response = tts_client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    print("Just before returning the audio file")
    return tts_response.audio_content, 200, {'Content-Type': 'audio/mpeg'}



def verify_google_jwt(google_jwt, email):
    """
    Consumed verify google jwt with googleapi and return profile info
    """
    google_token_info_url = f'https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={google_jwt}'
    response = requests.get(google_token_info_url)

    if response.status_code == 200:
        token_info = response.json()
        if token_info.get('email') == email:
            return token_info
    return False


@app.route('/verify-oauth-token', methods=['POST'])
def verify_google_token():
    """
    Verify provided google_jwt with provided email
    """
    print("request recevied")
    data = request.get_json()
    google_jwt = data.get('google_jwt')
    email = data.get('email')

    if not google_jwt or not email:
        return jsonify({'error': 'Missing parameters'}), 401

    validated_data = verify_google_jwt(google_jwt, email)
    if validated_data:
        # added expiry details
        expiration_time = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRATION_MINUTES)
        user_history_expiration_time = datetime.utcnow() + timedelta(minutes=HISTORY_TOKEN_EXPIRATION_MINUTES)
        # Create your own JWT token
        payload = {
            'email': email,
            'name': validated_data.get('given_name'),
            'exp': expiration_time
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        if token not in history_users:
            history_users[token] = validated_data
            history_users[token]['exp_time'] = user_history_expiration_time


        return jsonify({'custom_token': token})
    else:
        return jsonify({'error': 'Invalid Google JWT token or email'}), 401


@app.route('/verify-token', methods=['POST'])
def verify_own_token():
    """
    verify custom token
    """
    data = request.get_json()
    custom_token = data.get('custom_token')
    if not custom_token:
        return jsonify({'error': 'Missing custom token'}), 400
    try:
        decoded = jwt.decode(custom_token, SECRET_KEY, algorithms=['HS256'])
        email = decoded.get('email')

        # compare exp value with current timestamp
        if decoded.get('exp') < datetime.utcnow().timestamp():
            # raise expired error if exp is less than current time
            raise jwt.ExpiredSignatureError
        return jsonify({'email': email, 'message': 'Token is valid'})
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401

@app.route('/genai-chat', methods=['POST'])
def genai_chat():
    start = time.time()
    global history_users

    print("genai chat started")
    parameters = {
        "chat_temp":0.2,
        "chat_max_d":1024,
        "chat_top_p":1.0,
        "chat_top_k":40,
        "context": """ You are an expert providing accurate, clear and concise answers. If the query appears to be asking about Holcim information in any way, please reply:'For more information on Holcim please visit http://holcim.com'. """,
        "ws_context":"""You are an AI assistant for answering questions on extracts of documents. Only use the documents extracts to find the answer, if the extracts do not contain the asnwer say : 'I do not have this information' If the answer includes figures you must use the exact figures contained in the list of documents. To answer the question you must not use any data outside of the document extracts passed as context """
   
    }
   
    data = request.get_json()
    custom_token = request.headers.get('token')
    
    if not (custom_token and (custom_token in history_users)):
        print("token has expired so you will be logged out: ",history_users)
        return jsonify({'error': 'Missing custom token'}), 401
    
   
    tokenValidationResponse = verify_custom_token(custom_token)
    print("tokenValidationResponse", tokenValidationResponse)
    if 'error' in tokenValidationResponse:
        return jsonify(tokenValidationResponse), 401

    message = data.get('message')
    if not(message and message.strip()):
        return jsonify("Invalid input from the user. Please enter a valid question."),200

    temperature = data.get('temperature')
    if not temperature or (temperature > 1) or (temperature < 0):
        return jsonify({'error': 'Invalid temperature'}), 422

    context = data.get('context')
    if not(context and context.strip()):
        context = parameters['context']

    print("message : ", message)
    print("temperature : ", temperature)
    print("context : ", context)
   
    # cm = init_chat()
    ch = history_users.get(custom_token, {}).get('chat', [])
    print("chat history : ", ch)
    path = "chat"
    with concurrent.futures.ThreadPoolExecutor() as executor:
        t1 = executor.submit(genaiChatVertexCall, path, message, custom_token, context,temperature,parameters["chat_max_d"],parameters["chat_top_k"],parameters["chat_top_p"], ch)
        t2 = executor.submit(get_web_search, message)

    # print("Thread 1 : ", t1.result())
    print("Thread 2:::::::: : ", t2.result())
    end = time.time()
    print("Normal chat response time (ms) : ", 1000 * (end - start))

    if ('please visit http://holcim.com' in t1.result()) or ('holcim' in message.lower()):
        print("step-1, sub-1")
        if ('error' in t2.result()):
            print("step-1, sub-2")
            response = (jsonify({"message":str(t1.result()),"status":"success"},200))
            return response
        else:
            print("step-1, sub-3")
            response = (jsonify({"message":str(t2.result()),"status":"success"},200))
            return response
    elif ('error' in t2.result()):
        print("step-1, sub-2")
        response = (jsonify({"message":str(t1.result()),"status":"success"},200))
        return response
    elif 'Session not found for provided token' in t1.result():
        print("step-2, sub-1")
        return jsonify({"msg":"Session not found for provided token"}), 401
    elif not(str(t1.result()) and str(t1.result()).strip()):
        print("step-3, sub-1")
        response = (jsonify({"message":str(t2.result()),"status":"success"},200))
        return response
    elif not(str(t2.result()) and str(t2.result()).strip()):
        print("step-4, sub-1")
        response = (jsonify({"message":str(t1.result()),"status":"success"},200))
        return response
    else:
        print("step-5, sub-1")
        response = (jsonify({"message":str(t1.result()),"status":"success"},200))
        return response


  

@app.route('/genai-content-chat', methods=['POST'])
def genai_content_chat():
    start = time.time()
    global history_users
    print("genai content chat started")
    parameters = {
        "chat_temp":0.2,
        "chat_max_d":2048,
        "chat_top_p":1.0,
        "chat_top_k":40,
        "context": """ You are an expert providing accurate, clear and concise answers. If the query appears to be asking about Holcim information in any way, please reply:'For more information on Holcim please visit http://holcim.com'. """,
        "ws_context":"""You are an AI assistant for answering questions on extracts of documents. Only use the documents extracts to find the answer, if the extracts do not contain the asnwer say : 'I do not have this information' If the answer includes figures you must use the exact figures contained in the list of documents. To answer the question you must not use any data outside of the document extracts passed as context """
    }
   
    data = request.get_json()
    custom_token = request.headers.get('token')
    print("token : ",custom_token)

    if not (custom_token and (custom_token in history_users)):
        print("token has expired so you will be logged out: ",history_users)
        return jsonify({'error': 'Missing custom token'}), 401
    
    tokenValidationResponse = verify_custom_token(custom_token)
    if 'error' in tokenValidationResponse:
        return jsonify(tokenValidationResponse), 401
       
    message = data.get('message')
    if not(message and message.strip()):
        return jsonify("Invalid input from the user. Please enter a valid question."),200

    temperature = data.get('temperature')
    if not temperature or (temperature > 1) or (temperature < 0):
        return jsonify({'error': 'Invalid temperature'}), 422
       

    context = data.get('context')
    if not(context and context.strip()):
        context = parameters['context']
    
    print("message : ", message)
    print("temperature : ", temperature)
    print("context : ", context)
   
    # cm = init_chat()
    ch = history_users.get(custom_token, {}).get('content-chat', [])
    print("chat history : ", ch)
    path = "content-chat"

    with concurrent.futures.ThreadPoolExecutor() as executor:
        t1 = executor.submit(genaiChatVertexCall,path, message, custom_token, context,temperature,parameters["chat_max_d"],parameters["chat_top_k"],parameters["chat_top_p"], ch)
        t2 = executor.submit(get_web_search, message)

    # print("Thread 1 : ", t1.result())
    print("Thread 2 ::::::::::: ", t2.result())
    end = time.time()
    print("Content chat response time (ms) : ", 1000 * (end - start))

    if ('please visit http://holcim.com' in t1.result()) or ('holcim' in message.lower()):
        print("step-1, sub-1")
        if ('error' in t2.result()):
            print("step-1, sub-2")
            response = (jsonify({"message":str(t1.result()),"status":"success"},200))
            return response
        else:
            print("step-1, sub-3")
            response = (jsonify({"message":str(t2.result()),"status":"success"},200))
            return response
    elif ('error' in t2.result()):
        print("step-1, sub-2")
        response = (jsonify({"message":str(t1.result()),"status":"success"},200))
        return response
    elif 'Session not found for provided token' in t1.result():
        print("step-2, sub-1")
        return jsonify({"msg":"Session not found for provided token"}), 401
    elif not(str(t1.result()) and str(t1.result()).strip()):
        print("step-3, sub-1")
        response = (jsonify({"message":str(t2.result()),"status":"success"},200))
        return response
    elif not(str(t2.result()) and str(t2.result()).strip()):
        print("step-4, sub-1")
        response = (jsonify({"message":str(t1.result()),"status":"success"},200))
        return response
    else:
        print("step-5, sub-1")
        response = (jsonify({"message":str(t1.result()),"status":"success"},200))
        return response




def genaiChatVertexCall(path, message, custom_token, context, temperature, chat_max_d, chat_top_k, chat_top_p, ch):
    cm = init_chat()
    start = time.time()
    chat = cm.start_chat(context=context, temperature=temperature, max_output_tokens=chat_max_d, top_k=chat_top_k, top_p=chat_top_p, message_history=ch)
    response = chat.send_message(message).text
    end = time.time()
    print("VertexAI For Chat Response Latency(ms) : ", 1000 * (end - start))
    print("Chat response from VertexAI=== ", response)
    print("vertex chat history : ", chat.message_history)

    print("history_users object values =====", history_users)
   
    try:
        if path == 'chat':
            history_users[custom_token]['chat'] = chat.message_history
        else:
            history_users[custom_token]['content-chat'] = chat.message_history
    except KeyError as ex:
        print(f"Invalid jwt provided: {ex}")
        return "Session not found for provided token"

    return response

def verify_custom_token(token):
    """
    verify custom token
    """
   
    custom_token = token
    if not custom_token:
        return {'error': 'Missing custom token'}
    try:
        decoded = jwt.decode(custom_token, SECRET_KEY, algorithms=['HS256'])
        email = decoded.get('email')

        if (decoded.get('exp') < datetime.utcnow().timestamp()):
            print("history_users < datetimeutcnow")
            history_users.pop(custom_token)
            raise jwt.ExpiredSignatureError
        else: 
            if (history_users[custom_token]['exp_time'] < datetime.utcnow()):
                print("history_users < datetimeutcnow")
                history_users[custom_token]['chat'] = {}
                history_users[custom_token]['content-chat'] = {}
                history_users[custom_token]['query-doc'] = {}
                return {'email': email, 'message': 'Token is valid'}
            else:
                history_users[custom_token]['exp_time'] = (datetime.utcnow() + timedelta(minutes=HISTORY_TOKEN_EXPIRATION_MINUTES))
                return {'email': email, 'message': 'Token is valid'}

    except jwt.ExpiredSignatureError:
        return {'error': 'Token has expired'}
    except jwt.InvalidTokenError:
        return {'error': 'Invalid token'}


def create_ggl_credentials(credfile="credentials.json"):
    """
    Simple function to create the necessary Google Credentials from a local credentials file.
    The file we're using is for a GCP project service Account.
    The file is created by GitLab using a secretive project Variable.
    """
    #TODO Implement GCP Secrets instead of GitLab Env Variable. Anyone with the image would have the creds.
    try:
        return service_account.Credentials.from_service_account_file(credfile)
    except Exception as e:
        print("Failed to create Google Creds")
        print(e)
        return None

def init_chat(project_id:str="corsdsdds-test",location:str="us-central1",encryption_spec_key_name:str="holcim_ai",chat_model:str="chat-bison",tuned_model_name:str="")->ChatModel:
    """
    Used in creating the necessary Chat Model for which the orchestrator will communicate with.
    Returns vertexai.language_models._language_models.ChatModel
    """

    try:
        vertexai.init(project=project_id, location=location, encryption_spec_key_name=encryption_spec_key_name)
        cm = ChatModel.from_pretrained(chat_model)
        if tuned_model_name:
            return cm.get_tuned_model(tuned_model_name)
        else:
            return cm
       
    except Exception as e:
        print("Error creating Chat Model")
        print(e)
        return None

def init_text_gen_model(project_id:str="cosdsrp-gdsd-test",location:str="us-central1",encryption_spec_key_name:str="holcim_ai",chat_model:str="chat-bison@001",tuned_model_name:str="")->TextGenerationModel:
    """
    Used in creating the necessary Chat Model for which the orchestrator will communicate with.
    Returns vertexai.language_models._language_models.ChatModel
    """
    try:
        vertexai.init(project=project_id, location=location, encryption_spec_key_name=encryption_spec_key_name)
        cm = TextGenerationModel.from_pretrained(chat_model)
        if tuned_model_name:
            return cm.get_tuned_model(tuned_model_name)
        else:
            return cm
       
    except Exception as e:
        print("Error creating Chat Model")
        print(e)
        return None


# if __name__ == '__main__':
#     app.run(debug=True)
