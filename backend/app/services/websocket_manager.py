import asyncio
from threading import Lock
from typing import Any
from fastapi import WebSocket


class WebSocketManager:
    def __init__(self) -> None:
        self.active_connections: dict[str, list[WebSocket]] = {}
        self.lock = Lock()
        self.loop: asyncio.AbstractEventLoop | None = None

    async def connect(self, job_id: str, websocket: WebSocket) -> None:
        if self.loop is None:
            self.loop = asyncio.get_running_loop()

        await websocket.accept()
        with self.lock:
            self.active_connections.setdefault(job_id, []).append(websocket)

    def disconnect(self, job_id: str, websocket: WebSocket) -> None:
        with self.lock:
            connections = self.active_connections.get(job_id)
            if not connections:
                return
            if websocket in connections:
                connections.remove(websocket)
            if not connections:
                self.active_connections.pop(job_id, None)

    async def _broadcast(self, job_id: str, message: Any) -> None:
        with self.lock:
            connections = list(self.active_connections.get(job_id, []))

        for websocket in connections:
            try:
                await websocket.send_json(message)
            except Exception:
                self.disconnect(job_id, websocket)

    def send_frame(self, job_id: str, message: dict[str, Any]) -> None:
        if self.loop is None:
            return

        asyncio.run_coroutine_threadsafe(self._broadcast(job_id, message), self.loop)


ws_manager = WebSocketManager()
