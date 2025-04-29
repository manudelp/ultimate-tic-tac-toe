from flask import Blueprint
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from socketio_instance import socketio

# Create a blueprint for online routes
online_routes = Blueprint('online', __name__)

# In-memory storage for lobbies
lobbies = {}

# Import routes at the end to avoid circular imports
from . import routes
