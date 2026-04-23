### MONKEY PATCHING ###
from gevent import monkey
monkey.patch_all()
### END MONKEY PATCHING ###

import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from api.bots import bot_routes
from api.auth import auth_routes
from api.online import online_routes
from socketio_instance import socketio
from test_turnstile import test_bp


### CONFIGURATION ###
# Load environment variables
load_dotenv()

# Verify critical env vars are loaded
turnstile_key = os.getenv('TURNSTILE_SECRET_KEY')
jwt_key = os.getenv('JWT_SECRET_KEY')

class Config:
    """Base configuration."""
    DEBUG = os.getenv("DEBUG", True)
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = os.getenv("PORT", 5000)

app = Flask(__name__)
app.logger.info(f"Environment loaded - TURNSTILE_SECRET_KEY: {'✅ Present' if turnstile_key else '❌ MISSING'}")
app.logger.info(f"Environment loaded - JWT_SECRET_KEY: {'✅ Present' if jwt_key else '❌ MISSING'}")
app.config.from_object(Config)  
app.config['JWT_SECRET_KEY'] = jwt_key
### END CONFIGURATION ###


### CORS ###
allowed_origins = [
    "http://localhost:3000",
    "https://utictactoe.vercel.app"
]

CORS(app,
     origins=allowed_origins,
     supports_credentials=True)

def set_cors_headers(headers):
    """Set CORS headers on a response"""
    headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
    headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
    headers['Access-Control-Allow-Credentials'] = 'true'
    headers['Access-Control-Max-Age'] = '86400'
    return headers

@app.after_request
def after_request(response):
    set_cors_headers(response.headers)
    return response
### END CORS ###


### JWT ###
jwt = JWTManager(app)

@jwt.unauthorized_loader
def unauthorized_response(_callback):
    return jsonify({"message": "Missing or invalid token."}), 401

@jwt.expired_token_loader
def expired_token_response(_jwt_header, _jwt_payload):
    return jsonify({"message": "Token has expired."}), 401


### ROUTES ###
app.register_blueprint(bot_routes)
app.register_blueprint(auth_routes, url_prefix='/auth')
app.register_blueprint(online_routes)
app.register_blueprint(test_bp)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify(status="healthy"), 200

# Add OPTIONS handler for all routes
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify()
        set_cors_headers(response.headers)
        return response
#### END ROUTES ###


### SOCKET.IO ###
socketio.init_app(app, cors_allowed_origins=allowed_origins)
### END SOCKET.IO ###


### STARTUP LOGIC ###
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False, use_reloader=False)
### END STARTUP LOGIC ###
