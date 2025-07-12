# 确保导入所有必要的模块
from datetime import date
import os
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import secrets
from typing import Dict, List, Optional



app = FastAPI()

# 挂载静态文件目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR,"static")
print(STATIC_DIR)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
# app.mount("/static", StaticFiles(directory="app/static"), name="static")

# # /static：这是URL路径前缀，表示所有以/static开头的请求都会被交给StaticFiles处理。
# # StaticFiles(directory="static")：指定静态文件存放的目录为static。也就是说，static文件夹中的所有文件都可以通过/static路径来访问。
# # name="static"：为挂载的静态文件设置一个名称，可以方便地引用。



# 设置模板目录
# 获取当前文件所在目录
BASE_DIR = Path(__file__).resolve().parent

# 配置模板目录
TEMPLATE_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))
# # /templates：这是模板文件存放的目录，FastAPI会在这个目录下查找HTML模板文件。
# 模拟数据库 - 实际应用中应替换为真实数据库

# ========模板定义==============

from pydantic import BaseModel

class BaseInfo(BaseModel):
    real_name: str
    gender: str
    birthday: date
    height: float
    weight: float
    
#生活习惯
class Habit(BaseModel):
    habit: str
    frequency: int
    

class Psychology(BaseModel):
    ste:str

class User(BaseModel):
    username: str
    password: str
    #...
    baseInfo: BaseInfo

class Advice(BaseModel):
    advice: str
    content: str



# ===============全局变量===================

# 存储所有用户数据
users_db: Dict[str, User] = {}

# 存储当前登录用户
active_users: Dict[str, str] = {}  # session_id: username

# 对话历史
chat_history: Dict[str, List[Dict[str, str]]] = {}  # username: [message1, message2,...]
"""
user: [sender, message, time]
示例
chat_history = {
    "user1": [
        {"sender": "user1", "message": "hello", "time": "刚刚"},
        {"sender": "user2", "message": "hi", "time": "1分钟前"}
    ],
    "user2": [
        {"sender": "user2", "message": "how are you", "time": "2分钟前"}
    ]
}
"""

# 当前用户信息
my_info:User

advice: Dict[str, str]

#=========================功能函数==============================


# 获取当前用户
def get_current_user(request: Request)->Optional[User]:
    session_id = request.cookies.get("session_id")
    print(session_id, "尝试获取当前用户")
    if session_id and session_id in active_users:
        username = active_users[session_id]
        print(f"当前用户：{username}")

        return User(username=username, password="password")
    
        return users_db.get(username)
    
    print("未登录，返回None")
    return None


# 获取所有用户列表
def get_all_users()->List[User]:

    return list(users_db.values())


# 登录验证
def authenticate_user(username: str, password: str)->Optional[User]:
    # 检查硬编码的admin用户
    if username == "123" and password == "321":
        # 创建并返回User对象
        return User(username=username, password=password)
    # 检查数据库中的用户
    user = users_db.get(username)
    if user and user.password == password:
        return user
    return None


# 注册功能
def sign_up(username: str, password: str)->User:

    return User(username=username, password=password)


# ai回答生成
def generate_ai_reponse(user_input:str,model:str,temperature:float,max_tokens:int)->str:


    ai_response = ""
    return ai_response

# =================路由定义========================

# 首页路由
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, current_user: Optional[User] = Depends(get_current_user)):

    # 获取当前用户
    if not current_user:
        # 如果未登录，重定向到登录页面
        print("未登录，重定向到登录页面")
        return templates.TemplateResponse("login.html", {"request": request})
    

    print("已登录，显示主页")
    # 获取所有用户列表（用于用户切换）
    all_users = get_all_users()
    
    # 传递
    # 1. 当前用户信息
    # 2. 所有用户列表

    return templates.TemplateResponse("index.html", {
        "request": request,
        "current_user": current_user,
        "all_users": all_users
    })

# 登录页面
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """
    
    """
    return templates.TemplateResponse("login.html", {"request": request})


# 登录处理
@app.post("/login",summary="登录请求处理函数")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    """
    登录请求处理函数
    - **username**: 用户名
    - **password**: 密码
    
    """
    print(username, password,"尝试登录")
    user = authenticate_user(username, password)
    if not user:
        print("登录失败，返回错误页面")
        # 打印传递给模板的参数
        print(f"传递给模板的参数: request={request}, error={'用户名或密码错误'}")
        return templates.TemplateResponse(
            name="login.html", 
            context={
                "request": request,
                "error": "用户名或密码错误"
            }
        )
    

    
    # 创建session
    session_id = secrets.token_urlsafe(16)
    active_users[session_id] = username
    
    # 设置重定向响应
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        samesite="Lax"
    )
    return response


# 退出登录
@app.get("/logout")
async def logout(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id in active_users:
        del active_users[session_id]
    
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("session_id")
    return response


# 切换用户
@app.post("/switch-user")
async def switch_user(
    request: Request,
    target_user: str = Form(...),
    current_user: Optional[User] = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="未登录")
    
    if target_user not in users_db:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新当前会话的用户
    session_id = request.cookies.get("session_id")
    if session_id:
        active_users[session_id] = target_user
    
    return JSONResponse(content={"status": "success", "username": target_user})


# 添加新用户
@app.post("/add-user")
async def add_user(
    request: Request,
    new_username: str = Form(...),
    new_password: str = Form(...),
    current_user: Optional[User] = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="未登录")
    
    if new_username in users_db:
        return JSONResponse(content={"status": "error", "message": "用户名已存在"})
    
    # 创建新用户
    users_db[new_username] = User(
        username=new_username,
        password=new_password
    )
    
    return JSONResponse(content={"status": "success", "username": new_username})

# 导航页面路由
@app.get("/{view_name}", response_class=HTMLResponse)
async def get_view(
    request: Request,
    view_name: str,
    current_user: Optional[User] = Depends(get_current_user)
):
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    valid_views = ["home", "chat", "test", "profile", "advice"]
    
    if view_name not in valid_views:
        raise HTTPException(status_code=404, detail="页面不存在")
    
    # 获取所有用户列表
    all_users = list(users_db.values())
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "current_user": current_user,
        "all_users": all_users,
        "active_view": view_name
    })

# 聊天消息发送
@app.post("/send-message")
async def send_message(
    request: Request,
    message: str = Form(...),
    current_user: Optional[User] = Depends(get_current_user)
):
    if not current_user:
        raise HTTPException(status_code=401, detail="未登录")
    
    # 在实际应用中，这里会处理消息存储和转发
    return JSONResponse(content={
        "status": "success",
        "sender": current_user.username,
        "message": message,
        "time": "刚刚"
    })

# 获取用户列表
@app.get("/api/users", response_class=JSONResponse)
async def get_users(current_user: Optional[User] = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="未登录")
    
    return [user.dict() for user in users_db.values()]



# 启动应用
if __name__ == "__main__":

    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
