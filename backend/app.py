from gevent import monkey
monkey.patch_all()

import os
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from core.socketio import socketio
from api import bot_routes, game_routes, queue_routes

# Import route modules to register decorators on blueprints
import api.bots
import api.game
import api.queue

load_dotenv()

DEBUG = os.getenv("DEBUG", "false").lower() in ("1", "true", "yes")

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://utictactoe.vercel.app",
]

app = Flask(__name__)
app.config["DEBUG"] = DEBUG

CORS(app, origins=ALLOWED_ORIGINS, supports_credentials=True)

app.register_blueprint(bot_routes)
app.register_blueprint(game_routes)
app.register_blueprint(queue_routes)


@app.route("/health", methods=["GET"])
def health_check():
    return jsonify(status="healthy"), 200


socketio.init_app(app, cors_allowed_origins=ALLOWED_ORIGINS)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    print(f" * Running on http://0.0.0.0:{port} (debug={DEBUG})")
    print(" * Press CTRL+C to quit")
    socketio.run(app, host="0.0.0.0", port=port, debug=DEBUG, use_reloader=False, log_output=True)
