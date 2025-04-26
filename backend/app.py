import os
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import DevelopmentConfig
from api.bots import bot_routes
from api.auth import auth_routes
from api.online import online_routes
from socketio_instance import socketio

# Cargar variables de entorno desde .env
load_dotenv()

# Inicializar la aplicación Flask con configuración
app = Flask(__name__)
app.config.from_object(DevelopmentConfig)  # Cargar configuración
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')  # Clave JWT

# CORS
CORS(app, resources={r"/*": {"origins": [
    "http://localhost:3000",
    "https://www.utictactoe.online",
    "https://utictactoe.online",
    "https://utictactoe.vercel.app"
]}})

# Inicializar JWT
jwt = JWTManager(app)

# Manejadores de errores de JWT
@jwt.unauthorized_loader
def unauthorized_response(callback):
    return jsonify({"message": "Missing or invalid token."}), 401

@jwt.expired_token_loader
def expired_token_response(jwt_header, jwt_payload):
    return jsonify({"message": "Token has expired."}), 401

# Registrar blueprints
app.register_blueprint(bot_routes)
app.register_blueprint(auth_routes)
app.register_blueprint(online_routes)

# Ruta de verificación de estado
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify(status="healthy"), 200

# Manejo global de errores no controlados
@app.errorhandler(Exception)
def handle_exception(e):
    response = {
        "message": "An unexpected error occurred.",
        "details": str(e)
    }
    return jsonify(response), 500

# Inicializar Socket.IO con la aplicación Flask
socketio.init_app(app)

# Iniciar la aplicación Flask
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)  # Ejecutar la app
