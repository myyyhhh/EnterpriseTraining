from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from ..config import templates, active_users, users_db
from ..dependencies import get_current_user
from ..services.user_service import authenticate_user, create_user
import secrets

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, current_user=Depends(get_current_user)):
    if not current_user:
        return RedirectResponse("/login")
    return templates.TemplateResponse("index.html", {
        "request": request, "current_user": current_user, "users": users_db.values()
    })

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = authenticate_user(username, password)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request, "error": "用户名或密码错误"})
    
    # 创建会话
    session_id = secrets.token_urlsafe(16)
    active_users[session_id] = username
    response = RedirectResponse("/", status_code=302)
    response.set_cookie("session_id", session_id, httponly=True)
    return response

@router.post("/logout")
async def logout(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id in active_users:
        del active_users[session_id]
    response = RedirectResponse("/login")
    response.delete_cookie("session_id")
    return response

@router.post("/register", response_class=JSONResponse)
async def register(username: str = Form(...), password: str = Form(...)):
    try:
        user = create_user(username, password)
        return {"status": "success", "username": username}
    except ValueError as e:
        return {"status": "error", "message": str(e)}