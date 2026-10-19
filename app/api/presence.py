from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
import datetime
from app.database import get_db
from app.models import Topic, Task, User, StudentPresence
from app.websocket_manager import manager

router = APIRouter(prefix="/api/presence", tags=["presence"])

class HeartbeatRequest(BaseModel):
    user_id: int
    room_code: str
    is_tab_active: bool
    is_online: bool = True
    current_task_order: Optional[int] = None

@router.post("/heartbeat")
async def process_heartbeat(req: HeartbeatRequest, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter_by(room_code=req.room_code).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Тему не знайдено")
    
    user = db.query(User).filter_by(id=req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    current_task = None
    if req.current_task_order:
        current_task = db.query(Task).filter_by(topic_id=topic.id, task_order=req.current_task_order).first()

    presence = db.query(StudentPresence).filter_by(user_id=user.id, topic_id=topic.id).first()
    if not presence:
        presence = StudentPresence(
            user_id=user.id,
            topic_id=topic.id,
            is_online=req.is_online,
            is_tab_active=req.is_tab_active,
            current_task_id=current_task.id if current_task else None,
            last_heartbeat=datetime.datetime.utcnow()
        )
        db.add(presence)
    else:
        presence.is_online = req.is_online
        presence.is_tab_active = req.is_tab_active
        if current_task:
            presence.current_task_id = current_task.id
        presence.last_heartbeat = datetime.datetime.utcnow()
        presence.updated_at = datetime.datetime.utcnow()

    user.last_active_at = datetime.datetime.utcnow()
    db.commit()

    # Broadcast to room teachers
    await manager.broadcast_to_room_teachers(req.room_code, "presence_update", {
        "user_id": user.id,
        "student_name": user.name,
        "is_online": req.is_online,
        "is_tab_active": req.is_tab_active,
        "current_task_order": req.current_task_order,
        "last_active": user.last_active_at.strftime("%H:%M:%S")
    })

    return {"status": "ok"}
