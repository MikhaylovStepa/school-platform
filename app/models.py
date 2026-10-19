import datetime
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
from app.database import Base

class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    sort_order = Column(Integer, default=0)

    subjects = relationship("Subject", back_populates="grade", cascade="all, delete-orphan", order_by="Subject.sort_order")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    grade_id = Column(Integer, ForeignKey("grades.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    slug = Column(String(100), index=True, nullable=False)
    icon = Column(String(50), default="book")
    sort_order = Column(Integer, default=0)

    grade = relationship("Grade", back_populates="subjects")
    topics = relationship("Topic", back_populates="subject", cascade="all, delete-orphan", order_by="Topic.sort_order")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(200), index=True, nullable=False)
    room_code = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    theory_content = Column(Text, nullable=True)
    sort_order = Column(Integer, default=0)

    subject = relationship("Subject", back_populates="topics")
    tasks = relationship("Task", back_populates="topic", cascade="all, delete-orphan", order_by="Task.task_order")
    presences = relationship("StudentPresence", back_populates="topic", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    task_order = Column(Integer, default=1, index=True)
    question = Column(Text, nullable=False)
    task_type = Column(String(50), default="input_number") # input_number, choice, text
    correct_answer = Column(String(200), nullable=False)
    options_json = Column(Text, nullable=True) # JSON array of options if choice
    hint = Column(Text, nullable=True)
    media_url = Column(String(500), nullable=True)

    topic = relationship("Topic", back_populates="tasks")
    attempts = relationship("TaskAttempt", back_populates="task", cascade="all, delete-orphan")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(100), index=True, nullable=False)
    name = Column(String(150), nullable=False)
    role = Column(String(20), default="student", index=True) # student or teacher
    grade_level = Column(Integer, default=6, nullable=True) # 6 or 7
    class_letter = Column(String(10), default="Б", nullable=True) # 'А' or 'Б'
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_active_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    attempts = relationship("TaskAttempt", back_populates="user", cascade="all, delete-orphan")
    presences = relationship("StudentPresence", back_populates="user", cascade="all, delete-orphan")


class StudentPresence(Base):
    __tablename__ = "student_presences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    is_online = Column(Boolean, default=True)
    is_tab_active = Column(Boolean, default=True) # True = active on tab, False = tab blurred/hidden
    current_task_id = Column(Integer, ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)
    last_heartbeat = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="presences")
    topic = relationship("Topic", back_populates="presences")
    current_task = relationship("Task")

    __table_args__ = (
        Index("idx_presence_user_topic", "user_id", "topic_id", unique=True),
    )


class TaskAttempt(Base):
    __tablename__ = "task_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    submitted_answer = Column(String(200), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    attempt_number = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    user = relationship("User", back_populates="attempts")
    task = relationship("Task", back_populates="attempts")
