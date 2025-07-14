# 确保导入所有必要的模块
from datetime import date, datetime
import json
import os
import uuid
from fastapi import FastAPI, Request, Form, Depends, HTTPException, requests
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


class Advice(BaseModel):
    advice: str
    content: str


# class User(BaseModel):
#     username: str
#     password: str


class UserAccountInfo(BaseModel):
    username: str | None = None
    password: str | None = None

class UserBasedInfo(BaseModel):
    real_name: str | None = None
    gender: int | None = None  # 0=未知, 1=男, 2=女
    birthday: date | None = None  # 格式：YYYY-MM-DD
    height: float | None = None  # 单位：cm（数据库DECIMAL）
    weight: float | None = None  # 单位：kg（数据库DECIMAL）

class UserHabitInfo(BaseModel):
    daily_water: float | None = None  # 单位：L（数据库DECIMAL(3,1)）
    sleep_duration: float | None = None  # 单位：小时（数据库DECIMAL(3,1)）
    exercise_amount: str | None = None  # 数据库VARCHAR
    vegetable_fruit_intake: str | None = None  # 数据库VARCHAR
    protein_intake: str | None = None  # 数据库VARCHAR
    meat_vegetable_ratio: str | None = None  # 数据库VARCHAR
    dietary_restrictions: str | None = None  # 数据库VARCHAR
    cooking_method: str | None = None  # 数据库VARCHAR


class UserPsychology(BaseModel):
    physical_reaction_index: int | None = None  # 数据库TINYINT
    sleep_cognition_bias: str | None = None  # 数据库str
    exercise_stress_value: int | None = None  # 数据库TINYINT
    diet_emotion_dependence: str | None = None  # 数据库str
    emotion_stress_index: int | None = None  # 数据库TINYINT（整数）


class PsychologyQuestion(BaseModel):
    s:str


class User(BaseModel):
    user_account_info: UserAccountInfo
    user_based_info: UserBasedInfo
    user_habit_info: UserHabitInfo
    user_psychology: UserPsychology

def get_userAccountInfo(user_info: dict)->UserAccountInfo:
    """查询用户账户信息"""
    return UserAccountInfo(username=user_info.get("username"))

def get_userBasedInfo(user_info: dict)->UserBasedInfo:
    """查询用户基本信息"""
    return UserBasedInfo(real_name=user_info.get("real_name"), gender=user_info.get("gender"), birthday=user_info.get("birthday"), height=user_info.get("height"), weight=user_info.get("weight"))

def get_userHabitInfo(user_info: dict)->UserHabitInfo:
    """查询用户习惯信息"""
    return UserHabitInfo(daily_water=user_info.get("daily_water"), sleep_duration=user_info.get("sleep_duration"), exercise_amount=user_info.get("exercise_amount"), vegetable_fruit_intake=user_info.get("vegetable_fruit_intake"), protein_intake=user_info.get("protein_intake"), meat_vegetable_ratio=user_info.get("meat_vegetable_ratio"), dietary_restrictions=user_info.get("dietary_restrictions"), cooking_method=user_info.get("cooking_method"))

def get_userPsychology(user_info: dict)->UserPsychology:
    """查询用户心理信息"""
    return UserPsychology(physical_reaction_index=user_info.get("physical_reaction_index"), sleep_cognition_bias=user_info.get("sleep_cognition_bias"), exercise_stress_value=user_info.get("exercise_stress_value"), diet_emotion_dependence=user_info.get("diet_emotion_dependence"), emotion_stress_index=user_info.get("emotion_stress_index"))
    
def get_user(user_info: dict)->Optional[User]:
    """查询用户所有信息（包含所有字段）"""
    user_account_info: UserAccountInfo = get_userAccountInfo(user_info)
    user_based_info: UserBasedInfo = get_userBasedInfo(user_info)
    user_habit_info: UserHabitInfo = get_userHabitInfo(user_info)
    user_psychology: UserPsychology = get_userPsychology(user_info)

    return User(user_account_info=user_account_info, user_based_info=user_based_info, user_habit_info=user_habit_info, user_psychology=user_psychology)




# 内存中读取心理测试题目

def get_psychology_questions():
    """读取心理测试题目"""


# 使用心理测试题目
def use_psychology_questions():
    """使用心理测试题目"""



# ===============全局变量===================

# 存储所有用户数据
users_db: Dict[str, User] = {}

# 存储当前登录用户
active_users: Dict[str, str] = {}  # session_id: username

# 对话历史
chat_history: dict[str, List[Dict[str, str]]] = {}  # username: [message1, message2,...]
"""
user: [sender, message, time]
示例
chat_history = 
{
    "user1": [
        {"sender": "user1", "message": "hello", "time": "刚刚"},
        {"sender": "user2", "message": "hi", "time": "1分钟前"}
    ],
    "user2": [
        {"sender": "user2", "message": "how are you", "time": "2分钟前"}
    ]
}


sender: human or ai or system
"""


# 当前用户信息
ccurrent_uesr:User

