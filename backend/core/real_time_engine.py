"""
Real-Time Engine - WebSocket-based real-time communication
Advanced real-time features for today's update
"""

import logging
import asyncio
import json
from typing import Dict, List, Any, Optional, Set, Callable
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
from fastapi import WebSocket, WebSocketDisconnect
import uuid

logger = logging.getLogger(__name__)

class EventType(Enum):
    """Real-time event types"""
    AGENT_STATUS_UPDATE = "agent_status_update"
    WORKFLOW_PROGRESS = "workflow_progress"
    DOCUMENT_PROCESSED = "document_processed"
    CHAT_MESSAGE = "chat_message"
    SYSTEM_ALERT = "system_alert"
    USER_ACTIVITY = "user_activity"
    PERFORMANCE_METRICS = "performance_metrics"
    COLLABORATION_UPDATE = "collaboration_update"

@dataclass
class RealTimeEvent:
    """Real-time event structure"""
    id: str
    type: EventType
    data: Dict[str, Any]
    user_id: Optional[str] = None
    timestamp: datetime = None
    room: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.id is None:
            self.id = str(uuid.uuid4())

class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> connection_ids
        self.connection_users: Dict[str, str] = {}  # connection_id -> user_id
        self.room_connections: Dict[str, Set[str]] = {}  # room -> connection_ids
        self.connection_rooms: Dict[str, Set[str]] = {}  # connection_id -> rooms
        
    async def connect(self, websocket: WebSocket, connection_id: str, user_id: Optional[str] = None):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        
        if user_id:
            if user_id not in self.user_connections:
                self.user_connections[user_id] = set()
            self.user_connections[user_id].add(connection_id)
            self.connection_users[connection_id] = user_id
        
        self.connection_rooms[connection_id] = set()
        
        logger.info(f"WebSocket connection established: {connection_id} (user: {user_id})")
        
        # Send welcome message
        await self.send_to_connection(connection_id, RealTimeEvent(
            id=str(uuid.uuid4()),
            type=EventType.SYSTEM_ALERT,
            data={
                "message": "Connected to Multi-Agent MCP Real-Time Engine",
                "connection_id": connection_id,
                "server_time": datetime.utcnow().isoformat()
            }
        ))
    
    def disconnect(self, connection_id: str):
        """Remove a WebSocket connection"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        # Remove from user connections
        if connection_id in self.connection_users:
            user_id = self.connection_users[connection_id]
            if user_id in self.user_connections:
                self.user_connections[user_id].discard(connection_id)
                if not self.user_connections[user_id]:
                    del self.user_connections[user_id]
            del self.connection_users[connection_id]
        
        # Remove from rooms
        if connection_id in self.connection_rooms:
            for room in self.connection_rooms[connection_id].copy():
                self.leave_room(connection_id, room)
            del self.connection_rooms[connection_id]
        
        logger.info(f"WebSocket connection closed: {connection_id}")
    
    def join_room(self, connection_id: str, room: str):
        """Add connection to a room"""
        if room not in self.room_connections:
            self.room_connections[room] = set()
        
        self.room_connections[room].add(connection_id)
        
        if connection_id in self.connection_rooms:
            self.connection_rooms[connection_id].add(room)
        
        logger.debug(f"Connection {connection_id} joined room {room}")
    
    def leave_room(self, connection_id: str, room: str):
        """Remove connection from a room"""
        if room in self.room_connections:
            self.room_connections[room].discard(connection_id)
            if not self.room_connections[room]:
                del self.room_connections[room]
        
        if connection_id in self.connection_rooms:
            self.connection_rooms[connection_id].discard(room)
        
        logger.debug(f"Connection {connection_id} left room {room}")
    
    async def send_to_connection(self, connection_id: str, event: RealTimeEvent):
        """Send event to specific connection"""
        if connection_id in self.active_connections:
            try:
                websocket = self.active_connections[connection_id]
                await websocket.send_text(json.dumps({
                    "id": event.id,
                    "type": event.type.value,
                    "data": event.data,
                    "timestamp": event.timestamp.isoformat(),
                    "room": event.room
                }))
            except Exception as e:
                logger.error(f"Failed to send to connection {connection_id}: {str(e)}")
                self.disconnect(connection_id)
    
    async def send_to_user(self, user_id: str, event: RealTimeEvent):
        """Send event to all connections of a user"""
        if user_id in self.user_connections:
            tasks = []
            for connection_id in self.user_connections[user_id].copy():
                tasks.append(self.send_to_connection(connection_id, event))
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    async def send_to_room(self, room: str, event: RealTimeEvent):
        """Send event to all connections in a room"""
        if room in self.room_connections:
            event.room = room
            tasks = []
            for connection_id in self.room_connections[room].copy():
                tasks.append(self.send_to_connection(connection_id, event))
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    async def broadcast(self, event: RealTimeEvent):
        """Send event to all active connections"""
        tasks = []
        for connection_id in list(self.active_connections.keys()):
            tasks.append(self.send_to_connection(connection_id, event))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def get_connection_count(self) -> int:
        """Get total number of active connections"""
        return len(self.active_connections)
    
    def get_user_count(self) -> int:
        """Get number of unique connected users"""
        return len(self.user_connections)
    
    def get_room_stats(self) -> Dict[str, int]:
        """Get statistics for all rooms"""
        return {room: len(connections) for room, connections in self.room_connections.items()}

class RealTimeEngine:
    """Main real-time engine for the system"""
    
    def __init__(self):
        self.connection_manager = ConnectionManager()
        self.event_handlers: Dict[EventType, List[Callable]] = {}
        self.event_history: List[RealTimeEvent] = []
        self.max_history = 1000
        self.is_running = False
        
        # Performance tracking
        self.events_sent = 0
        self.events_failed = 0
        self.start_time = datetime.utcnow()
    
    def register_event_handler(self, event_type: EventType, handler: Callable):
        """Register an event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        logger.info(f"Registered event handler for {event_type.value}")
    
    async def emit_event(self, event: RealTimeEvent):
        """Emit an event to appropriate recipients"""
        try:
            # Store in history
            self.event_history.append(event)
            if len(self.event_history) > self.max_history:
                self.event_history.pop(0)
            
            # Call registered handlers
            if event.type in self.event_handlers:
                for handler in self.event_handlers[event.type]:
                    try:
                        await handler(event)
                    except Exception as e:
                        logger.error(f"Event handler error: {str(e)}")
            
            # Send to appropriate recipients
            if event.room:
                await self.connection_manager.send_to_room(event.room, event)
            elif event.user_id:
                await self.connection_manager.send_to_user(event.user_id, event)
            else:
                await self.connection_manager.broadcast(event)
            
            self.events_sent += 1
            
        except Exception as e:
            self.events_failed += 1
            logger.error(f"Failed to emit event: {str(e)}")
    
    async def handle_websocket(self, websocket: WebSocket, user_id: Optional[str] = None):
        """Handle WebSocket connection lifecycle"""
        connection_id = str(uuid.uuid4())
        
        try:
            await self.connection_manager.connect(websocket, connection_id, user_id)
            
            while True:
                try:
                    # Receive messages from client
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    
                    await self.handle_client_message(connection_id, message)
                    
                except WebSocketDisconnect:
                    break
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from connection {connection_id}")
                except Exception as e:
                    logger.error(f"Error handling message from {connection_id}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"WebSocket error for connection {connection_id}: {str(e)}")
        finally:
            self.connection_manager.disconnect(connection_id)
    
    async def handle_client_message(self, connection_id: str, message: Dict[str, Any]):
        """Handle messages from WebSocket clients"""
        try:
            message_type = message.get("type")
            
            if message_type == "join_room":
                room = message.get("room")
                if room:
                    self.connection_manager.join_room(connection_id, room)
                    await self.connection_manager.send_to_connection(connection_id, RealTimeEvent(
                        id=str(uuid.uuid4()),
                        type=EventType.SYSTEM_ALERT,
                        data={"message": f"Joined room: {room}"}
                    ))
            
            elif message_type == "leave_room":
                room = message.get("room")
                if room:
                    self.connection_manager.leave_room(connection_id, room)
                    await self.connection_manager.send_to_connection(connection_id, RealTimeEvent(
                        id=str(uuid.uuid4()),
                        type=EventType.SYSTEM_ALERT,
                        data={"message": f"Left room: {room}"}
                    ))
            
            elif message_type == "ping":
                await self.connection_manager.send_to_connection(connection_id, RealTimeEvent(
                    id=str(uuid.uuid4()),
                    type=EventType.SYSTEM_ALERT,
                    data={"message": "pong", "server_time": datetime.utcnow().isoformat()}
                ))
            
            elif message_type == "get_stats":
                stats = self.get_statistics()
                await self.connection_manager.send_to_connection(connection_id, RealTimeEvent(
                    id=str(uuid.uuid4()),
                    type=EventType.PERFORMANCE_METRICS,
                    data=stats
                ))
            
        except Exception as e:
            logger.error(f"Error handling client message: {str(e)}")
    
    async def emit_agent_status_update(self, agent_id: str, status: Dict[str, Any], user_id: Optional[str] = None):
        """Emit agent status update event"""
        await self.emit_event(RealTimeEvent(
            id=str(uuid.uuid4()),
            type=EventType.AGENT_STATUS_UPDATE,
            data={
                "agent_id": agent_id,
                "status": status,
                "timestamp": datetime.utcnow().isoformat()
            },
            user_id=user_id
        ))
    
    async def emit_workflow_progress(self, workflow_id: str, progress: Dict[str, Any], user_id: Optional[str] = None):
        """Emit workflow progress event"""
        await self.emit_event(RealTimeEvent(
            id=str(uuid.uuid4()),
            type=EventType.WORKFLOW_PROGRESS,
            data={
                "workflow_id": workflow_id,
                "progress": progress,
                "timestamp": datetime.utcnow().isoformat()
            },
            user_id=user_id,
            room=f"workflow_{workflow_id}"
        ))
    
    async def emit_document_processed(self, document_id: str, result: Dict[str, Any], user_id: Optional[str] = None):
        """Emit document processing completion event"""
        await self.emit_event(RealTimeEvent(
            id=str(uuid.uuid4()),
            type=EventType.DOCUMENT_PROCESSED,
            data={
                "document_id": document_id,
                "result": result,
                "timestamp": datetime.utcnow().isoformat()
            },
            user_id=user_id
        ))
    
    async def emit_chat_message(self, conversation_id: str, message: Dict[str, Any], user_id: Optional[str] = None):
        """Emit chat message event"""
        await self.emit_event(RealTimeEvent(
            id=str(uuid.uuid4()),
            type=EventType.CHAT_MESSAGE,
            data={
                "conversation_id": conversation_id,
                "message": message,
                "timestamp": datetime.utcnow().isoformat()
            },
            user_id=user_id,
            room=f"chat_{conversation_id}"
        ))
    
    async def emit_system_alert(self, message: str, level: str = "info", user_id: Optional[str] = None):
        """Emit system alert event"""
        await self.emit_event(RealTimeEvent(
            id=str(uuid.uuid4()),
            type=EventType.SYSTEM_ALERT,
            data={
                "message": message,
                "level": level,
                "timestamp": datetime.utcnow().isoformat()
            },
            user_id=user_id
        ))
    
    async def emit_performance_metrics(self, metrics: Dict[str, Any]):
        """Emit performance metrics event"""
        await self.emit_event(RealTimeEvent(
            id=str(uuid.uuid4()),
            type=EventType.PERFORMANCE_METRICS,
            data=metrics
        ))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get real-time engine statistics"""
        uptime = datetime.utcnow() - self.start_time
        
        return {
            "connections": {
                "total": self.connection_manager.get_connection_count(),
                "users": self.connection_manager.get_user_count(),
                "rooms": self.connection_manager.get_room_stats()
            },
            "events": {
                "sent": self.events_sent,
                "failed": self.events_failed,
                "success_rate": (self.events_sent / max(self.events_sent + self.events_failed, 1)) * 100
            },
            "performance": {
                "uptime_seconds": uptime.total_seconds(),
                "events_per_second": self.events_sent / max(uptime.total_seconds(), 1),
                "history_size": len(self.event_history)
            }
        }
    
    async def start(self):
        """Start the real-time engine"""
        self.is_running = True
        self.start_time = datetime.utcnow()
        logger.info("Real-Time Engine started")
    
    async def stop(self):
        """Stop the real-time engine"""
        self.is_running = False
        # Disconnect all connections
        for connection_id in list(self.connection_manager.active_connections.keys()):
            self.connection_manager.disconnect(connection_id)
        
        logger.info("Real-Time Engine stopped")

# Global real-time engine instance
real_time_engine = RealTimeEngine() 