from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
import datetime
from app.database import get_db
from app.models import Topic, Task, TaskAttempt, User, StudentPresence
from app.websocket_manager import manager

router = APIRouter(prefix="/api/teacher", tags=["teacher"])

@router.get("/rooms/{room_code}/dashboard")
def get_room_dashboard(
    room_code: str,
    class_name: Optional[str] = Query(None, description="Фільтр за класом (наприклад 6-А)"),
    db: Session = Depends(get_db)
):
    topic = db.query(Topic).filter_by(room_code=room_code).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Кабінет теми не знайдено")
    
    tasks = db.query(Task).filter_by(topic_id=topic.id).order_by(Task.task_order).all()
    task_id_to_order = {t.id: t.task_order for t in tasks}
    total_tasks = len(tasks)

    # Find all students who have a presence record or attempts in this topic
    presence_records = db.query(StudentPresence).filter_by(topic_id=topic.id).all()
    presence_user_ids = {p.user_id for p in presence_records}

    attempt_user_ids = set(
        uid[0] for uid in db.query(TaskAttempt.user_id).filter(
            TaskAttempt.task_id.in_([t.id for t in tasks])
        ).distinct().all()
    )

    all_student_ids = presence_user_ids.union(attempt_user_ids)
    
    students_data = []
    now = datetime.datetime.utcnow()

    # Load all attempts for this topic in one query
    attempts_by_user = {}
    if all_student_ids:
        all_attempts = db.query(TaskAttempt).filter(
            TaskAttempt.user_id.in_(all_student_ids),
            TaskAttempt.task_id.in_([t.id for t in tasks])
        ).order_by(TaskAttempt.created_at.asc()).all()

        for att in all_attempts:
            if att.user_id not in attempts_by_user:
                attempts_by_user[att.user_id] = {}
            if att.task_id not in attempts_by_user[att.user_id]:
                attempts_by_user[att.user_id][att.task_id] = []
            attempts_by_user[att.user_id][att.task_id].append(att)

    presence_map = {p.user_id: p for p in presence_records}
    users = db.query(User).filter(User.id.in_(all_student_ids)).all() if all_student_ids else []
    
    for u in users:
        pres = presence_map.get(u.id)
        is_online = False
        is_tab_active = False
        current_task_order = 1
        seconds_since_heartbeat = 9999

        if pres:
            seconds_since_heartbeat = int((now - pres.last_heartbeat).total_seconds()) if pres.last_heartbeat else 9999
            # Consider online if heartbeat was within last 30 seconds and pres.is_online
            is_online = pres.is_online and (seconds_since_heartbeat <= 30)
            is_tab_active = pres.is_tab_active if is_online else False
            if pres.current_task_id and pres.current_task_id in task_id_to_order:
                current_task_order = task_id_to_order[pres.current_task_id]

        u_attempts = attempts_by_user.get(u.id, {})
        solved_count = 0
        total_attempts_count = 0
        tasks_progress = []

        for t in tasks:
            t_attempts = u_attempts.get(t.id, [])
            total_attempts_count += len(t_attempts)
            is_solved = any(a.is_correct for a in t_attempts)
            if is_solved:
                solved_count += 1
            
            last_att = t_attempts[-1] if t_attempts else None
            tasks_progress.append({
                "task_id": t.id,
                "task_order": t.task_order,
                "question": t.question,
                "correct_answer": t.correct_answer,
                "is_solved": is_solved,
                "attempt_count": len(t_attempts),
                "last_answer": last_att.submitted_answer if last_att else None,
                "last_is_correct": last_att.is_correct if last_att else None,
                "history": [
                    {
                        "submitted_answer": a.submitted_answer,
                        "is_correct": a.is_correct,
                        "attempt_number": a.attempt_number,
                        "created_at": a.created_at.strftime("%H:%M:%S")
                    } for a in t_attempts
                ]
            })

        st_grade = u.grade_level or 6
        st_letter = u.class_letter or "Б"
        st_class = f"{st_grade}-{st_letter}"

        students_data.append({
            "user_id": u.id,
            "name": u.name,
            "grade_level": st_grade,
            "class_letter": st_letter,
            "class_name": st_class,
            "ip_address": u.ip_address,
            "device_id": u.device_id,
            "is_online": is_online,
            "is_tab_active": is_tab_active,
            "seconds_since_heartbeat": seconds_since_heartbeat,
            "current_task_order": current_task_order,
            "solved_count": solved_count,
            "total_tasks": total_tasks,
            "total_attempts": total_attempts_count,
            "tasks_progress": tasks_progress,
            "last_active": u.last_active_at.strftime("%H:%M:%S") if u.last_active_at else ""
        })

    # Sort students: online first, then active tab first, then solved count desc, then name asc
    students_data.sort(key=lambda s: (not s["is_online"], not s["is_tab_active"], -s["solved_count"], s["name"]))

    available_classes = sorted(list(set(s["class_name"] for s in students_data)))
    if class_name and class_name != "all":
        filtered_students = [s for s in students_data if s["class_name"] == class_name]
    else:
        filtered_students = students_data

    return {
        "room": {
            "room_code": topic.room_code,
            "topic_name": topic.name,
            "subject_name": topic.subject.name,
            "grade_name": topic.subject.grade.name,
            "total_tasks": total_tasks
        },
        "tasks": [
            {
                "id": t.id,
                "task_order": t.task_order,
                "question": t.question,
                "correct_answer": t.correct_answer
            } for t in tasks
        ],
        "students": filtered_students,
        "all_students_count": len(students_data),
        "available_classes": available_classes,
        "online_count": sum(1 for s in filtered_students if s["is_online"]),
        "active_tab_count": sum(1 for s in filtered_students if s["is_online"] and s["is_tab_active"]),
        "total_students": len(filtered_students)
    }


