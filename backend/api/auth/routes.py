import os
import re
import jwt
import requests
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from supabase import create_client
from dotenv import load_dotenv
from turnstile_utils import validate_turnstile

# Load environment variables
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
TURNSTILE_SECRET_KEY = os.getenv("TURNSTILE_SECRET_KEY")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Define blueprint
auth_routes = Blueprint('auth_routes', __name__)

# --- User Registration ---
@auth_routes.route('/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return '', 204

    data = request.json
    turnstile_token = data.get("turnstile")
    email = data.get("email")
    password = data.get("password")
    username = data.get("username")

    if not turnstile_token:
        return jsonify({"message": "Turnstile token required"}), 400

    is_valid, error_message = validate_turnstile(turnstile_token, request.remote_addr)
    if not is_valid:
        return jsonify({"message": "Invalid verification"}), 400

    if not all([email, password, username]):
        return jsonify({"message": "Missing required fields."}), 400

    result = supabase.auth.sign_up({"email": email, "password": password})
    user = getattr(result.data, 'user', None) if hasattr(result, 'data') else getattr(result, 'user', None)

    if not user:
        return jsonify({"message": "Registration failed"}), 400

    try:
        profile_result = supabase.table("profiles").insert({
            "id": user.id,
            "email": email,
            "username": username
        }).execute()
    except Exception:
        return jsonify({"message": "Failed to create user profile."}), 500

    if not profile_result.data:
        return jsonify({"message": "Profile creation failed"}), 400

    return jsonify({"message": "User registered successfully!"}), 201

# --- User Login ---
@auth_routes.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 204

    data = request.json
    turnstile_token = data.get("turnstile")
    email = data.get("email")
    password = data.get("password")

    if not turnstile_token:
        return jsonify({"message": "Turnstile token required"}), 400

    is_valid, error_message = validate_turnstile(turnstile_token, request.remote_addr)
    if not is_valid:
        return jsonify({"message": "Invalid verification"}), 400

    if not all([email, password]):
        return jsonify({"message": "Missing email or password"}), 400

    # Retrieve user and check if password identity exists
    user_result = supabase.auth.admin.get_user_by_email(email)
    user = getattr(user_result, "user", None)

    if not user:
        return jsonify({"message": "User not found"}), 404

    has_password = any(
        identity.get("provider") == "email"
        for identity in getattr(user, "identities", [])
    )

    if not has_password:
        return jsonify({"message": "This account doesn't have a password. Please log in using Google or set a password first."}), 403

    result = supabase.auth.sign_in_with_password({"email": email, "password": password})

    if hasattr(result, 'error') and result.error:
        return jsonify({"message": f"Login failed: {result.error.message}"}), 401

    user = getattr(result.data, 'user', None) if hasattr(result.data, 'user') else getattr(result.data, 'get', lambda: None)().get('user')

    if not user:
        return jsonify({"message": "Authentication failed - no user data"}), 401

    user_id = user.id
    user_email = user.email

    profile_result = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
    if not profile_result.data:
        return jsonify({"message": "User profile not found"}), 404

    profile = profile_result.data

    access_token = create_access_token(
        identity=user_id,
        additional_claims={
            "email": user_email,
            "username": profile.get("username"),
            "name": profile.get("name"),
            "avatar_url": profile.get("avatar_url")
        }
    )

    return jsonify({
        "access_token": access_token,
        "user": {
            "id": user_id,
            "email": user_email,
            "username": profile.get("username"),
            "name": profile.get("name"),
            "avatar_url": profile.get("avatar_url")
        }
    }), 200

# --- Password Reset ---
@auth_routes.route('/forgot-password', methods=['POST', 'OPTIONS'])
def forgot_password():
    if request.method == 'OPTIONS':
        return '', 204

    data = request.json
    email = data.get("email")
    turnstile_token = data.get("turnstile")

    if not turnstile_token:
        return jsonify({"message": "Turnstile token required"}), 400

    is_valid, error_message = validate_turnstile(turnstile_token, request.remote_addr)
    if not is_valid:
        return jsonify({"message": "Invalid verification"}), 400

    if not email:
        return jsonify({"message": "Email is required"}), 400

    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        return jsonify({"message": "Invalid email format"}), 400

    origin = request.headers.get('Origin')
    referer = request.headers.get('Referer')
    base_url = origin or (f"{request.scheme}://{request.host}" if not referer else f"{request.scheme}://{request.host}")

    try:
        supabase.auth.reset_password_for_email(email, {"redirect_to": f"{base_url}/reset-password"})
    except Exception:
        pass  # Always respond with generic message for security

    return jsonify({"message": "If an account with that email exists, a password reset link has been sent"}), 200

# --- Set Password for OAuth users ---
@auth_routes.route('/set-password', methods=['POST'])
@jwt_required()
def set_password():
    data = request.json
    new_password = data.get('password')

    if not new_password or len(new_password) < 6:
        return jsonify({"message": "Password must be at least 6 characters"}), 400

    user_id = get_jwt_identity()
    result = supabase.auth.admin.update_user_by_id(user_id, {"password": new_password})

    if result.error:
        return jsonify({"message": "Failed to set password"}), 400

    return jsonify({"message": "Password set successfully"}), 200

# --- Verify JWT ---
@auth_routes.route('/verify-token', methods=['POST', 'OPTIONS'])
@jwt_required()
def verify_token():
    if request.method == 'OPTIONS':
        return '', 204

    current_user_id = get_jwt_identity()
    claims = get_jwt()

    return jsonify({
        "valid": True,
        "user": {
            "id": current_user_id,
            "email": claims.get("email"),
            "username": claims.get("username"),
            "name": claims.get("name"),
            "avatar_url": claims.get("avatar_url")
        }
    }), 200

# --- Get User Identities ---
@auth_routes.route('/user-identities/<user_id>', methods=['GET'])
def get_user_identities(user_id):
    provided_key = request.headers.get("X-Internal-API-Key")
    expected_key = os.getenv("INTERNAL_API_KEY")

    if provided_key != expected_key:
        return jsonify({"error": "Unauthorized"}), 403

    result = supabase.auth.admin.get_user_by_id(user_id)
    user = getattr(result, "user", None)

    if not user:
        return jsonify({"error": "User not found"}), 404

    identities = getattr(user, "identities", [])
    return jsonify({"identities": identities}), 200

# --- Turnstile Verification ---
@auth_routes.route('/verify-turnstile', methods=['POST', 'OPTIONS'])
def verify_turnstile_route():
    if request.method == 'OPTIONS':
        return '', 204

    data = request.json
    is_valid, error_message = validate_turnstile(data.get("turnstile"), request.remote_addr)
    if not is_valid:
        return jsonify({"success": False, "message": error_message}), 400

    return jsonify({"success": True}), 200

# --- Connection Health Check ---
@auth_routes.route('/test-connection', methods=['GET', 'OPTIONS'])
def test_connection():
    if request.method == 'OPTIONS':
        return '', 204

    try:
        result = supabase.table("profiles").select("count", count="exact").execute()
        return jsonify({
            "supabase_connection": "OK",
            "profile_count": result.count if hasattr(result, 'count') else "unknown"
        }), 200
    except Exception as e:
        return jsonify({"supabase_connection": "FAILED", "error": str(e)}), 500

# --- Supabase OAuth Token Exchange ---
@auth_routes.route('/supabase-exchange', methods=['POST', 'OPTIONS'])
def supabase_exchange():
    if request.method == 'OPTIONS':
        return '', 204

    data = request.json
    supabase_token = data.get("supabase_token")
    user_data = data.get("user_data")

    if not supabase_token or not user_data:
        return jsonify({"message": "Missing required data"}), 400

    try:
        # Decode token without signature check (client-side token validation only)
        decoded = jwt.decode(supabase_token, options={"verify_signature": False})
        user_id = decoded.get('sub')

        if not user_id or user_id != user_data.get('id'):
            return jsonify({"message": "Invalid token"}), 401
    except Exception:
        return jsonify({"message": "Invalid token format"}), 401

    try:
        # Fetch profile from database
        profile_result = supabase.table("profiles").select("*").eq("id", user_id).single().execute()

        if profile_result.data and not profile_result.data.get('linked_to'):
            db_profile = profile_result.data
            token_user_data = {
                "id": user_id,
                "email": db_profile.get('email', user_data.get('email')),
                "username": db_profile.get('username', user_data.get('username')),
                "name": db_profile.get('name', user_data.get('name')),
                "avatar_url": db_profile.get('avatar_url', user_data.get('avatar_url')),
                "provider": db_profile.get('provider', user_data.get('provider', 'email'))
            }
        else:
            token_user_data = {
                "id": user_data.get('id'),
                "email": user_data.get('email'),
                "username": user_data.get('username'),
                "name": user_data.get('name'),
                "avatar_url": user_data.get('avatar_url'),
                "provider": user_data.get('provider', 'email')
            }
            supabase.table("profiles").upsert(token_user_data).execute()
    except Exception:
        token_user_data = {
            "id": user_data.get('id'),
            "email": user_data.get('email'),
            "username": user_data.get('username'),
            "name": user_data.get('name'),
            "avatar_url": user_data.get('avatar_url'),
            "provider": user_data.get('provider', 'email')
        }

    access_token = create_access_token(
        identity=token_user_data["id"],
        additional_claims={
            "email": token_user_data.get("email"),
            "username": token_user_data.get("username"),
            "name": token_user_data.get("name"),
            "avatar_url": token_user_data.get("avatar_url")
        }
    )

    return jsonify({
        "access_token": access_token,
        "user": token_user_data
    }), 200
