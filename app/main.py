import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base, SessionLocal
from app.seed_data import seed_database
from app.websocket_manager import manager
from app.api import auth, hierarchy, tasks, teacher, presence

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure tables exist and seed database
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield
    # Shutdown

app = FastAPI(
    title="Шкільна платформа уроків та завдань",
    description="Інтерактивна система навчання математики з живим моніторингом для вчителів",
    version="1.0.0",
    lifespan=lifespan
)

# CORS setup for LAN / ngrok flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static and Templates
app_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(app_dir, "static")
templates_dir = os.path.join(app_dir, "templates")

app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates = Jinja2Templates(directory=templates_dir)

# Register API Routers
app.include_router(auth.router)
app.include_router(hierarchy.router)
app.include_router(tasks.router)
app.include_router(teacher.router)
app.include_router(presence.router)

# HTML Views
@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/hierarchy", response_class=HTMLResponse)
async def hierarchy_page(request: Request):
    return templates.TemplateResponse(request=request, name="select_hierarchy.html")

@app.get("/room/{room_code}", response_class=HTMLResponse)
async def student_room_page(room_code: str, request: Request):
    return templates.TemplateResponse(request=request, name="topic_student.html", context={"room_code": room_code})

@app.get("/teacher/room/{room_code}", response_class=HTMLResponse)
async def teacher_room_page(room_code: str, request: Request):
    return templates.TemplateResponse(request=request, name="teacher_cabinet.html", context={"room_code": room_code})

# Real-Time WebSocket Endpoint
@app.websocket("/ws/room/{room_code}/{client_type}/{user_id}")
async def websocket_room_endpoint(websocket: WebSocket, room_code: str, client_type: str, user_id: int):
    if client_type == "teacher":
        await manager.connect_teacher(room_code, websocket)
        try:
            while True:
                data = await websocket.receive_text()
                # Teacher ping/pong or control messages
        except WebSocketDisconnect:
            manager.disconnect_teacher(room_code, websocket)
    else:
        await manager.connect_student(room_code, user_id, websocket)
        try:
            while True:
                data = await websocket.receive_text()
        except WebSocketDisconnect:
            manager.disconnect_student(room_code, user_id)
