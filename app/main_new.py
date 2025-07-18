# 导入
from datetime import date, datetime
import json
import logging
import os
import re
import uuid
import secrets
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple
import requests
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel


app = FastAPI()

# 挂载静态文件目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR,"static")
# print(STATIC_DIR)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")




# 设置模板目录
# 获取当前文件所在目录
BASE_DIR = Path(__file__).resolve().parent

# 配置模板目录
TEMPLATE_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))


# ========模板定义==============

from pydantic import BaseModel


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
    # 修改
    physical_reaction_index: str | None = None  # 数据库TINYINT ：躯体反应
    sleep_cognition_bias: str | None = None  # 数据库str：睡眠认知偏差
    exercise_stress_value: str | None = None  # 数据库TINYINT：运动压力值
    emotion_stress_index: str | None = None  # 数据库TINYINT（整数）：情绪压力指标


class User(BaseModel):
    user_account_info: UserAccountInfo
    user_based_info: UserBasedInfo
    user_habit_info: UserHabitInfo
    user_psychology: UserPsychology

def user_get_username(user:User)->str:
    return user.user_account_info.username

def user_set_user(user:User,new_user:User)->None:
    # 1. 更新账户信息（仅更新非空字段）
    if updated_user.user_account_info:
        if updated_user.user_account_info.username is not None:
            target_user.user_account_info.username = updated_user.user_account_info.username
        if updated_user.user_account_info.password is not None:
            target_user.user_account_info.password = updated_user.user_account_info.password  # 实际应用中应加密
    
    # 2. 更新基本信息
    if updated_user.user_based_info:
        if updated_user.user_based_info.real_name is not None:
            target_user.user_based_info.real_name = updated_user.user_based_info.real_name
        if updated_user.user_based_info.gender is not None:
            target_user.user_based_info.gender = updated_user.user_based_info.gender
        if updated_user.user_based_info.birthday is not None:
            target_user.user_based_info.birthday = updated_user.user_based_info.birthday
        if updated_user.user_based_info.height is not None:
            target_user.user_based_info.height = updated_user.user_based_info.height
        if updated_user.user_based_info.weight is not None:
            target_user.user_based_info.weight = updated_user.user_based_info.weight
    
    # 3. 更新生活习惯信息
    if updated_user.user_habit_info:
        if updated_user.user_habit_info.daily_water is not None:
            target_user.user_habit_info.daily_water = updated_user.user_habit_info.daily_water
        if updated_user.user_habit_info.sleep_duration is not None:
            target_user.user_habit_info.sleep_duration = updated_user.user_habit_info.sleep_duration
        if updated_user.user_habit_info.exercise_amount is not None:
            target_user.user_habit_info.exercise_amount = updated_user.user_habit_info.exercise_amount
        if updated_user.user_habit_info.vegetable_fruit_intake is not None:
            target_user.user_habit_info.vegetable_fruit_intake = updated_user.user_habit_info.vegetable_fruit_intake
        if updated_user.user_habit_info.protein_intake is not None:
            target_user.user_habit_info.protein_intake = updated_user.user_habit_info.protein_intake
        if updated_user.user_habit_info.meat_vegetable_ratio is not None:
            target_user.user_habit_info.meat_vegetable_ratio = updated_user.user_habit_info.meat_vegetable_ratio
        if updated_user.user_habit_info.dietary_restrictions is not None:
            target_user.user_habit_info.dietary_restrictions = updated_user.user_habit_info.dietary_restrictions
        if updated_user.user_habit_info.cooking_method is not None:
            target_user.user_habit_info.cooking_method = updated_user.user_habit_info.cooking_method
    
    # 4. 更新心理信息
    if updated_user.user_psychology:
        if updated_user.user_psychology.physical_reaction_index is not None:
            target_user.user_psychology.physical_reaction_index = updated_user.user_psychology.physical_reaction_index
        if updated_user.user_psychology.sleep_cognition_bias is not None:
            target_user.user_psychology.sleep_cognition_bias = updated_user.user_psychology.sleep_cognition_bias
        if updated_user.user_psychology.exercise_stress_value is not None:
            target_user.user_psychology.exercise_stress_value = updated_user.user_psychology.exercise_stress_value
        # if updated_user.user_psychology.diet_emotion_dependence is not None:
        #     target_user.user_psychology.diet_emotion_dependence = updated_user.user_psychology.diet_emotion_dependence
        if updated_user.user_psychology.emotion_stress_index is not None:
            target_user.user_psychology.emotion_stress_index = updated_user.user_psychology.emotion_stress_index


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

