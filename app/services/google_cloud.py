from google.cloud import storage, speech_v1, texttospeech_v1

def get_storage_client():
    return storage.Client()

def transcribe_speech(audio_content):
    client = speech_v1.SpeechClient()
    audio = speech_v1.RecognitionAudio(content=audio_content)
    config = speech_v1.RecognitionConfig(
        encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code="en-US",
    )
    response = client.recognize(config=config, audio=audio)
    return response.results[0].alternatives[0].transcript if response.results else ''

def synthesize_speech(text):
    client = texttospeech_v1.TextToSpeechClient()
    input_text = texttospeech_v1.SynthesisInput(text=text)
    voice = texttospeech_v1.VoiceSelectionParams(language_code="en-US", ssml_gender=texttospeech_v1.SsmlVoiceGender.NEUTRAL)
    audio_config = texttospeech_v1.AudioConfig(audio_encoding=texttospeech_v1.AudioEncoding.MP3)
    response = client.synthesize_speech(input=input_text, voice=voice, audio_config=audio_config)
    return response.audio_content
