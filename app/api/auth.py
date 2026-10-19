from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
import datetime
from app.database import get_db
from app.models import User
from app.config import TEACHER_PASSWORD

router = APIRouter(prefix="/api/auth", tags=["auth"])

class StudentSessionRequest(BaseModel):
    name: str
    device_id: str
    grade_level: Optional[int] = 6
    class_letter: Optional[str] = "Б"

class TeacherLoginRequest(BaseModel):
    name: str
    password: str
    device_id: str

def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"

@router.post("/student-session")
def create_student_session(req: StudentSessionRequest, request: Request, db: Session = Depends(get_db)):
    name = req.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Ім'я не може бути порожнім")
    
    ip = get_client_ip(request)
    user_agent = request.headers.get("user-agent", "")

    grade_level = req.grade_level if req.grade_level in (6, 7, 8, 9) else 6
    class_letter = (req.class_letter.strip().upper() if req.class_letter else "Б")
    if class_letter not in ("А", "Б"):
        class_letter = "Б"

    # Find existing student with device_id or create new
    user = db.query(User).filter_by(device_id=req.device_id, role="student").first()
    if not user:
        user = User(
            device_id=req.device_id,
            name=name,
            role="student",
            grade_level=grade_level,
            class_letter=class_letter,
            ip_address=ip,
            user_agent=user_agent
        )
        db.add(user)
    else:
        user.name = name
        user.grade_level = grade_level
        user.class_letter = class_letter
        user.ip_address = ip
        user.user_agent = user_agent
        user.last_active_at = datetime.datetime.utcnow()

    db.commit()
    db.refresh(user)

    return {
        "success": True,
        "user_id": user.id,
        "name": user.name,
        "role": user.role,
        "grade_level": user.grade_level or 6,
        "class_letter": user.class_letter or "Б",
        "class_name": f"{user.grade_level or 6}-{user.class_letter or 'Б'}",
        "device_id": user.device_id,
        "ip_address": user.ip_address
    }

@router.post("/teacher-login")
def teacher_login(req: TeacherLoginRequest, request: Request, db: Session = Depends(get_db)):
    if req.password != TEACHER_PASSWORD:
        raise HTTPException(status_code=401, detail="Невірний пароль вчителя")
    
    name = req.name.strip() or "Вчитель"
    ip = get_client_ip(request)
    user_agent = request.headers.get("user-agent", "")

    user = db.query(User).filter_by(device_id=req.device_id, role="teacher").first()
    if not user:
        user = User(
            device_id=req.device_id,
            name=name,
            role="teacher",
            ip_address=ip,
            user_agent=user_agent
        )
        db.add(user)
    else:
        user.name = name
        user.ip_address = ip
        user.user_agent = user_agent
        user.last_active_at = datetime.datetime.utcnow()

    db.commit()
    db.refresh(user)

    return {
        "success": True,
        "user_id": user.id,
        "name": user.name,
        "role": user.role,
        "device_id": user.device_id
    }
