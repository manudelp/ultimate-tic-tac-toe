# backend/app.py

import os
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import DevelopmentConfig
from api.bots import bot_routes
from api.auth import auth_routes

load_dotenv()  # Load environment variables from .env
users = []  # List to store user data

# Initialize Flask app with configuration
app = Flask(__name__)
app.config.from_object(DevelopmentConfig)  # Load configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

# Configurar CORS
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "https://www.utictactoe.online/", "https://utictactoe.online/"]}})

# Initialize JWT
jwt = JWTManager(app)

# Register routes
app.register_blueprint(bot_routes)
app.register_blueprint(auth_routes)

# Health check route
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify(status="healthy"), 200

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Run the app	