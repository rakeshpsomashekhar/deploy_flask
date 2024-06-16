from flask import Blueprint

auth_bp = Blueprint('auth', __name__)
file_ops_bp = Blueprint('file_ops', __name__)
genai_bp = Blueprint('genai', __name__)
speech_bp = Blueprint('speech', __name__)
profile_bp = Blueprint('profile', __name__)

from . import auth, file_operations, genai, speech