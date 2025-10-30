from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, Any, List
import json
import asyncio
import logging
from datetime import datetime
from app.models.auth import User
from app.services.data_provider_service import DataProviderService

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections for real-time data streaming."""

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.subscriptions: Dict[str, Dict[str, Any]] = {}

    async def connect(self, websocket: WebSocket, data_type: str, user_id: int):
        await websocket.accept()
        connection_key = f"{data_type}:{user_id}"

        if connection_key not in self.active_connections:
            self.active_connections[connection_key] = []

        self.active_connections[connection_key].append(websocket)
        logger.info(f"WebSocket connected: {connection_key}")

    def disconnect(self, websocket: WebSocket, data_type: str, user_id: int):
        connection_key = f"{data_type}:{user_id}"

        if connection_key in self.active_connections:
            self.active_connections[connection_key].remove(websocket)
            if not self.active_connections[connection_key]:
                del self.active_connections[connection_key]

        logger.info(f"WebSocket disconnected: {connection_key}")

    async def broadcast_to_type(self, data_type: str, message: Dict[str, Any]):
        """Broadcast message to all connections subscribed to data_type."""
        for connection_key, connections in self.active_connections.items():
            if connection_key.startswith(f"{data_type}:"):
                for connection in connections:
                    try:
                        await connection.send_json(message)
                    except Exception as e:
                        logger.error(f"Broadcast error: {str(e)}")

    async def send_personal_message(
        self, message: Dict[str, Any], websocket: WebSocket
    ):
        """Send message to specific WebSocket connection."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Personal message error: {str(e)}")


manager = ConnectionManager()


@router.websocket("/stream/{data_type}")
async def stream_data(websocket: WebSocket, data_type: str, token: str = None):
    """WebSocket endpoint for real-time data streaming."""
    try:
        # Simple token validation (would use proper JWT validation in production)
        if not token:
            await websocket.close(code=1008, reason="Authentication required")
            return

        # Mock user ID from token (would decode JWT in production)
        user_id = 1  # Mock user ID

        await manager.connect(websocket, data_type, user_id)

        # Send welcome message
        await manager.send_personal_message(
            {
                "type": "welcome",
                "data_type": data_type,
                "timestamp": datetime.utcnow().isoformat(),
                "message": f"Connected to {data_type} data stream",
            },
            websocket,
        )

        # Keep connection alive and listen for messages
        while True:
            try:
                # Wait for client messages (ping, subscription updates, etc.)
                data = await websocket.receive_json()

                if data.get("type") == "ping":
                    await manager.send_personal_message(
                        {"type": "pong", "timestamp": datetime.utcnow().isoformat()},
                        websocket,
                    )

                elif data.get("type") == "subscribe":
                    # Handle subscription updates
                    filters = data.get("filters", {})
                    manager.subscriptions[f"{data_type}:{user_id}"] = {
                        "filters": filters,
                        "active": True,
                    }

                    await manager.send_personal_message(
                        {
                            "type": "subscription_confirmed",
                            "data_type": data_type,
                            "filters": filters,
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                        websocket,
                    )

            except Exception as e:
                logger.error(f"WebSocket message handling error: {str(e)}")
                break

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for {data_type}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        # Mock user ID for cleanup
        user_id = 1
        manager.disconnect(websocket, data_type, user_id)


async def broadcast_data_update(data_type: str, data: Dict[str, Any]):
    """Broadcast data update to all WebSocket connections for the data type."""
    message = {
        "type": "data_update",
        "data_type": data_type,
        "data": data,
        "timestamp": datetime.utcnow().isoformat(),
    }

    await manager.broadcast_to_type(data_type, message)


# Background task to simulate real-time data updates
async def simulate_realtime_updates():
    """Simulate real-time data updates for testing."""
    while True:
        try:
            # Simulate BACEN rate updates
            bacen_data = {
                "selic_rate": 12.25 + (0.01 * (datetime.utcnow().timestamp() % 10)),
                "cdi_rate": 12.15 + (0.01 * (datetime.utcnow().timestamp() % 10)),
                "timestamp": datetime.utcnow().isoformat(),
            }

            await broadcast_data_update("bacen", bacen_data)

            # Simulate market price updates
            market_data = {
                "inverters_avg": 2500.00 + (10 * (datetime.utcnow().timestamp() % 5)),
                "panels_avg": 1800.00 + (5 * (datetime.utcnow().timestamp() % 5)),
                "timestamp": datetime.utcnow().isoformat(),
            }

            await broadcast_data_update("market", market_data)

            await asyncio.sleep(30)  # Update every 30 seconds

        except Exception as e:
            logger.error(f"Real-time update simulation error: {str(e)}")
            await asyncio.sleep(5)


def start_realtime_updates():
    """Start the real-time update simulation task."""
    asyncio.create_task(simulate_realtime_updates())
