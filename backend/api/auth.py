# api/auth.py
import os
import json
from flask import Blueprint, request
import bcrypt

auth_routes = Blueprint('auth', __name__)

DATA_FILE = 'users.json'

def load_users():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_users(users):
    with open(DATA_FILE, 'w') as f:
        json.dump(users, f)

@auth_routes.route('/register', methods=['POST'])
def register():
    data = request.json
    users = load_users()
    # Check if user already exists
    for user in users:
        if user['email'] == data['email']:
            return {"message": "User already exists."}, 400
    # Hash the password
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    # Add user to the list
    users.append({
        "name": data['name'],
        "email": data['email'],
        "password": hashed_password.decode('utf-8'),  # Store as string
    })
    save_users(users)
    return {"message": "User registered successfully!"}, 201

@auth_routes.route('/login', methods=['POST'])
def login():
    data = request.json
    users = load_users()
    for user in users:
        if user['email'] == data['email']:
            # Check the hashed password
            if bcrypt.checkpw(data['password'].encode('utf-8'), user['password'].encode('utf-8')):
                return {
                    "access_token": "some_jwt_token",  # Replace with your JWT token generation logic
                    "name": user['name']
                }, 200
    return {"message": "Invalid credentials."}, 401