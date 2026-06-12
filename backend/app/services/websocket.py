from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        existing = self.active_connections.get(user_id)
        if existing is not None:
            await existing.close(code=1000, reason="Replaced by new connection")
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int) -> None:
        self.active_connections.pop(user_id, None)

    async def send_to_user(self, user_id: int, message: dict) -> bool:
        websocket = self.active_connections.get(user_id)
        if websocket is None:
            return False
        await websocket.send_json(message)
        return True

    def is_connected(self, user_id: int) -> bool:
        return user_id in self.active_connections


manager = ConnectionManager()
