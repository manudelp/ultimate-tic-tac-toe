from flask import Blueprint
import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('online')
logger.setLevel(logging.DEBUG)

# Adjust system path to ensure proper imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from socketio_instance import socketio

# Create a blueprint for online routes
online_routes = Blueprint('online', __name__)

# In-memory storage for lobbies
lobbies = {}

from . import routes
