import json
import asyncio
from typing import Dict, Set, Any
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # room_code -> set of teacher websockets
        self.teacher_connections: Dict[str, Set[WebSocket]] = {}
        # room_code -> dict of user_id -> WebSocket for students
        self.student_connections: Dict[str, Dict[int, WebSocket]] = {}

    async def connect_teacher(self, room_code: str, websocket: WebSocket):
        await websocket.accept()
        if room_code not in self.teacher_connections:
            self.teacher_connections[room_code] = set()
        self.teacher_connections[room_code].add(websocket)

    def disconnect_teacher(self, room_code: str, websocket: WebSocket):
        if room_code in self.teacher_connections:
            self.teacher_connections[room_code].discard(websocket)
            if not self.teacher_connections[room_code]:
                del self.teacher_connections[room_code]

    async def connect_student(self, room_code: str, user_id: int, websocket: WebSocket):
        await websocket.accept()
        if room_code not in self.student_connections:
            self.student_connections[room_code] = {}
        self.student_connections[room_code][user_id] = websocket

    def disconnect_student(self, room_code: str, user_id: int):
        if room_code in self.student_connections:
            self.student_connections[room_code].pop(user_id, None)
            if not self.student_connections[room_code]:
                del self.student_connections[room_code]

    async def broadcast_to_room_teachers(self, room_code: str, event_type: str, data: Any):
        if room_code in self.teacher_connections:
            payload = json.dumps({"event": event_type, "data": data})
            dead_sockets = set()
            for ws in self.teacher_connections[room_code]:
                try:
                    await ws.send_text(payload)
                except Exception:
                    dead_sockets.add(ws)
            for ws in dead_sockets:
                self.teacher_connections[room_code].discard(ws)

manager = ConnectionManager()
