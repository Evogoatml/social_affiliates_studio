"""
Custom native WebSocket connection manager for FastAPI.
No third-party WebSocket libraries - uses FastAPI's built-in WebSocket support.
"""

from fastapi import WebSocket
from typing import List, Dict, Any


class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.client_metadata: Dict[WebSocket, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, metadata: Dict[str, Any] = None):
        """Accept connection and track client"""
        await websocket.accept()
        self.active_connections.append(websocket)
        if metadata:
            self.client_metadata[websocket] = metadata
        return websocket

    def disconnect(self, websocket: WebSocket):
        """Remove disconnected client"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.client_metadata:
            del self.client_metadata[websocket]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send message to single client"""
        await websocket.send_text(message)

    async def broadcast(self, message: str, exclude: WebSocket = None):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections:
            if connection != exclude:
                await connection.send_text(message)

    async def broadcast_json(self, data: Dict[str, Any], exclude: WebSocket = None):
        """Broadcast JSON data to all connected clients"""
        import json
        for connection in self.active_connections:
            if connection != exclude:
                await connection.send_json(data)

    def get_connected_count(self) -> int:
        return len(self.active_connections)
