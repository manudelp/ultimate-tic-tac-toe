# socketio_instance.py

from flask_socketio import SocketIO

# Initialize the SocketIO instance
socketio = SocketIO(cors_allowed_origins="*")
