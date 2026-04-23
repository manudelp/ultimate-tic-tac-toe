### MONKEY PATCHING ###
from gevent import monkey
monkey.patch_all()
### END MONKEY PATCHING ###

import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from api.bots import bot_routes
from api.online import online_routes
from socketio_instance import socketio


### CONFIGURATION ###
load_dotenv()

class Config:
    """Base configuration."""
    DEBUG = os.getenv("DEBUG", True)
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = os.getenv("PORT", 5000)

app = Flask(__name__)
app.config.from_object(Config)
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
    headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Requested-With'
    headers['Access-Control-Allow-Credentials'] = 'true'
    headers['Access-Control-Max-Age'] = '86400'
    return headers

@app.after_request
def after_request(response):
    set_cors_headers(response.headers)
    return response
### END CORS ###


### ROUTES ###
app.register_blueprint(bot_routes)
app.register_blueprint(online_routes)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify(status="healthy"), 200

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify()
        set_cors_headers(response.headers)
        return response
### END ROUTES ###


### SOCKET.IO ###
socketio.init_app(app, cors_allowed_origins=allowed_origins)
### END SOCKET.IO ###


### STARTUP LOGIC ###
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False, use_reloader=False)
### END STARTUP LOGIC ###