def setPsychologyTestResult(user:User,result:list[str]):
    """设置心理测评结果"""
    user.user_psychology.physical_reaction_index = result[0]
    user.user_psychology.sleep_cognition_bias = result[1]
    user.user_psychology.exercise_stress_value = result[2]
    user.user_psychology.emotion_stress_index = result[3]

# ======================数据库中信息读取成user对象=======================


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
    return UserPsychology(
        physical_reaction_index=user_info.get("physical_reaction_index"), 
        sleep_cognition_bias=user_info.get("sleep_cognition_bias"), 
        exercise_stress_value=user_info.get("exercise_stress_value"), 
        emotion_stress_index=user_info.get("emotion_stress_index")
        )
    
def get_user(user_info: dict)->Optional[User]:
    """查询用户所有信息（包含所有字段）"""
    user_account_info: UserAccountInfo = get_userAccountInfo(user_info)
    user_based_info: UserBasedInfo = get_userBasedInfo(user_info)
    user_habit_info: UserHabitInfo = get_userHabitInfo(user_info)
    user_psychology: UserPsychology = get_userPsychology(user_info)

    return User(user_account_info=user_account_info, user_based_info=user_based_info, user_habit_info=user_habit_info, user_psychology=user_psychology)


# ======================心理测试==========

# 内存中读取心理测试题目
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



# =======================================项目测试模块====================================


def get_some_user()->User:
    return User(
            user_account_info=UserAccountInfo(
                username="test_user_001",
                password="test_password_123"  # 实际测试时可使用加密后的密码
            ),
            user_based_info=UserBasedInfo(
                real_name="张三",
                gender=1,  # 1=男，2=女，0=未知
                birthday=date(1990, 5, 15),
                height=175.5,  # 单位：cm
                weight=70.3    # 单位：kg
            ),
            user_habit_info=UserHabitInfo(
                daily_water=1.8,  # 单位：L
                sleep_duration=7.5,  # 单位：小时
                exercise_amount="每周3次，每次40分钟",
                vegetable_fruit_intake="每天约500克",
                protein_intake="每天约70克",
                meat_vegetable_ratio="3:7",
                dietary_restrictions="海鲜过敏",
                cooking_method="蒸、煮为主，少油少盐"
            ),
            user_psychology=UserPsychology(
                physical_reaction_index="偶尔会有心理压力",  
                sleep_cognition_bias="偶尔会担心失眠，但影响不大",
                exercise_stress_value="偶尔会有运动压力",  
                emotion_stress_index="情绪压力指标： "  
            )
        )

