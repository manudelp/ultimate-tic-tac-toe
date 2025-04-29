from flask import Blueprint
import os

# Create the auth blueprint
auth_routes = Blueprint('auth', __name__)

# Define constants
SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default_secret_key')
DATA_FILE = 'users.json'
RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY")

# Import routes at the end to avoid circular imports
from . import routes
