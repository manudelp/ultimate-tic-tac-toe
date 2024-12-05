import bcrypt
import jwt
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import os
import json
import requests

auth_routes = Blueprint('auth', __name__)

# Ruta al archivo donde se almacenan los usuarios
DATA_FILE = 'users.json'

# Cargar la clave secreta desde las variables de entorno
SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default_secret_key')  # Asegúrate de configurar una clave secreta segura

# Funciones auxiliares
def load_users():
    """Carga los usuarios desde un archivo JSON."""
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    """Guarda los usuarios en un archivo JSON."""
    with open(DATA_FILE, 'w') as f:
        json.dump(users, f)

def generate_token(user):
    """Genera un token JWT para el usuario."""
    payload = {
        "id": user.get("id"),  # ID único del usuario
        "name": user.get("name"),
        "email": user.get("email"),
        "exp": datetime.utcnow() + timedelta(hours=1)  # Token expira en 1 hora
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

# Rutas
@auth_routes.route('/register', methods=['POST'])
def register():
    """Registro de usuarios."""
    data = request.json

    # Validar los datos recibidos
    if not data.get("name") or not data.get("email") or not data.get("password"):
        return jsonify({"message": "Missing required fields."}), 400

    users = load_users()

    # Verificar si el usuario ya existe
    for user in users:
        if user['email'] == data['email']:
            return jsonify({"message": "User already exists."}), 400

    # Hashear la contraseña
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())

    # Añadir el nuevo usuario
    new_user = {
        "id": len(users) + 1,  # Genera un ID único basado en la longitud actual
        "name": data['name'],
        "email": data['email'],
        "password": hashed_password.decode('utf-8'),  # Guardar como string
    }
    users.append(new_user)
    save_users(users)

    return jsonify({"message": "User registered successfully!"}), 201

@auth_routes.route('/login', methods=['POST'])
def login():
    """Inicio de sesión."""
    data = request.json

    # Validar los datos recibidos
    if not data.get("email") or not data.get("password"):
        return jsonify({"message": "Missing email or password."}), 400

    users = load_users()

    # Verificar el email y la contraseña
    for user in users:
        if user['email'] == data['email']:
            if bcrypt.checkpw(data['password'].encode('utf-8'), user['password'].encode('utf-8')):
                token = generate_token(user)  # Generar token JWT
                return jsonify({
                    "access_token": token,
                    "name": user['name']
                }), 200

    return jsonify({"message": "Invalid credentials."}), 401

@auth_routes.route('/verify-token', methods=['POST'])
def verify_token():
    """Verificar la validez del token JWT."""
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({"message": "Token is missing."}), 401

    try:
        # Decodificar el token
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return jsonify({"valid": True, "data": decoded}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({"message": "Token has expired."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "Invalid token."}), 401
    
    
RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY")

@auth_routes.route('/verify-recaptcha', methods=['POST'])
def verify_recaptcha():
    data = request.json
    token = data.get("captchaToken")

    if not token:
        return jsonify({"success": False, "message": "Missing captcha token"}), 400

    # Verificar el token con la API de Google
    url = "https://www.google.com/recaptcha/api/siteverify"
    response = requests.post(url, data={
        "secret": RECAPTCHA_SECRET_KEY,
        "response": token
    })

    result = response.json()
    if result.get("success"):
        return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False, "message": "Invalid reCAPTCHA"}), 400