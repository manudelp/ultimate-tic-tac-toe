from flask import Blueprint
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from socketio_instance import socketio

game_routes = Blueprint('game', __name__)

from . import routes