def get_some_chatHistory()->dict:
    return {
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

def test_init():
    # 全局变量初始化/generate-advice
    global users_db, active_users, chat_history,current_user
    

    current_user = get_some_user()
    chat_history = get_some_chatHistory()


# ===============全局变量===================



# 存储session的当前登录用户
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



psychology_questions = load_psychology_assessment(json_path="app\\static\\mental_health_assessment.json")

test = assessment_data2BaseModels(assessment_data=psychology_questions)


#=========================功能函数==============================

# _________________________用户信息_______________________

# 获取当前用户
def get_current_user(request: Request) -> Optional[User]:

    session_id = request.cookies.get("session_id")
    print(session_id, "尝试获取当前用户")
    if session_id and session_id in active_users:
        username = active_users[session_id]
        print(f"当前用户：{username}")
        
        # 1. 优先从数据库获取用户（如果存在）
        if db_user_exists(username):
            return db_get_user(username)
        
        # 2. 数据库中不存在时，创建符合结构的临时用户
        # return User(
        #     # user_account_info=UserAccountInfo(
        #         username=username,  # 子模型中传入用户名
        #         password="password"  # 临时密码（实际场景可留空）
        #     # ),
        #     # user_based_info=UserBasedInfo(),  # 空的基本信息
        #     # user_habit_info=UserHabitInfo(),  # 空的习惯信息
        #     # user_psychology=UserPsychology()  # 空的心理信息
        # )
    
    print("未登录，返回None")
    return None


# # 获取所有用户列表
# def get_all_users()->List[User]:

#     return list(users_db.values())


# 创建一个新用户
def get_new_user(username: str, password: str)->User:
    return User(
        user_account_info=UserAccountInfo(
            username=username,
            password=password
        ),
        user_based_info=UserBasedInfo(),
        user_habit_info=UserHabitInfo(),
        user_psychology=UserPsychology()
    )


# __________________数据库函数_______________________


# 存储所有用户数据
users_db: Dict[str, User] = {
    "test_user_001":get_some_user()

}

def db_user_exists(username: str)->bool:
    """
    检查数据库中是否存在指定用户名的用户
    """
    return username in users_db

def db_get_user(username: str)->Optional[User]:
    """
    从数据库中获取指定用户名的用户
    """
    if db_user_exists(username):
        return users_db[username]
    
    logging.warning(f"F(db_get_user):数据库中不存在用户名为{username}的用户")
    return None

def db_add_user(user: User)->None:
    """
    向数据库中添加用户
    """
    if db_user_exists(user.user_account_info.username):
        logging.warning(f"F(db_add_user):数据库中已存在用户名为{user.user_account_info.username}的用户")
        return
    
    users_db[user.user_account_info.username] = user

def db_authenticate_user(username: str, password: str)->Optional[User]:
    """
    验证用户名和密码是否匹配,返回User对象或None
    """
    if db_user_exists(username=username):
        user = db_get_user(username=username)
        if user.user_account_info.password == password:
            return user
    
    # 3. 验证失败返回None

def db_update_user(updated_user: User)->None:
    """
    更新数据库中指定用户的信息
    """
    if not db_user_exists(user_get_username(updated_user)):
        logging.warning(f"F(db_update_user):数据库中不存在用户名为{updated_user.user_account_info.username}的用户")
        return
    
    #****** 数据库操作：更新，这是暂时的************
    # 1. 更新用户名和密码
    target_user = db_get_user(user_get_username(updated_user))
    if updated_user.user_account_info:
        if updated_user.user_account_info.username is not None:
            target_user.user_account_info.username = updated_user.user_account_info.username
        if updated_user.user_account_info.password is not None:
            target_user.user_account_info.password = updated_user.user_account_info.password  # 实际应用中应加密
    
    # 2. 更新基本信息
    if updated_user.user_based_info:
        if updated_user.user_based_info.real_name is not None:
            target_user.user_based_info.real_name = updated_user.user_based_info.real_name
        if updated_user.user_based_info.gender is not None:
            target_user.user_based_info.gender = updated_user.user_based_info.gender
        if updated_user.user_based_info.birthday is not None:
            target_user.user_based_info.birthday = updated_user.user_based_info.birthday
        if updated_user.user_based_info.height is not None:
            target_user.user_based_info.height = updated_user.user_based_info.height
        if updated_user.user_based_info.weight is not None:
            target_user.user_based_info.weight = updated_user.user_based_info.weight
    
    # 3. 更新生活习惯信息
    if updated_user.user_habit_info:
        if updated_user.user_habit_info.daily_water is not None:
            target_user.user_habit_info.daily_water = updated_user.user_habit_info.daily_water
        if updated_user.user_habit_info.sleep_duration is not None:
            target_user.user_habit_info.sleep_duration = updated_user.user_habit_info.sleep_duration
        if updated_user.user_habit_info.exercise_amount is not None:
            target_user.user_habit_info.exercise_amount = updated_user.user_habit_info.exercise_amount
        if updated_user.user_habit_info.vegetable_fruit_intake is not None:
            target_user.user_habit_info.vegetable_fruit_intake = updated_user.user_habit_info.vegetable_fruit_intake
        if updated_user.user_habit_info.protein_intake is not None:
            target_user.user_habit_info.protein_intake = updated_user.user_habit_info.protein_intake
        if updated_user.user_habit_info.meat_vegetable_ratio is not None:
            target_user.user_habit_info.meat_vegetable_ratio = updated_user.user_habit_info.meat_vegetable_ratio
        if updated_user.user_habit_info.dietary_restrictions is not None:
            target_user.user_habit_info.dietary_restrictions = updated_user.user_habit_info.dietary_restrictions
        if updated_user.user_habit_info.cooking_method is not None:
            target_user.user_habit_info.cooking_method = updated_user.user_habit_info.cooking_method
    
    # 4. 更新心理信息
    if updated_user.user_psychology:
        if updated_user.user_psychology.physical_reaction_index is not None:
            target_user.user_psychology.physical_reaction_index = updated_user.user_psychology.physical_reaction_index
        if updated_user.user_psychology.sleep_cognition_bias is not None:
            target_user.user_psychology.sleep_cognition_bias = updated_user.user_psychology.sleep_cognition_bias
        if updated_user.user_psychology.exercise_stress_value is not None:
            target_user.user_psychology.exercise_stress_value = updated_user.user_psychology.exercise_stress_value
        if updated_user.user_psychology.emotion_stress_index is not None:
            target_user.user_psychology.emotion_stress_index = updated_user.user_psychology.emotion_stress_index


# ___________________注册/登录_________________________

# 登录验证:未完成
def authenticate_user(username: str, password: str) -> Optional[User]:
    """
        验证用户名和密码是否匹配,返回User对象或None
    """
    if db_user_exists(username=username) and db_authenticate_user(username=username, password=password):
            return db_get_user(username=username)
        

    
    # 3. 验证失败返回None
    return None

# 返回一个新user
def get_new_user(username: str, password: str)->User:
    return User(
        user_account_info=UserAccountInfo(
            username=username,
            password=password
        ),
        user_based_info=UserBasedInfo(),
        user_habit_info=UserHabitInfo(),
        user_psychology=UserPsychology()
    )

# 注册功能
def sign_up(username: str, password: str)->User:
    if username in users_db:
        raise HTTPException(status_code=400, detail="用户名已存在")
    new_uesr = get_new_user(username, password)
    users_db[username] = new_uesr
    return new_uesr

# ____________________AI_______________________________

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
        f"{'用户' if msg['sender'] == 'human' else 'AI'}：{msg['message']}"
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

# ai意见
def subjection(user_info: User) -> str:
    """根据用户信息生成健康建议"""
    API_BASE: str = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    API_KEY = os.getenv("DASHSCOPE_API_KEY")
    
    if not API_KEY:
        raise ValueError("请设置DASH_API_KEY环境变量")
    
    # 构建提示词
    prompt = build_prompt(user_info)
    
    # 调用API
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    
    payload = {
        "model": "qwen-max",
        "input": {
            "prompt": prompt
        },
        "parameters": {
            "temperature": 0.3,
            "top_p": 0.8
        }
    }
    
    try:
        response = requests.post(API_BASE, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()
        
        # 提取生成的文本
        if "output" in result and "text" in result["output"]:
            advices =result["output"]["text"]
            
            return re.findall(r'@([^&]+)&',advices)
        else:
            return "抱歉，未能生成健康建议。"
    except requests.exceptions.RequestException as e:
        return f"API请求错误: {str(e)}"

# 提示词生成
def build_prompt(user_info: User) -> str:
    """构建向API发送的提示词"""
    # 确定称呼
    gender_title = ""
    if user_info.user_based_info.gender == 1:
        gender_title = "先生"
    elif user_info.user_based_info.gender == 2:
        gender_title = "女士"
    else:
        gender_title = "朋友"
    
    name = user_info.user_based_info.real_name or user_info.user_account_info.username or "佚名"
    
    # 基本信息部分
    base_info = ""
    if user_info.user_based_info.height and user_info.user_based_info.weight:
        bmi = user_info.user_based_info.weight / ((user_info.user_based_info.height / 100) ** 2)
        base_info += f"您的身高是{user_info.user_based_info.height}cm，体重是{user_info.user_based_info.weight}kg，BMI为{round(bmi, 1)}。"
    
    # 健康习惯部分
    habit_info = ""
    if user_info.user_habit_info.daily_water:
        habit_info += f"您目前每天饮水量为{user_info.user_habit_info.daily_water}L。"
    if user_info.user_habit_info.sleep_duration:
        habit_info += f"睡眠时间为{user_info.user_habit_info.sleep_duration}小时。"
    if user_info.user_habit_info.exercise_amount:
        habit_info += f"运动频率为{user_info.user_habit_info.exercise_amount}。"
    
    # 饮食习惯部分
    diet_info = ""
    if user_info.user_habit_info.vegetable_fruit_intake:
        diet_info += f"果蔬摄入量为{user_info.user_habit_info.vegetable_fruit_intake}。"
    if user_info.user_habit_info.protein_intake:
        diet_info += f"蛋白质摄入量为{user_info.user_habit_info.protein_intake}。"
    if user_info.user_habit_info.meat_vegetable_ratio:
        diet_info += f"肉菜比例为{user_info.user_habit_info.meat_vegetable_ratio}。"
    if user_info.user_habit_info.dietary_restrictions:
        diet_info += f"饮食禁忌为{user_info.user_habit_info.dietary_restrictions}。"
    
    # 心理状态部分
    psychology_info = ""
    if user_info.user_psychology.emotion_stress_index:
        psychology_info += f"您的情绪压力指数为{user_info.user_psychology.emotion_stress_index}。"
    if user_info.user_psychology.physical_reaction_index:
        psychology_info += f"身体反应指数为{user_info.user_psychology.physical_reaction_index}。"
    if user_info.user_psychology.sleep_cognition_bias:
        psychology_info += f"睡眠认知偏差为{user_info.user_psychology.sleep_cognition_bias}。"
    if user_info.user_psychology.exercise_stress_value: 
        psychology_info += f"运动压力值为{user_info.user_psychology.exercise_stress_value}。"
    
    # 构建完整提示词
    prompt = f"""
        {name}{gender_title}，作为您的健康管家，根据您的个人信息，我为您给出如下健康建议：

        1. 根据健康指标：{base_info}{habit_info}
        2. 根据饮食指标：{diet_info}
        3. 根据心理指标：{psychology_info}

        从以下几个方面给出建议.
        1. 运动方面，
        2. 饮食方面，
        3. 睡眠方面，
        4. 心理方面。

        使用基本文本格式（有各种数字序号、换行等），不要使用markdown格式

        在每个方面的建议开始前加“@”，结束后"&"作为标记符号

        """
    
    return prompt.strip()



# /===========================================================
# =================路由定义====================================
# ===========================================================/



# 首页路由
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, current_user: Optional[User] = Depends(get_current_user)):

    # 获取当前用户
    if not current_user:
        # 如果未登录，重定向到登录页面
        print("未登录，重定向到登录页面")
        return templates.TemplateResponse("login.html", {"request": request})
    

    print("已登录，显示主页")
    
    # 传递
    # 1. 当前用户信息
    # 2. 所有用户列表

    return templates.TemplateResponse("index.html", {
        "request": request,
        "current_user": current_user,
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
    global active_users

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



# 显示注册页面
@app.get("/register")
async def show_register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


# 退出登录
@app.post("/logout")  # 改为POST方法
async def logout(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id and session_id in active_users:
        # 可选：获取用户名并清理关联数据（如临时会话缓存）
        # username = active_users[session_id]
        # if username in temp_data:  # 示例：清理临时数据
        #     del temp_data[username]
        del active_users[session_id]
    
    response = RedirectResponse(url="/login", status_code=303)
    # 删除cookie时指定与设置时一致的参数（确保正确删除）
    response.delete_cookie(
        key="session_id",
        httponly=True,
        samesite="Lax"
    )
    return response


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
    
    if db_user_exists(username=new_username):
        return JSONResponse(content={"status": "error", "message": "用户名已存在"})
    


    # 创建新用户
    new_user =  get_new_user(username=new_username, password=new_password)

    db_add_user(new_user)
    
    return JSONResponse(
        content={
            "status": "success",
            "username": new_username
            }
        )



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
            current_user=current_user.user_account_info.username,
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


# 注册处理 - 接收前端POST请求
@app.post("/register", response_class=JSONResponse)
async def handle_register(
    username: str = Form(...),
    password: str = Form(...)
):
    """
    处理用户注册请求
    - 接收前端传来的username和password
    - 验证用户是否已存在
    - 创建新用户并保存到数据库
    """
    try:
        # 检查用户名是否已存在
        if db_user_exists(username):
            return JSONResponse(
                content={"status": "error", "message": "用户名已存在"},
                status_code=400
            )
        
        # 创建新用户
        new_user = get_new_user(username=username, password=password)
        
        # 保存到数据库
        db_add_user(new_user)
        
        # 注册成功，返回成功响应
        return JSONResponse(
            content={
                "status": "success",
                "message": f"用户 {username} 注册成功",
                "username": username
            }
        )
    
    except Exception as e:
        # 处理异常情况
        logging.error(f"注册处理错误: {str(e)}")
        return JSONResponse(
            content={"status": "error", "message": "注册失败，请稍后重试"},
            status_code=500
        )




# 心理测试提交路由
@app.post("/submit-test")
async def submit_test(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user)
):
    global test

    if not current_user:
        raise HTTPException(status_code=401, detail="未登录")
    
    # 解析请求数据
    data = await request.json()
    answers = data.get('answers', {})

    # print(answers)
    
    if not answers:
        return JSONResponse(
            content={"status": "error", "message": "未提交任何答案"},
            status_code=400
        )


    cleaned_answers = {}
    for key, value in answers.items():
        cleaned_key = key.replace(" ", "").replace("　", "")
        cleaned_answers[cleaned_key] = value

    results = []
    
    # 遍历每个评估维度
    for dimension in test.dimensions:
        dim_name = dimension.name
        # dim_name = dimension["name"]
        total_score = 0
        
        # 计算当前维度总分
        for question in dimension.questions:
            answer_key = f"{dim_name}-{question.id}".replace(" ", "")
            if answer_key in cleaned_answers:
                total_score += cleaned_answers[answer_key]["score"]
        
        # 获取对应分数段的评估建议
        assessment = ""
        suggestion = ""
        for score_range in dimension.ranges:
            if score_range.min <= total_score <= score_range.max:
                assessment = score_range.assessment
                suggestion = score_range.suggestion
                break
        
        # 添加到结果集
        results.append({
            "dimension": dim_name,
            "score": total_score,
            "assessment": assessment,
            "suggestion": suggestion
        })

    assessment_list = [result["assessment"] for result in results]


    setPsychologyTestResult(user=current_user, result=assessment_list)


    # print(results)

    return JSONResponse(content={
        "status": "success",
        "results": results
    })





# 更新用户信息路由
@app.post("/update-user-info", response_class=JSONResponse)
async def update_user_info(
    updated_user: User,  # 接收前端发送的用户信息（使用User模型验证）
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    更新当前登录用户的信息
    - 接收前端发送的完整用户信息（包含所有子模型）
    - 仅允许已登录用户修改自己的信息
    """
    # 验证登录状态
    if not current_user:
        print("未登录，返回401")
        raise HTTPException(status_code=401, detail="未登录，请先登录")
    
    # 获取当前用户的用户名（作为users_db的键）

    current_username = user_get_username(current_user)

    if not current_username:
        print("当前用户信息不完整，返回400")
        raise HTTPException(status_code=400, detail="用户信息不完整")
    
    # 验证用户是否存在于数据库中
    if not db_user_exists(username=current_username):
        # 如果用户不存在，初始化一个新记录
        db_add_user(
            user=User(
                user_account_info=UserAccountInfo(),
                user_based_info=UserBasedInfo(),
                user_habit_info=UserHabitInfo(),
                user_psychology=UserPsychology()
            )
        )

    db_update_user(updated_user)



    return JSONResponse(
        content={
            "status": "success",
            "message": "用户信息更新成功",
            "user_info":  updated_user.model_dump()
        }
    )

# 生成管家意见
@app.post("/generate-advice")
async def generate_advice(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user)
    ):
    try:

        logging.info(f"开始生成管家意见")

        advices=subjection(current_user)

        

        logging.info(f"生成管家意见成功：{advices}")

        response = JSONResponse(
            content={"status": "success", "advices": advices}
        )
    
    except Exception as e:
        print(e)
        return JSONResponse(content={"status": "error", "message": "系统错误"})
    
