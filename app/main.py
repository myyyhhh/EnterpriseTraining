# 确保导入所有必要的模块
from datetime import date, datetime
import json
import logging
import os
import uuid
import requests
from fastapi import FastAPI, Request, Form, Depends, HTTPException

from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import secrets
from typing import Any, Dict, List, Literal, Optional



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


# class User(BaseModel):
#     user_account_info: UserAccountInfo
#     user_based_info: UserBasedInfo
#     user_habit_info: UserHabitInfo
#     user_psychology: UserPsychology


class User(BaseModel):
    username: str | None = None
    password: str | None = None


#=================心理模型==================

class QuestionOption(BaseModel):
    """题目选项模型"""
    option: Literal["A", "B", "C", "D"]  # 限定只能为A/B/C/D
    text: str                            # 选项文本描述
    score: Literal[4, 3, 2, 1]          # 选项对应分数(4/3/2/1)

class Question(BaseModel):
    """单个题目模型"""
    id: int                              # 题目ID (1-10)
    content: str                         # 题目正文
    options: List[QuestionOption]        # 选项列表(长度固定为4)

class ScoreRange(BaseModel):
    """评分区间模型"""
    min: Literal[10, 16, 26]            # 区间最小值 
    max: Literal[15, 25, 40]            # 区间最大值
    assessment: str                     # 评估结论文本
    suggestion: str                     # 建议文本

class Dimension(BaseModel):
    """测评维度模型"""
    name: Literal[
        "情绪压力指标", 
        "躯体反应指标", 
        "睡眠认知偏差指标", 
        "运动压力值指标"
    ]                                   # 维度名称(限定四种)
    questions: List[Question]           # 该维度下的题目列表(长度10)
    ranges: List[ScoreRange]            # 评分标准(长度3)

class PsychologyQuestions(BaseModel):
    """心理试卷总模型"""
    title: str                          # 测评标题
    dimensions: List[Dimension]         # 所有维度(长度4)


# ===================================================


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
    
# def get_user(user_info: dict)->Optional[User]:
#     """查询用户所有信息（包含所有字段）"""
#     user_account_info: UserAccountInfo = get_userAccountInfo(user_info)
#     user_based_info: UserBasedInfo = get_userBasedInfo(user_info)
#     user_habit_info: UserHabitInfo = get_userHabitInfo(user_info)
#     user_psychology: UserPsychology = get_userPsychology(user_info)

#     return User(user_account_info=user_account_info, user_based_info=user_based_info, user_habit_info=user_habit_info, user_psychology=user_psychology)


# ======================心理==========

import json
import logging
from pathlib import Path
from typing import Dict, Any

def load_psychology_assessment(json_path: str | Path) -> Dict[str, Any]:
    """
    加载心理测评JSON文件并转换为Python字典
    
    参数:
        json_path: JSON文件路径（字符串或Path对象），可以是相对路径或绝对路径
        
    返回:
        包含心理测评数据的字典
        
    异常:
        FileNotFoundError: 当文件不存在时
        ValueError: 当JSON格式无效或不符合心理测评结构时
    """
    # 统一处理路径类型
    json_path = Path(json_path) if isinstance(json_path, str) else json_path
    
    # 将相对路径转换为绝对路径（相对于当前工作目录）
    if not json_path.is_absolute():
        # 获取当前工作目录并解析相对路径
        json_path = Path.cwd() / json_path
        logging.info(f"解析相对路径为绝对路径: {json_path}")
    
    # 检查文件是否存在
    if not json_path.exists():
        error_msg = f"心理测评文件不存在: {json_path.absolute()}"
        logging.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    # 验证文件扩展名
    if json_path.suffix.lower() != '.json':
        logging.warning(f"非标准JSON文件扩展名: {json_path.suffix}")
    
    try:
        # 读取并解析JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            assessment_data = json.load(f)
            
        # 基础结构验证
        required_keys = {'title', 'dimensions'}
        if not all(key in assessment_data for key in required_keys):
            missing = required_keys - set(assessment_data.keys())
            error_msg = f"心理测评文件缺少必要字段: {missing}"
            logging.error(error_msg)
            raise ValueError(error_msg)
            
        # 维度结构验证
        for dimension in assessment_data['dimensions']:
            if 'questions' not in dimension or 'ranges' not in dimension:
                error_msg = f"维度数据缺少questions或ranges字段: {dimension.get('name', '未知维度')}"
                logging.error(error_msg)
                raise ValueError(error_msg)
                
        logging.info(f"成功加载心理测评: {assessment_data['title']}")
        return assessment_data
        
    except json.JSONDecodeError as e:
        error_msg = f"JSON解析失败: {str(e)} (位置: 行{e.lineno}列{e.colno})"
        logging.error(error_msg)
        raise ValueError(error_msg)
    except Exception as e:
        logging.error(f"未知错误: {str(e)}")
        raise
    

