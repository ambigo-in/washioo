from services.websocket_manager import websocket_manager


def emit_user_event(user_id, event_type: str, data: dict | None = None):
    websocket_manager.emit_to_user(
        user_id,
        {
            "type": event_type,
            "data": data or {},
        },
    )


def emit_role_event(role: str, event_type: str, data: dict | None = None):
    websocket_manager.emit_to_role(
        role,
        {
            "type": event_type,
            "data": data or {},
        },
    )