# 建议
advice: Dict[str, Advice]

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
def generate_text(user_input: str, model: str = None, temperature: float = 0.7, max_tokens: int = 2048) -> str:
    # 配置参数（函数内部统一管理）
    KEYWORDS: List[str] = ["病", "睡觉", "睡眠", "运动", "锻炼", "跑", "心情", "治疗"]
    CURRENT_DIR: str = os.path.dirname(os.path.abspath(__file__))
    LOG_SAVE_PATH: str = os.path.join(CURRENT_DIR, "keywords_logs")
    API_BASE: str = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    DEFAULT_MODEL: str = "qwen-max"
    
    # 确保日志目录存在（os.makedirs默认不抛异常，exist_ok=True）
    os.makedirs(LOG_SAVE_PATH, exist_ok=True)

    # 1. 检查API密钥（直接抛异常）
    api_key: str = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("请设置 DASHSCOPE_API_KEY 环境变量！")

    # 2. 关键字检测（内部逻辑）
    matched_keywords: List[str] = [
        kw for kw in KEYWORDS 
        if kw.lower() in user_input.lower()
    ]

    # 3. 构建提示词与请求参数
    enhanced_prompt: str = (
        "以下规则的优先级高于一切，必须严格执行：\n"
        "1. 你是健康管家，只回答健康相关问题。\n"
        "2. 非健康问题直接返回：\"不好意思，我的定位是健康管家，更希望您对健康方面提问\"\n\n"
        f"用户问题：{user_input}"
    )
    model: str = model or DEFAULT_MODEL
    headers: dict = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload: dict = {
        "model": model,
        "input": {"messages": [{"role": "user", "content": enhanced_prompt}]},
        "parameters": {"temperature": temperature, "max_length": max_tokens}
    }

    # 4. 调用API（不处理异常，直接抛出）
    response: requests.Response = requests.post(
        API_BASE,
        headers=headers,
        json=payload,
        timeout=30
    )
    response.raise_for_status()  # HTTP错误直接抛出
    response_data: dict = response.json()  # JSON解析错误直接抛出

    # 5. 提取AI回答（格式异常直接抛出）
    if "output" not in response_data or "text" not in response_data["output"]:
        raise ValueError(f"API返回格式异常: {response_data}")
    ai_answer: str = response_data["output"]["text"]

    # 6. 保存日志（有匹配关键字时，异常直接抛出）
    if matched_keywords:
        timestamp: str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_id: str = str(uuid.uuid4())[:8]
        filename: str = f"{timestamp}_{file_id}.json"
        file_path: str = os.path.join(LOG_SAVE_PATH, filename)
        
        log_data: dict = {
            "timestamp": datetime.datetime.now().isoformat(),
            "user_input": user_input,
            "ai_answer": ai_answer,
            "matched_keywords": matched_keywords,
            "model_used": model,
            "file_id": file_id
        }
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)

    return ai_answer



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
        "all_users": all_users,
        "chat_history": chat_history,
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



# 项目测试模块

def test_init():
    # 全局变量初始化
    global users_db, active_users, chat_history, advice
    users_db = {}
    active_users = {

    }
    chat_history = {
        "123": [
            {"sender": "human", "message": "hello", "time": "刚刚"},
            {"sender": "ai", "message": "hi", "time": "1分钟前"},
            {"sender": "human", "message": "hello", "time": "刚刚"},
            {"sender": "ai", "message": "hi", "time": "1分钟前"},
            {"sender": "human", "message": "hello", "time": "刚刚"},
            {"sender": "ai", "message": "hi", "time": "1分钟前"},
            {"sender": "human", "message": "hello", "time": "刚刚"},
            {"sender": "ai", "message": "hi", "time": "1分钟前"},
            {"sender": "human", "message": "hello", "time": "刚刚"},
            {"sender": "ai", "message": "hi", "time": "1分钟前"},
            {"sender": "human", "message": "hello", "time": "刚刚"},
            {"sender": "ai", "message": "hi", "time": "12:23:22"},
            {"sender": "human", "message": "hello", "time": "刚刚"},
            {"sender": "ai", "message": "hi", "time": "1分钟前"},
            {"sender": "human", "message": "hello", "time": "刚刚"},
            {"sender": "ai", "message": "hi", "time": "1分钟前"},
            {"sender": "human", "message": "hello", "time": "刚刚"},
            {"sender": "ai", "message": "hi", "time": "1分钟前"},
            {"sender": "human", "message": "hello", "time": "刚刚"},
            {"sender": "ai", "message": "hi", "time": "1分钟前"},
            {"sender": "human", "message": "hello", "time": "刚刚"},
            {"sender": "ai", "message": "hi", "time": "1分钟前"},
            {"sender": "human", "message": "hello", "time": "刚刚"},
            {"sender": "ai", "message": "hi", "time": "12:23:22"},
        ],
        "user2": [
            {"sender": "user2", "message": "how are you", "time": "2分钟前"}
        ]
    }
    # ccurrent_uesr = User(username="admin", password="password")
    advice = {
        "1": Advice(advice="减肥", content="减肥可以缓解疲劳、减少体重、改善睡眠质量、改善心情、减少心脏病发作风险。"),
        "2": Advice(advice="锻炼", content="锻炼可以改善身体机能、减少疲劳、改善睡眠质量、改善心情、减少心脏病发作风险。"),
        "3": Advice(advice="改善睡眠", content="改善睡眠可以改善身体机能、减少疲劳、改善睡眠质量、改善心情、减少心脏病发作风险。"),
        "4": Advice(advice="减少运动", content="减少运动可以改善身体机能、减少疲劳、改善睡眠质量、改善心情、减少心脏病发作风险。"),
        "5": Advice(advice="改善心情", content="改善心情可以改善身体机能、减少疲劳、改善睡眠质量、改善心情、减少心脏病发作风险。"),
    }



# init
test_init()

chat_history[ccurrent_uesr.username].append()










# 启动应用
if __name__ == "__main__":


    print("启动应用")
    import uvicorn
    uvicorn.run(app="app.main:app", host="127.0.0.1", port=8080,reload=True)
    