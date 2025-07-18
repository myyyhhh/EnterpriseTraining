import os
import json
import requests
import uuid
from datetime import datetime
from ..config import API_BASE, DEFAULT_MODEL, KEYWORDS, LOG_SAVE_PATH, chat_history

def generate_text(user_input: str, username: str) -> tuple[str, dict]:
    """生成AI回复并更新对话历史"""
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("请设置DASHSCOPE_API_KEY")

    # 构建带历史的提示词（简化版）
    history = chat_history.get(username, [])[-10:]  # 只保留最近10条
    history_prompt = "\n".join([f"{'用户' if m['sender']=='human' else 'AI'}：{m['message']}" for m in history])
    prompt = f"对话历史：{history_prompt}\n用户问：{user_input}\n请以健康管家身份回答"

    # 调用API
    response = requests.post(
        API_BASE,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        json={
            "model": DEFAULT_MODEL,
            "input": {"prompt": prompt},
            "parameters": {"temperature": 0.7}
        },
        timeout=30
    )
    response.raise_for_status()
    ai_answer = response.json()["output"]["text"]

    # 更新对话历史
    time_str = datetime.now().strftime("%H:%M:%S")
    chat_history.setdefault(username, []).extend([
        {"sender": "human", "message": user_input, "time": time_str},
        {"sender": "ai", "message": ai_answer, "time": time_str}
    ])
    return ai_answer, chat_history

def generate_advice(user_info) -> list[str]:
    """生成健康建议"""
    from ..utils.text_utils import build_prompt, extract_advice
    api_key = os.getenv("DASHSCOPE_API_KEY")
    prompt = build_prompt(user_info)
    
    response = requests.post(
        API_BASE,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        json={"model": DEFAULT_MODEL, "input": {"prompt": prompt}}
    )
    response.raise_for_status()
    return extract_advice(response.json()["output"]["text"])