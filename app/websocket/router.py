from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.orm import Session
from app.database.session import SessionLocal
from app.models.models import Booking, BookingStatus
import json
from typing import Dict, Set

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, booking_id: str):
        await websocket.accept()
        if booking_id not in self.active_connections:
            self.active_connections[booking_id] = set()
        self.active_connections[booking_id].add(websocket)

    def disconnect(self, websocket: WebSocket, booking_id: str):
        if booking_id in self.active_connections:
            self.active_connections[booking_id].discard(websocket)
            if not self.active_connections[booking_id]:
                del self.active_connections[booking_id]

    async def broadcast(self, booking_id: str, message: dict):
        if booking_id in self.active_connections:
            for connection in self.active_connections[booking_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"Error sending message: {e}")

manager = ConnectionManager()

@router.websocket("/ws/booking/{booking_id}")
async def websocket_endpoint(websocket: WebSocket, booking_id: str):
    """WebSocket endpoint for real-time booking updates"""
    await manager.connect(websocket, booking_id)
    
    db = SessionLocal()
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Handle different message types
            event_type = message_data.get("type")
            
            if event_type == "status_update":
                # Broadcast status update to all connected clients
                await manager.broadcast(booking_id, {
                    "type": "status_update",
                    "status": message_data.get("status"),
                    "booking_id": booking_id,
                    "timestamp": message_data.get("timestamp")
                })
            
            elif event_type == "location_update":
                # Broadcast cleaner location update
                await manager.broadcast(booking_id, {
                    "type": "location_update",
                    "latitude": message_data.get("latitude"),
                    "longitude": message_data.get("longitude"),
                    "booking_id": booking_id,
                    "timestamp": message_data.get("timestamp")
                })
            
            elif event_type == "message":
                # Broadcast general message
                await manager.broadcast(booking_id, {
                    "type": "message",
                    "message": message_data.get("message"),
                    "booking_id": booking_id,
                    "timestamp": message_data.get("timestamp")
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, booking_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, booking_id)
    finally:
        db.close()
