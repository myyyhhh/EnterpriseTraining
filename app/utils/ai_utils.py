import os
import json
import uuid
import requests
from datetime import datetime
from typing import Dict, List, Tuple, Optional

from app.config import (
    AI_API_BASE,
    AI_MODEL,
    AI_TEMPERATURE,
    AI_MAX_TOKENS,
    LOG_SAVE_PATH
)
from app.models.user import User

def generate_text(
    user_input: str,
    current_user: str,
    model: Optional[str] = None,
    temperature: float = AI_TEMPERATURE,
    max_tokens: int = AI_MAX_TOKENS,
    chat_history: Optional[Dict[str, List[Dict[str, str]]]] = None
) -> Tuple[str, Dict[str, List[Dict[str, str]]]]:
    """带对话历史的AI文本生成"""
    # 初始化参数
    chat_history = chat_history or {}
    model = model or AI_MODEL
    KEYWORDS = ["病", "睡觉", "睡眠", "运动", "锻炼", "跑", "心情", "治疗"]
    
    # 初始化用户对话历史
    if current_user not in chat_history:
        chat_history[current_user] = []
    user_messages = chat_history[current_user][-10:]  # 保留最近10条
    
    # 构建带历史的提示词
    history_prompt = "\n".join([
        f"{'用户' if msg['sender'] == 'human' else 'AI'}：{msg['message']}"
        for msg in user_messages
    ])
    
    enhanced_prompt = (
        "以下规则优先级最高：\n"
        "1. 作为健康管家，只回答健康问题，结合对话历史理解上下文。\n"
        "2. 非健康问题返回：\"不好意思，我的定位是健康管家，更希望您对健康方面提问\"\n\n"
        f"用户[{current_user}]的对话历史：\n{history_prompt}\n\n"
        f"当前问题：{user_input}"
    )
    
    # 调用AI API
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("请设置DASHSCOPE_API_KEY环境变量")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": model,
        "input": {"messages": [{"role": "user", "content": enhanced_prompt}]},
        "parameters": {"temperature": temperature, "max_length": max_tokens}
    }
    
    try:
        response = requests.post(
            AI_API_BASE,
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        ai_answer = response.json()["output"]["text"]
    except Exception as e:
        raise RuntimeError(f"AI API调用失败: {str(e)}")
    
    # 更新对话历史
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    chat_history[current_user].extend([
        {"sender": "human", "message": user_input, "time": current_time},
        {"sender": "ai", "message": ai_answer, "time": current_time}
    ])
    
    # 关键字日志记录
    matched = [kw for kw in KEYWORDS if kw in user_input]
    if matched:
        os.makedirs(LOG_SAVE_PATH, exist_ok=True)
        log_data = {
            "timestamp": current_time,
            "user": current_user,
            "input": user_input,
            "keywords": matched
        }
        with open(f"{LOG_SAVE_PATH}/{uuid.uuid4()}.json", "w") as f:
            json.dump(log_data, f, ensure_ascii=False)
    
    return ai_answer, chat_history

def build_prompt(user: User) -> str:
    """构建健康建议提示词"""
    # 处理用户信息
    gender_title = "先生" if user.user_based_info.gender == 1 else \
                   "女士" if user.user_based_info.gender == 2 else "朋友"
    name = user.user_based_info.real_name or user.user_account_info.username or "佚名"
    
    # 拼接用户信息
    base_info = f"身高{user.user_based_info.height}cm，体重{user.user_based_info.weight}kg，" if \
                user.user_based_info.height and user.user_based_info.weight else ""
    
    habit_info = f"每日饮水{user.user_habit_info.daily_water}L，睡眠{user.user_habit_info.sleep_duration}小时，" if \
                 user.user_habit_info.daily_water and user.user_habit_info.sleep_duration else ""
    
    # 构建提示词
    return (
        f"{name}{gender_title}，作为健康管家，根据您的信息给出建议：\n"
        f"1. 基本信息：{base_info}{habit_info}\n"
        f"2. 心理状态：{user.user_psychology.emotion_stress_index}情绪压力，"
        f"{user.user_psychology.physical_reaction_index}躯体反应\n"
        "从运动、饮食、睡眠、心理4个方面给出建议，每个建议用@开头、&结尾标记。"
    )

def subjection(user: User) -> List[str]:
    """生成健康建议（调用AI）"""
    from re import findall
    prompt = build_prompt(user)
    api_key = os.getenv("DASHSCOPE_API_KEY")
    
    if not api_key:
        raise ValueError("请设置DASHSCOPE_API_KEY环境变量")
    
    response = requests.post(
        AI_API_BASE,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        json={
            "model": "qwen-max",
            "input": {"prompt": prompt},
            "parameters": {"temperature": 0.3}
        }
    )
    
    response.raise_for_status()
    advice_text = response.json()["output"]["text"]
    return findall(r'@([^&]+)&', advice_text)  # 提取建议内容