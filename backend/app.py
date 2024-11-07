# backend/app.py

import os
import logging
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import DevelopmentConfig
from api.bots import bot_routes
from api.auth import auth_routes
from api.online import online_routes
from socketio_instance import socketio

load_dotenv()  # Load environment variables from .env
users = []  # List to store user data

# Initialize Flask app with configuration
app = Flask(__name__)
app.config.from_object(DevelopmentConfig)  # Load configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

# CORS(app, resources={r"/*": {"origins": "https://utictactoe.vercel.app"}})
CORS(app) # TODO: ONLY FOR DEVELOPMENT

# Initialize JWT
jwt = JWTManager(app)

# Initialize SocketIO
socketio.init_app(app, cors_allowed_origins="*")

# Register routes
app.register_blueprint(bot_routes)
app.register_blueprint(auth_routes)
app.register_blueprint(online_routes)

# Health check route
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify(status="healthy"), 200

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
    socketio.run(app, 
                    host='0.0.0.0',   # Escuchar en todas las interfaces
                    port=5000,        # El puerto que desees
                    debug=True,       # Habilitar modo de depuración
                    ssl_context=(
                        'C:/Users/manud/certificates/certificate.pem',  # Ruta al archivo del certificado
                        'C:/Users/manud/certificates/private-key.pem'   # Ruta a la clave privada
                    ))