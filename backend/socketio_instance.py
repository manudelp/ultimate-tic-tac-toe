from flask_socketio import SocketIO
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('socketio')
logger.setLevel(logging.DEBUG)

allowed_origins = [
    "http://localhost:3000",
    "https://utictactoe.vercel.app",
]

socketio = SocketIO(
    cors_allowed_origins=allowed_origins,
    async_mode='gevent',
    logger=True,
    engineio_logger=True
)


logger.info("SocketIO initialized with gevent mode")