@router.post("/rooms/{room_code}/students/{user_id}/reset")
async def reset_student_progress(
    room_code: str,
    user_id: int,
    task_id: Optional[int] = Query(None, description="Опціональний ID конкретного завдання для скидання"),
    db: Session = Depends(get_db)
):
    topic = db.query(Topic).filter_by(room_code=room_code).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Кабінет теми не знайдено")
    
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Учня не знайдено")
    
    tasks = db.query(Task).filter_by(topic_id=topic.id).all()
    topic_task_ids = [t.id for t in tasks]

    if task_id:
        if task_id not in topic_task_ids:
            raise HTTPException(status_code=400, detail="Завдання не належить до цієї теми")
        deleted_count = db.query(TaskAttempt).filter(
            TaskAttempt.user_id == user_id,
            TaskAttempt.task_id == task_id
        ).delete(synchronize_session=False)
    else:
        deleted_count = db.query(TaskAttempt).filter(
            TaskAttempt.user_id == user_id,
            TaskAttempt.task_id.in_(topic_task_ids)
        ).delete(synchronize_session=False)
        
        # Reset current task in presence
        presence = db.query(StudentPresence).filter_by(user_id=user_id, topic_id=topic.id).first()
        if presence and topic_task_ids:
            first_task = sorted(tasks, key=lambda t: t.task_order)[0]
            presence.current_task_id = first_task.id
            presence.updated_at = datetime.datetime.utcnow()

    db.commit()

    # Broadcast reset event to both teachers and students
    reset_data = {
        "user_id": user_id,
        "student_name": user.name,
        "room_code": room_code,
        "task_id": task_id,
        "is_full_reset": task_id is None,
        "deleted_attempts": deleted_count,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
    await manager.broadcast_to_room(room_code, "student_progress_reset", reset_data)

    return {
        "success": True,
        "message": f"Прогрес учня {user.name} успішно скинуто",
        "deleted_attempts": deleted_count,
        "task_id": task_id
    }
