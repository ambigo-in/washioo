from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from core.database import SessionLocal
from core.security import TokenExpired, TokenInvalid, decode_token_or_raise
from repositories.user_repository import get_user_with_roles
from services.websocket_manager import websocket_manager

router = APIRouter()


def _role_names(user) -> list[str]:
    return [
        user_role.role.role_name
        for user_role in user.user_roles
        if user_role.role
    ]


@router.websocket("/ws")
async def realtime_socket(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        payload = decode_token_or_raise(token)
    except (TokenExpired, TokenInvalid):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    if payload.get("type") != "access" or not payload.get("sub"):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    db = SessionLocal()
    try:
        user = get_user_with_roles(db, payload["sub"])
        if not user or not user.is_active:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        roles = _role_names(user)
    finally:
        db.close()

    await websocket_manager.connect(websocket, str(payload["sub"]), roles)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket)
    except Exception:
        await websocket_manager.disconnect(websocket)
