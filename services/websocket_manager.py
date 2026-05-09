import asyncio
import logging
from collections import defaultdict

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    def __init__(self):
        self._connections: dict[str, set[WebSocket]] = defaultdict(set)
        self._roles: dict[str, set[str]] = defaultdict(set)
        self._socket_users: dict[WebSocket, str] = {}
        self._lock = asyncio.Lock()
        self._loop: asyncio.AbstractEventLoop | None = None

    async def connect(self, websocket: WebSocket, user_id: str, roles: list[str]):
        await websocket.accept()
        async with self._lock:
            self._loop = asyncio.get_running_loop()
            self._connections[user_id].add(websocket)
            self._socket_users[websocket] = user_id
            for role in roles:
                self._roles[role].add(user_id)

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            user_id = self._socket_users.pop(websocket, None)
            if not user_id:
                return
            self._connections[user_id].discard(websocket)
            if not self._connections[user_id]:
                self._connections.pop(user_id, None)
                for user_ids in self._roles.values():
                    user_ids.discard(user_id)

    async def send_to_user(self, user_id, payload: dict):
        websockets = list(self._connections.get(str(user_id), set()))
        await self._send_many(websockets, payload)

    async def send_to_role(self, role: str, payload: dict):
        user_ids = list(self._roles.get(role, set()))
        for user_id in user_ids:
            await self.send_to_user(user_id, payload)

    async def _send_many(self, websockets: list[WebSocket], payload: dict):
        stale: list[WebSocket] = []
        for websocket in websockets:
            try:
                await websocket.send_json(payload)
            except Exception as exc:
                logger.info("Realtime send failed; dropping socket: %s", exc)
                stale.append(websocket)
        for websocket in stale:
            await self.disconnect(websocket)

    def emit_to_user(self, user_id, payload: dict):
        self._schedule(self.send_to_user(user_id, payload))

    def emit_to_role(self, role: str, payload: dict):
        self._schedule(self.send_to_role(role, payload))

    def _schedule(self, coroutine):
        if self._loop and self._loop.is_running():
            asyncio.run_coroutine_threadsafe(coroutine, self._loop)
            return
        logger.debug("Realtime event skipped because no websocket loop is active.")


websocket_manager = WebSocketManager()
