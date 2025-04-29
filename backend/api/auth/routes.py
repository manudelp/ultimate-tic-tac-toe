import bcrypt
import jwt
from flask import request, jsonify
from datetime import datetime, timedelta
import os
import json
import requests
from . import auth_routes, SECRET_KEY, DATA_FILE, RECAPTCHA_SECRET_KEY

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

# REGISTER
@auth_routes.route('/register', methods=['POST'])
def register():
    """Registro de usuarios."""
    data = request.json

    # Validar captchaToken antes de continuar
    captcha_token = data.get("captchaToken")
    if not captcha_token:
        return jsonify({"message": "Captcha token is missing"}), 400

    # Verificar el token con la API de Google
    captcha_response = requests.post("https://www.google.com/recaptcha/api/siteverify", data={
        "secret": RECAPTCHA_SECRET_KEY,
        "response": captcha_token
    }).json()

    if not captcha_response.get("success"):
        return jsonify({"message": "Invalid reCAPTCHA"}), 400

    # Continuar con la lógica de registro
    if not data.get("name") or not data.get("email") or not data.get("password"):
        return jsonify({"message": "Missing required fields."}), 400

    users = load_users()

    for user in users:
        if user['email'] == data['email']:
            return jsonify({"message": "User already exists."}), 400

    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    new_user = {
        "id": len(users) + 1,
        "name": data['name'],
        "email": data['email'],
        "password": hashed_password.decode('utf-8'),
    }
    users.append(new_user)
    save_users(users)

    return jsonify({"message": "User registered successfully!"}), 201

# LOGIN
@auth_routes.route('/login', methods=['POST'])
def login():
    """Inicio de sesión."""
    data = request.json

    # Validar captchaToken antes de continuar
    captcha_token = data.get("captchaToken")
    if not captcha_token:
        return jsonify({"message": "Captcha token is missing"}), 400

    # Verificar el token con la API de Google
    captcha_response = requests.post("https://www.google.com/recaptcha/api/siteverify", data={
        "secret": RECAPTCHA_SECRET_KEY,
        "response": captcha_token
    }).json()

    if not captcha_response.get("success"):
        return jsonify({"message": "Invalid reCAPTCHA"}), 400

    # Continuar con la lógica de inicio de sesión
    if not data.get("email") or not data.get("password"):
        return jsonify({"message": "Missing email or password."}), 400

    users = load_users()

    for user in users:
        if user['email'] == data['email']:
            if bcrypt.checkpw(data['password'].encode('utf-8'), user['password'].encode('utf-8')):
                token = generate_token(user)
                return jsonify({
                    "access_token": token,
                    "name": user['name']
                }), 200

    return jsonify({"message": "Invalid credentials."}), 401

# VERIFY TOKEN
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

# VERIFY RECAPTCHA
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