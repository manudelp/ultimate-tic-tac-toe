# backend/socketio_instance.py

from flask_socketio import SocketIO, Namespace

socketio = SocketIO(cors_allowed_origins="*")  # Permitir todas las conexiones CORS