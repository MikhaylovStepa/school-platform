import re
import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
import datetime
from app.database import get_db
from app.models import Topic, Task, TaskAttempt, User, StudentPresence
from app.websocket_manager import manager

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

class SubmitAnswerRequest(BaseModel):
    user_id: int
    task_id: int
    submitted_answer: str
    room_code: str

def normalize_general_answer(ans: str) -> str:
    s = ans.strip().lower()
    s = s.replace("−", "-").replace("—", "-").replace("–", "-")
    trans = str.maketrans({"а": "a", "в": "b", "с": "c", "д": "d", "х": "x", "у": "y", "е": "e", "к": "k", "м": "m", "н": "n", "р": "p", "т": "t", "о": "o"})
    s = s.translate(trans)
    # Convert mixed fraction "3 2/5" or "3_2/5" to standardized "3_2/5" before stripping other whitespace
    s = re.sub(r'(\d+)\s+(\d+)\s*/\s*(\d+)', r'\1_\2/\3', s)
    s = s.replace(" ", "").replace("*", "").replace("·", "")
    s = re.sub(r'(\d+),(\d+)', r'\1.\2', s)
    # Only strip leading '+' if it is a signed number (e.g. '+5' -> '5'), but keep for sign sequences (e.g. '+-+', '+++')
    if s.startswith("+") and len(s) > 1 and (s[1].isdigit() or s[1] == '.'):
        s = s[1:]
    return s

def parse_fraction_or_mixed(val: str):
    # Match mixed number "3_2/5" or "3 2/5"
    m_mixed = re.match(r'^(\d+)[_\s\+](\d+)/(\d+)$', val.strip())
    if m_mixed:
        w, n, d = int(m_mixed.group(1)), int(m_mixed.group(2)), int(m_mixed.group(3))
        if d != 0:
            return w + n / d
    # Match simple fraction "2/5"
    m_frac = re.match(r'^(\d+)/(\d+)$', val.strip())
    if m_frac:
        n, d = int(m_frac.group(1)), int(m_frac.group(2))
        if d != 0:
            return n / d
    return None

