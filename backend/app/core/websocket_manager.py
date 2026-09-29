"""
WebSocket Hub for Real-Time Streaming
Manages connected client sockets and broadcasts JSON envelopes:
{
  "event_type": "...",
  "timestamp": "...",
  "data": {...}
}
"""

import json
from datetime import datetime, timezone
from typing import List, Dict, Any
from fastapi import WebSocket

class WebSocketHub:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, event_type: str, data: Dict[str, Any]):
        """Broadcast message using standard envelope."""
        message = {
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": data,
        }
        json_payload = json.dumps(message)
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json_payload)
            except Exception:
                dead_connections.append(connection)

        for dead in dead_connections:
            self.disconnect(dead)

ws_hub = WebSocketHub()
