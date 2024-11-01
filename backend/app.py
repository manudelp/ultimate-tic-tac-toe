import os
import logging
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import DevelopmentConfig
from config import ProductionConfig
from api.bots import bot_routes
from api.auth import auth_routes

load_dotenv()  # Load environment variables from .env
users = []  # List to store user data

# Initialize Flask app with configuration
app = Flask(__name__)
app.config.from_object(ProductionConfig)  # Load configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
CORS(app)

# Initialize JWT
jwt = JWTManager(app)

# Register routes
app.register_blueprint(bot_routes)
app.register_blueprint(auth_routes)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Error handling
@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Server Error: {error}")
    return jsonify(message="Internal Server Error"), 500

@app.errorhandler(Exception)
def unhandled_exception(e):
    app.logger.error(f"Unhandled Exception: {e}")
    return jsonify(message="Unhandled Exception"), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)