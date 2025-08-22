from fastapi import WebSocket
from app.logger import logger

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accepts a new WebSocket connection and adds it to the list."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("Admin client connected.")

    def disconnect(self, websocket: WebSocket):
        """Removes a WebSocket connection from the list."""
        self.active_connections.remove(websocket)
        logger.info("Admin client disconnected.")

    async def broadcast(self, message: str):
        """Sends a message to all active WebSocket connections."""
        for connection in self.active_connections:
            await connection.send_text(message)

# Instantiate the manager
manager = ConnectionManager()