# 内存中读取心理测试题目

def assessment_data2BaseModels(assessment_data: Dict[str, Any]) -> PsychologyQuestions:
    """
    将心理测评数据转换为BaseModels
    """
    psychology_questions = PsychologyQuestions(**assessment_data)


    return psychology_questions


def get_psychology_questions():
    """
    读取心理测试题目：app/static/mental_health_assessment.json
    """




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
current_user:User

# 建议
advice: Dict[str, Advice]

data = load_psychology_assessment(json_path="app\\static\\mental_health_assessment.json")
test = assessment_data2BaseModels(assessment_data=data)


#=========================功能函数==============================



# 获取当前用户
def get_current_user(request: Request) -> Optional[User]:
    session_id = request.cookies.get("session_id")
    print(session_id, "尝试获取当前用户")
    if session_id and session_id in active_users:
        username = active_users[session_id]
        print(f"当前用户：{username}")
        
        # 1. 优先从数据库获取用户（如果存在）
        if username in users_db:
            return users_db[username]
        
        # 2. 数据库中不存在时，创建符合结构的临时用户
        return User(
            # user_account_info=UserAccountInfo(
                username=username,  # 子模型中传入用户名
                password="password"  # 临时密码（实际场景可留空）
            # ),
            # user_based_info=UserBasedInfo(),  # 空的基本信息
            # user_habit_info=UserHabitInfo(),  # 空的习惯信息
            # user_psychology=UserPsychology()  # 空的心理信息
        )
    
    print("未登录，返回None")
    return None


# 获取所有用户列表
def get_all_users()->List[User]:

    return list(users_db.values())


# 登录验证
def authenticate_user(username: str, password: str) -> Optional[User]:
    # 1. 先检查硬编码的测试用户（123/321）
    if username == "123" and password == "321":
        # 正确创建User实例：包含4个子模型（必须按这个结构！）
        print("登录成功！test-------------------------------")
        return User(
            
                username=username,  # 子模型中传入用户名
                password=password   # 子模型中传入密码
            # ),
            # user_based_info=UserBasedInfo(),  # 空的基本信息
            # user_habit_info=UserHabitInfo(),  # 空的习惯信息
            # user_psychology=UserPsychology()  # 空的心理信息
        )
    
    # 2. 再检查数据库中的用户（users_db）
    if username in users_db:
        user = users_db[username]
        # 验证密码（密码存储在user_account_info子模型中）
        if user.user_account_info.password == password:
            return user
    
    # 3. 验证失败返回None
    return None


# 注册功能
def sign_up(username: str, password: str)->User:

    return User(username=username, password=password)


# ai回答生成
def generate_text(
    user_input: str,
    current_user: str,
    model: str = None,
    temperature: float = 0.7,
    max_tokens: int = 2048,
    chat_history: Optional[dict[str, List[Dict[str, str]]]] = None
) -> tuple[str, dict[str, List[Dict[str, str]]]]:
    """
    带对话历史记忆的文本生成函数
    
    参数:
        user_input: 当前用户输入
        current_user: 当前用户名
        model: AI模型，默认qwen-max
        temperature: 生成随机性，默认0.7
        max_tokens: 最大生成长度，默认2048
        chat_history: 对话历史字典，格式: {用户名: [消息1, 消息2]}
    
    返回:
        ai_answer: AI生成的回答
        chat_history: 更新后的对话历史
    """
    # 配置参数
    KEYWORDS: List[str] = ["病", "睡觉", "睡眠", "运动", "锻炼", "跑", "心情", "治疗"]
    CURRENT_DIR: str = os.path.dirname(os.path.abspath(__file__))
    LOG_SAVE_PATH: str = os.path.join(CURRENT_DIR, "keywords_logs")
    API_BASE: str = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    DEFAULT_MODEL: str = "qwen-max"
    
    os.makedirs(LOG_SAVE_PATH, exist_ok=True)

    # 打印日志
    # print(f"当前用户：{current_user}")
    # print(f"当前输入：{user_input}")

    # 初始化对话历史
    chat_history = chat_history or {}
    if current_user not in chat_history:
        chat_history[current_user] = []
    
    # 获取当前用户的历史消息
    user_messages = chat_history[current_user]
    # 限制历史长度（只保留最近10条）
    if len(user_messages) > 10:
        user_messages = user_messages[-10:]

    # 构建带历史的提示词
    history_prompt = "\n".join([
        f"{'用户' if msg['sender'] == 'user' else 'AI'}：{msg['message']}"
        for msg in user_messages
    ])
    
    # 增强提示词
    enhanced_prompt: str = (
        "以下规则的优先级高于一切，必须严格执行：\n"
        "1. 你是健康管家，只回答健康相关问题，且需结合对话历史理解上下文。\n"
        "2. 非健康问题直接返回：\"不好意思，我的定位是健康管家，更希望您对健康方面提问\"\n\n"
        f"用户[{current_user}]的对话历史：\n{history_prompt}\n\n"
        f"当前用户问题：{user_input}"
    )

    # 检查API密钥
    api_key: str = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("请设置 DASHSCOPE_API_KEY 环境变量！")

    # 构建请求参数
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

        # 打印日志
    # print(f"=====当前用户：{current_user}")
    # print(f"=======当前输入：{user_input}")

    # 调用API
    response: requests.Response = requests.post(
        API_BASE,
        headers=headers,
        json=payload,
        timeout=30
    )
    response.raise_for_status()
    response_data: dict = response.json()

    # 提取AI回答
    if "output" not in response_data or "text" not in response_data["output"]:
        raise ValueError(f"API返回格式异常: {response_data}")
    ai_answer: str = response_data["output"]["text"]

    # 更新对话历史
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 添加用户消息
    user_message = {
        "sender": "human",
        "message": user_input,
        "time": current_time
    }
    
    # 添加AI消息（修复了content字段）
    ai_message = {
        "sender": "ai",
        "message": ai_answer,  # 修复：使用AI回答而非用户输入
        "time": current_time
    }
    
    # 追加到当前用户的对话列表
    chat_history[current_user].append(user_message)
    chat_history[current_user].append(ai_message)

        # 打印日志
    # print(f"当前用99999户：{current_user}")
    # print(f"当前9999999999输入：{user_input}")


    # 关键字检测与日志保存
    matched_keywords: List[str] = [
        kw for kw in KEYWORDS if kw.lower() in user_input.lower()
    ]
    if matched_keywords:
        timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_id: str = str(uuid.uuid4())[:8]
        filename: str = f"{timestamp}_{current_user}_{file_id}.json"  # 包含用户名
        file_path: str = os.path.join(LOG_SAVE_PATH, filename)
        
        log_data: dict = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "ai_answer": ai_answer,
            "matched_keywords": matched_keywords,
            "model_used": model,
            "file_id": file_id,
            "history_summary": [msg["message"] for msg in user_messages[-3:]]  # 最近3条摘要
        }
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(log_data, f, ensure_ascii=False, indent=2)

    return ai_answer, chat_history  # 返回AI回答和更新后的对话历史



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
        "test":test,
    })