def check_answer_match(submitted: str, correct_spec: str) -> bool:
    norm_sub = normalize_general_answer(submitted)
    options = [opt.strip() for opt in correct_spec.split("|")]
    
    # 1. Exact normalized match
    for opt in options:
        norm_opt = normalize_general_answer(opt)
        if norm_sub == norm_opt:
            return True

    # 1b. Check fraction and mixed number mathematical equivalence
    sub_frac = parse_fraction_or_mixed(norm_sub)
    if sub_frac is not None:
        for opt in options:
            norm_opt = normalize_general_answer(opt)
            opt_frac = parse_fraction_or_mixed(norm_opt)
            if opt_frac is not None and abs(sub_frac - opt_frac) < 1e-7:
                return True
            try:
                if not any(c.isalpha() for c in norm_opt) and not ("-" in norm_opt and not norm_opt.startswith("-")):
                    val_opt = float(norm_opt)
                    if abs(sub_frac - val_opt) < 1e-7:
                        return True
            except Exception:
                pass
            
    # 2. Check multi-choice list match (e.g. "A, C" vs "C, A" vs "AC")
    sub_letters = sorted(re.findall(r'[a-z]', norm_sub))
    for opt in options:
        opt_letters = sorted(re.findall(r'[a-z]', normalize_general_answer(opt)))
        if sub_letters and opt_letters and sub_letters == opt_letters:
            return True

    # 3. Check prime factors list / equation roots match (e.g. "-2; 4" vs "4; -2", "2, 2, 3" vs "2*2*3")
    def extract_signed_numbers(text: str):
        return [float(x) for x in re.findall(r'[-+]?\d+(?:\.\d+)?', text)]

    sub_signed = extract_signed_numbers(norm_sub)
    for opt in options:
        opt_signed = extract_signed_numbers(normalize_general_answer(opt))
        if sub_signed and opt_signed and len(sub_signed) > 1 and len(opt_signed) > 1:
            if sorted(sub_signed) == sorted(opt_signed):
                return True
        if sub_signed and opt_signed and set(sub_signed) == set(opt_signed):
            if sorted(sub_signed) == sorted(opt_signed):
                return True
            if len(set(opt_signed)) == 1 and len(set(sub_signed)) == 1:
                return True

    # 4. Check algebraic equivalents (e.g. "0a" matches "0", "1x" matches "x", "-1x" matches "-x")
    zero_aliases = {"0", "0a", "0b", "0c", "0x", "0y", "0m", "0k", "0n", "0p", "0t", "0z"}
    if norm_sub in zero_aliases:
        for opt in options:
            if normalize_general_answer(opt) in zero_aliases:
                return True
    if norm_sub.startswith("1") and len(norm_sub) > 1 and norm_sub[1:].isalpha():
        var = norm_sub[1:]
        for opt in options:
            if normalize_general_answer(opt) == var:
                return True
    if norm_sub.startswith("-1") and len(norm_sub) > 2 and norm_sub[2:].isalpha():
        var = "-" + norm_sub[2:]
        for opt in options:
            if normalize_general_answer(opt) == var:
                return True
    for opt in options:
        norm_opt = normalize_general_answer(opt)
        if norm_opt.startswith("1") and len(norm_opt) > 1 and norm_opt[1:].isalpha():
            if norm_sub == norm_opt[1:]:
                return True
        if norm_opt.startswith("-1") and len(norm_opt) > 2 and norm_opt[2:].isalpha():
            if norm_sub == "-" + norm_opt[2:]:
                return True

    # 5. Check numeric equivalence with small tolerance
    for opt in options:
        norm_opt = normalize_general_answer(opt)
        try:
            sub_nums = extract_signed_numbers(norm_sub)
            opt_nums = extract_signed_numbers(norm_opt)
            if len(sub_nums) == 1 and len(opt_nums) == 1 and not any(c.isalpha() for c in norm_sub) and not any(c.isalpha() for c in norm_opt):
                sub_num = sub_nums[0]
                opt_num = opt_nums[0]
                if abs(sub_num - opt_num) < 0.06 or (opt_num != 0 and abs(sub_num - opt_num) / abs(opt_num) < 0.05):
                    return True
        except Exception:
            pass
        # Check numeric range (e.g. 320-335 or 190-200)
        if "-" in opt and not opt.startswith("-") and not any(c.isalpha() for c in opt):
            parts = opt.split("-")
            if len(parts) == 2:
                try:
                    low = float(parts[0])
                    high = float(parts[1])
                    sub_val = float(re.sub(r'[^\d\.\-]', '', norm_sub))
                    if low <= sub_val <= high:
                        return True
                except Exception:
                    pass
    return False

@router.get("/topic/{room_code}")
def get_topic_tasks(room_code: str, user_id: Optional[int] = None, db: Session = Depends(get_db)):
    topic = db.query(Topic).filter_by(room_code=room_code).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Тему не знайдено")
    
    tasks = db.query(Task).filter_by(topic_id=topic.id).order_by(Task.task_order).all()
    
    # If user_id is provided, get student's attempt state
    attempts_map = {}
    if user_id:
        user_attempts = db.query(TaskAttempt).filter_by(user_id=user_id).filter(
            TaskAttempt.task_id.in_([t.id for t in tasks])
        ).order_by(TaskAttempt.created_at.asc()).all()

        for a in user_attempts:
            if a.task_id not in attempts_map:
                attempts_map[a.task_id] = {
                    "attempts_count": 0,
                    "is_solved": False,
                    "last_answer": "",
                    "last_is_correct": False
                }
            attempts_map[a.task_id]["attempts_count"] += 1
            attempts_map[a.task_id]["last_answer"] = a.submitted_answer
            attempts_map[a.task_id]["last_is_correct"] = a.is_correct
            if a.is_correct:
                attempts_map[a.task_id]["is_solved"] = True

    result_tasks = []
    for t in tasks:
        user_state = attempts_map.get(t.id, {
            "attempts_count": 0,
            "is_solved": False,
            "last_answer": "",
            "last_is_correct": False
        })
        
        task_type = t.task_type
        options = t.options_json

        # Ensure multi-number prime factorization tasks for GCD and LCM have proper options
        if topic.slug == "math-6-gcd-lcm" or topic.room_code == "math-6-gcd-lcm":
            if t.task_order == 11:
                task_type = "prime_factorization"
                options = json.dumps({"numbers": [72, 96]}, ensure_ascii=False)
            elif t.task_order == 12:
                task_type = "prime_factorization"
                options = json.dumps({"numbers": [36, 54, 72]}, ensure_ascii=False)
            elif t.task_order == 13:
                task_type = "prime_factorization"
                options = json.dumps({"numbers": [28, 42]}, ensure_ascii=False)
            elif t.task_order == 14:
                task_type = "prime_factorization"
                options = json.dumps({"numbers": [12, 15, 18]}, ensure_ascii=False)

        result_tasks.append({
            "id": t.id,
            "task_order": t.task_order,
            "question": t.question,
            "task_type": task_type,
            "hint": t.hint,
            "media_url": t.media_url,
            "options": options,
            "attempts_count": user_state["attempts_count"],
            "is_solved": user_state["is_solved"],
            "last_answer": user_state["last_answer"],
            "last_is_correct": user_state["last_is_correct"]
        })

    return {
        "topic": {
            "id": topic.id,
            "name": topic.name,
            "slug": topic.slug,
            "room_code": topic.room_code,
            "description": topic.description,
            "theory_content": topic.theory_content,
            "subject_name": topic.subject.name,
            "grade_name": topic.subject.grade.name,
            "total_tasks": len(tasks)
        },
        "tasks": result_tasks
    }

