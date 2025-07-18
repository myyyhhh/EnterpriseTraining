from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import secrets

from app.config import TEMPLATE_DIR
from app.database import active_users, users_db, current_user
from app.services.auth_service import authenticate_user, sign_up
from app.models.user import User

router = APIRouter(tags=["认证"])
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

# 登录页面
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# 登录处理
@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    user = authenticate_user(username, password)
    if not user:
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error": "用户名或密码错误"}
        )
    
    # 创建会话
    session_id = secrets.token_urlsafe(16)
    active_users[session_id] = username
    global current_user
    current_user = user  # 更新当前用户

    # 设置Cookie并重定向
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        samesite="Lax"
    )
    return response

# 退出登录
@router.get("/logout")
async def logout(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id in active_users:
        del active_users[session_id]
    
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("session_id")
    return response

# 注册路由
@router.post("/signup")
async def signup(
    username: str = Form(...),
    password: str = Form(...)
):
    if username in users_db:
        return JSONResponse(
            content={"status": "error", "message": "用户名已存在"},
            status_code=400
        )
    user = sign_up(username, password)
    users_db[username] = user
    return JSONResponse(
        content={"status": "success", "message": "注册成功"}
    )