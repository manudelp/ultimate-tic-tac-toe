import os
import signal
import sys
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import DevelopmentConfig
from api.bots import bot_routes

load_dotenv()  # Load environment variables from .env
users = []  # List to store user data

# Initialize Flask app with configuration
app = Flask(__name__)
app.config.from_object(DevelopmentConfig)  # Load configura1tion
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
CORS(app)

# Initialize JWT
jwt = JWTManager(app)

# Register routes
app.register_blueprint(bot_routes)

# Signal handler for graceful shutdown
def signal_handler(_, __):
    print("Cerrando servidor...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