@router.post("/submit")
async def submit_task_answer(req: SubmitAnswerRequest, db: Session = Depends(get_db)):
    task = db.query(Task).filter_by(id=req.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Завдання не знайдено")
    
    user = db.query(User).filter_by(id=req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    raw_submitted = req.submitted_answer.strip()
    is_correct = check_answer_match(raw_submitted, task.correct_answer)

    # Previous attempt count
    prev_attempts_count = db.query(TaskAttempt).filter_by(user_id=user.id, task_id=task.id).count()
    attempt_num = prev_attempts_count + 1

    attempt = TaskAttempt(
        user_id=user.id,
        task_id=task.id,
        submitted_answer=raw_submitted,
        is_correct=is_correct,
        attempt_number=attempt_num
    )
    db.add(attempt)

    # Update or create presence
    presence = db.query(StudentPresence).filter_by(user_id=user.id, topic_id=task.topic_id).first()
    if not presence:
        presence = StudentPresence(
            user_id=user.id,
            topic_id=task.topic_id,
            is_online=True,
            is_tab_active=True,
            current_task_id=task.id,
            last_heartbeat=datetime.datetime.utcnow()
        )
        db.add(presence)
    else:
        presence.is_online = True
        presence.current_task_id = task.id
        presence.last_heartbeat = datetime.datetime.utcnow()
        presence.updated_at = datetime.datetime.utcnow()

    user.last_active_at = datetime.datetime.utcnow()
    db.commit()

    # Calculate student overall progress in this topic
    total_tasks = db.query(Task).filter_by(topic_id=task.topic_id).count()
    solved_count = db.query(TaskAttempt.task_id).filter(
        TaskAttempt.user_id == user.id,
        TaskAttempt.is_correct == True,
        TaskAttempt.task_id.in_(db.query(Task.id).filter_by(topic_id=task.topic_id))
    ).distinct().count()

    # Broadcast to teachers in real-time
    await manager.broadcast_to_room_teachers(req.room_code, "task_attempt", {
        "user_id": user.id,
        "student_name": user.name,
        "task_id": task.id,
        "task_order": task.task_order,
        "submitted_answer": raw_submitted,
        "is_correct": is_correct,
        "attempt_number": attempt_num,
        "solved_count": solved_count,
        "total_tasks": total_tasks,
        "timestamp": datetime.datetime.utcnow().isoformat()
    })

    if is_correct:
        message = "Правильно! Відмінна робота! 🎉"
    else:
        message = "Неправильно. Зверни увагу на знаки та спробуй ще раз! 💡"

    return {
        "is_correct": is_correct,
        "attempt_number": attempt_num,
        "hint": task.hint if not is_correct else None,
        "message": message,
        "solved_count": solved_count,
        "total_tasks": total_tasks
    }