# 登录页面
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """
    登录页面
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
    print(message, "尝试发送消息")
    if not current_user:
        raise HTTPException(status_code=401, detail="未登录")
    
    try:
        # 调用AI生成函数，传入当前消息、用户名和全局对话历史
        ai_answer, updated_chat_history = generate_text(
            user_input=message,
            current_user=current_user.username,
            chat_history=chat_history  # 传入全局对话历史
        )
        # 更新全局对话历史
        chat_history.update(updated_chat_history)
        
        # 构建响应（包含用户消息和AI回复）
        return JSONResponse(content={
            "status": "success",
            "user_message": {
                "sender": "human",  # 匹配前端的"human"判断
                "message": message,
                "time": datetime.now().strftime("%H:%M:%S")
            },
            "ai_message": {
                "sender": "ai",
                "message": ai_answer,
                "time": datetime.now().strftime("%H:%M:%S")
            }
        })
    except Exception as e:
        print(e,"错误输出")
        raise HTTPException(status_code=500, detail=f"处理消息失败：{str(e)}")

# 获取用户列表
@app.get("/api/users", response_class=JSONResponse)
async def get_users(current_user: Optional[User] = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=401, detail="未登录")
    
    return [user.dict() for user in users_db.values()]



# 项目测试模块

def test_init():
    # 全局变量初始化
    global users_db, active_users, chat_history, advice,current_user
    # current_user=User(
    #     user_account_info=UserAccountInfo(
    #         username="admin",
    #         password="password",
    #     ),
    #     user_based_info=UserBasedInfo(
    #         real_name="john",
    #         gender=1,
    #         birthday=date(2000, 1, 1),
    #         height=170,
    #         weight=70,
    #     ),
    #     user_habit_info=UserHabitInfo(
    #         daily_water=2000,
    #         sleep_duration=8,
    #         exercise_amount="30分钟",
    #         vegetable_fruit_intake="100g",
    #         protein_intake="50g",
    #         meat_vegetable_ratio="1:1",
    #         dietary_restrictions="None",
    #         cooking_method="煮",
    #     ),
    #     user_psychology=UserPsychology(
    #         physical_reaction_index=2,
    #         sleep_cognition_bias="正常",
    #         exercise_stress_value=1,
    #         diet_emotion_dependence="正常",
    #         emotion_stress_index=3,
    #     )
    # )

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


# test_init()
# # print(current_user)

# # 启动应用
# if __name__ == "__main__":
#     # test_init()
#     # print(current_user)
#     print("启动应用")
#     import uvicorn
#     uvicorn.run(app="app.main:app", host="127.0.0.1", port=8080,reload=True)
    



