from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Grade, Subject, Topic

router = APIRouter(prefix="/api/hierarchy", tags=["hierarchy"])

@router.get("")
def get_full_hierarchy(db: Session = Depends(get_db)):
    grades = db.query(Grade).order_by(Grade.sort_order).all()
    result = []
    for g in grades:
        grade_data = {
            "id": g.id,
            "name": g.name,
            "slug": g.slug,
            "subjects": []
        }
        for s in g.subjects:
            subject_data = {
                "id": s.id,
                "name": s.name,
                "slug": s.slug,
                "icon": s.icon,
                "topics": []
            }
            for t in s.topics:
                subject_data["topics"].append({
                    "id": t.id,
                    "name": t.name,
                    "slug": t.slug,
                    "room_code": t.room_code,
                    "description": t.description,
                    "tasks_count": len(t.tasks)
                })
            grade_data["subjects"].append(subject_data)
        result.append(grade_data)
    return {"grades": result}

@router.get("/topics/{room_code}")
def get_topic_by_room_code(room_code: str, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter_by(room_code=room_code).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Тему або кабінет не знайдено")
    
    return {
        "id": topic.id,
        "name": topic.name,
        "slug": topic.slug,
        "room_code": topic.room_code,
        "description": topic.description,
        "theory_content": topic.theory_content,
        "subject_name": topic.subject.name,
        "grade_name": topic.subject.grade.name,
        "tasks_count": len(topic.tasks)
    }
