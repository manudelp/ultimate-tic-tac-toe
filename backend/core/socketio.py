import os
from flask_socketio import SocketIO

debug = os.getenv("DEBUG", "false").lower() in ("1", "true", "yes")

socketio = SocketIO(
    async_mode="gevent",
    logger=debug,
    engineio_logger=debug,
)
