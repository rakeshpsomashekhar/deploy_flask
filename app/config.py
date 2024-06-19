import os

basedir = os.path.abspath(os.path.dirname(__file__))
import datetime as dt

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'rakesh')
    # SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'app.db'))
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:TfE(^P>G3#cq"jix@34.29.14.109:5432/copilotdev')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TOKEN_EXPIRATION_MINUTES = 1400
    HISTORY_TOKEN_EXPIRATION_MINUTES = 120
    # PROJECT_ID = 'e3fsf34fdf'
    # BUCKET_NAME = 'dvfeeec'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MIDDLEWARE_API_TOKEN = os.getenv('MIDDLEWARE_API_TOKEN', "default-api-token")
    
    LANGUAGE='en' 
    APPLICATION_THEME='light'
    IS_SPEECH=False
    IS_MIC=False
    IS_HOLCIM_DATA=True
    IS_MY_LIBRARY=True
    IS_CUSTOM_COPILOT=False
    CONVERSE_STYLE= '0.8'
    CUSTOM_INSTRUCTION= ''
    CREATED_DATETIME=dt.datetime.utcnow()
    CREATED_BY='system'          

    
                